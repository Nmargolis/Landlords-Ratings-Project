"""Utility file to seed ratings database from MovieLens data in seed_data/"""


from model import User  # Landlord, Address, Review, Convo, Userconvo, Message, Building, Resource
from model import connect_to_db, db
from server import app
import datetime


def load_users():
    """Load users from u.user into database."""

#     print "Users"

    # Delete all rows in table to avoid adding duplicates
    User.query.delete()

#     # Read u.user file and insert data
    for row in open("data/u.users"):
        row = row.rstrip()
        print row
        user_id, fname, lname, email, password = row.split("|")

        user = User(user_id=user_id,
                    fname=fname,
                    lname=lname,
                    email=email,
                    password=password)

        # user = [user_id, fname, lname, email, password]

        print user

        # Add the user to the database
        db.session.add(user)

    # Commit all users to database
    db.session.commit()



if __name__ == "__main__":
    connect_to_db(app)

    # # In case tables haven't been created, create them
    db.create_all()

    # Import different types of data
    load_users()
