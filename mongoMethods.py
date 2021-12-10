from pymongo import MongoClient
import bcrypt
import helper

#initialize mongo
client=MongoClient()

def dbInit():
    #create tables if they don't already exist
    db=client['312ChatApp']
    collection=db['accounts']
    collectionTwo=db['inc']
    collectionThree=db['images']
    results=collectionTwo.find()
    print(results)
    if results == None or results == {} or len(list(results)) == 0:
        collectionTwo.insert_one({"inc": "1", "static": "1"})
    return 1

def addImage(imgName):
    db=client['312ChatApp']
    collection=db['images']
    results=collection.insert_one({"img":imgName})
    return 1

def imageExists(imgName):
    db=client['312ChatApp']
    collection=db['images']
    results=collection.find()
    for r in results:
        if imgName == r["img"]:
            return True
    return False

def doInc():
    db=client['312ChatApp']
    collection=db['inc']
    results=collection.find_one({"static": "1"})
    inc=results["inc"]
    incTwo=int(inc)+1
    collection.delete_one({"static":"1"})
    collection.insert_one({"inc":str(incTwo), "static":"1"})
    return incTwo

def getImage(user):
    db=client['312ChatApp']
    accountCollection=db['accounts']
    userDict=accountCollection.find_one({"username": user})
    image=userDict["image"]
    return image


def addAccount(username, password):
    db=client['312ChatApp']
    accountCollection=db['accounts']
    #hash password here
    hashedPassword=bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    docToInsert={ "username": username, "password": hashedPassword, "lastToken": "", "image": "default"}
    accountCollection.insert_one(docToInsert)
    return 1

def verifyToken(token):
    db=client['312ChatApp']
    accountCollection=db['accounts']
    cursor=accountCollection.find()
    for item in cursor:
        print(item)
        hashedToken=item["token"]
        if bcrypt.checkpw(token.encode(), hashedToken): #if tokens match we found the username this cookie is validating
            return True
    print("Did not find token to match")
    return False
"""
    db=client['312ChatApp']
    accountCollection=db['accounts']
    cursor=accountCollection.find()
    for item in cursor:
        print(item)
        hashedToken=item["token"]

        if bcrypt.checkpw(token, hashedToken): #if tokens match we found the username this cookie is validating
            return item["username"]
    return None
"""

#returns true or false if the user is a valid login
def verifyLogin(username, password):
    db=client['312ChatApp']
    accountCollection=db['accounts']
    hashedPassword=accountCollection.find_one({"username": username})
    if hashedPassword != None:
        passwordMatch=bcrypt.checkpw(password.encode(), hashedPassword["password"]) #true if passwords match/authed login. false otherwise
        return passwordMatch
    else:
        #user did not sign in successfully
        # this handles the case where the username was not in the database
        return False

#verify the account, then remove them from database
def deleteAccount(username, password):
    db=client['312ChatApp']
    accountCollection=db['accounts']
    if verifyLogin(client, username, password):
        accountCollection.remove({"username": username})

def updateImage(username, image):
    db=client['312ChatApp']
    accountCollection=db['accounts']
    userDict=accountCollection.find_one({"username": username})
    hashedPassword=userDict["password"]
    tok=userDict["token"]
    #hash token here
    accountCollection.delete_one({"username": username})
    docToInsert={ "username": username, "password":hashedPassword , "token": tok, "image":image}
    accountCollection.insert_one(docToInsert)
    return 1


def newUserToken(username, token):
    db=client['312ChatApp']
    accountCollection=db['accounts']
    userDict=accountCollection.find_one({"username": username})
    hashedPassword=userDict["password"]
    image=userDict["image"]
    #hash token here
    hashedToken=bcrypt.hashpw(token.encode(), bcrypt.gensalt())
    accountCollection.delete_one({"username": username})
    docToInsert={ "username": username, "password":hashedPassword , "token": hashedToken, "image":image}
    accountCollection.insert_one(docToInsert)
    print(accountCollection.find_one({"username": username}))
    
    return 1


def addPost(username, postMessage):
    db=client['312ChatApp']
    postCollection=db['posts']
    postDoc={"username": username, "postMessage": postMessage}
    postCollection.insert_one(postDoc)


def getUsername(token):
    db=client['312ChatApp']
    accountCollection=db['accounts']
    cursor=accountCollection.find()
    for item in cursor:
        print(item)
        hashedToken=item["token"]

        if bcrypt.checkpw(token.encode(), hashedToken): #if tokens match we found the username this cookie is validating
            return item["username"]
    return None

def getUsers(user):
    return 1
