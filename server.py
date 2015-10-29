"""Server for creating Flask app and handling routes"""

from flask import Flask, request, render_template, session
from flask_debugtoolbar import DebugToolbarExtension
import os
from jinja2 import StrictUndefined
from model import connect_to_db, db


app = Flask(__name__)
# app.secret_key=os.environ['SESSION_KEY']


@app.route('/')
def display_homepage():
    return render_template('index.html')



if __name__ == "__main__":
    app.run(debug=True)
