import os
import colorama
from colorama import Fore, Style

from dotenv import load_dotenv
from flask import Blueprint, jsonify, request, abort
from extensions import db  # Import the shared db instance
from models import Client, HairProfile, ClientInterest, ClientAddress, UidToClientId

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

    print(Fore.RED)
    print("clientid: ", client.id, "uid: ", data['uid'])
    print(Fore.RESET)

    # authentication purposes
    uid_to_clientid = UidToClientId(
        uid=data['uid'],
        client_id=client.id
    )
    db.session.add(uid_to_clientid)

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
    

@client_bp.route('/send-otp', methods=['POST'])
def send_otp():
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    
    try:
        # Generate and send the OTP
        otp_response = supabase.auth.sign_in_with_otp({
            'email': email,
            'options': {
                'email_redirect_to': 'https://people.tamu.edu/~sebastianoberg2002/'
            }
        })
        
        # if otp_response.status_code == 200:
        #     return jsonify({'message': 'OTP sent successfully'}), 200
        # else:
        #     return jsonify({'error': 'Failed to send OTP'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@client_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    try:
        data = request.get_json()
        _email = data.get('email')
        _otp = data.get('otp')
        
        if not _email or not _otp:
            raise ValueError('Email and OTP are required')
        
        res = supabase.auth.verify_otp(_email, _otp)
        print(Fore.GREEN + str(res) + Fore.RESET)
        
        user_id = res.user.id if res.user else None
        session_token = res.session.access_token if res.session else None
        
        if user_id and session_token:
            return jsonify({
                'message': 'OTP verification successful',
                'access_token': session_token,
                'user_uid': user_id
            }), 200
        else:
            raise ValueError('User or session not found in the response')
    
    except Exception as e:
        print(Fore.RED + str(e) + Fore.RESET)
        return jsonify({
            'message': 'Failed to verify OTP',
            'error': str(e),
            'access_token': None,
            'user_uid': None
        }), 400