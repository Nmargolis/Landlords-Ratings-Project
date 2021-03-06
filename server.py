"""Server for creating Flask app and handling routes"""

from flask import Flask, request, render_template, session, redirect, flash, jsonify
import os
from model import connect_to_db, db, User, Landlord, Address, Review, Convo, Userconvo, Message
import mapbox
import requests
from datetime import datetime
import pprint
# from flask_debugtoolbar import DebugToolbarExtension
# from jinja2 import StrictUndefined

mapbox_token = os.environ.get('MAPBOX_TOKEN')
geocoder = mapbox.Geocoder(access_token=mapbox_token)
pp = pprint.PrettyPrinter(indent=4)


app = Flask(__name__)
app.secret_key = os.environ.get('SESSION_KEY', 'ABCDEF')


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
        flash("Successfully created an account.")

        session['user'] = new_user.user_id
        return redirect('/account-home')

    # Otherwise, flash message saying an account with that email already exists.
    else:
        flash("You already have an account. Please login to see your account home")
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


@app.route('/lookup-by-address.json')
def find_landlords_by_address():
    """Query for landlords associated with address and return json object with landlords"""

    print "I'm at lookup-by-address"
    street = request.args.get('street')
    city = request.args.get('city')
    state = request.args.get('state')

    address_result = db.session.query(Address).filter(Address.street == street,
                                                 Address.state == state,
                                                 Address.city == city).first()

    if not address_result:
        return "found-no-addresses"

    else:
        reviews = address_result.reviews

        if not reviews:
            return"found-address-no-reviews"

        landlord_dict = {}

        for review in reviews:
            landlord = review.landlord
            landlord_dict[landlord.landlord_id] = landlord.convert_to_dict()

        #TO DO: also return GeoJSON for that address

        return jsonify(landlord_dict)


@app.route('/lookup-by-name.json')
def find_landlords_by_name():
    """Query for landlords by name and return json object with landlords"""

    print "Im at lookup-by-name.json route"
    fname = request.args.get('fname')
    lname = request.args.get('lname')

    landlords = find_landlords_by_name(fname, lname)

    if landlords:

        landlord_dict = {}

        for landlord in landlords:
            landlord_dict[landlord.landlord_id] = landlord.convert_to_dict()

        print landlord_dict

        return jsonify(landlord_dict)
    else:
        return "found-no-landlords"


@app.route('/landlord/<int:landlord_id>')
def display_landlord_page(landlord_id):
    """Show page with landlord info and ratings"""
    landlord = Landlord.query.get(landlord_id)

    return render_template('landlord.html', landlord=landlord)


@app.route('/get_landlord_geojson.json')
def get_landlord_geojson():
    """Returns geojson with all addresses and reviews for a landlord"""
    landlord_id = request.args.get('landlord-id')

    landlord = Landlord.query.get(landlord_id)
    # print landlord.get_geojson()

    return jsonify(landlord.get_geojson())


@app.route('/add-new-landlord.json', methods=['POST'])
def add_new_landlord():
    """Add new landlord to database"""
    print "At add-new-landlord"
    fname = request.form.get('fname-add')
    lname = request.form.get('lname-add')

    print "Adding {} {} as a landlord.".format(fname, lname)

    landlord = Landlord(fname=fname, lname=lname)

    db.session.add(landlord)
    db.session.commit()

    return "added-landlord"


