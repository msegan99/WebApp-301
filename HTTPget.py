import helper
import mongoMethods



def niceTry(mess):
    htmlString=helper.generateHeader("200", "text/plain", mess.encode(), "null")
    return b"".join([bytes(htmlString, 'ascii'), mess.encode()])

def chatPage(token):
    #this should replace "/chatpage"
    #get username from mongo using token
    dataStr = helper.getFileString("chat.html")
    username=mongoMethods.getUsername(token)
    #fill html template with username
    dataStr=dataStr.replace("@@", username)
    data=dataStr.encode('UTF-8')
    htmlString=helper.generateHeader("200", "text/html", data, "null")
    return b"".join([bytes(htmlString, 'ascii'), data])


def doAuth(header):
    cookHeadVal = helper.getHeaderElement(header, "Cookie")
    print(cookHeadVal)
    if cookHeadVal == "":
        return ""
    authTok = helper.parseCookies(cookHeadVal)
    if authTok != "" and authTok != None:
        auth = mongoMethods.verifyToken(authTok)
        if auth:
            return authTok
        else:
            return ""
    return ""

def processRequest(data):
    route = data.decode().split(" ", maxsplit=2)[1]
    header = data.decode().split("\r\n\r\n", maxsplit=1)[0]
    print("GET request on route: "+route)
    return createResponse(route, header)


def createResponse(route, header):
    print("I'm about to send a response for the route "+route)


    if route == "/":
        return bytes(helper.generateHeader("301", "null", "null", "/login"), 'ascii')

    elif route.startswith("/image"):
        path = route.split("image/", maxsplit=1)[1]
        if mongoMethods.imageExists(path):
            return bytes(helper.generateHeader("404", "null", "null", "null"), 'ascii')
            data = helper.getFile("image/"+path)
            return b"".join([bytes(helper.generateHeader("200", "image/jpeg", data, "null"), 'ascii'), data])


    elif route == "/login":
        data = helper.getFile("login.html")
        #check their auth cookie
        tok = doAuth(header)
        if (tok != ""):
            return bytes(helper.generateHeader("301", "null", "null", "/chatpage"), 'ascii')
        else:
            return b"".join([bytes(helper.generateHeader("200", "text/html", data, "null"), 'ascii'), data])


    elif route == "/chatpage":
        tok = doAuth(header)
        if (tok != ""):
            print(True)
            return chatPage(tok)
        else:
            mess = "403: Nice try, but you need to be authenticated to view this page."
            return bytes(helper.generateHeader("403", "text/plain", mess, "null"), 'ascii')


    elif route == "/chat.js":
        data = helper.getFile("chat.js")
        return b"".join([bytes(helper.generateHeader("200", "text/javascript", data, "null"), 'ascii'), data])


    elif route == "/register":
        data = helper.getFile("register.html")
        return b"".join([bytes(helper.generateHeader("200", "text/html", data, "null"), 'ascii'), data])


    elif route == "/account":
        data = helper.getFile("account.html")
        return b"".join([bytes(helper.generateHeader("200", "text/html", data, "null"), 'ascii'), data])



    elif route == "/login.css":
        data = helper.getFile("login.css")
        return b"".join([bytes(helper.generateHeader("200", "text/css", data, "null"), 'ascii'), data])

    elif route == "/register.css":
        data = helper.getFile("register.css")
        return b"".join([bytes(helper.generateHeader("200", "text/css", data, "null"), 'ascii'), data])

    else:
        # 404
        return bytes(helper.generateHeader("404", "null", "null", "null"), 'ascii')
    # another 404 just in case cause why not
    return bytes(helper.generateHeader("404", "null", "null", "null"), 'ascii')
