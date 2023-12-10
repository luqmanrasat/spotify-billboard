import requests

from bs4 import BeautifulSoup
from lib.spotify import Spotify


def scrapeChartForTracks(date):
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


chart_date = input(
    "Which date of the chart you want? Type the date in this format YYYY-MM-DD: "
)
tracks = scrapeChartForTracks(chart_date)

s = Spotify()

track_uris = []
for track in tracks:
    track_uri = s.fetchTrackUri(track["name"], track["artist"])
    if track_uri is None:
        continue
    track_uris.append(track_uri)

playlist_name = input("Enter playlist name: ")
playlist_id = s.createPlaylist(playlist_name)

s.addTracksToPlaylist(playlist_id, track_uris)
