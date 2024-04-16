import os
import requests
from dotenv import load_dotenv

# imports for testing
import colorama
from colorama import Fore, Style


# imports for stylists-nearby route
from models import Client, ClientAddress, UidToUserId, Stylist, StylistAddress, StylistSpeciality, Rating, RatingTag, StylistContact
from useful_helpers import haversine, get_client_profile, hair_tags

# imports for create-stylist route
from flask import jsonify, request, abort
from extensions import db

from . import stylist_bp

load_dotenv()

def decision_tree_comp(stylist, client):
    client_interests = client.get('interests', [])
    print(Fore.GREEN, client_interests, Fore.RESET)
    stylist_specialities = stylist.get('specialities', [])
    print(Fore.RED, stylist_specialities, Fore.RESET)

    match_count = sum(
        1 for interest in client_interests if interest in stylist_specialities)
    total_interests = len(client_interests)

    if total_interests == 0:
        return 0  
    match_percentage = (match_count / total_interests) * 100

    return round(match_percentage, 2)


@stylist_bp.route('/create-stylist', methods=['POST'])
def create_stylist_profile():
    data = request.get_json()

    contacts_data = data.get('contacts', {})
    
    stylist_contact = StylistContact(
        phone_num=contacts_data.get('phone_num'), 
        instagram=contacts_data.get('instagram'),
        twitter=contacts_data.get('twitter'),
        linked_tree=contacts_data.get('linked_tree')
    )
    db.session.add(stylist_contact)
    db.session.flush()

    # Extract address data
    address_data = data['address']
    street = address_data['street']
    city = address_data['city']
    state = address_data['state']
    zip_code = address_data['zip_code']
    country = address_data['country']
    comfort_radius = address_data['comfort_radius']

    # Make API request to get longitude and latitude
    api_key = os.getenv('GMAPS_API_KEY')
    api_url = f'https://maps.googleapis.com/maps/api/geocode/json?address={street},{city},{state},{zip_code},{country}&key={api_key}'
    response = requests.get(api_url)
    api_data = response.json()

    if api_data['status'] == 'OK':
        result = api_data['results'][0]
        longitude = result['geometry']['location']['lng']
        latitude = result['geometry']['location']['lat']
    else:
        abort(500, description="Failed to retrieve longitude and latitude from the API")

    stylist = Stylist(
        fname=data['fname'],
        lname=data['lname'],
        clients_should_know=data['clients_should_know'],
        avg_price=data['avg_price'],
        contacts_id=stylist_contact.id
    )
    db.session.add(stylist)
    db.session.flush()

    stylist_address = StylistAddress(
        stylist_id=stylist.id,
        street=street,
        city=city,
        state=state,
        zip_code=zip_code,
        country=country,
        comfort_radius=comfort_radius,
        longitude=longitude,
        latitude=latitude
    )
    db.session.add(stylist_address)

    # Writing in specialities the Stylist has
    for speciality_id in data['specialities']:
        stylist_speciality = StylistSpeciality(
            stylist_id=stylist.id,
            speciality=speciality_id
        )
        db.session.add(stylist_speciality)

    # Authentication purposes
    uid_to_clientid = UidToUserId(
        uid=data['uid'],
        user_id=stylist.id,
        user_type='stylist'
    )
    db.session.add(uid_to_clientid)

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
        Stylist.avg_price,
        StylistAddress.street,
        StylistAddress.city,
        StylistAddress.state,
        StylistAddress.zip_code,
        StylistAddress.latitude,
        StylistAddress.longitude
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
            specialties_list = [(specialty.speciality) for specialty in specialties]
            stylists_output.append({
                "id": stylist.id,
                "fname": stylist.fname,
                "lname": stylist.lname,
                "street": stylist.street,
                "city": stylist.city,
                "state": stylist.state,
                "zip_code": stylist.zip_code,
                "distance": distance,
                "rating": stylist.rating,
                "specialities": specialties_list,
                "avg_price": stylist.avg_price
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

    # getting the stylists data
    stylists_data = get_stylists_nearby(client_id)
    if not isinstance(stylists_data, dict):
        return jsonify({"error": "Could not retrieve stylists nearby"}), 400
    
    if len(stylists_data.get('stylists', [])) == 0:
        return jsonify({"message": "There are no stylists in your comfort radius, please consider increasing it."}), 400
    

    stylists_output = []

    if 'stylists' in stylists_data:
        for stylist in stylists_data['stylists']:
            match_percentage = decision_tree_comp(stylist, client_data)
            stylist['match_percentage'] = match_percentage
            specialties_list = [hair_tags.get(specialty, "no corresponding string in hair tags") for specialty in stylist['specialities']]
            stylist['specialities'] = specialties_list
            stylists_output.append(stylist)

    stylists_output_sorted = sorted(stylists_output, key=lambda x: x['match_percentage'], reverse=True)

    return jsonify({"stylists": stylists_output_sorted}), 200

import supabase
from supabase import create_client

url: str = os.getenv('SUPABASE_URL')
key: str = os.getenv("SUPABASE_KEY")
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

    print("response: ", res)
    
    if 'error' in res:
        return jsonify({'error': res['error']}), 400

    return jsonify({'message': 'OTP sent to your email'}), 200

@stylist_bp.route('/read-stylist/<int:stylist_id>', methods=['GET'])
def get_stylist_profile(stylist_id):
    stylist = Stylist.query.get_or_404(stylist_id)
    stylist_address = StylistAddress.query.filter_by(stylist_id=stylist.id).first()
    stylist_specialities = StylistSpeciality.query.filter_by(stylist_id=stylist.id).all()

    stylist_data = {
        'fname': stylist.fname,
        'lname': stylist.lname,
        'clients_should_know': stylist.clients_should_know,
        'rating': stylist.rating,
        'avg_price': stylist.avg_price, 
        'address': {
            'street': stylist_address.street,
            'city': stylist_address.city,
            'state': stylist_address.state,
            'zip_code': stylist_address.zip_code,
            'country': stylist_address.country,
            'comfort_radius': stylist_address.comfort_radius,
            'longitude': stylist_address.longitude,
            'latitude': stylist_address.latitude
        },
        'specialities': [hair_tags.get(speciality.speciality) for speciality in stylist_specialities]
    }

    return jsonify(stylist_data)

@stylist_bp.route('/get-ratings/<int:stylist_id>', methods=['GET'])
def get_ratings(stylist_id):
    stylist = Stylist.query.get(stylist_id)
    if not stylist:
        return jsonify({"error": "Stylist not found"}), 404

    ratings = Rating.query.filter_by(stylist_id=stylist_id).all()
    rating_data = []

    for rating in ratings:
        client = Client.query.get(rating.client_id)
        client_name = f"{client.fname} {client.lname}" if client else "Unknown"

        rating_tags = RatingTag.query.filter_by(rating_id=rating.id).all()
        tags = [hair_tags.get(tag.tag, "Unknown") for tag in rating_tags]

        rating_data.append({
            "rating_id": rating.id,
            "client_id": rating.client_id,
            "client_name": client_name,
            "review": rating.review,
            "stars": rating.stars,
            "tags": tags
        })

    average_rating = stylist.rating if stylist.rating else 0

    return jsonify({
        "stylist_id": stylist_id,
        "average_rating": average_rating,
        "ratings": rating_data,
        "ayo_status": "success"
    })

@stylist_bp.route('/update-address/<int:stylist_id>', methods=['PUT'])
def update_stylist_address(stylist_id):
    address_data = request.get_json()

    stylist = Stylist.query.get(stylist_id)
    if not stylist:
        abort(404, description=f"Stylist with ID {stylist_id} not found")

    if not address_data:
        abort(400, description="Address data is required")

    stylist_address = StylistAddress.query.filter_by(stylist_id=stylist_id).first()
    if not stylist_address:
        abort(404, description=f"Address for stylist with ID {stylist_id} not found")

    stylist_address.street = address_data.get('street', stylist_address.street)
    stylist_address.city = address_data.get('city', stylist_address.city)
    stylist_address.state = address_data.get('state', stylist_address.state)
    stylist_address.zip_code = address_data.get('zip_code', stylist_address.zip_code)
    stylist_address.country = address_data.get('country', stylist_address.country)
    stylist_address.comfort_radius = address_data.get('comfort_radius', stylist_address.comfort_radius)

    api_key = os.getenv('GMAPS_API_KEY')
    api_url = f'https://maps.googleapis.com/maps/api/geocode/json?address={stylist_address.street},{stylist_address.city},{stylist_address.state},{stylist_address.zip_code},{stylist_address.country}&key={api_key}'
    response = requests.get(api_url)
    api_data = response.json()

    if api_data['status'] == 'OK':
        result = api_data['results'][0]
        stylist_address.longitude = result['geometry']['location']['lng']
        stylist_address.latitude = result['geometry']['location']['lat']
    else:
        abort(500, description="Failed to retrieve longitude and latitude from the API")

    try:
        db.session.commit()
        return jsonify(message="Stylist address updated successfully", ayo_status="success"), 200
    except Exception as e:
        db.session.rollback()
        abort(500, description=str(e))