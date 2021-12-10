from pymongo import MongoClient
import bcrypt

#initialize mongo
client=MongoClient()

def dbInit():
    #create tables if they don't already exist
    db=client['312ChatApp']
    collection=db['accounts']
    return 1

def addAccount(username, password):
    db=client['312ChatApp']
    accountCollection=db['accounts']
    #hash password here
    hashedPassword=bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    docToInsert={ "username": username, "password": hashedPassword, "lastToken": ""}
    accountCollection.insert_one(docToInsert)
    return 1

#returns true or false if the user is a valid login
def verifyLogin(username, password):
    db=client['312ChatApp']
    accountCollection=db['accounts']
    hashedPassword=accountCollection.find_one({"username": username})["password"]
    passwordMatch=bcrypt.checkpw(password.encode(), hashedPassword) #true if passwords match/authed login. false otherwise
    return passwordMatch

#verify the account, then remove them from database
def deleteAccount(username, password):
    db=client['312ChatApp']
    accountCollection=db['accounts']
    if verifyLogin(client, username, password):
        accountCollection.remove({"username": username})


def newUserToken(username, token):
    db=client['312ChatApp']
    accountCollection=db['accounts']
    hashedPassword=accountCollection.find_one({"username": username})["password"]
    #hash token here
    hashedToken=bcrypt.hashpw(token.encode(), bcrypt.gensalt())
    accountCollection.remove({"username": username})
    docToInsert={ "username": username, "password":hashedPassword , "token": hashedToken}
    accountCollection.insert_one(docToInsert)
    return 1


def addPost(username, postMessage):
    db=client['312ChatApp']
    postCollection=db['accounts']
    postDoc={"username": username, "postMessage": postMessage}
    postCollection.insert_one(postDoc)

