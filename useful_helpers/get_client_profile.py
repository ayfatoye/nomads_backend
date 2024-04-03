from models import Client, HairProfile, ClientAddress, ClientInterest

def get_client_profile(client_id):
    client = Client.query.get_or_404(client_id)
    hair_profile = HairProfile.query.get_or_404(client.hair_id)
    client_address = ClientAddress.query.get_or_404(client.address_id)
    client_interests = ClientInterest.query.filter_by(hair_id=client.hair_id).all()
    interests = [
        hair_profile.thickness,
        hair_profile.hair_type,
        hair_profile.hair_gender
    ] + [interest.interest for interest in client_interests]

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
        'interests': interests
    }

    return client_data