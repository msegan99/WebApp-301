# (HW2)
# errors in/name/comment not working
# (Lecture 14) add security

# for TCP socket.
import socketserver
# for sha 1 hashing web socket key.
from hashlib import sha1
# for base 64 encoding accept
from base64 import b64encode
# for generating random image file names.
import random
# Database
from pymongo import MongoClient
# json
import json
# secrets, bcrypt, hashlib
import secrets
import bcrypt
import hashlib

# Variables
# dictionary for comments
comments = {}
# images uploaded
images = []
# GUID for web socket keys
GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
# WebSocket clients
websocket_clients = {}
active_users = []

# Database setup
my_client = MongoClient("mongodb://mongo:27017/")
my_db = my_client["mydatabase"]
# creating a collection for chat
chat_history = my_db["chat"]
# creating a collection for user accounts
user_accounts = my_db["useraccounts"]
# creating a collection for user IDs
user_IDs = my_db["useraccountIDs"]
user_IDs.insert_one({'id': 0})
# member accounts
members_accounts = my_db["member_accounts"]


class MyTCPHandler(socketserver.BaseRequestHandler):
    print("Server is listening for connections. . .")

    def handle(self):
        client_request = self.request.recv(1024)
        # separate headers and body
        blank_line_bytes = '\r\n\r\n'.encode()
        request_parts = client_request.split(blank_line_bytes)
        # headers in bytes
        headers = request_parts[0]
        # body in bytes
        # decoding headers
        headers_decoded = headers.decode()
        headers_dec_part = headers_decoded.split(" ", 1)
        req_type = headers_dec_part[0]

        if req_type == "GET":
            req_lines = headers_dec_part[1].split('\r\n')
            request_line = req_lines[0].split(' ')
            if request_line[0] == "/":
                token = "empty"
                username = ""
                # get the headers
                headers_processed = parse_headers(req_lines[1:], ": ")
                # check if headers contain cookie and update visits
                if "Cookie" in headers_processed:
                    cookies = headers_processed["Cookie"]
                    # this will give a list of all cookies set.
                    cookies_l = cookies.split('; ')
                    cookies_dict = parse_headers(cookies_l, "=")
                    if "id" in cookies_dict:
                        token_foo = cookies_dict['id']
                        hashed_token = hashlib.sha256(token_foo.encode()).hexdigest()
                        account = members_accounts.find_one({"id": hashed_token})
                        if account is not None:
                            username = account['username']
                            token = token_foo
                if token == "empty":
                    # redirect to login
                    redirect_response = f"HTTP1.1 301 Moved Permanently\r\nLocation: /login\r\n\r\n"
                    redirect_response = redirect_response.encode()
                    self.request.sendall(redirect_response)
                else:
                    with open('index.html', 'r') as file:
                        html_content = file.read()
                        file.close()
                    # adding chat
                    html_content
                    chat_index = html_content.find('{{chat}}')
                    chat_html = f'<h3>Welcome, {username}!</h3>' \
                                f'<div id="username" style="display:none;">{username}</div>' \
                                f'<label for="chat-comment">Chat: </label>' \
                                f'<input id="chat-comment" type="text" name="comment">' \
                                f'<button onclick="sendMessage()">Chat</button>' \
                                f'<div id="chat"></div><br/><br/><br/><br/><br/><br/><br/><br/><br/>' \
                                f'<br/><br/><br/>'
                    html_content = html_content[:chat_index] + chat_html + html_content[chat_index:]
                    html_content = html_content.replace("{{chat}}", "")
                    html_len = len(html_content)
                    home_response = f"HTTP1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: {html_len}" \
                                    f"\r\n\r\n{html_content}"
                    home_response_enc = home_response.encode()
                    self.request.sendall(home_response_enc)
            elif request_line[0] == "/About":
                with open('about.html', 'r') as ab_file:
                    ab_content = ab_file.read()
                    ab_file.close()
                ab_len = len(ab_content)
                ab_response = f"HTTP1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: {ab_len}\r\n\r\n" \
                              f"{ab_content}"
                ab_response_encoded = ab_response.encode()
                self.request.sendall(ab_response_encoded)
            elif request_line[0] == "/login":
                token = "empty"
                username = ""
                # get the headers
                headers_processed = parse_headers(req_lines[1:], ": ")
                # check if headers contain cookie and update visits
                if "Cookie" in headers_processed:
                    cookies = headers_processed["Cookie"]
                    # this will give a list of all cookies set.
                    cookies_l = cookies.split('; ')
                    cookies_dict = parse_headers(cookies_l, "=")
                    if "id" in cookies_dict:
                        token_foo = cookies_dict['id']
                        hashed_token = hashlib.sha256(token_foo.encode()).hexdigest()
                        account = members_accounts.find_one({"id": hashed_token})
                        if account is not None:
                            username = account['username']
                            token = token_foo
                if token == "empty":
                    with open('login.html', 'r') as file:
                        html_content = file.read()
                        file.close()
                    html_content = html_content.encode()
                    html_len = len(html_content)
                    hello_response = "HTTP1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\nContent-Length: " \
                                     f"{html_len}\r\n\r\n"
                    response_encoded = hello_response.encode() + html_content
                    self.request.sendall(response_encoded)
                else:
                    with open('index.html', 'r') as file:
                        html_content = file.read()
                        file.close()
                    # adding chat
                    chat_index = html_content.find('{{chat}}')
                    chat_html = f'<h3>Welcome, {username}!</h3>' \
                                f'<div id="username" style="display:none;">{username}</div>' \
                                f'<label for="chat-comment">Chat: </label>' \
                                f'<input id="chat-comment" type="text" name="comment">' \
                                f'<button onclick="sendMessage()">Chat</button>' \
                                f'<div id="chat"></div><br/><br/><br/><br/><br/><br/><br/><br/><br/>' \
                                f'<br/><br/><br/>'
                    html_content = html_content[:chat_index] + chat_html + html_content[chat_index:]
                    html_content = html_content.replace("{{chat}}", "")
                    html_len = len(html_content)
                    home_response = f"HTTP1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: {html_len}" \
                                    f"\r\n\r\n{html_content}"
                    home_response_enc = home_response.encode()
                    self.request.sendall(home_response_enc)
            elif request_line[0] == "/loginredirect":
                with open('loginredirect.html', 'r') as file:
                    html_content = file.read()
                    file.close()
                html_content = html_content.encode()
                html_len = len(html_content)
                hello_response = "HTTP1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\nContent-Length: " \
                                 f"{html_len}\r\n\r\n"
                response_encoded = hello_response.encode() + html_content
                self.request.sendall(response_encoded)
            elif request_line[0] == "/register":
                token = "empty"
                username = ""
                # get the headers
                headers_processed = parse_headers(req_lines[1:], ": ")
                # check if headers contain cookie and update visits
                if "Cookie" in headers_processed:
                    cookies = headers_processed["Cookie"]
                    # this will give a list of all cookies set.
                    cookies_l = cookies.split('; ')
                    cookies_dict = parse_headers(cookies_l, "=")
                    if "id" in cookies_dict:
                        token_foo = cookies_dict['id']
                        hashed_token = hashlib.sha256(token_foo.encode()).hexdigest()
                        account = members_accounts.find_one({"id": hashed_token})
                        if account is not None:
                            username = account['username']
                            token = token_foo
                if token == "empty":
                    with open('register.html', 'r') as file:
                        html_content = file.read()
                        file.close()
                    html_content = html_content.encode()
                    html_len = len(html_content)
                    hello_response = "HTTP1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\nContent-Length: " \
                                     f"{html_len}\r\n\r\n"
                    response_encoded = hello_response.encode() + html_content
                    self.request.sendall(response_encoded)
                else:
                    with open('index.html', 'r') as file:
                        html_content = file.read()
                        file.close()
                    # adding chat
                    chat_index = html_content.find('{{chat}}')
                    chat_html = f'<h3>Welcome, {username}!</h3>' \
                                f'<div id="username" style="display:none;">{username}</div>' \
                                f'<label for="chat-comment">Chat: </label>' \
                                f'<input id="chat-comment" type="text" name="comment">' \
                                f'<button onclick="sendMessage()">Chat</button>' \
                                f'<div id="chat"></div><br/><br/><br/><br/><br/><br/><br/><br/><br/>' \
                                f'<br/><br/><br/>'
                    html_content = html_content[:chat_index] + chat_html + html_content[chat_index:]
                    html_content = html_content.replace("{{chat}}", "")
                    html_len = len(html_content)
                    home_response = f"HTTP1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: {html_len}" \
                                    f"\r\n\r\n{html_content}"
                    home_response_enc = home_response.encode()
                    self.request.sendall(home_response_enc)
            elif request_line[0] == "/registerfailed":
                with open('registerfailed.html', 'r') as file:
                    html_content = file.read()
                    file.close()
                html_content = html_content.encode()
                html_len = len(html_content)
                hello_response = "HTTP1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\nContent-Length: " \
                                 f"{html_len}\r\n\r\n"
                response_encoded = hello_response.encode() + html_content
                self.request.sendall(response_encoded)
            elif request_line[0] == "/accountexists":
                with open('accountexists.html', 'r') as file:
                    html_content = file.read()
                    file.close()
                html_content = html_content.encode()
                html_len = len(html_content)
                hello_response = "HTTP1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\nContent-Length: " \
                                 f"{html_len}\r\n\r\n"
                response_encoded = hello_response.encode() + html_content
                self.request.sendall(response_encoded)
            elif request_line[0] == "/loginregistered":
                with open('loginregistered.html', 'r') as file:
                    html_content = file.read()
                    file.close()
                html_content = html_content.encode()
                html_len = len(html_content)
                hello_response = "HTTP1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\nContent-Length: " \
                                 f"{html_len}\r\n\r\n"
                response_encoded = hello_response.encode() + html_content
                self.request.sendall(response_encoded)
            elif request_line[0] == "/chatpage":
                token = "empty"
                username = ""
                # get the headers
                headers_processed = parse_headers(req_lines[1:], ": ")
                # check if headers contain cookie and update visits
                if "Cookie" in headers_processed:
                    cookies = headers_processed["Cookie"]
                    # this will give a list of all cookies set.
                    cookies_l = cookies.split('; ')
                    cookies_dict = parse_headers(cookies_l, "=")
                    if "id" in cookies_dict:
                        token_foo = cookies_dict['id']
                        hashed_token = hashlib.sha256(token_foo.encode()).hexdigest()
                        account = members_accounts.find_one({"id": hashed_token})
                        if account is not None:
                            username = account['username']
                            token = token_foo
                if token == "empty":
                    # redirect to login
                    redirect_response = f"HTTP1.1 301 Moved Permanently\r\nLocation: /login\r\n\r\n"
                    redirect_response = redirect_response.encode()
                    self.request.sendall(redirect_response)
                else:
                    with open('index.html', 'r') as file:
                        html_content = file.read()
                        file.close()
                    # adding chat
                    chat_index = html_content.find('{{chat}}')
                    chat_html = f'<h2>Active Users</h2>' \
                                f'<h3>Welcome, {username}!</h3>' \
                                f'<label for="chat-comment">Chat: </label>' \
                                f'<input id="chat-comment" type="text" name="comment">' \
                                f'<button onclick="sendMessage()">Send</button>' \
                                f'<div id="chat">' \
                                f'<div id="username" style="display:none;">{username}</div>'
                    html_content = html_content[:chat_index] + chat_html + html_content[chat_index:]
                    html_content = html_content.replace("{{chat}}", "")
                    users_index = html_content.find('<h2>You are the only one online!</h2>')
                    for user in active_users:
                        html_content = html_content[:users_index] + f'<h3>{user}</h3>' + html_content[users_index:]
                    html_content = html_content.replace("<h2>You are the only one online!</h2>", "")
                    html_len = len(html_content)
                    home_response = f"HTTP1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: {html_len}" \
                                    f"\r\n\r\n{html_content}"
                    home_response_enc = home_response.encode()
                    self.request.sendall(home_response_enc)
            elif request_line[0] == "/websocket":
                # req_lines[1] onwards are the headers.
                headers_dict = process_headers(req_lines)
                # Connection and Upgrade headers are assumed to be correct.
                key = headers_dict["Sec-WebSocket-Key"]
                # test from here
                key = (key + GUID).encode()  # encode removed the TypeError
                key_sha1 = sha1(key).digest()
                accept = b64encode(key_sha1)
                websocket_response = f"HTTP1.1 101 Switching Protocols\r\n" \
                                     f"Connection: Upgrade\r\n" \
                                     f"Upgrade: websocket\r\n" \
                                     f"Sec-WebSocket-Accept: "
                websocket_response = websocket_response.encode() + accept + "\r\n\r\n".encode()
                self.request.sendall(websocket_response)
                # add this client to clients list
                websocket_clients[self.client_address] = self.request
                WebSocket_Handle(self.client_address, self.request)
            elif request_line[0] == "/style.css":
                with open('style.css', 'r') as css_file:
                    css_content = css_file.read()
                    css_file.close()
                css_len = len(css_content)
                css_response = f"HTTP1.1 200 OK\r\nContent-Type: text/css\r\nContent-Length: {css_len}\r\n\r\n" \
                               f"{css_content}"
                css_response_encoded = css_response.encode()
                self.request.sendall(css_response_encoded)
            elif request_line[0] == "/frontend.js":
                with open('frontend.js', 'r') as js_file:
                    js_content = js_file.read()
                    js_file.close()
                js_len = len(js_content)
                js_response = f"HTTP1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\nContent-Type: " \
                              f"text/javascript\r\nContent-Length: {js_len}\r\n\r\n" \
                              f"{js_content}"
                js_response_encoded = js_response.encode()
                self.request.sendall(js_response_encoded)
            else:
                msg404 = "ERROR 404: Not Found\r\nThe requested resource is not available!"
                msg404_len = len(msg404)
                response404 = f"HTTP1.1 404 NOT FOUND\r\nContent-Type: text/plain\r\nContent-Length: {msg404_len}" \
                              f"\r\n\r\n{msg404}"
                response404_encoded = response404.encode()
                self.request.sendall(response404_encoded)
        elif req_type == "POST":
            # only get body when we get a POST request.
            body = request_parts[1]
            req = headers_dec_part[1].split(" ", 1)
            if req[0] == "/login":
                # decode the body and get email and username.
                body = body.decode()
                email, password = body.split('&')
                email = email.split('=')[1]
                email = email.replace("%3A", ":")
                email = email.replace("%2F", "/")
                email = email.replace("%3F", "?")
                email = email.replace("%23", "#")
                email = email.replace("%5B", "[")
                email = email.replace("%5D", "]")
                email = email.replace("%40", "@")
                email = email.replace("%21", "!")
                email = email.replace("%24", "$")
                email = email.replace("%26", "&")
                email = email.replace("%27", "'")
                email = email.replace("%28", "(")
                email = email.replace("%29", ")")
                email = email.replace("%2A", "*")
                email = email.replace("%2B", "+")
                email = email.replace("%2C", ",")
                email = email.replace("%3B", ";")
                email = email.replace("%3D", "=")
                email = email.replace("%25", "%")
                email = email.replace("%20", " ")
                email = email.replace("+", " ")
                password = password.split('=')[1]
                password = password.replace("%3A", ":")
                password = password.replace("%2F", "/")
                password = password.replace("%3F", "?")
                password = password.replace("%23", "#")
                password = password.replace("%5B", "[")
                password = password.replace("%5D", "]")
                password = password.replace("%40", "@")
                password = password.replace("%21", "!")
                password = password.replace("%24", "$")
                password = password.replace("%26", "&")
                password = password.replace("%27", "'")
                password = password.replace("%28", "(")
                password = password.replace("%29", ")")
                password = password.replace("%2A", "*")
                password = password.replace("%2B", "+")
                password = password.replace("%2C", ",")
                password = password.replace("%3B", ";")
                password = password.replace("%3D", "=")
                password = password.replace("%25", "%")
                password = password.replace("%20", " ")
                password = password.replace("+", " ")
                # check if the this email is already
                # check if an account exists.
                account = members_accounts.find_one({"username": email})
                if account is None:
                    # redirect to login
                    redirect_response = f"HTTP1.1 301 Moved Permanently\r\nLocation: /loginredirect\r\n\r\n"
                    redirect_response = redirect_response.encode()
                    self.request.sendall(redirect_response)
                else:
                    # logged in
                    token = secrets.token_urlsafe(40)
                    hashed_token = hashlib.sha256(token.encode()).hexdigest()
                    # get info
                    real_pass = account['password']
                    members_accounts.update_one({"username": email}, {"$set": {'id': hashed_token}})
                    if bcrypt.checkpw(password.encode(), real_pass):
                        active_users.append(email)
                        # send a response
                        reg_failed_res = f'HTTP1.1 301 Moved Permanently\r\n' \
                                         f'Location: /chatpage\r\n' \
                                         f'Set-Cookie: id={token}; Max-Age=3600; HttpOnly' \
                                         f'\r\n\r\n'
                        resp_enc = reg_failed_res.encode()
                        self.request.sendall(resp_enc)
                    else:
                        # redirect to login
                        redirect_response = f"HTTP1.1 301 Moved Permanently\r\nLocation: /loginredirect\r\n\r\n"
                        redirect_response = redirect_response.encode()
                        self.request.sendall(redirect_response)
            elif req[0] == "/register":
                # decode the body and get email and username.
                body = body.decode()
                email, password = body.split('&')
                email = email.split('=')[1]
                email = email.replace("%3A", ":")
                email = email.replace("%2F", "/")
                email = email.replace("%3F", "?")
                email = email.replace("%23", "#")
                email = email.replace("%5B", "[")
                email = email.replace("%5D", "]")
                email = email.replace("%40", "@")
                email = email.replace("%21", "!")
                email = email.replace("%24", "$")
                email = email.replace("%26", "&")
                email = email.replace("%27", "'")
                email = email.replace("%28", "(")
                email = email.replace("%29", ")")
                email = email.replace("%2A", "*")
                email = email.replace("%2B", "+")
                email = email.replace("%2C", ",")
                email = email.replace("%3B", ";")
                email = email.replace("%3D", "=")
                email = email.replace("%25", "%")
                email = email.replace("%20", " ")
                email = email.replace("+", " ")
                password = password.split('=')[1]
                password = password.replace("%3A", ":")
                password = password.replace("%2F", "/")
                password = password.replace("%3F", "?")
                password = password.replace("%23", "#")
                password = password.replace("%5B", "[")
                password = password.replace("%5D", "]")
                password = password.replace("%40", "@")
                password = password.replace("%21", "!")
                password = password.replace("%24", "$")
                password = password.replace("%26", "&")
                password = password.replace("%27", "'")
                password = password.replace("%28", "(")
                password = password.replace("%29", ")")
                password = password.replace("%2A", "*")
                password = password.replace("%2B", "+")
                password = password.replace("%2C", ",")
                password = password.replace("%3B", ";")
                password = password.replace("%3D", "=")
                password = password.replace("%25", "%")
                password = password.replace("%20", " ")
                password = password.replace("+", " ")
                # check if the this email is already registered.
                account = members_accounts.find_one({'username': email})
                if account is None:
                    if Check_Password(password):
                        # no record of user account
                        Register_User(email, password)
                        # send a response
                        reg_failed_res = f'HTTP1.1 301 Moved Permanently\r\nLocation: /loginregistered\r\n\r\n'
                        resp_enc = reg_failed_res.encode()
                        self.request.sendall(resp_enc)
                    else:
                        # send a response
                        reg_failed_res = f'HTTP1.1 301 Moved Permanently\r\nLocation: /registerfailed\r\n\r\n'
                        resp_enc = reg_failed_res.encode()
                        self.request.sendall(resp_enc)
                else:
                    # send a response
                    reg_failed_res = f'HTTP1.1 301 Moved Permanently\r\nLocation: /accountexists\r\n\r\n'
                    resp_enc = reg_failed_res.encode()
                    self.request.sendall(resp_enc)


