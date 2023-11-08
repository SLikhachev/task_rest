""" Simple test to check tht Flask application is installed correctly and worked """

from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    """ Test it """
    return 'Hello, World!'
