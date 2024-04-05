import os
import colorama
from colorama import Fore, Style

from dotenv import load_dotenv
from flask import jsonify, request, abort
from extensions import db 
from models import Client, HairProfile, ClientInterest, ClientAddress, UidToUserId, Rating, RatingTag, Stylist, ClientFavourite


from . import client_bp
from supabase import create_client, Client as SupabaseClient

def create_hair_profile(hair_data):
    hair_profile = HairProfile(
        thickness=hair_data['thickness'],
        hair_type=hair_data['hair_type'],
        hair_gender=hair_data['hair_gender'],
        color_level=hair_data['color_level'],
        color_hist=hair_data['color_hist']
    )
    return hair_profile

import requests
def create_client_address(address_data):
    street = address_data['street']
    city = address_data['city']
    state = address_data['state']
    zip_code = address_data['zip_code']
    country = address_data['country']
    comfort_radius = address_data['comfort_radius']

    api_key = os.getenv('GMAPS_API_KEY')
    api_url = f'https://maps.googleapis.com/maps/api/geocode/json?address={street},{city},{state},{zip_code},{country}&key={api_key}'
    response = requests.get(api_url)
    data = response.json()

    if data['status'] == 'OK':
        result = data['results'][0]
        longitude = result['geometry']['location']['lng']
        latitude = result['geometry']['location']['lat']

        print(Fore.GREEN, f'Longitude: {longitude}, Latitude: {latitude}', Fore.RESET)

        # Add longitude and latitude to the address_data
        address_data['longitude'] = longitude
        address_data['latitude'] = latitude

        # Create the ClientAddress instance
        client_address = ClientAddress(
            street=street,
            city=city,
            state=state,
            zip_code=zip_code,
            country=country,
            comfort_radius=comfort_radius,
            longitude=longitude,
            latitude=latitude
        )
        return client_address
    else:
        raise ValueError('Failed to retrieve longitude and latitude from the API')


@client_bp.route('/create-client', methods=['POST'])
def client_profile():
    data = request.get_json()

    print(Fore.GREEN + data.get('fname', "fname not included") + Fore.RESET)

    # I'm creating and inserting instances of HairProfile, ClientAddress, and ClientInterest
    hair_profile = create_hair_profile(data['hair_profile'])
    '''
    extract address data to be run through an api that will give me the longitude and latitude
    and latitude of the address. then add the long and lat to the json object representing the address
    then use said json object to create the client address
    '''
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

    print(Fore.RED)
    print("clientid: ", client.id, "uid: ", data['uid'])
    print(Fore.RESET)

    # authentication purposes
    uid_to_userid = UidToUserId(
        uid=data['uid'],
        user_id=client.id,
        user_type="client"
    )
    db.session.add(uid_to_userid)

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


load_dotenv()
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

supabase: SupabaseClient = create_client(SUPABASE_URL, SUPABASE_KEY)

@client_bp.route('/signup-client', methods=['POST'])
def signup_client():
    try:
        data = request.get_json()
        _email = data.get('email')
        _password = data.get('password')

        res = supabase.auth.sign_up({
            "email": _email,
            "password": _password,
        })

        print(Fore.GREEN + str(res) + Fore.RESET)

        # Extracting user ID and access token from the response
        user_id = res.user.id if res.user else None
        session_token = res.session.access_token if res.session else None

        if user_id and session_token:
            return jsonify({
                'message': 'Client successfully created',
                'ayo_status': 'success',
                'session': session_token,
                'user_uid': user_id
            }), 200
        else:
            raise ValueError('User or session not found in the response')

    except Exception as e:
        print(Fore.RED + str(e) + Fore.RESET)
        return jsonify({
            'message': 'Account already exists, please sign in',
            'error': str(e),
            'ayo_status': 'fail',
            'session': None,
            'user_uid': None
        }), 400

