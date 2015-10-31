"""Server for creating Flask app and handling routes"""

from flask import Flask, request, render_template, session, redirect, flash
from flask_debugtoolbar import DebugToolbarExtension
import os
from jinja2 import StrictUndefined
from model import connect_to_db, db


app = Flask(__name__)
# app.secret_key=os.environ['SESSION_KEY']


@app.route('/')
def display_homepage():
    """Show homepage"""
    return render_template('index.html')


@app.route('/login')
def display_login_form():
    """Show login form"""

    #If logged in, alert user. Provide option to logout and login as a different user
    if 'user' in session:
        flash('You are already logged in')
    # Should I do this in jinja and use javascript alerts?

    #If not logged in, display form
    #Also display option to sign up and redirect to /signup
    #This may be in jinja, not in the route.

    return render_template('login.html')


@app.route('/process-login', methods=['POST'])
def process_login():
    """Process login form"""

    # Get form input
    email = request.form.get('email')
    password = request.form.get('password')

    # Find the associated user from the databse
    account = User.query.filter_by(email=email).first()

    # Get the password associated with that email and check if it matches password input

    # Get the user_id to add to the session
    user_id = account.user_id
   
    #Check if username/email and password match
    #If they don't match, flash message or alert and redirect back to /login
    #Add user to session

    return render_template('account-home.html')


@app.route('/logout')
def process_logout():
    #Remove user from session
    #Flash message
    return render_template('index.html')


@app.route('/signup')
def display_signup_form():
    """Show sign-up form"""

    #Check if user logged in. If logged in, give option to logout
    #^Maybe do in jinja

    return render_template('signup.html')


@app.route('/process-signup', methods=['POST'])
def process_signup():
    """Process sign-up form"""

    #Get inputs from signup form
    #Check if email is already in the database.
    #If email already associated with account,
    #   flash/alert message with 2 options:
    #      login and redirect to '/login'
    #       Or signup with a different email and redirect back to '/signup'
    #Otherwise, add user to database

    #return render_template('account-home.html')
    pass


@app.route('/lookup')
def display_lookup_page():
    """Show page with options to look up landlords"""

    return render_template('lookup.html')


@app.route('/landlord')
def display_landlord_page():
    """Show page with landlord info and ratings"""

    return render_template('landlord.html')


@app.route('/rate')
def display_rating_form():
    """Show form for rating landlord"""

    return render_template('rate.html')


@app.route('/send-message')
def send_message_():
    """Initiate conversation if new, send message"""

    pass

if __name__ == "__main__":

    connect_to_db(app)
    app.run(debug=True)
