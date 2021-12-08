from flask import Flask, request, redirect, render_template, abort, session
from flask_socketio import SocketIO, send, emit
from flask_session import Session
import json
from pymongo import MongoClient
import bcrypt, secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_urlsafe(16)
app.config['SESSION_TYPE']='filesystem'
Session(app)
socketio=SocketIO(app)
client= MongoClient('localhost', 27017)
db=client["312ProjectDatabase"]
accountCollection=db["accountCollection"]
postCollection=db["chatCollection"]
currentUserCollection=db["currentUserCollection"]

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
            passwordMatch=bcrypt.checkpw(password, hashedPassword)
            if passwordMatch: #SUCCESSFUL login. password keys match
                print("Successful login!")
                session['username']=username
                return redirect('/chatpage')

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
            hashedPassword=bcrypt.hashpw(password, bcrypt.gensalt())
            document={ "username": username, "password": hashedPassword}
            accountCollection.insert(document)
            session['username']=username
            return redirect('/chatpage')

@app.route('/chatpage', methods=['GET', 'POST'])
def chat():
    if request.method == 'GET':
        return render_template("chat.html", username=session['username'])
    if request.method == 'POST':
        postMessage=request.form["postBox"]
        document={"username": session['username'], "post": postMessage}
        postCollection.insert_one(document)
        return redirect('/chatpage')
    else:
        return abort(403)


@app.route('/chat.js', methods=['GET'])
def chatjs():
    if request.method == 'GET':
        return render_template("chat.js")
    else:
        return abort(404)

@app.route('/account', methods=['GET', 'POST'])
def account():
    # for some methods we should double check that a client is logged in, because that is a security feature in the project requirements
    # we can double check by going through a dictionary of users mapped to their addresses,

    # this dictionary contains all currently logged in users and if their address matches
    # the user, we know it's legit, because they were authenticated when the key value pair was added to the dictionary
    if request.method == 'GET':
        return render_template("account.html")
    elif request.method == 'POST':
        # updating profile picture
        return "" #probably some status code
    else:
        return abort(403)


@socketio.on('user connected')
def test_connect(auth):
    #update current user list
    userDoc={ "username": session['username']}
    currentUserCollection.insert_one(userDoc)
    currentUserListCursor=currentUserCollection.find()
    currentUserListStr=""
    doc=next(currentUserListCursor, None)
    while doc :
        user=doc['username']
        currentUserListStr+=(user+", ")
        doc=next(currentUserListCursor, None)

    #update current chat. send over current chat log
    currentChatCursor=postCollection.find()
    currentChatStr=""
    doc2=next(currentChatCursor, None)
    while doc2 :
        user2=doc2['username']
        postMessage=doc2['post']
        currentChatStr+=(user2+": "+postMessage+"<br>")
        doc2=next(currentChatCursor, None)



    emit('username joined', {'username': session['username'], 'currentUserList': currentUserListStr, 'currentChat': currentChatStr}, broadcast=True)

@socketio.on('disconnect')
def test_disconnect():
    userDoc={"username": session['username']}
    currentUserCollection.deleteOne(userDoc)
    currentUserListCursor=currentUserCollection.find()
    currentUserListStr=""
    doc=next(currentUserListCursor, None)
    while doc :
        user=doc['username']
        currentUserListStr+=(user+", ")
        doc=next(currentUserListCursor, None)

    emit('username left', {'username': session['username'], 'currentUserList': currentUserListStr}, broadcast=True)
    print('Client disconnected')





if __name__ == '__main__':
    socketio.run(app,debug=True)
