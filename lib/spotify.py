import os
import base64
import requests
import webbrowser
import urllib.parse as url

from dotenv import load_dotenv

load_dotenv()


def encodeStringToBase64(text):
    text_bytes = text.encode("ascii")
    base64_bytes = base64.b64encode(text_bytes)
    return base64_bytes.decode("ascii")


class Spotify:
    user_id = os.getenv("USER_ID")
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    redirect_uri = os.getenv("REDIRECT_URI")
    auth_code = ""
    token = ""

    def __init__(self):
        # TODO: listen to callback and get auth code
        self.getUserAuthorization()
        self.requestAccessToken()

    def getUserAuthorization(self):
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "scope": "playlist-modify-public",
            "redirect_uri": self.redirect_uri,
        }
        webbrowser.open(
            f"https://accounts.spotify.com/authorize?{url.urlencode(params)}"
        )
        parsed_url = url.urlparse(input("enter redirected url after login: "))
        code = url.parse_qs(parsed_url.query)["code"]
        self.auth_code = code

    def requestAccessToken(self):
        auth_string = f"{self.client_id}:{self.client_secret}"
        auth_string_base64 = encodeStringToBase64(auth_string)

        url = "https://accounts.spotify.com/api/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {auth_string_base64}",
        }
        payload = {
            "grant_type": "authorization_code",
            "code": self.auth_code,
            "redirect_uri": self.redirect_uri,
        }

        result = requests.post(url, data=payload, headers=headers)
        parsed_result = result.json()
        self.token = parsed_result["access_token"]

    def fetchTrackUri(self, name, artist):
        url = "https://api.spotify.com/v1/search"
        headers = {"Authorization": f"Bearer {self.token}"}
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

    def createPlaylist(self, name):
        url = f"https://api.spotify.com/v1/users/{self.user_id}/playlists"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
        }
        payload = {"name": name}

        result = requests.post(url, json=payload, headers=headers)
        parsed_result = result.json()

        id = parsed_result["id"]
        name = parsed_result["name"]
        print(f"Playlist {name} created")
        return id

    def addTracksToPlaylist(self, playlist_id, track_uris):
        url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
        }
        payload = {"uris": track_uris}

        requests.post(url, json=payload, headers=headers)
        print(f"{len(track_uris)} tracks added to playlist")
        pass
