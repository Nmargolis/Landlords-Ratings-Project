"""Model and functions for Landlord Ratings project."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):

    __tablename__ = "Users"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fname = db.Column(db.String(30))
    lname = db.Column(db.String(30))
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return "<User user_id = {} fname = {} lname = {} email = {} password = {}>".format(self.user_id, self.fname, self.lname, self.email, self.password)


class Landlord(db.Model):

    __tablename__ = "Landlords"

    landlord_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fname = db.Column(db.String(30))
    lname = db.Column(db.String(30))

    def __repr__(self):
        return "<Landlord landlord_id = {} fname = {} lname = {}>".format(
            self.landlord_id, self.fname, self.lname)


class Address(db.Model):

    __tablename__ = "Addresses"

    address_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    street = db.Column(db.String(60))
    city = db.Column(db.String(30))
    state = db.Column(db.String(30))
    zipcode = db.Column(db.String(30))
    country = db.Column(db.String(30))
    unit = db.Column(db.String(30))

    def __repr__(self):
        return "<Address address_id = {} street = {} city = {} state= {} zipcode = {} country = {} unit = {}>".format(
            self.address_id, self.city, self.state, self.zipcode, self.country, self.unit)


class Review(db.Model):

    __tablename__ = "Reviews"

    review_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'))
    landlord_id = db.Column(db.Integer, db.ForeignKey('Landlords.landlord_id'))
    address_id = db.Column(db.Integer, db.ForeignKey('Addresses.address_id'))
    created_at = db.Column(db.DateTime)  # Is this how to do datetime? Should I do .utcnow?
    unit = db.Column(db.Integer)

    user = db.relationship('User', backref='reviews')
    landlord = db.relationship('Landlord', backref='reviews')
    address = db.relationship('Address', backref='reviews')

    def __repr__(self):
        return "<Review review_id = {} user_id = {} landlord_id = {} address_id = {} created_at = {} unit = {}>".format(
            self.user_id, self.landlord_id, self.address_id, self.created_at, self.unit)


class Convo(db.Model):

    __tablename__ = "Convos"

    convo_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    def __repr__(self):
        return "<Convo convo_id = {}>".format(self.convo_id)


class Userconvo(db.Model):

    __tablename__ = "Userconvos"

    userconvo_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'))
    convo_id = db.Column(db.Integer, db.ForeignKey('Convos.convo_id'))

    user = db.relationship('User', backref='userconvos')
    convo = db.relationship('Convo', backref='convos')

    def __repr__(self):
        return "<Userconvo userconvo_id = {} user_id = {} convo_id = {}>".format(
            self.userconvo_id, self.user_id, self.convo_id)


class Message(db.Model):

    __tablename__ = "Messages"

    message_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userconvo_id = db.Column(db.Integer, db.ForeignKey('Convos.convo_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'))
    sent_at = db.Column(db.DateTime) # maybe add utc.now

    userconvo = db.relationship('Userconvo', backref='messages')
    user = db.relationship('User', backref='messages')

    def __repr__(self):
        return "<Message message_id = {} userconvo_id = {} user_id = {} sent_at = {}>".format(
            self.message_id, self.userconvo, self.user_id, self.sent_at)


class Resource(db.Model):

    __tablename__ = "Resources"

    resource_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    url = db.Column(db.String(100))
    title = db.Column(db.String(30))
    description = db.Column(db.Text)
    city = db.Column(db.String(30))
    state = db.Column(db.String(30))
    country = db.Column(db.String(30))

    def __repr__(self):
        return "<Resource resource_id = {} url = {} title = {} description = {} city = {} state = {} country = {}>".format(
            self.resource_id, self.url, self.title, self.description, self.city, self.state, self.country)
  
##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///landlordratings.db'
    db.app = app
    db.init_app(app)



if __name__ == "__main__":

    from server import app

    connect_to_db(app)
    print "Connected to DB."
    db.create_all()


# Do I need to do this in two places??

