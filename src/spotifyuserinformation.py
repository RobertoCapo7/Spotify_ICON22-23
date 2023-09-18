import spotipy
import pandas as pd
from spotipy.oauth2 import SpotifyOAuth
from datetime import date


client_id = "1572e8f11a55483ba6336cc98058160e"
client_secret = "f6e304f95c1d41d1b3f9434437e88435"
redirect_uri = "http://localhost:8888/callback"

auth_manager = SpotifyOAuth(client_id=client_id, client_secret=client_secret,
                            redirect_uri=redirect_uri, scope='user-top-read')
sp = spotipy.Spotify(auth_manager=auth_manager)

def getTopUserArtists(sp):
    time_ranges = ['short_term', 'medium_term', 'long_term']

    for tr in time_ranges:
        current_artists = []
        results = sp.current_user_top_artists(time_range=tr, limit=50)
        artists = results['items']

        for artist in artists:
            # print(f"ID: {track['id']} - Nome Artista: {track['name']}")

            current_artist = {
                'id': artist['id'],
                'name': artist['name']
            }

            current_artists.append(current_artist)

        df_top_artists = pd.DataFrame(current_artists)
        df_top_artists.to_csv(f"top_user_artists_{tr}_{date.today()}.csv", index=False)

def getTopUserTracks(sp):
    time_ranges = ['short_term', 'medium_term', 'long_term']

    for tr in time_ranges:
        current_tracks = []
        results = sp.current_user_top_tracks(time_range=tr, limit=50)
        tracks = results['items']

        for track in tracks:
            # print(f"ID: {track['id']} - Nome brano: {track['name']}")

            current_track = {
                'id': track['id'],
                'name': track['name']
            }

            current_tracks.append(current_track)

        df_top_track = pd.DataFrame(current_tracks)
        df_top_track.to_csv(f"top_user_track_{tr}_{date.today()}.csv", index=False)