@client_bp.route('/signin-client', methods=['POST'])
def signin_client():
    try:
        data = request.get_json()
        _email = data.get('email')
        _password = data.get('password')

        res = supabase.auth.sign_in_with_password({
            "email": _email,
            "password": _password,
        })

        print(Fore.GREEN + str(res) + Fore.RESET)

        user_id = res.user.id if res.user else None
        session_token = res.session.access_token if res.session else None

        if user_id and session_token:
            return jsonify({
                'message': 'Client successfully signed in',
                'access_token': session_token,
                'user_uid': user_id
            }), 200
        else:
            raise ValueError('User or session not found in the response')

    except Exception as e:
        print(Fore.RED + str(e) + Fore.RESET)
        return jsonify({
            'message': 'Failed to sign in client',
            'error': str(e),
            'access_token': None,
            'user_uid': None
        }), 400

@client_bp.route('/signout-client', methods=['GET'])
def signout_client():
    try:
        res = supabase.auth.sign_out()

        print(Fore.GREEN + str(res) + Fore.RESET)

        user_id = res['user'].id if 'user' in res else None
        session_token = res['session'].access_token if 'session' in res else None

        return jsonify({
            'message': 'Client successfully signed in',
            'session': session_token,
            'user_uid': user_id
        }), 200
    except Exception as e:
        return jsonify({
            'message': 'Failed to sign out client',
            'error': str(e)
        }), 400
    

@client_bp.route('/create-rating', methods=['POST'])
def create_rating():
    # function to let clients create ratings for stylists
    data = request.get_json()

    client_id = data['client_id']
    stylist_id = data['stylist_id']
    review = data['review']
    stars = data['stars']

    rating = Rating(stylist_id=stylist_id, client_id=client_id, review=review, stars=stars)
    db.session.add(rating)
    db.session.commit()
    rating_id = rating.id

    client = Client.query.get(client_id)
    hair_id = client.hair_id

    hair_profile = HairProfile.query.get(hair_id)
    thickness = hair_profile.thickness
    hair_type = hair_profile.hair_type
    hair_gender = hair_profile.hair_gender

    interests = ClientInterest.query.filter_by(hair_id=hair_id).all()
    interest_tags = [interest.interest for interest in interests]

    tags = [thickness, hair_type, hair_gender] + interest_tags
    # print(Fore.RED, str(tags), Fore.RESET)
    for tag in tags:
        rating_tag = RatingTag(rating_id=rating_id, tag=tag)
        db.session.add(rating_tag)

    stylist = Stylist.query.get(stylist_id)
    if stylist:
        ratings = Rating.query.filter_by(stylist_id=stylist_id).all()
        total_stars = sum(rating.stars for rating in ratings)
        num_ratings = len(ratings)
        if num_ratings > 0:
            average_rating = total_stars / num_ratings
            stylist.rating = average_rating
            db.session.commit()


    db.session.commit()

    return jsonify({"message": "Ratings successfully made!"})

