import colorama
from colorama import Fore, Style

import supabase
import os
from dotenv import load_dotenv

from flask import Blueprint, jsonify, request, abort
from extensions import db  # Import the shared db instance
from models.stylist import Stylist, StylistSpeciality, StylistAddress
from models import Client, ClientAddress, HairProfile, ClientInterest

from . import auth_bp

from supabase import create_client

load_dotenv()
auth_bp = Blueprint('auth_bp', __name__)
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@auth_bp.route('/signup-client', methods=['POST'])
def signup_client():
    data = request.get_json()
    _email = data.get('email')
    _password = data.get('password')
    

    # so at least we have username and password working for sure for now
    print("email: ", _email)
    res = supabase.auth.sign_up({
    "email": _email,
    "password": _password,
    })

    print("response: ", res)
    
    if 'error' in res:
        return jsonify({'error': res['error']}), 400

    return jsonify({'message': 'client sucessfully created'}), 200
