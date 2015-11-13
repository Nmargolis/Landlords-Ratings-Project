"""Model and functions for Landlord Ratings project."""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):

    __tablename__ = "Users"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fname = db.Column(db.String(30))
    lname = db.Column(db.String(30))
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(30), nullable=False)

    conversations = db.relationship('Convo',
                                    secondary='Userconvos',
                                    backref='users')

    messages = db.relationship('Message',
                               secondary='Userconvos',
                               backref='user')

    def __repr__(self):
        return "<User user_id = {} fname = {} lname = {} email = {} password = {}>".format(
            self.user_id, self.fname, self.lname, self.email, self.password)


class Landlord(db.Model):

    __tablename__ = "Landlords"

    landlord_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fname = db.Column(db.String(30))
    lname = db.Column(db.String(30))

    def __repr__(self):
        return "<Landlord landlord_id = {} fname = {} lname = {}>".format(
            self.landlord_id, self.fname, self.lname)

    def convert_to_dict(self):
        """Returns landlord object in dictionary form"""

        landlord_dict = {'landlord_id': self.landlord_id,
                        'fname': self.fname,
                        'lname': self.lname}

        return landlord_dict

    def get_geojson(self):
        """Returns GeoJSON of addresses and reviews associated with landlord"""

        features = []

        for address in self.addresses:
            addr_feature = address.return_geojson()
            features.append(addr_feature)

        geojson = {"features": [
                {
                    "type": "FeatureCollection",
                    "features": features
                }
                ]}

        return geojson



class Building(db.Model):

    __tablename__ = "Buildings"

    building_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30))


class Address(db.Model):

    __tablename__ = "Addresses"

    address_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    street = db.Column(db.String(60))
    city = db.Column(db.String(30))
    state = db.Column(db.String(30))
    zipcode = db.Column(db.String(30))
    country = db.Column(db.String(30))
    unit = db.Column(db.String(30))
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    building_id = db.Column(db.Integer, db.ForeignKey('Buildings.building_id'))

    building = db.relationship('Building', backref='addresses')
    landlords = db.relationship('Landlord',
                                secondary='Reviews',
                                backref='addresses')

    def __repr__(self):
        return "<Address address_id = {} street = {} city = {} state= {} zipcode = {} country = {} unit = {}>".format(
            self.address_id, self.street, self.city, self.state, self.zipcode, self.country, self.unit)

    def return_geojson(self):

        landlords = self.landlords

        # print landlords

        landlord_list = []

        for landlord in landlords:
            landlord_list.append(
                {
                    "landlord": "{} {}".format(landlord.fname, landlord.lname),
                    "averagerating": 4.5
                }
                )


        # print landlord_list
        return {
            "type": "Feature",
            "geometry": {
              "type": "Point",
              "coordinates": [
                self.lng,
                self.lat
              ]
            },
            "properties": {
            "address": self.street,
            "city": self.city,
            "country": self.country,
            "postalCode": self.zipcode,
            "state": self.state,
            "addressid": self.address_id,
            "landlords": landlord_list
            }
          }





class Review(db.Model):

    __tablename__ = "Reviews"

    review_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'))
    landlord_id = db.Column(db.Integer, db.ForeignKey('Landlords.landlord_id'))
    address_id = db.Column(db.Integer, db.ForeignKey('Addresses.address_id'))
    moved_in_at = db.Column(db.DateTime)
    moved_out_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime)
    rating1 = db.Column(db.Integer)
    rating2 = db.Column(db.Integer)
    rating3 = db.Column(db.Integer)
    rating4 = db.Column(db.Integer)
    rating5 = db.Column(db.Integer)
    comment = db.Column(db.Text)

    user = db.relationship('User', backref='reviews')
    landlord = db.relationship('Landlord', backref='reviews')
    address = db.relationship('Address', backref='reviews')

    def __repr__(self):
        return "<Review review_id = {} user_id = {} landlord_id = {} address_id = {} created_at = {}>".format(
            self.review_id, self.user_id, self.landlord_id, self.address_id, self.created_at)

    def convert_to_dict(self):
        """Returns review object in dictionary form"""

        review_dict = {'review_id': self.review_id,
                        'user_id': self.user_id,
                        'landlord_id': self.landlord_id,
                        'moved_in_at': self.moved_in_at,
                        'moved_out_at': self.moved_out_at,
                        'created_at': self.created_at,
                        'rating1': self.rating1,
                        'rating2': self.rating2,
                        'rating3': self.rating3,
                        'rating4': self.rating4,
                        'rating5': self.rating5,
                        'comment': self.comment}

        return review_dict


class Convo(db.Model):

    __tablename__ = "Convos"

    convo_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subject = db.Column(db.String(50))

    messages = db.relationship('Message',
                               secondary='Userconvos',
                               backref='conversation',
                               order_by='desc(Message.sent_at)')

    participants = db.relationship('User',
                                   secondary='Userconvos')

    def __repr__(self):
        return "<Convo convo_id = {} subject = {}>".format(self.convo_id, self.subject)

    # def get_participant_ids(self):
    #     """Return a list of participants in the conversation"""
    #     pass


class Userconvo(db.Model):
    """Association table between user and convo"""

    __tablename__ = "Userconvos"

    userconvo_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'))
    convo_id = db.Column(db.Integer, db.ForeignKey('Convos.convo_id'))

    user = db.relationship('User', backref='userconvos')
    convo = db.relationship('Convo', backref='userconvos')

    def __repr__(self):
        return "<Userconvo userconvo_id = {} user_id = {} convo_id = {}>".format(
            self.userconvo_id, self.user_id, self.convo_id)


class Message(db.Model):

    __tablename__ = "Messages"

    message_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userconvo_id = db.Column(db.Integer, db.ForeignKey('Userconvos.userconvo_id'))
    sent_at = db.Column(db.DateTime)  # maybe add utc.now
    content = db.Column(db.Text)
    read = db.Column(db.Boolean, default=False)

    userconvo = db.relationship('Userconvo', backref='messages')

    def __repr__(self):
        return "<Message message_id = {} userconvo_id = {} sent_at = {} content = {} read = {}>".format(
            self.message_id, self.userconvo_id, self.sent_at, self.content, self.read)


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
    # db.create_all()
