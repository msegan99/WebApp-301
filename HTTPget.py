import helper
import mongoMethods







def processRequest(data):
    route = data.decode().split(" ", maxsplit=2)[1]
    print("GET request on route: "+route)
    return createResponse(route, data)


def createResponse(route, data):
    print("I'm about to send a response for the route "+route)


    if route == "/":
        return bytes(helper.generateHeader("301", "null", "null", "/login"), 'ascii')


    if route == "/login":
        data = helper.getFile("login.html")
        return b"".join([bytes(helper.generateHeader("200", "text/html", data, "null"), 'ascii'), data])


    elif route == "/chatpage":
        dataStr = helper.getFile("chat.html").decode("UTF-8")
        #get token from cookie in data(data is wholeRequest)
        reqLines=(data.decode('UTF-8')).split("\r\n")
        token=""
        for line in reqLines:
            kvList=line.split(": ")
            if kvList[0]=="Cookie":
                kv=kvList[1]
                if kv.split("=")[0]=="token":
                    token=kv.split("=")[1]

        if token=="": #no token cookie
            htmlString=helper.generateHeader("200", "text/html", data, "null")
            return b"".join([bytes(htmlString, 'ascii'), data])

        else: 
            #get username from mongo using token
            username=mongoMethods.getUsername(token)
            #fill html template with username
            dataStr=dataStr.replace("@@", username)
            data=dataStr.encode('UTF-8')
            htmlString=helper.generateHeader("200", "text/html", data, "null")
            return b"".join([bytes(htmlString, 'ascii'), data])


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


    elif route.startswith("/image"):
        # get image list from datbase
        #IMAGE LIST WILL COME FROM DATABASE
        for img in imgList:
            #print("\n\n\n\n\n"+route+"\n\n\n\n\n\n\n")
            print("/image/"+img)

            if (("/image/"+img) == route):
                data = helper.getFile("image/"+img)
                return b"".join([bytes(helper.generateHeader("200", "image/jpeg", data, "null"), 'ascii'), data])
            else:
                print("we don't have that picture")
                return bytes(helper.generateHeader("404", "null", "null", "null"), 'ascii')


    else:
        # 404
        return bytes(helper.generateHeader("404", "null", "null", "null"), 'ascii')
    # another 404 just in case cause why not
    return bytes(helper.generateHeader("404", "null", "null", "null"), 'ascii')
