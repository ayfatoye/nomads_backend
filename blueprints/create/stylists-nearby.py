import colorama
from colorama import Fore, Style

from extensions import db
from models.stylist import Stylist, StylistAddress
from models.client import Client, ClientAddress
from geoalchemy2 import functions as geofunc

from . import stylist_bp

@stylist_bp.route('/stylists-nearby/<int:client_id>', methods=['GET'])
def get_stylists_nearby(client_id):
    # Get the client's address
    print(Fore.GREEN + "mina-bugger: Client profile data created" + Fore.RESET)

    client_address = db.session.query(ClientAddress).filter(ClientAddress.client_id == client_id).first()
    if not client_address:
        return {"error": "Client address not found"}, 404

    # Query to find stylists ordered by distance from the client's address
    stylist_infos = db.session.query(
        Stylist.id,
        Stylist.fname,
        Stylist.lname,
        geofunc.ST_Distance(
            geofunc.ST_SetSRID(geofunc.ST_MakePoint(client_address.longitude, client_address.latitude), 4326),
            geofunc.ST_SetSRID(geofunc.ST_MakePoint(StylistAddress.longitude, StylistAddress.latitude), 4326)
        ).label('distance')
    ).join(StylistAddress, Stylist.address_id == StylistAddress.id
    ).order_by('distance').all()

    # Format the output to include both ID and name of the stylists
    stylists_output = [
        {
            "id": stylist.id,
            "name": f"{stylist.fname} {stylist.lname}",
            "distance": stylist.distance
        } for stylist in stylist_infos
    ]

    # Print out the names of the stylists and their distances
    for stylist in stylists_output:
        print(f"Stylist ID: {stylist['id']}, Name: {stylist['name']}, Distance: {stylist['distance']}")

    # Return the array of stylists with their ID, name, and distance
    return {"stylists": stylists_output}, 200

# Be sure to register this route with the Flask app and Blueprint as you have done with others
