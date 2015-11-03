"""Utility file to seed ratings database from MovieLens data in seed_data/"""


from model import User, Landlord, Address, Review, Convo, Userconvo, Message, Building, Resource
from model import connect_to_db, db
from server import app
import datetime


def load_users():
    """Load users from u.users into database."""

#     print "Users"

    # Delete all rows in table to avoid adding duplicates
    User.query.delete()

    # Read u.user file and insert data
    for row in open("data/u.users"):
        row = row.rstrip()

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

    # Commit all additons to database
    db.session.commit()


def load_landlords():
    """Load landlords from u.landlords into database."""

    # Delete all rows in table to avoid adding duplicates
    Landlord.query.delete()

    for row in open("data/u.landlords"):
        row = row.rstrip()

        landlord_id, fname, lname = row.split("|")

        landlord = Landlord(landlord_id=landlord_id,
                            fname=fname,
                            lname=lname)

        # Add the landlord to the database
        db.session.add(landlord)

        # Commit all additions to database
        db.session.commit()

def load_buildings():
    """Load buildings from u.buildings into database."""

    # Delete all rows in table to avoid adding duplicates
    Building.query.delete()

    for row in open("data/u.buildings"):
        row = row.rstrip()

        building_id, name = row.split("|")

        building = Building(building_id=building_id,
                            name=name)

        # Add the building to the database
        db.session.add(building)

        # Commit all additions to database
        db.session.commit()


def load_addresses():
    """Load addresses from u.addresses into database."""

    # Delete all rows in table to avoid adding duplicates
    Address.query.delete()

    for row in open("data/u.addresses"):
        row = row.rstrip()

        address_id, street, city, state, zipcode, country, unit, lat, lng, building_id = row.split("|")

        address = Address(address_id=address_id,
                            street=street,
                            city=city,
                            state=state,
                            zipcode=zipcode,
                            country=country,
                            unit=unit,
                            lat=lat,
                            lng=lng,
                            building_id=building_id)

    # Add the address to the database
    db.session.add(address)

    # Commit all additions to database
    db.session.commit()



if __name__ == "__main__":
    connect_to_db(app)

    # # In case tables haven't been created, create them
    # db.create_all()

    # Import different types of data
    load_users()
    load_landlords()
    load_buildings()
    load_addresses()
