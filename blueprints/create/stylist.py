#imports for testing
import colorama
from colorama import Fore, Style

#imports for stylists-nearby route
from models import Client, ClientAddress
from useful_helpers import haversine

#imports for create-stylist route
from flask import jsonify, request, abort
from extensions import db
from models.stylist import Stylist, StylistSpeciality, StylistAddress

from . import stylist_bp

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

    client_address = db.session.query(ClientAddress).filter(ClientAddress.id == client.address_id).first()
    if not client_address:
        return {"error": "Client address not found"}, 404

    stylists_info = db.session.query(
        Stylist.fname,
        Stylist.lname,
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
            stylists_output.append({
                "fname": stylist.fname,
                "lname": stylist.lname,
                "latitude": stylist.latitude,
                "longitude": stylist.longitude,
                "distance": distance
            })

    # just sorting the results by distance
    stylists_output.sort(key=lambda x: x['distance'])

    return {"stylists": stylists_output}, 200