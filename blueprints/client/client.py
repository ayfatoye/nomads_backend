# from flask import Blueprint, jsonify

# client_bp = Blueprint('client_bp', __name__)

# @client_bp.route('/create', methods=['POST'])
# def client_profile():
#     # Imagine fetching client profile information here
#     print("mina-bugger: Client profile data created")
#     return jsonify({"message": "Client profile data"})

from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from models import db, Client, HairProfile, ClientInterest, ClientAddress 

app = Flask(__name__)
# I need to configure our Flask app to connect to the database, e.g.:
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://...'

db.init_app(app)

@app.route('/client', methods=['POST'])
def create_client():
    data = request.get_json()

    # I'm creating and inserting instances of HairProfile, ClientAddress, and ClientInterest
    hair_profile = create_hair_profile(data['hair_profile'])
    client_address = create_client_address(data['address'])
    db.session.add(hair_profile)
    db.session.add(client_address)
    db.session.flush()

    # Creating and inserting interests
    interests_ids = []
    for interest in data['interests']:
        client_interest = ClientInterest(hair_id=hair_profile.id, interest=interest)
        db.session.add(client_interest)
        interests_ids.append(client_interest.id)
    
    # Type shit. Now I'll create the Client instance with foreign keys from HairProfile and ClientAddress
    client = Client(
        hair_id=hair_profile.id,
        address_id=client_address.id,
        fname=data['fname'],
        lname=data['lname'],
        ethnicity=data['ethnicity'],
        stylist_should_know=data['stylist_should_know']
    )
    db.session.add(client)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        abort(500, description=str(e))

    return jsonify(client_id=client.id, hair_profile_id=hair_profile.id, client_address_id=client_address.id, client_interest_ids=interests_ids), 201

def create_hair_profile(hair_data):
    hair_profile = HairProfile(
        thickness=hair_data['thickness'],
        hair_type=hair_data['hair_type'],
        hair_gender=hair_data['hair_gender'],
        color_level=hair_data['color_level'],
        color_hist=hair_data['color_hist']
    )
    return hair_profile

def create_client_address(address_data):
    client_address = ClientAddress(
        street=address_data['street'],
        city=address_data['city'],
        state=address_data['state'],
        zip_code=address_data['zip_code'],
        country=address_data['country'],
        comfort_radius=address_data['comfort_radius'],
        longitude=address_data['longitude'],
        latitude=address_data['latitude']
    )
    return client_address

if __name__ == '__main__':
    app.run(debug=True)
