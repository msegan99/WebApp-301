from flask import Flask, request, redirect, render_template, abort

app = Flask(__name__)


@app.route('/')
def hello():
    #return "Hello 312"
    return redirect("/login")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("<html><body>chat page</body></html>")
    if request.method == 'POST':
        user = request.form["user"]
        passwordhash = request.form["password"]
        #hash the password and then store it in the database using hashlib
        return redirect("/mainpage")

@app.route('/createaccount')
def createAccount():
    return render_template("<html><body>create account page</body></html>")

@app.route('/mainpage')
def mainpage():
    return render_template("<html><body>main page</body></html>")

@app.route('/chatpage', methods=['GET', 'POST'])
def chat():
    if request.method == 'GET':
        return render_template("<html><body>chat page</body></html>")
    if request.method == 'POST':
        #if it was a form, you can access it on request.form
        return "wow you made a post request to me!"
    else:
        return abort(403)




if __name__ == '__main__':
    app.run(debug=True)
