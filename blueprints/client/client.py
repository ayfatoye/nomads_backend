from flask import Blueprint, jsonify

client_bp = Blueprint('client_bp', __name__)

@client_bp.route('/create', methods=['POST'])
def client_profile():
    # Imagine fetching client profile information here
    print("mina-bugger: Client profile data created")
    return jsonify({"message": "Client profile data"})
