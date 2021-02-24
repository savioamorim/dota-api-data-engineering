import requests
from pymongo import MongoClient

MONGODB_IP = "localhost"
MONGODB_PORT = 27017
mongodb_client = MongoClient(MONGODB_IP, MONGODB_PORT)
mongodb_database = mongodb_client["dota_raw"]


def insert_match_mongo(match_data_details, db_collection):
    db_collection.insert_one(match_data_details)


def get_player_infos(steam_id):
    url = f"https://api.opendota.com/api/players/{steam_id}"
    player_data_json = requests.get(url).json()
    player_data = {'name': player_data_json['profile']['personaname'],
                   'mmr': player_data_json['mmr_estimate']['estimate']}
    return player_data


def get_player_matches(steam_id):
    url = f"https://api.opendota.com/api/players/{steam_id}/matches"
    player_match_json = requests.get(url).json()
    match_id = []
    for match in player_match_json:
        match_id.append(match['match_id'])

    player_match = {'matches_id': match_id,
                    'total_matches': len(match_id)}
    return player_match


def get_match_details(player_match_id):
    url = f"https://api.opendota.com/api/matches/{player_match_id}"
    player_match_detail = requests.get(url).json()
    print(f"Hooking match id: {player_match_detail['match_id']}")
    return player_match_detail


player_data_return = get_player_infos(21916823)
print(f"Searching matches for {player_data_return['name']} - {player_data_return['mmr']}")

player_match_return = get_player_matches(21916823)
print(f"{player_match_return['total_matches']} found!")
for match_id in player_match_return['matches_id']:
    match_data_details = get_match_details(match_id)
    insert_match_mongo(match_data_details, mongodb_database["match_player_history"])


