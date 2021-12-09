import hashlib
import base64






def responseUpgrade(header):
    response = "HTTP/1.1 "
    response+="101 Switching Protocols\r\n"
    response+="Connection: Upgrade\r\n"
    response+="Upgrade: websocket\r\n"
    headLines = header.split("\r\n")
    for line in headLines:
        if line.startswith("Sec-WebSocket-Key"):
            SecKey = line.split("Sec-WebSocket-Key: ", maxsplit=1)[1]
            SecKey+="258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
            theHash = hashlib.sha1(SecKey.encode()).digest()
            theBase = base64.b64encode(theHash)
            response+="Sec-WebSocket-Accept: "+ theBase.decode()+"\r\n\r\n"
            return response


def getByteArray(someByteArray, startIndex, EndIndex):
    returnArray = []
    i = startIndex
    while (i < EndIndex+1):
        returnArray.append(someByteArray[i])
        i+=1
    return returnArray



def performMask(mask, someBytes, extra):
    m1 = 0
    m2 = 0
    m3 = 0
    m4 = 0
    if extra == 0:
        m1 = (mask[0] ^ someBytes[0]).to_bytes(1, "big")
        m2 = (mask[1] ^ someBytes[1]).to_bytes(1, "big")
        m3 = (mask[2] ^ someBytes[2]).to_bytes(1, "big")
        m4 = (mask[3] ^ someBytes[3]).to_bytes(1, "big")
        return b"".join([m1, m2, m3, m4])
    elif extra == 1:
        m1 = (mask[0] ^ someBytes[0]).to_bytes(1, "big")
        return b"".join([b"", m1])
    elif extra == 2:
        m1 = (mask[0] ^ someBytes[0]).to_bytes(1, "big")
        m2 = (mask[1] ^ someBytes[1]).to_bytes(1, "big")
        return b"".join([m1, m2])
    elif extra == 3:
        m1 = (mask[0] ^ someBytes[0]).to_bytes(1, "big")
        m2 = (mask[1] ^ someBytes[1]).to_bytes(1, "big")
        m3 = (mask[2] ^ someBytes[2]).to_bytes(1, "big")
        return b"".join([m1, m2, m3])
    else:
        print("Something went horribly wrong")
        return b""



def createWebFrame(Data):
    returnFrame = b'\x81'
    payData = Data.encode()
    payload = len(payData)
    if payload <126:
        # len less than 126
        print("This should be less than 126 and have a zero at begining when convert to binary")
        print(payload.to_bytes(1, byteorder="big"))
        returnFrame = b"".join([returnFrame, payload.to_bytes(1, byteorder="big"), payData])
        return returnFrame
    else:
        # len is 126 or more
        print((126).to_bytes(1, byteorder="big"))
        returnFrame = b"".join([returnFrame, b'\x7e', payData])
    return returnFrame

def processWebFrame(byteArrayFrame):
    #take first byte and mask it with 15 to get opCode
    opCode = int(byteArrayFrame[0] & b'\x0f'[0])
    if opCode != 1:
        return b'\x00'
    #fin bit is assumed to be 1 for this hw
    #this means we won't get another frame with a continuation of data from the last
    #reserved bits are 000 for this hw
    #opcode is 1 for text for this hw
    #mask bit will be 1 when recieving from client


    #find frame length, will be represented in 7, 16, or 64 bits
    print("This should be 93: " + str(    int(b'\xDD'[0] & b'\x7f'[0])      )        ) #it checks out
    print("This should be 32639: " + str(     int.from_bytes(b'\x7f\x7f', byteorder="big")       )) #error :(
    print("This is: " + str( int.from_bytes(b'\x7f\x7f\x7f\x7f\x7f\x7f\x7f\x7f', byteorder="big")))


    payByteLen = int(byteArrayFrame[1] & b'\x7f'[0])
    nextByte = 2
    if payByteLen == 126:
        #then next 16 bits is the actual payload length
        payByteLen = int.from_bytes( b"".join([byteArrayFrame[2], byteArrayFrame[3]]), byteorder="big"  )
        nextByte = 4
    elif payByteLen == 127:
        #then next 64 bits is the actual payload length
        payByteLen = int.from_bytes( getByteArray(byteArrayFrame, 2, 9) , byteorder="big")
        nextByte = 10
    #next 4 bytes is mask (32 bits)
    mask = getByteArray(byteArrayFrame, nextByte, nextByte+3)
    nextByte+=4
    #now iterate over every 4 bytes with the mask
    payloads = 0
    extra = payByteLen % 4
    if extra == 0:
        payloads = payByteLen / 4
    else:
        payloads = (payByteLen - extra) / 4

    originalData = b""
    i = payloads
    while i > 0:
        original = performMask(mask, getByteArray(byteArrayFrame, nextByte, nextByte+3), 0)
        originalData = b"".join([originalData, original])
        nextByte+=4
        i=i-1
    if extra != 0:
        #print(mask)
        #print(getByteArray(byteArrayFrame, nextByte, nextByte+extra-1))
        # then account for the last extra payload bytes

        print("There were "+str(extra)+" extra bytes")
        original = performMask(mask, getByteArray(byteArrayFrame, nextByte, nextByte+extra-1), extra)
        originalData = b"".join([originalData, original])


    actualData = originalData.decode()
    print(actualData)

    #
    return createWebFrame(useData(helper.sanitizeInput(actualData)))



def useData(SomeData):

    User = ""
    Comm = ""
    theList = (SomeData.lstrip("{")).rstrip("}").split(",")
    for d in theList:
        keyVal = d.split(":",maxsplit=1)
        if keyVal[0] == "\"username\"":
            User = keyVal[1].strip("\"")
        elif keyVal[0] == "\"comment\"":
            Comm = keyVal[1].strip("\"")

    # DO SOMETHING WITH THIS INFO HERE! THIS IS WHERE UPVOTE FUNCTIONALITY SHOULD BE

    return ("{\"username\":\"" +User+ "\",\"comment\":\"" +Comm+ "\"}")
