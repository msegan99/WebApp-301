import helper
import mongoMethods
import secrets





def processRequest(header, body):
    route = header.split(" ", maxsplit=2)[1]
    return createPostResponse(route, header, body)


def createPostResponse(route, header, body):
    print("started creating post response!")


    if route.startswith("/login"):
        formDict = helper.getFormData(header, body, ["username", "password"])
        username=formDict["username"]
        password=formDict["password"]
        print(formDict)
        authorized=mongoMethods.verifyLogin(username, password)
        if authorized:
            #update database with a new token for every valid login. (There shouldnt be a need to login if a valid token was sent already)
            token = secrets.token_urlsafe(50)
            mongoMethods.newUserToken(username, token)
            responseWithoutAuthCookie=(helper.generateHeader("301", "null", "null", "/chatpage"))+"\r\n"
            #add token cookie
            responseWithoutAuthCookie+="Set-Cookie: "+token+"\r\n"
            return bytes(responseWithoutAuthCookie, 'ascii')
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
