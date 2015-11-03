"""Utility file to seed ratings database from MovieLens data in seed_data/"""


from model import User, Landlord, Address, Review, Convo, Userconvo, Message, Building, Resource
from model import connect_to_db, db
from server import app
import datetime
from faker import Faker
import requests
import json
import mapbox
import os

fake = Faker()

geocoder = mapbox.Geocoder(access_token=os.environ['MAPBOX_TOKEN'])

def load_users():
    """Create fake users and load into database."""

#     print "Users"

    # Delete all rows in table to avoid adding duplicates
    User.query.delete()

    for i in range(0, 10):

        user = User(fname=fake.first_name(),
                    lname=fake.last_name(),
                    email=fake.safe_email(),
                    password=fake.password(length=10, special_chars=True, digits=True, upper_case=True, lower_case=True))

        # print user

        # Add the user to the database
        db.session.add(user)

    # Commit all additons to database
    db.session.commit()


def load_landlords():
    """Create fake landlords and load into database."""

    # Delete all rows in table to avoid adding duplicates
    Landlord.query.delete()

    for i in range(0, 10):
        landlord = Landlord(fname=fake.first_name(),
                            lname=fake.last_name())

        # Add the landlord to the database
        db.session.add(landlord)

        # Commit all additions to database
        db.session.commit()


def load_buildings():
    """Create fake buildings and load into database."""

    # Delete all rows in table to avoid adding duplicates
    Building.query.delete()

    for i in range(0, 10):
    # Question, if I only want 5 buildings, how do I do that when I'm creating addresses? Random number between 1 and 5?
        building = Building(name=fake.company())

        # Add the building to the database
        db.session.add(building)

        # Commit all additions to database
        db.session.commit()


def load_addresses():
    """Create addresses and load into database."""

    # Delete all rows in table to avoid adding duplicates
    Address.query.delete()

    # Use mapbox for reverse geocoding using requests

    # Create list to hold address json results from reverse geocoding requests
    addresses = []

    # Iterate through text file with each line containing "lattitude|longigude"
    for pair in open('data/u.coordinates'):
        latlng = pair.split('|')
        lat = latlng[0]
        lng = latlng[1]

        # Make request to mapbox geocoding api using lng and lat
        # req = 'https://api.mapbox.com/geocoding/v5/mapbox.places/{},{}.json?access_token=pk.eyJ1Ijoibm1hcmdvbGlzODkiLCJhIjoibGxsVVJETSJ9.dQv5byiwSyj--mr7Bgwezw'.format(lng, lat)
        # r = requests.get(req)
        response = geocoder.reverse(lon=lng, lat=lat)
        json_result = response.json()

        # Add the first result in json_result to list of addresses
        addresses.append(json_result[0])

    # for i in range(0, 50):

    #     # Get the street address from the ith address in addresses
    #     street = addresses[i]["features"]["properties"]["address"]
    #     address = Address(street=street,
    #                     city=city,
    #                     state=state,
    #                     zipcode=zipcode,
    #                     country=country,
    #                     unit=unit,
    #                     lat=lat,
    #                     lng=lng,
    #                     building_id=building_id)

    # # Add the address to the database
    # db.session.add(address)

    # # Commit all additions to database
    # db.session.commit()



if __name__ == "__main__":
    connect_to_db(app)

    # # In case tables haven't been created, create them
    # db.create_all()

    # Import different types of data
    load_users()
    load_landlords()
    load_buildings()
    # load_addresses()