# this function takes a list of headers divided by new line character,
# ignores the first element, and returns a dictionary of those headers.
def parse_headers(raw_headers, sep):
    headers = {}
    for i in raw_headers:
        key, val = i.split(sep)
        headers[key] = val
    return headers


# this function takes a list of headers divided by new line character,
# ignores the first element, and returns a dictionary of those headers.
def process_headers(raw_headers):
    headers = {}
    for i in range(1, len(raw_headers)):
        kv_pair = raw_headers[i].split(': ')
        headers[kv_pair[0]] = kv_pair[1]
    return headers


# this function is called when client connection is upgraded to a WebSocket connection.
def WebSocket_Handle(address, client):
    # send this user full chat history
    Chat_History(client)
    # loop keeps running for a WebSocket connection
    while True:
        # WebSocket frame received.
        frame = client.recv(1024)
        # extract the opcode
        try:
            opcode = frame[0] & 15
        except IndexError:
            print("client disconnected. . .")
            raise
        if opcode == 1:
            # list of unmasked payload bytes
            payload_unmasked = []
            # get first 7 bits of payload length, ignoring the mask bit
            payload_len = frame[1] & 127
            # check payload length
            if payload_len < 126:
                # get the mask bytes in a list.
                mask = [frame[2], frame[3], frame[4], frame[5]]
                # loop over the payload and unmask each byte and store it
                for i in range(0, payload_len):
                    i_mod = i % 4
                    unmasked_byte = frame[i + 6] ^ mask[i_mod]
                    if unmasked_byte == 60:
                        payload_unmasked.append(38)
                        payload_unmasked.append(108)
                        payload_unmasked.append(116)
                    elif unmasked_byte == 62:
                        payload_unmasked.append(38)
                        payload_unmasked.append(103)
                        payload_unmasked.append(116)
                    elif unmasked_byte == 38:
                        payload_unmasked.append(38)
                        payload_unmasked.append(97)
                        payload_unmasked.append(109)
                        payload_unmasked.append(112)
                    else:
                        payload_unmasked.append(unmasked_byte)
                # insert the chat in the database
                document = {'chat': payload_unmasked}
                chat_history.insert_one(document)
                # send this chat to every user
                Echo_Message(payload_unmasked)
            # payload 7 bits = 126, would never be 127 for the HW.
            else:
                # getting the actual payload length from next two bytes.
                payload_len = int.from_bytes([frame[2], frame[3]], byteorder="big")
                # get the mask bytes in a list
                mask = [frame[4], frame[5], frame[6], frame[7]]
                # loop over the payload and unmask each byte and store it
                for i in range(0, payload_len):
                    i_mod = i % 4
                    unmasked_byte = frame[i + 8] ^ mask[i_mod]
                    if unmasked_byte == 60:
                        payload_unmasked.append(38)
                        payload_unmasked.append(108)
                        payload_unmasked.append(116)
                    elif unmasked_byte == 62:
                        payload_unmasked.append(38)
                        payload_unmasked.append(103)
                        payload_unmasked.append(116)
                    elif unmasked_byte == 38:
                        payload_unmasked.append(38)
                        payload_unmasked.append(97)
                        payload_unmasked.append(109)
                        payload_unmasked.append(112)
                    else:
                        payload_unmasked.append(unmasked_byte)
                # insert the chat in the database
                document = {'chat': payload_unmasked}
                chat_history.insert_one(document)
                # send this chat to every user
                Echo_Message(payload_unmasked)
        else:
            websocket_clients.pop(address)


