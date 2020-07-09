from yandex_music.client import Client
from bs4 import BeautifulSoup
import requests
import sys
import json


class YMusicImporter():
    def __init__(self, email, password):
        print(email, password)
        self.client = Client.from_credentials(email, password)

    def print_info(self, text):
        print()
        print("- - - - - - - - -")
        print(text)
        print("- - - - - - - - -")
        print()

    def import_playlist_from_apple(self, url):
        self.print_info('TRY TO IMPORT PLAYLIST FROM {}'.format(url))
        playlist = self.parse_apple_playlist(url)
        self.create_playlist(playlist)
        self.print_info('IMPORT COMPLETED')


    def parse_apple_playlist(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, features="html.parser")
        playlist = {
            "title": "",
            "tracks": []
        }
        playlist["title"] = " ".join(soup.find("h1", {"class": "product-name"}).contents).strip()
        track_wrappers = soup.find_all("div", {"class": "song-name-wrapper"})
        for track_wrapper in track_wrappers:
            song_name = "".join(track_wrapper.find("div", {"class": "song-name"}).stripped_strings)
            artist_name = track_wrapper.find("a").string
            playlist["tracks"].append((song_name, artist_name))
        return playlist


    def create_playlist(self, playlist_info):
        playlist = self.client.users_playlists_create(playlist_info["title"])
        for i, track in enumerate(playlist_info["tracks"]):
            track_number = i + 1
            track_name = "{}".format(" - ".join(track))
            res = self.client.search(text=track_name, type_="track")
            if res and res.tracks:
                playlist = self.client.users_playlists_insert_track(
                    kind=playlist.kind,
                    track_id=res.tracks.results[0].id,
                    album_id=res.tracks.results[0].albums[0].id,
                    revision=playlist.revision,
                    at=playlist.track_count,
                    timeout=60
                )
            print("{}. {}{}".format(track_number, track_name, "" if res and res.tracks else " [NOT FOUND] "))

def get_settings():
    with open("settings.json", "r") as read_file:
        return json.load(read_file)

if __name__ == "__main__":
    settings = get_settings()
    ya_client = YMusicImporter(**settings)
    ya_client.import_playlist_from_apple(sys.argv[1])