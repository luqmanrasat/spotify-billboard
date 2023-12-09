# TODO: handle errors
# TODO: listen to callback and get auth code

import os
import base64
import requests
import webbrowser
import urllib.parse

from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()

user_id = os.getenv("USER_ID")
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = os.getenv("REDIRECT_URI")
code = os.getenv("CODE")


def getUserAuthorization():
    params = {
        "response_type": "code",
        "client_id": client_id,
        "scope": "playlist-modify-public",
        "redirect_uri": redirect_uri,
    }
    webbrowser.open(
        f"https://accounts.spotify.com/authorize?{urllib.parse.urlencode(params)}"
    )


def fetchTracks(date):
    url = f"https://www.billboard.com/charts/hot-100/{date}"
    soup = BeautifulSoup(requests.get(url).text, "html.parser")

    track_names = soup.select(".o-chart-results-list__item .a-font-primary-bold-s")
    artists = soup.select(".o-chart-results-list__item .a-font-primary-s")

    tracks = []
    for i in range(len(track_names)):
        track = {
            "name": track_names[i].text.replace("\n", "").replace("\t", ""),
            "artist": artists[i].text.replace("\n", "").replace("\t", ""),
        }
        tracks.append(track)

    print(f"Done scraping chart on {date}")
    return tracks


def encodeStringToBase64(text):
    text_bytes = text.encode("ascii")
    base64_bytes = base64.b64encode(text_bytes)
    return base64_bytes.decode("ascii")


def requestAccessToken():
    auth_string = f"{client_id}:{client_secret}"
    auth_string_base64 = encodeStringToBase64(auth_string)

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {auth_string_base64}",
    }
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
    }

    result = requests.post(url, data=payload, headers=headers)
    parsed_result = result.json()

    return parsed_result["access_token"]


def createPlaylist(name):
    url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    payload = {"name": name}

    result = requests.post(url, json=payload, headers=headers)
    parsed_result = result.json()

    id = parsed_result["id"]
    name = parsed_result["name"]
    print(f"Playlist {name} created")
    return id


def addTracksToPlaylist(playlist_id, track_uris):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    payload = {"uris": track_uris}

    requests.post(url, json=payload, headers=headers)
    print(f"{len(track_uris)} tracks added to playlist")
    pass


def fetchTrackUri(name, artist):
    url = "https://api.spotify.com/v1/search"
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "q": f"track:{name} artist:{artist}",
        "type": "track",
        "limit": 1,
    }

    result = requests.get(url, params=params, headers=headers)
    parsed_result = result.json()
    tracks = parsed_result["tracks"]["items"]
    if not tracks:
        print(f"NOT FOUND: {name} by {artist}")
        return None

    print(f"FOUND: {name} by {artist}")
    return tracks[0]["uri"]


# getUserAuthorization()

chart_date = input(
    "Which date of the chart you want? Type the date in this format YYYY-MM-DD: "
)
tracks = fetchTracks(chart_date)

token = requestAccessToken()

playlist_name = input("Enter playlist name: ")
playlist_id = createPlaylist(playlist_name)

track_uris = []
for track in tracks:
    track_uri = fetchTrackUri(track["name"], track["artist"])
    if track_uri is None:
        continue
    track_uris.append(track_uri)

addTracksToPlaylist(playlist_id, track_uris)
