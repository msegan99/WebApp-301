


def sanitizeInput(input):
    l = len(input)
    newInput = ""
    for i in range(l):
        if input[i] == "<":
            newInput+="&lt"
        elif input[i] == ">":
            newInput+="&gt"
        elif input[i] == "&":
            newInput+="&amp"
        else:
            newInput+=input[i]
    return newInput


def sanitizePath(s):
    l = len(s)
    newS = ""
    for i in range(l):
        if not (s[i] == "/"):
            newS+=s[i]
    return newS


def getHeaderElement(header, someKey):
    return 1

# Given a header (string), a body (bytes), and a list of names inside a multipart form
# this returns the names given mapped to their values in the form data
def getFormData(header, body, nameList):
    returnDict={}
    headerLines = header.split("\r\n")
    bound = ""
    for line in headerLines:
        if line.startswith("Content-Type: "):
            print("the content type line is: " + line)
            type = line.split(" ", maxsplit=1)[1]
            if type.startswith("multipart/form-data; boundary="):
                bound = type.split("=", maxsplit=1)[1]
    fields = body.decode().split(bound)
    for field in fields:
        i = 0
        for l in field.split("\n"):
            print("index "+str(i)+": " + l)
            i+=1
            for n in nameList:
                if l.startswith("Content-Disposition: form-data; name=\""+n+"\""):
                    name = field.split("\n")[3].rstrip("\r")
                    returnDict[n] = name
    return returnDict


def uploadImage(file, data, caption):
    # file should be path sanitized
    #IMPLEMENT AN INCREMENTOR FROM DATABASE TO GENERATE FILE NAMES
    fi = open( ("image/" + file), "x")
    with open( ("image/" + file), "wb") as f:
        f.write(data)
        f.close()
    #imgList.append(file)
    return True


def copyFile(filename, newFilename):
    with open(filename, "rb") as file:
        b = file.read()
        with open(newFilename, "wb") as file2:
            file2.write(b)

def getFile(filename):
    #returns file data as bytes
    with open(filename, "rb") as f:
        return f.read()


def getContentLength(header):
    headerLines = header.split("\r\n")
    for line in headerLines:
        if line.startswith("Content-Length: "):
            return int(line.split(" ", maxsplit=1)[1])


def generateHeader(code, type, data, newPath):
    # generateHeader("200", "type", "datahere" as bytes, "null")
    head = "HTTP/1.1 "
    if code == "200":
        head+="200 OK\r\n"
        head+="Content-Type: "+type+"\r\n"
        head+="X-Content-Type-Options: nosniff\r\n"
        length = len(data)
        head+="Content-Length: "+str(length)+"\r\n\r\n"
        #head+=data
        return head
    elif code == "201":
        head+="201 Created\r\n"
        head+="Content-Type: "+type+"\r\n"
        head+="X-Content-Type-Options: nosniff\r\n"
        length = len(data)
        head+="Content-Length: "+str(length)+"\r\n\r\n"
        #head+=data
        return head
    elif code == "204":
        head+="204 No Content\r\n"
        head+="X-Content-Type-Options: nosniff\r\n"
        return head+"\r\n"
    elif code == "404":
        head+="404 Not Found\r\n"
        head+="Content-Type: text/plain\r\n"
        head+="X-Content-Type-Options: nosniff\r\n"
        head+="Content-Length: 36\r\n\r\nThe requested content does not exist"
        return head
    elif code == "301":
        head+="301 Moved Permanently\r\n"
        head+="X-Content-Type-Options: nosniff\r\n"
        head+="Content-Length: 0\r\nLocation: "+newPath
        return head
    elif code == "403":
        head+="403 Forbidden\r\n"
        head+="Content-Type: text/plain\r\n"
        head+="X-Content-Type-Options: nosniff\r\n"
        head+="Content-Length: 34\r\n\r\nThe requested content is forbidden"
        return head
    else:
        head+=""
