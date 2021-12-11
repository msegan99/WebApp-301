import helper
import mongoMethods
import secrets
import HTTPget





def processRequest(header, body):
    route = header.split(" ", maxsplit=2)[1]
    return createPostResponse(route, header, body)


def createPostResponse(route, header, body):
    print("started creating post response!")

    if route.startswith("/image"):
        tok = HTTPget.doAuth(header)
        if (tok != ""):
            user=mongoMethods.getUsername(tok)
            data = helper.getImg(header, body)
            file = helper.uploadImage(data)
            print(file)
            mongoMethods.addImage(file)
            mongoMethods.updateImage(user, file)
            data = helper.getFile("account.html")
            return b"".join([bytes(helper.generateHeader("200", "text/html", data, "null"), 'ascii'), data])


    elif route.startswith("/login"):
        formDict = helper.getFormData(header, body, ["username", "password"])
        username=formDict["username"]
        password=formDict["password"]
        print(formDict)
        authorized=mongoMethods.verifyLogin(username, password)
        if authorized:
            #update database with a new token for every valid login. (There shouldnt be a need to login if a valid token was sent already)
            token = secrets.token_urlsafe(50)
            a = mongoMethods.newUserToken(username, token)
            print("I did it"+ str(a))
            htmlString=helper.getFileString("chat.html")
            htmlString=htmlString.replace("@@", username)
            length=len(htmlString)
            response=("HTTP/1.1 200 OK\r\n" +
                                        "Content-Type: text/html\r\n" +
                                        "X-Content-Type-Options: nosniff\r\n" +
                                        "Set-Cookie: token="+token+"\r\n"
                                        "Content-Length: "+str(length)+"\r\n\r\n" +
                                        htmlString)
            #add token cookie
            return bytes(response, 'ascii')
        else:
            #redirect to/login. login was not verified
            return bytes(helper.generateHeader("301", "null", "null", "/login"), 'ascii')



    elif route.startswith("/register"):
        formDict = helper.getFormData(header, body, ["username", "password"])
        print(formDict)
        #now do something with the formDict
        if len(formDict) != 2:
            return bytes(helper.generateHeader("404", "null", "null", "null"), 'ascii')
        if formDict["username"] == "" or formDict["password"] == "":

            #temporary redirect to register again
            return bytes(helper.generateHeader("301", "null", "null", "/register"), 'ascii')
        username = formDict["username"]
        password = formDict["password"]
        #insert account into database(addAccount method will hash password)
        mongoMethods.addAccount(username, password)

        #redirect to login if credentials are added
        return bytes(helper.generateHeader("301", "null", "null", "/login"), 'ascii')



    elif route.startswith("/image"):
        return bytes(helper.generateHeader("404", "null", "null", "null"), 'ascii')
    else:
        return bytes(helper.generateHeader("404", "null", "null", "null"), 'ascii')
