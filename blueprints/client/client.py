from flask import Blueprint, jsonify

client_bp = Blueprint('client_bp', __name__)

'''
draft for how I will approach designing the backend:

# models/Client.py

class Client:
    def __init__(self, client_id, profile_id, address_id, first_name, last_name, ethnicity, stylist_should_know):
        self.client_id = client_id
        self.profile_id = profile_id
        self.address_id = address_id
        self.first_name = first_name
        self.last_name = last_name
        self.ethnicity = ethnicity
        self.stylist_should_know = stylist_should_know

    def __repr__(self):
        return f"<Client {self.first_name} {self.last_name}>"


from flask import Blueprint, request, jsonify
from models import db, Client, Address, HairProfile, ClientInterest  # Assuming models are defined elsewhere

client_bp = Blueprint('client_bp', __name__)

@client_bp.route('/create', methods=['POST'])
def client_profile():
    data = request.get_json()  # Parse JSON data from request

    # Create Address entry
    address = Address(
        street=data['address']['street'],
        city=data['address']['city'],
        state=data['address']['state'],
        zip_code=data['address']['zip_code'],
        country=data['address']['country'],
        comfort_radius=data['address']['comfort_radius'],
        longitude=data['address']['longitude'],
        latitude=data['address']['latitude']
    )
    db.session.add(address)
    db.session.commit()

    # Create HairProfile entry
    hair_profile = HairProfile(
        thickness=data['hair_profile']['thickness'],
        hair_type=data['hair_profile']['hair_type'],
        hair_gender=data['hair_profile']['hair_gender'],
        color_hist=data['hair_profile']['color_hist'],
        color_level=data['hair_profile']['color_level']
    )
    db.session.add(hair_profile)
    db.session.commit()

    # Create Client entry
    client = Client(
        first_name=data['first_name'],
        last_name=data['last_name'],
        profile_id=data['profile_id'],
        address_id=address.id,  # Use the generated ID from the address entry
        ethnicity=data['ethnicity'],
        stylist_should_know=data['stylist_should_know']
    )
    db.session.add(client)
    db.session.commit()

    # Create ClientInterest entries
    for interest_id in data['interests']:
        client_interest = ClientInterest(
            hair_id=hair_profile.hair_id,  # Use the generated hair_id from the hair_profile entry
            interest=interest_id
        )
        db.session.add(client_interest)

    db.session.commit()

    print("mina-bugger: Client profile data created")
    return jsonify({"message": "Client profile data"})



'''

@client_bp.route('/create', methods=['POST'])
def client_profile():
    # Imagine fetching client profile information here
    print("mina-bugger: Client profile data created")
    return jsonify({"message": "Client profile data"})