@client_bp.route('/change-radius/<int:client_id>', methods=['PUT'])
def change_radius(client_id):
    data = request.get_json()
    new_radius = data.get('comfort_radius')

    if new_radius is None:
        return jsonify({'error': 'comfort_radius is required'}), 400

    client = Client.query.get(client_id)

    if client is None:
        return jsonify({'error': 'Client not found'}), 404

    address_id = client.address_id
    client_address = ClientAddress.query.get(address_id)

    if client_address is None:
        return jsonify({'error': 'Client address not found'}), 404

    client_address.comfort_radius = new_radius

    try:
        db.session.commit()
        return jsonify({'message': 'Comfort radius updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
@client_bp.route('/add-to-favourites/<int:client_id>', methods=['POST'])
def add_to_favourites(client_id):
    data = request.get_json()
    stylist_id = data.get('stylist_id')

    if not stylist_id:
        abort(400, description="Stylist ID is required")

    client = Client.query.get(client_id)
    if not client:
        abort(404, description=f"Client with ID {client_id} not found")

    stylist = Stylist.query.get(stylist_id)
    if not stylist:
        abort(404, description=f"Stylist with ID {stylist_id} not found")

    favourite = ClientFavourite(client_id=client_id, stylist_id=stylist_id)
    db.session.add(favourite)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        abort(500, description=str(e))

    return jsonify(message="Stylist added to favorites"), 201

@client_bp.route('/remove-from-favourites/<int:client_id>', methods=['DELETE'])
def remove_from_favorites(client_id):
    data = request.get_json()
    stylist_id = data.get('stylist_id')

    if not stylist_id:
        abort(400, description="Stylist ID is required")

    client = Client.query.get(client_id)
    if not client:
        abort(404, description=f"Client with ID {client_id} not found")

    favourite = ClientFavourite.query.filter_by(client_id=client_id, stylist_id=stylist_id).first()
    if not favourite:
        abort(404, description=f"Stylist with ID {stylist_id} not found in favorites")

    db.session.delete(favourite)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        abort(500, description=str(e))

    return jsonify(message="Stylist removed from favorites"), 200

@client_bp.route('/get-all-favs/<int:client_id>', methods=['GET'])
def get_all_favs(client_id):
    client = Client.query.get(client_id)
    if not client:
        abort(404, description=f"Client with ID {client_id} not found")

    favorites = ClientFavourite.query.filter_by(client_id=client_id).all()
    stylist_ids = [fav.stylist_id for fav in favorites]

    stylists = Stylist.query.filter(Stylist.id.in_(stylist_ids)).all()

    stylist_data = []
    for stylist in stylists:
        stylist_info = {
            'id': stylist.id,
            'fname': stylist.fname,
            'lname': stylist.lname,
            'avg_price': stylist.avg_price
        }
        stylist_data.append(stylist_info)

    return jsonify(stylists=stylist_data), 200

@client_bp.route('/update-address/<int:client_id>', methods=['PUT'])
def update_client_address(client_id):
    data = request.get_json()

    street = data.get('street')
    city = data.get('city')
    state = data.get('state')
    zip_code = data.get('zip_code')
    country = data.get('country')
    comfort_radius = data.get('comfort_radius')

    if not all([street, city, state, zip_code, country, comfort_radius]):
        abort(400, description="All address fields are required")

    client = Client.query.get(client_id)
    if not client:
        abort(404, description=f"Client with ID {client_id} not found")

    client_address = ClientAddress.query.get(client.address_id)
    if not client_address:
        abort(404, description=f"Address for client with ID {client_id} not found")

    client_address.street = street
    client_address.city = city
    client_address.state = state
    client_address.zip_code = zip_code
    client_address.country = country
    client_address.comfort_radius = comfort_radius

    api_key = os.getenv('GMAPS_API_KEY')
    api_url = f'https://maps.googleapis.com/maps/api/geocode/json?address={street},{city},{state},{zip_code},{country}&key={api_key}'
    response = requests.get(api_url)
    data = response.json()

    if data['status'] == 'OK':
        result = data['results'][0]
        client_address.longitude = result['geometry']['location']['lng']
        client_address.latitude = result['geometry']['location']['lat']
    else:
        abort(500, description="Failed to retrieve longitude and latitude from the API")

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        abort(500, description=str(e))

    return jsonify(message="Client address updated successfully", ayo_status="success"), 200

@client_bp.route('/update-stylists-should-know/<int:client_id>', methods=['PUT'])
def update_stylists_should_know(client_id):
    data = request.get_json()

    stylists_should_know = data.get('stylists_should_know')

    if not stylists_should_know:
        return jsonify(message="stylists_should_know field is required", ayo_status="error"), 400

    client = Client.query.get(client_id)
    if not client:
        return jsonify(message=f"Client with ID {client_id} not found", ayo_status="error"), 404

    client.stylists_should_know = stylists_should_know

    try:
        db.session.commit()
        return jsonify(message="stylists_should_know updated successfully", ayo_status="success"), 200
    except Exception as e:
        db.session.rollback()
        return jsonify(message=str(e), ayo_status="error"), 500
    
@client_bp.route('/update-interests/<int:client_id>', methods=['PUT'])
def update_interests(client_id):
    data = request.get_json()

    interests = data.get('interests')

    if not interests:
        return jsonify(message="interests field is required", ayo_status="error"), 400

    client = Client.query.get(client_id)
    if not client:
        return jsonify(message=f"Client with ID {client_id} not found", ayo_status="error"), 404

    hair_id = client.hair_id

    ClientInterest.query.filter_by(hair_id=hair_id).delete()

    for interest in interests:
        client_interest = ClientInterest(hair_id=hair_id, interest=interest)
        db.session.add(client_interest)

    try:
        db.session.commit()
        return jsonify(message="Interests updated successfully", ayo_status="success"), 200
    except Exception as e:
        db.session.rollback()
        return jsonify(message=str(e), ayo_status="error"), 500