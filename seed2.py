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
from random import randint

fake = Faker()

geocoder = mapbox.Geocoder(access_token=os.environ['MAPBOX_TOKEN'])


def load_users():
    """Create fake users and load into database."""

    # Delete all rows in table to avoid adding duplicates
    User.query.delete()

    for i in range(0, 50):

        user = User(fname=fake.first_name(),
                    lname=fake.last_name(),
                    email=fake.safe_email(),
                    password=fake.password(length=10, special_chars=False, digits=True, upper_case=True, lower_case=True))

        # print user

        # Add the user to the database
        db.session.add(user)

    # Commit all additons to database
    db.session.commit()


def load_landlords():
    """Create fake landlords and load into database."""

    # Delete all rows in table to avoid adding duplicates
    Landlord.query.delete()

    for i in range(0, 50):
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

    for i in range(0, 50):
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

    # Initialize counter to add unit numbers 1/4 of the time
    i = 0

    # Iterate through text file with each line containing "lattitude|longigude"
    for pair in open('data/u.coordinates'):
        latlng = pair.split('|')
        lat = latlng[0]
        lng = latlng[1]

        # Make request to mapbox geocoding api using lng and lat
        # req = 'https://api.mapbox.com/geocoding/v5/mapbox.places/{},{}.json?access_token=pk.eyJ1Ijoibm1hcmdvbGlzODkiLCJhIjoibGxsVVJETSJ9.dQv5byiwSyj--mr7Bgwezw'.format(lng, lat)
        # r = requests.get(req)
        response = geocoder.reverse(lon=lng, lat=lat, types=['address'])
        json_response = response.json()
        # print 'response: ', json_response, '\n'

        if json_response["features"] == []:
            # print 'empty'
            continue
        else:
            num = json_response["features"][0]["address"]
            st = json_response["features"][0]["text"]
            street = '{} {}'.format(num, st)
            if len(json_response["features"][0]["context"]) == 5:
                city = json_response["features"][0]["context"][1]["text"]
                zipcode = json_response["features"][0]["context"][2]["text"]
                state = json_response["features"][0]["context"][3]["text"]
                country = json_response["features"][0]["context"][4]["text"]
            else:
                continue

            # For some reason -122.42691912,37.81240737 doesn't have the city attribute in context.
            # https://api.mapbox.com/geocoding/v5/mapbox.places/-122.42691912,37.81240737.json?types=address&access_token=pk.eyJ1Ijoibm1hcmdvbGlzODkiLCJhIjoibGxsVVJETSJ9.dQv5byiwSyj--mr7Bgwezw

            # 1/4 of the times, create an address with unit and building id
            if i % 4 == 0:
                building_id = randint(0, 10)
                address = Address(street=street,
                                city=city,
                                state=state,
                                zipcode=zipcode,
                                country=country,
                                unit=fake.building_number(),
                                lat=lat,
                                lng=lng,
                                building_id=building_id)

            # The rest of the time, create an address without unit and building id
            else:
                address = Address(street=street,
                                city=city,
                                state=state,
                                zipcode=zipcode,
                                country=country,
                                lat=lat,
                                lng=lng,)

            # Add the address to the database
            db.session.add(address)

            # Commit all additions to database
            db.session.commit()

            i += 1


def load_reviews():
    """Create reviews and load into database."""

    # Delete all rows in table to avoid adding duplicates
    Review.query.delete()

    for i in range(0, 50):

        # Set moved_in_at because moved_out_at and created_at depend on moved_in_at
        moved_in_at = fake.date_time_between(start_date="-5y", end_date="now")

        review = Review(user_id=randint(1, 50),
                        landlord_id=randint(1, 50),
                        address_id=randint(1, 44),
                        moved_in_at=moved_in_at,
                        moved_out_at=fake.date_time_between_dates(datetime_start=moved_in_at, datetime_end=None),
                        created_at=fake.date_time_between_dates(datetime_start=moved_in_at, datetime_end=None),
                        rating1=randint(1, 5),
                        rating2=randint(1, 5),
                        rating3=randint(1, 5),
                        rating4=randint(1, 5),
                        rating5=randint(1, 5),
                        comment=fake.text(max_nb_chars=500))

        # Add the review to the database
        db.session.add(review)

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
    load_reviews()
