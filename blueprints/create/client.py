import colorama
from colorama import Fore, Style

from flask import Blueprint, jsonify, request, abort
from extensions import db  # Import the shared db instance
from models import Client, HairProfile, ClientInterest, ClientAddress

from . import client_bp

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


@client_bp.route('/create-client', methods=['POST'])
def client_profile():
    data = request.get_json()

    print(Fore.GREEN + data.get('fname', "fname not included") + Fore.RESET)

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
        stylists_should_know=data['stylists_should_know']
    )
    db.session.add(client)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        abort(500, description=str(e))

    return jsonify(client_id=client.id, hair_profile_id=hair_profile.id, client_address_id=client_address.id, client_interest_ids=interests_ids), 201
    return jsonify({"message": "Client profile data 2"})


@client_bp.route('/read-client/<int:client_id>', methods=['GET'])
def get_client_profile(client_id):
    client = Client.query.get_or_404(client_id)
    hair_profile = HairProfile.query.get_or_404(client.hair_id)
    client_address = ClientAddress.query.get_or_404(client.address_id)
    client_interests = ClientInterest.query.filter_by(hair_id=client.hair_id).all()

    client_data = {
        'fname': client.fname,
        'lname': client.lname,
        'ethnicity': client.ethnicity,
        'stylists_should_know': client.stylists_should_know,
        'hair_profile': {
            'thickness': hair_profile.thickness,
            'hair_type': hair_profile.hair_type,
            'hair_gender': hair_profile.hair_gender,
            'color_level': hair_profile.color_level,
            'color_hist': hair_profile.color_hist
        },
        'address': {
            'street': client_address.street,
            'city': client_address.city,
            'state': client_address.state,
            'zip_code': client_address.zip_code,
            'country': client_address.country,
            'comfort_radius': client_address.comfort_radius,
            'longitude': client_address.longitude,
            'latitude': client_address.latitude
        },
        'interests': [interest.interest for interest in client_interests]
    }

    return jsonify(client_data)
