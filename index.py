"""Contains main web app entry point."""


from flask import Flask


app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello world!'