# this function takes a list of payload bytes and sends it to all connected clients.
def Echo_Message(message):
    payload_len = len(message)
    if payload_len < 126:
        headers = [129, payload_len & 127]
        frame = headers + message
        frame_bytes = bytes(frame)
        for client in websocket_clients.values():
            client.sendall(frame_bytes)
    else:
        len_bytes = payload_len.to_bytes(2, byteorder="big")
        headers = [129, 126, len_bytes[0], len_bytes[1]]
        frame = headers + message
        frame_bytes = bytes(frame)
        for client in websocket_clients.values():
            client.sendall(frame_bytes)


# this method takes a client information and sends whole chat history.
def Chat_History(client):
    # getting all documents from the chat collection
    chats = chat_history.find()
    for d in chats:
        pl = d['chat']
        payload_len = len(pl)
        if payload_len < 126:
            headers = [129, payload_len]
            frame = headers + pl
            frame_bytes = bytes(frame)
            client.sendall(frame_bytes)
        else:
            len_bytes = payload_len.to_bytes(2, byteorder="big")
            headers = [129, 126, len_bytes[0], len_bytes[1]]
            frame = headers + pl
            frame_bytes = bytes(frame)
            client.sendall(frame_bytes)


# this method takes email and password and creates a new account.
def Register_User(email, password):
    # generate a salt and hashed password.
    salt = bcrypt.gensalt()
    hashed_pass = bcrypt.hashpw(password.encode(), salt)
    # create a document and store it in the database.
    record = {"username": email, "password": hashed_pass, "salt": salt}
    members_accounts.insert_one(record)


