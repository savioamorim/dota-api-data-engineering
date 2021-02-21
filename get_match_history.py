import requests

url = "https://api.opendota.com/api/proMatches"
data = requests.get(url).json()