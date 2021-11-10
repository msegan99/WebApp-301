from flask import Flask
from pymongo import MongoClient

app = Flask(__name__)


@app.route('/')
def hello():
    return "Hello 312"


if __name__ == '__main__':
    app.run(debug=True)
