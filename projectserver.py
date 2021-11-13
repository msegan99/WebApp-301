from flask import Flask, request, redirect, render_template, abort
from pymongo import MongoClient
import hashlib, os

app = Flask(__name__)
client= MongoClient('localhost', 27017)
db=client["312ProjectDatabase"]
accountCollection=db["accountCollection"]
chatCollection=db["chatCollection"]
userSalts={}

@app.route('/')
def hello():
    # return "Hello 312"
    return render_template("index.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]
        if(accountCollection.count_documents({"username": username})==1): #if this username exist
            accountDocument=accountCollection.find_one({"username": username})
            hashedPassword=accountDocument["password"]
            unhashedPasswordKey= hashedPassword[32:] #randomSalt was 32 bytes. key is the rest
            userSalt=userSalts[username]
            keyToCheck=hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), userSalt, 100000)

            if keyToCheck==unhashedPasswordKey: #SUCCESSFUL login. password keys match
                print("Successful login!")
                return redirect('/mainpage')
                
            else: #username exist, but wrong password given
                return redirect("/login")
            
        else: #No such username exists
            return redirect('/login')
        


@app.route('/register', methods=['GET', 'POST'])
def createAccount():
    if request.method=="GET": #if serving register.html
        return render_template("register.html")
    elif request.method=="POST": #if user is attempting to register from register page
        username=request.form["username"]
        password=request.form["password"]
        query= { "username": username }
        #***registering users validation should be here***
        if accountCollection.count(query)==1:  #if this username already exists just send back to register page for now
            return redirect('/register') 

        else: #successful register
            #Hash password and then add username and password to accountCollection
            randomSalt= os.urandom(32)
            userSalts[username]=randomSalt #store salt so we can verify login attempts
            saltkey = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), randomSalt, 100000)
            hashedPassword = randomSalt + saltkey 
            document={ "username": username, "password": hashedPassword}
            accountCollection.insert(document)
            return redirect('/mainpage')


@app.route('/mainpage')
def mainpage():
    return render_template("<html><body>main page</body></html>")


@app.route('/chatpage', methods=['GET', 'POST'])
def chat():
    if request.method == 'GET':
        return render_template("<html><body>chat page</body></html>")
    if request.method == 'POST':
        # if it was a form, you can access it on request.form
        return "wow you made a post request to me!"
    else:
        return abort(403)


if __name__ == '__main__':
    app.run(debug=True)
