def decision_tree_comp(stylist, client):
    client_interests = client.get('interests', [])
    stylist_specialities = stylist.get('specialities', [])
    
    match_count = sum(1 for interest in client_interests if interest in stylist_specialities)
    total_interests = len(client_interests)
    
    if total_interests == 0:
        return 0  # Avoid division by zero
    match_percentage = (match_count / total_interests) * 100
    
    return round(match_percentage, 2)

# for now, I'm just simplifying things. will obviously implement read api for client and stylist
client_json = {
    "interests": [1, 3, 5, 7, 9]
}

stylists_json = [
    {
        "fname": "Olivia",
        "lname": "Martinez",
        "specialities": [1, 3, 5, 7, 9]
    },
    {
        "fname": "Ayo",
        "lname": "Fatoye",
        "specialities": [1, 3, 5]
    }
]

# Comparing the client with each stylist and printing the match percentage
match_results = []
for stylist in stylists_json:
    match_percentage = decision_tree_comp(stylist, client_json)
    match_results.append((stylist['fname'] + ' ' + stylist['lname'], match_percentage))

print(match_results)
