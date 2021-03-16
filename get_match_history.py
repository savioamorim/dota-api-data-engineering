import argparse
import requests
import time
from pymongo import MongoClient


def insert_match_mongo(match_data_details, db_collection, sleep_time=0):
    db_collection.insert_one(match_data_details)
    time.sleep(sleep_time)


def get_player_infos(steam_id):
    url = f"https://api.opendota.com/api/players/{steam_id}"
    player_data_json = requests.get(url).json()
    player_data = {'name': player_data_json['profile']['personaname'],
                   'mmr': player_data_json['mmr_estimate']['estimate']}
    return player_data


def get_all_player_matches_id(steam_id):
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


def get_most_recent_matches(player_match_return, db_collection):
    most_recent_player_match = db_collection.find_one(sort=[('start_time', -1)])
    if most_recent_player_match is not None:
        most_recent_player_match = most_recent_player_match['start_time']

    for match_id in player_match_return['matches_id']:
        match_data_details_api = get_match_details(match_id)
        if most_recent_player_match == match_data_details_api['start_time']:
            print("All matches already in MongoDB!")
            break
        insert_match_mongo(match_data_details_api, db_collection, 1)


def get_all_matches(player_match_return, db_collection):
    matches_id_mongo = list(db_collection.find({}, {'_id': 0, 'match_id': 1}))
    matches_id = []
    for match_id in matches_id_mongo:
        matches_id.append(match_id['match_id'])

    print(matches_id)
    for match_id_api in player_match_return['matches_id']:
        print(f"MATCH_ID_API:{match_id_api}")
        if match_id_api in matches_id:
            continue
        match_data_details_api = get_match_details(match_id_api)
        insert_match_mongo(match_data_details_api, db_collection, 1)


def main():
    MONGODB_IP = "localhost"
    MONGODB_PORT = 27017
    mongodb_client = MongoClient(MONGODB_IP, MONGODB_PORT)
    mongodb_database = mongodb_client["dota_raw"]

    parser = argparse.ArgumentParser()
    parser.add_argument("steam_id")
    parser.add_argument("--search_type", choices=["recent", "all"])
    args = parser.parse_args()

    player_data_return = get_player_infos(args.steam_id)
    print(f"Searching matches for {player_data_return['name']} - MMR: {player_data_return['mmr']}")

    player_matches_id_return = get_all_player_matches_id(args.steam_id)
    print(f"{player_matches_id_return['total_matches']} matches found!")

    if args.search_type == 'recent':
        get_most_recent_matches(player_matches_id_return, mongodb_database["match_player_history"])
    elif args.search_type == 'all':
        get_all_matches(player_matches_id_return, mongodb_database["match_player_history"])


if __name__ == "__main__":
    main()
