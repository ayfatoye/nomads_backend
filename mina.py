'''
my first draft of mina, our recommender system algorithm

- find the stylists that fall within price range
- do some math to find the stylists that fall within distance range
- then simpler decision making tree
    - does the stylist cut my hair type?
    - does the stylist cut my level of hair thickness?
    - if I need color services, does the stylist offer that?
    - if I need speciality 1, does the stylist offer that?
    - if I need speciality 2, does the stylist offer that?
    - etc
'''

# show casing a very very very simple version of our decision tree
import math

# Define the client
nick = {
    'hair_type': '2A',
    'hair_texture': 'coarse',
    'location': (100, 100),  # x, y coordinates used to represent nick's location
    'comfort_radius': 2  # in maybe Miles or we might also wind up going with kms
}

# Define potential stylists
stylists = [
    {'name': 'Stylist A', 'hair_types': ['2A'], 'hair_textures': ['coarse'], 'location': (105, 105)},
    {'name': 'Stylist B', 'hair_types': ['1C'], 'hair_textures': ['fine'], 'location': (101, 101)}, 
    {'name': 'Stylist C', 'hair_types': ['2A', '3C'], 'hair_textures': ['coarse', 'medium'], 'location': (100.02, 100.02)},
    {'name': 'Stylist D', 'hair_types': ['4A'], 'hair_textures': ['coarse'], 'location': (100.01, 100.01)},
]

def calculate_distance(loc1, loc2):
    return math.sqrt((loc1[0] - loc2[0])**2 + (loc1[1] - loc2[1])**2)

def check_stylist(stylist, client):
    distance = calculate_distance(stylist['location'], client['location'])
    if distance > client['comfort_radius']:
        # print(f"{stylist['name']} is too far from Nick.")
        return f"{stylist['name']} is too far from Nick."
    if client['hair_texture'] not in stylist['hair_textures'] or client['hair_type'] not in stylist['hair_types']:
        return f"{stylist['name']} does not specialize in Nick's hair type or texture."
    return f"{stylist['name']} is a match for Nick."

# our current Decision tree logic
def find_stylist(client, stylists):
    for stylist in stylists:
        decision = check_stylist(stylist, client)
        print(decision)
        if "match" in decision:
            return stylist['name']
    return "No suitable stylist found."

winning_stylist = find_stylist(nick, stylists)
print(f"The winning stylist for Nick is: {winning_stylist}")
