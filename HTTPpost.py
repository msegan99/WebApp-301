import helper







def processRequest(header, body):
    route = header.split(" ", maxsplit=2)[1]
    return createPostResponse(route, header, body)


def createPostResponse(route, header, body):
    print("started creating post response!")


    if route.startswith("/login"):
        formDict = helper.getFormData(header, body, ["username", "password"])
        print(formDict)
        return bytes(helper.generateHeader("301", "null", "null", "/chatpage"), 'ascii')



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
        #hash the password and stuff
        #do stuff with the credentials, like database stuff

        #redirect to login if credentials are added
        return bytes(helper.generateHeader("301", "null", "null", "/login"), 'ascii')



    elif route.startswith("/image"):
        return bytes(helper.generateHeader("404", "null", "null", "null"), 'ascii')
    else:
        return bytes(helper.generateHeader("404", "null", "null", "null"), 'ascii')
