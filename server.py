"""Server for creating Flask app and handling routes"""

from flask import Flask, request, render_template, session, redirect, flash, jsonify
from flask_debugtoolbar import DebugToolbarExtension
import os
from jinja2 import StrictUndefined
from model import connect_to_db, db, User, Landlord, Building, Address, Review, Convo, Userconvo, Message
import mapbox
import pprint
import requests
from datetime import datetime


mapbox_token = os.environ['MAPBOX_TOKEN']
geocoder = mapbox.Geocoder(access_token=mapbox_token)
pp = pprint.PrettyPrinter(indent=4)


app = Flask(__name__)
app.secret_key = os.environ['SESSION_KEY']


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

    print "Im at lookup-by-name"
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


# @app.route('/process-address.json')
# def process_address():
#     """Get address input and return json with the matching places"""


@app.route('/process-rating', methods=['POST'])
def process_rating():
    """Get ratings from form and store them in reviews table"""

    user_id = session['user']
    landlord_id = request.form.get('landlord-id')

    street_number = request.form.get('street-number')
    street_name = request.form.get('street-name')
    city = request.form.get('city')
    state = request.form.get('state')
    country = request.form.get('country')
    zipcode = request.form.get('zipcode')

    moved_in_at = datetime.strptime(request.form.get('move-in'), "%Y-%m-%d")
    moved_out_at = datetime.strptime(request.form.get('move-out'), "%Y-%m-%d")

    rating1 = request.form.get('rating1')
    rating2 = request.form.get('rating2')
    rating3 = request.form.get('rating3')
    rating4 = request.form.get('rating4')
    rating5 = request.form.get('rating5')
    comment = request.form.get('comment')

    # Process address to check if it is already in the databse
    street = street_number + ' ' + street_name

    # Query for the address in the database that matches the street, city and state
    address = db.session.query(Address).filter(Address.street == street,
                                               Address.city == city,
                                               Address.state == state).first()
    if address:
        address_id = address.address_id

    # If the address is not in the database
    elif address is None:

        # Geocode to find lat and lng
        # Use center of San Francisco for proximity lat and lng
        proxim_lng = -122.4194155
        proxim_lat = 37.7749295
        req = 'https://api.mapbox.com/geocoding/v5/mapbox.places/{}.json?proximity={},{}&access_token={}'.format(street, proxim_lng, proxim_lat, mapbox_token)
        r = requests.get(req)
        json_response = r.json()
        # pp.pprint(json_response)

        feature_to_add = None

        # Isolate the feature in the city the user searched for
        for feature in json_response['features']:
            print 'iterating over json response'
            if city == feature['context'][1]["text"]:
                feature_to_add = feature
                break

        # If there are no features that match the city the user searched for
        if feature_to_add is None:
            flash("Can't find the street address you entered in the city you entered.")
            return "failed to find address"

        # Otherwise, continue the process to add the address to the database
        else:
            address = Address(street=street,
                              city=city,
                              state=state,
                              zipcode=zipcode,
                              country=country,
                              lng=feature_to_add['center'][0],
                              lat=feature_to_add['center'][1])

            db.session.add(address)
            db.session.commit()

            address_id = address.address_id

    # Add the review to the database

    review = Review(user_id=user_id,
                    landlord_id=landlord_id,
                    address_id=address_id,
                    moved_in_at=moved_in_at,
                    moved_out_at=moved_out_at,
                    created_at=datetime.utcnow(),
                    rating1=rating1,
                    rating2=rating2,
                    rating3=rating3,
                    rating4=rating4,
                    rating5=rating5,
                    comment=comment)

    db.session.add(review)
    db.session.commit()

    return "success"


@app.route('/send-message/<int:user_to>')
def send_message(user_to):
    """Initiate conversation if new, send message"""

    user_from = User.query.get(session['user'])
    user_to = User.query.get(user_to)

    user_from_convos = user_from.conversations
    user_to_convos = user_to.conversations

    # Convert to set for faster runtime
    user_to_convos = set(user_to_convos)

    # convo_exists = False

    existing_convo = None

    for convo in user_from_convos:
        if convo in user_to_convos:
            # convo_exists = True
            existing_convo = convo
            break

    return render_template('message.html', user_to=user_to.user_id, existing_convo=existing_convo)


@app.route('/process-new-message', methods=['POST'])
def process_message():
    """Create new convo, userconvos and message and store in database"""

    user_to_id = request.form.get('user-to')
    user_from_id = session['user']

    convo = Convo()
    db.session.add(convo)
    db.session.commit()

    # Get the convo_id to use in creating new userconvos
    convo_id = convo.convo_id

    new_userconvo_1 = Userconvo(user_id=user_from_id, convo_id=convo_id)
    db.session.add(new_userconvo_1)
    db.session.commit()

    new_userconvo_2 = Userconvo(user_id=user_to_id, convo_id=convo_id)
    db.session.add(new_userconvo_2)
    db.session.commit()

    userconvo_id = new_userconvo_1.userconvo_id

    # Create new message
    content = request.form.get('message')

    new_message = Message(userconvo_id=userconvo_id, sent_at=datetime.utcnow(), content=content)
    db.session.add(new_message)
    db.session.commit()

    return "success"



    # user_from = User.query.get('user_from_id')

    # user_to = User.query.get('user_to_id')

    # user_from_convos = db.session.query(Userconvo.convo_id).filter(Userconvo.user_id == user_from_id).all()
    # user_to_convos = db.session.query(Userconvo.convo_id).filter(Userconvo.user_id == user_to_id).all()

    # # user_from_convos = user_from.conversations
    # # user_to_convos = user_to.conversations

    # # # Convert to set for faster runtime
    # # user_to_convos = set(user_to_convos)

    # convo_exists = False



    # If not, create a convo and 2 userconvos add them to the database
    # if convo_exists is False:
    #     # Create new convo and add to database
    #     convo = Convo()
    #     db.session.add(convo)
    #     db.session.commit(convo)

    #     # Get the convo_id to use in creating new userconvos
    #     convo_id = convo.convo_id

    #     new_userconvo_1 = Userconvo(user_id=user_from_id, convo_id=convo_id)
    #     db.session.add(new_userconvo_1)
    #     db.session.commit()

    #     new_userconvo_2 = Userconvo(user_id=user_to_id, convo_id=convo_id)
    #     db.session.add(new_userconvo_2)
    #     db.session.commit()

    #     userconvo_id = new_userconvo_1.userconvo_id


        # Create 2 userconvos, each with the new convo id

        # Create message referencing convo_id

    # Add message to the database

    # convo_id = convo_id
    # user_id = user_from
    # sent_at = utc.now


if __name__ == "__main__":

    connect_to_db(app)
    app.run(debug=True)
