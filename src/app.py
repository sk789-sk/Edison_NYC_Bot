from flask import Flask, make_response, jsonify, request, session

from config import app, db
from models import *

@app.route('/')
def home():
    return 'testing'


if __name__ == '__main__':

    app.run(port=5557, debug=True) 