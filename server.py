"""Server for creating Flask app and handling routes"""

from flask import Flask, request, render_template, session, redirect, flash, jsonify
from flask_debugtoolbar import DebugToolbarExtension
import os
from jinja2 import StrictUndefined
from model import connect_to_db, db, User, Landlord, Building, Address, Review


app = Flask(__name__)
app.secret_key=os.environ['SESSION_KEY']


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
        return redirect('/account-home')

        # TO DO: decide whether to redirect to account-home
        # or figure out a way to give the option of logging out or going to account-home
        # Also decide whether to do this in jinja or here.
    else:
    #If not logged in, display form
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
    # TO DO: Deal with error if user does not exist. Redirect to sign up.

    if account is not None:

        # If the password entered matches the password assciated with the email in the database
        if account.password == password:

            # Get the user_id to add to the session
            user_id = account.user_id

            #Add user to session
            session['user'] = user_id
            return redirect('/account-home')
            # return redirect('/')

        # If they don't match, flash message and redirect back to /login
        else:
            flash('Email does not match password. Please try again.')
            return redirect('/login')

    else:
        flash('There is no account associated with that email. Please try again or sign up.')
        return redirect('/login')
        # To Do: Figure out how to give the option to try logging in again or sign up.


@app.route('/logout')
def process_logout():
    #Remove user from session
    if 'user' in session:
        session.pop('user')
        flash('successfully logged out')

    else:
        flash('You are not logged in.')

    # TO DO: Deal with keyerror that happens when there is no user in session
    #Flash message
    return render_template('index.html')


@app.route('/signup')
def display_signup_form():
    """Show sign-up form"""

    if 'user' in session:

        flash('You are already logged in. If you would like to sign up, please log out first.')
        return redirect('/')
    else:
        return render_template('signup.html')


@app.route('/process-signup', methods=['POST'])
def process_signup():
    """Process sign-up form"""

    #Get inputs from signup form
    fname = request.form.get('fname')
    lname = request.form.get('lname')
    email = request.form.get('email')
    password = request.form.get('password')

    #Check if email is already in the database.
    account = User.query.filter_by(email=email).first()

    # If email is not in the database, add the new user to the database
    if account is None:
        new_user = User(fname=fname, lname=lname, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash("You created an account. Please login to see your account home.")

    # Otherwise, flash message saying an account with that email already exists.
    else:
        flash("You already have an account. Please login to see your account home")
        # To Do: Figure out how to show two options: logout or account home.

    return redirect('/login')


@app.route('/account-home')
def display_account_home():
    # If user is logged in, show account home.
    if 'user' in session:
        user = User.query.get(session['user'])
        return render_template('account-home.html', user=user)

        return redirect('/')
    # Otherwise, flash message and redirect to login
    else:
        flash('You are not logged in. Please log in.')
        return redirect('/login')


@app.route('/lookup')
def display_lookup_page():
    """Show page with options to look up landlords"""

    return render_template('lookup.html')


@app.route('/lookup-by-address.json')
def find_landlords_by_address():
    """Query for landlords associated with address and return json object with landlords"""

    print "I'm at lookup-by-address"
    street = request.args.get('street')
    city = request.args.get('city')
    state = request.args.get('state')

    reviews = db.session.query(Review).join(Address).filter(Address.street == street,
                                                            Address.state == state,
                                                            Address.city == city).all()

    landlord_dict = {}

    for review in reviews:
        landlord = review.landlord
        landlord_dict[landlord.landlord_id] = landlord.convert_to_dict()

    return jsonify(landlord_dict)


@app.route('/lookup-by-name.json')
def find_landlords_by_name():
    """Query for landlords by name and return json object with landlords"""
    fname = request.args.get('fname')
    lname = request.args.get('lname')

    landlords = db.session.query(Landlord).filter(Landlord.fname == fname,
                                                  Landlord.lname == lname).all()
    print landlords

    landlord_dict = {}

    for landlord in landlords:
        landlord_dict[landlord.landlord_id] = landlord.convert_to_dict()

    return jsonify(landlord_dict)


@app.route('/landlord/<int:landlord_id>')
def display_landlord_page(landlord_id):
    """Show page with landlord info and ratings"""
    landlord = Landlord.query.get(landlord_id)

    return render_template('landlord.html', landlord=landlord)


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
