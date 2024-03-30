# imports for testing
import colorama
from colorama import Fore, Style


# imports for stylists-nearby route
from models import Client, ClientAddress, HairProfile, ClientInterest
from useful_helpers import haversine

# imports for create-stylist route
from flask import jsonify, request, abort
from extensions import db
from models.stylist import Stylist, StylistSpeciality, StylistAddress

from . import stylist_bp


def get_client_profile(client_id):
    client = Client.query.get_or_404(client_id)
    hair_profile = HairProfile.query.get_or_404(client.hair_id)
    client_address = ClientAddress.query.get_or_404(client.address_id)
    client_interests = ClientInterest.query.filter_by(
        hair_id=client.hair_id).all()

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

    return client_data


def decision_tree_comp(stylist, client):
    client_interests = client.get('interests', [])
    print(Fore.GREEN)
    print(client_interests)
    print(Fore.RESET)
    stylist_specialities = stylist.get('specialities', [])
    print(Fore.RED)
    print("stylist_specialities: ", stylist_specialities)
    print(Fore.RESET)

    match_count = sum(
        1 for interest in client_interests if interest in stylist_specialities)
    total_interests = len(client_interests)

    if total_interests == 0:
        return 0  # Avoid division by zero
    match_percentage = (match_count / total_interests) * 100

    return round(match_percentage, 2)


@stylist_bp.route('/create-stylist', methods=['POST'])
def create_stylist_profile():
    data = request.get_json()

    stylist = Stylist(
        fname=data['fname'],
        lname=data['lname'],
        clients_should_know=data['clients_should_know']
    )
    db.session.add(stylist)
    db.session.flush()

    stylist_address = StylistAddress(
        stylist_id=stylist.id,  # linking the address with the stylist
        street=data['address']['street'],
        city=data['address']['city'],
        state=data['address']['state'],
        zip_code=data['address']['zip_code'],
        country=data['address']['country'],
        comfort_radius=data['address']['comfort_radius'],
        longitude=data['address']['longitude'],
        latitude=data['address']['latitude']
    )
    db.session.add(stylist_address)

    # writing in specialities the Stylist has
    for speciality_id in data['specialities']:
        stylist_speciality = StylistSpeciality(
            stylist_id=stylist.id,  # Associate the speciality with the stylist
            speciality=speciality_id
        )
        db.session.add(stylist_speciality)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        abort(500, description=str(e))

    return jsonify(stylist_id=stylist.id, stylist_address_id=stylist_address.id), 201


@stylist_bp.route('/stylists-nearby/<int:client_id>', methods=['GET'])
def get_stylists_nearby(client_id):

    client = db.session.query(Client).get(client_id)
    if not client:
        return {"error": "Client not found"}, 404

    client_address = db.session.query(ClientAddress).filter(
        ClientAddress.id == client.address_id).first()
    if not client_address:
        return {"error": "Client address not found"}, 404

    stylists_info = db.session.query(
        Stylist.id,
        Stylist.fname,
        Stylist.lname,
        Stylist.rating,
        StylistAddress.latitude,
        StylistAddress.longitude,
    ).join(StylistAddress, Stylist.id == StylistAddress.stylist_id).all()

    stylists_output = []
    for stylist in stylists_info:
        distance = haversine(
            client_address.longitude,
            client_address.latitude,
            stylist.longitude,
            stylist.latitude
        )
        if distance <= client_address.comfort_radius:
            specialties = db.session.query(StylistSpeciality.speciality).filter(StylistSpeciality.stylist_id == stylist.id).all()
            specialties_list = [specialty.speciality for specialty in specialties]
            stylists_output.append({
                "id": stylist.id,
                "fname": stylist.fname,
                "lname": stylist.lname,
                "latitude": stylist.latitude,
                "longitude": stylist.longitude,
                "distance": distance,
                "rating": stylist.rating,
                "specialities": specialties_list
            })

    # just sorting the results by distance
    stylists_output.sort(key=lambda x: x['distance'])

    # return {"stylists": stylists_output}, 200
    return {"stylists": stylists_output}


@stylist_bp.route('/mina/<int:client_id>', methods=['GET'])
def mina(client_id):
    client_data = get_client_profile(client_id)
    if not isinstance(client_data, dict):
        return jsonify({"error": "Could not retrieve client profile"}), 400
    # print(Fore.GREEN)
    # print(client_data)
    # print(Fore.RESET)

    # getting the stylists data
    stylists_data = get_stylists_nearby(client_id)
    if not isinstance(stylists_data, dict):
        return jsonify({"error": "Could not retrieve stylists nearby"}), 400
    
    if len(stylists_data.get('stylists', [])) == 0:
        return jsonify({"message": "There are no stylists in your comfort radius, please consider increasing it."}), 400
    
    # print(Fore.GREEN)
    # print(stylists_data)
    # print(Fore.RESET)

    stylists_output = []

    if 'stylists' in stylists_data:
        for stylist in stylists_data['stylists']:
            match_percentage = decision_tree_comp(stylist, client_data)
            stylist['match_percentage'] = match_percentage
            stylists_output.append(stylist)

    stylists_output_sorted = sorted(stylists_output, key=lambda x: x['match_percentage'], reverse=True)

    return jsonify({"stylists": stylists_output_sorted}), 200

import supabase
from supabase import create_client

url: str = "https://sockukwcrqgwpkebbqfq.supabase.co"
key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNvY2t1a3djcnFnd3BrZWJicWZxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcwODU2NjM0OSwiZXhwIjoyMDI0MTQyMzQ5fQ.uWR6ho-B7FnRY_dcPeqJO-KkW2uOpK7y-h3qpcipA-Y"
supabase: Client = create_client(url, key)

@stylist_bp.route('/send-otp', methods=['POST'])
def send_otp():
    data = request.get_json()
    _email = data.get('email')
    _password = data.get('password')
    
    res = supabase.auth.sign_in_with_otp({
        "email": _email,
        "options": {
            "email_redirect_to": 'https://people.tamu.edu/~sebastianoberg2002',
            "should_create_user": True
        }
    })

    # so at least we have username and password working for sure for now
    # print("email: ", _email)
    # res = supabase.auth.sign_up({
    # "email": _email,
    # "password": _password,
    # })


    print("response: ", res)
    
    if 'error' in res:
        return jsonify({'error': res['error']}), 400

    return jsonify({'message': 'OTP sent to your email'}), 200

