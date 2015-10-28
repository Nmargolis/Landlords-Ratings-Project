"""Server for creating Flask app and handling routes"""

# from jinja2 import StrictUndefined

from flask import Flask, request, render_template, session

from flask_debugtoolbar import DebugToolbarExtension

# from model import connect_to_db, db


app = Flask(__name__)
app.secret_key=SESSIONKEY




if __name__ == "__main__":
    app.run(debug=True)