# this method checks the password for all the requirements.
def Check_Password(password):
    # length
    ret_bool1 = False
    # uppercase
    ret_bool2 = False
    # lowercase
    ret_bool3 = False
    # digit
    ret_bool4 = False
    ret_bool5 = False

    # check the length
    if len(password) >= 8:
        ret_bool1 = True
        print("Password length: passed...\n")

    for char in password:
        if char.isupper():
            ret_bool2 = True
            print("Uppercase: passed...\n")
        elif char.islower():
            ret_bool3 = True
            print("Lowercase: passed...\n")
        elif char.isdigit():
            ret_bool4 = True
            print("Digit: passed...\n")
        else:
            ret_bool5 = True
            print("Special char: passed...\n")

    if ret_bool1 and ret_bool2 and ret_bool3 and ret_bool4 and ret_bool5:
        print("All requirements passed...")
        return True
    else:
        return False


if __name__ == "__main__":
    # tuple of host name, and port number that the server will bind to
    HOST = "0.0.0.0"
    PORT = 8080
    ADDR = (HOST, PORT)
    print(f"Starting server on {ADDR}")
    # creating the server that binds to ADDR
    with socketserver.ThreadingTCPServer(ADDR, MyTCPHandler) as server:
        # activating the server
        server.serve_forever()
