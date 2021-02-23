import requests


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
    print(player_match_detail)


player_data_return = get_player_infos(21916823)
print(f"Searching matches for {player_data_return['name']} - {player_data_return['mmr']}")
player_match_return = get_player_matches(21916823)
print(f"{player_match_return['total_matches']} found!")
for match_id in player_match_return['matches_id']:
    get_match_details(match_id)
