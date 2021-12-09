from pymongo import MongoClient, Document
import bcrypt

def dbInit(client):
    #create tables if they don't already exist
    db=client['312ChatApp']
    collection=db['accounts']
    return 1

def addAccount(client, username, password):
    db=client['312ChatApp']
    accountCollection=db['accounts']
    #hash password here
    hashedPassword=bcrypt.hashpw(password, bcrypt.gensalt())
    docToInsert={ "username": username, "password": hashedPassword}
    accountCollection.insert_one(docToInsert)
    return 1

def verifyLogin(client, username, password):
    db=client['312ChatApp']
    accountCollection=db['accounts']
    hashedPassword=accountCollection.find({"username": username})["password"]
    passwordMatch=bcrypt.checkpw(password, hashedPassword) #true if passwords match/authed login. false otherwise
    return passwordMatch
