from flask import Flask, request, redirect, render_template, abort
from werkzeug.exceptions import FailedDependency
from pymongo import MongoClient

app = Flask(__name__)
client= MongoClient('localhost', 27017)
db=client["312ProjectDatabase"]
accountCollection=db["accountCollection"]
chatCollection=db["chatCollection"]

@app.route('/')
def hello():
    # return "Hello 312"
    return render_template("index.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("<html><body>chat page</body></html>")
    if request.method == 'POST':
        user = request.form["user"]
        passwordhash = request.form["password"]
        # hash the password and then store it in the database using hashlib
        return redirect("/mainpage")


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
        else:
            #add username and password to accountCollection
            document={ "username": username, "password": password}
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
