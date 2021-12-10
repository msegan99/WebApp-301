import socketserver

import helper
import mongoMethods
import handleWebsocket
import HTTPpost
import HTTPget

import hashlib
import base64
import sys

from pymongo import MongoClient
websockets = [] # list of sockets that were upgraded and being held in a thread, it need not be stored in a database

class MyTCPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        self.data = self.request.recv(2048)
        notClosed = True # for websockets

        if (self.data.startswith(bytes("POST", 'ascii'))):
            #print(self.data)
            header = self.data.decode().split("\r\n\r\n", maxsplit=1)[0]
            body = self.data.split(bytes("\r\n\r\n", 'ascii'), maxsplit=1)[1]

            contentLength = helper.getContentLength(header)
            bytesRecieved = len(body)

            if contentLength > bytesRecieved:
                #then we need more information to complete the body
                while bytesRecieved < bodyLen:
                    #get the next set of bytes
                    self.data = self.request.recv(1024)
                    newBody = self.data
                    bytesRecieved += len(newBody)
                    body = b"".join([body, newBody])

                response = HTTPpost.processRequest(header, body)
                #response = httpServer.processRequest(b"".join([bytes(header, 'ascii'), body]))
                self.request.sendall(response)
            else:
                #then we have all we need in the first recieve
                response = HTTPpost.processRequest(header, body)
                self.request.sendall(response)


        if (self.data.startswith(bytes("GET", 'ascii'))):

            print(self.data.decode().split(" ", maxsplit=2)[1])
            if (self.data.decode().split(" ", maxsplit=2)[1] == "/websocket"):

                websockets.append(self)
                newWS = True
                sys.stdout.flush()
                sys.stderr.flush()

                header = self.data.split(bytes("\r\n\r\n", 'ascii'), maxsplit=1)[0].decode()
                response = handleWebsocket.responseUpgrade(header)

                self.request.sendall(response.encode())

                #needs to be handled still!!!!!!!!
                #for chat in httpServer.getChats():
                #    self.request.sendall(httpServer.createWebFrame(chat)) --- sends each chat message as a websocket frame
                #needs to be handled still !!!!!!!!!

                print("I'm about to go into a websocket loop")
                while (notClosed):
                    self.data = self.request.recv(2048) #maybe make this byte size bigger...?

                    # when client closes connection, stop the loop
                    if (self.data == b""):
                        print("Closing the websocket")
                        notClosed = False
                        websockets.remove(self)
                        break

                    newResponse = handleWebsocket.processWebFrame(self.data)
                    for ws in websockets:
                        ws.request.sendall(newResponse)


            else:
                # if generic get request
                response = HTTPget.processRequest(self.data)
                self.request.sendall(response)
        if notClosed:
            if (not self.data.startswith(bytes("GET", 'ascii')) and not self.data.startswith(bytes("POST", 'ascii'))):
                self.request.sendall(bytes(helper.generateHeader("404", "null", "null", "null"), 'ascii'))


if __name__ == "__main__":

    mongoMethods.dbInit()

    HOST, PORT = "localhost", 8000

    # Create the server, binding to localhost on port 9999
    with socketserver.ThreadingTCPServer((HOST, PORT), MyTCPHandler) as server:

        # interrupt the program with Ctrl-C
        print("\n\n\n\n")
        print("starting server")
        server.serve_forever()
