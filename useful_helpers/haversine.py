from math import radians, sin, cos, asin, sqrt

def haversine(lon1, lat1, lon2, lat2):
    # radius of the Earth in miles
    R = 3959

    # converting latitude and longitude from degrees to radians, i'm so smart
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    
    # implementing the haversine formula I read about
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    distance = R * c
    return distance