@app.route('/process-rating2.json', methods=['POST'])
def process_rating2():
    """Get ratings from modal form and store them in reviews table"""
    print "At process-rating"

    user_id = session['user']

    # If landlord_id was passed as data, set it equal to landlord_id to be used in review
    landlord_id = request.form.get('landlord-id-field')
    if landlord_id:
        print "Received landlord_id: {}".format(landlord_id)

    if not landlord_id:

        fname = request.form.get('fname')
        lname = request.form.get('lname')

        # See if landlord exists in database as entered (case insensitive)
        landlord_result = db.session.query(Landlord).filter(db.func.lower(Landlord.fname) == db.func.lower(fname),
                                                            db.func.lower(Landlord.lname) == db.func.lower(lname)).first()

        # TO DO: change to .all() and return both, giving user option to choose

        if landlord_result:
            print "{} {} exists as a landlord.".format(fname, lname)
            landlord_id = landlord_result.landlord_id
        else:
            print "{} {} does not exist as a landlord as entered.".format(fname, lname)
            print "Searching for possible matches."

            # Use more flexible lookup to find possible matches
            landlord_results = find_landlords_by_name(fname, lname)

            # Return json object with landlord results
            if landlord_results:

                landlord_list = []

                for landlord in landlord_results:
                    landlord_list.append(landlord.convert_to_dict())

                landlord_dict = {'landlords': landlord_list}

                return jsonify(landlord_dict)

            else:
                return "found-no-landlords"
            # landlord = Landlord(fname=fname, lname=lname)

            # db.session.add(landlord)
            # db.session.commit()
            # flash("Successfully added {} {} as a landlord.".format(fname, lname))

    street = request.form.get('street-field')
    city = request.form.get('city')
    state = request.form.get('state')
    country = request.form.get('country')
    zipcode = request.form.get('zipcode')

    moved_in_at = request.form.get('move-in')
    moved_out_at = request.form.get('move-out')

    if moved_in_at:
        moved_in_at = datetime.strptime(moved_in_at, "%Y-%m-%d")

    else:
        moved_in_at = None

    if moved_out_at:
        moved_out_at = datetime.strptime(moved_out_at, "%Y-%m-%d")

    else:
        moved_out_at = None

    rating1 = request.form.get('rating1') or None
    rating2 = request.form.get('rating2') or None
    rating3 = request.form.get('rating3') or None
    rating4 = request.form.get('rating4') or None
    rating5 = request.form.get('rating5') or None
    comment = request.form.get('comment', None)

    # Query for the address in the database that matches the street, city and state
    address = db.session.query(Address).filter(Address.street.ilike("%"+street+"%"),
                                               Address.city.ilike("%"+city+"%"),
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
            # print json_response['features']
            print 'iterating over json response'
            if city == feature['context'][1]["text"]:
                feature_to_add = feature
                break

        # If there are no features that match the city the user searched for
        if feature_to_add is None:
            # flash("Can't find the street address you entered in the city you entered.")
            return "Address-not-valid"

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

    success = {'success': landlord_id}
    print success

    return jsonify(success)


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

    print existing_convo

    return render_template('message.html', user_to=user_to.user_id, existing_convo=existing_convo)


@app.route('/process-message-new', methods=['POST'])
def process_message_new():
    """Create new convo, userconvos and message and store in database"""

    user_to_id = request.form.get('user-to')
    user_from_id = session['user']
    subject = request.form.get('subject')

    convo = Convo(subject=subject)
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

    flash('Successfully started conversation and sent message.')
    return redirect('/account-home')


@app.route('/process-message-existing', methods=['POST'])
def process_message_existing():
    """Store message in database, associated with an existing userconvo"""

    convo_id = request.form.get('convo')
    sender_id = session['user']
    content = request.form.get('message')

    convo = Convo.query.get(convo_id)

    userconvos = convo.userconvos

    userconvo_id = None

    for userconvo in userconvos:
        if userconvo.user_id == sender_id:
            userconvo_id = userconvo.userconvo_id

    if userconvo_id is None:
        print "something weird happened."

    new_message = Message(userconvo_id=userconvo_id,
                          sent_at=datetime.utcnow(),
                          content=content)

    print new_message

    db.session.add(new_message)
    db.session.commit()

    flash('Successfully sent message.')

    return redirect('/account-home')


@app.route('/map')
def display_map():
    """Displays map.html"""

    return render_template('map.html')


@app.route('/all_addresses.json')
def get_addresses():
    """Returns geojson with all addresses and their reviews"""

    addresses = Address.query.all()

    features = []

    for address in addresses:
        features.append(address.return_geojson())

    geojson = {"features": [
                {
                    "type": "FeatureCollection",
                    "features": features
                }
                ]}

    return jsonify(geojson)


@app.route('/get_recent_reviews')
def get_recent_reviews():
    """Get a list of the 5 most recent reviews and return json object"""
    recent_reviews = db.session.query(Review).order_by(db.desc(Review.created_at)).limit(5).all()

    reviews_list = []
    for review in recent_reviews:
        reviews_list.append(review.convert_to_dict())

    reviews_dict = {'results': reviews_list}
    return jsonify(reviews_dict)


@app.route("/error")
def error():
    raise Exception("Error!")

#####################################################################
"""Helper functions"""

def find_landlords_by_name(fname=None, lname=None):
    """Returns a list of landlord objects that loosely match fname or lname in query"""

    print "At find landlords by name."
    print "Query: {} {}".format(fname, lname)

    # Query for landlords where fname or lname is like either of the fname or lname inputs
    if fname and lname:
        landlords = db.session.query(Landlord).filter(db.or_(Landlord.fname.ilike("%"+fname+"%"),
                                                             Landlord.fname.ilike("%"+lname+"%"),
                                                             Landlord.lname.ilike("%"+fname+"%"),
                                                             Landlord.lname .ilike("%"+lname+"%"))).all()

    elif fname and not lname:
        landlords = db.session.query(Landlord).filter(db.or_(Landlord.fname.ilike("%"+fname+"%"),
                                                             Landlord.lname.ilike("%"+fname+"%"))).all()

    elif lname and not fname:
        landlords = db.session.query(Landlord).filter(db.or_(Landlord.fname.ilike("%"+lname+"%"),
                                                             Landlord.lname.ilike("%"+lname+"%"))).all()

    else:
        print "Received no arguments"
        raise TypeError

    if landlords:
        for landlord in landlords:
            print "Found {} {}.\n".format(landlord.fname, landlord.lname)
        return landlords
    else:
        print "{} {} was not found.".format(fname, lname)
        return None

    # TO DO: Prioritize closest match

if __name__ == "__main__":

    connect_to_db(app)
    # db.create_all()
    PORT = int(os.environ.get("PORT", 5000))
    DEBUG = "NO_DEBUG" not in os.environ

    app.run(debug=DEBUG, host="0.0.0.0", port=PORT)
