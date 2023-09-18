import spotipy
import saveTracks
import pandas as pd

from spotipy.oauth2 import SpotifyOAuth
from datetime import date

client_id = "1572e8f11a55483ba6336cc98058160e"
client_secret = "f6e304f95c1d41d1b3f9434437e88435"
redirect_uri = "http://localhost:8888/callback"

auth_manager = SpotifyOAuth(client_id=client_id, client_secret=client_secret,
                            redirect_uri=redirect_uri, scope='user-library-read')
sp = spotipy.Spotify(auth_manager=auth_manager)

artists = []
albums = []

offset = 0
limit = 50
brani_preferiti = []

while True:
    results = sp.current_user_saved_tracks(limit=limit, offset=offset)
    tracks = results['items']

    if not tracks:
        break

    brani_preferiti.extend(tracks)
    offset += limit

df_brani_preferiti, artists, albums = saveTracks.saveTracksIntoFile(sp, brani_preferiti, "brani_preferiti", artists, albums)

frames = []
playlist_IDs = [
    "37i9dQZF1DWVKDF4ycOESi", # New Music Friday Italy
    "37i9dQZF1DX6wfQutivYYr", # Hot Hits Italia
    "37i9dQZF1DX0ckkFHFOpuK", # in tendenza
    "37i9dQZEVXbIQnj7RRhdSX", # Top 50 Italia
    "37i9dQZF1DX4JAvHpjipBk", # New Music Friday
    "37i9dQZF1DXcBWIGoYBM5M", # Today's Top Hits
    "37i9dQZEVXbMDoHDwVN2tF", # Top 50 Globale
    "37i9dQZF1DX0XUsuxWHRQd", # RapCaviar
    "37i9dQZF1DX10zKzsJ2jva", # Viva Latino
    "37i9dQZF1DWY7IeIP1cdjF", # Baila Reggaeton
    "37i9dQZF1DWXRqgorJj26U", # Rock Classics
    "37i9dQZF1DWWMOmoXKqHTD", # Songs to Sings in the Car
    "37i9dQZF1DX4o1oenSJRJd", # All Out 2000s
    "37i9dQZF1DX4UtSsGT1Sbe", # All Out 80s
    "37i9dQZF1DX76Wlfdnj7AP", # Beast Mode
    ]

for playlist_id in playlist_IDs:
    results = sp.playlist(playlist_id=playlist_id)
    tracks = results['tracks']['items']
    temp_dataframe, artist, albums = saveTracks.saveTracksIntoFile(sp, tracks, results['name'], artists, albums, saveCSV=False)
    frames.append(temp_dataframe)

other_tracks = pd.concat(frames)
other_tracks = other_tracks.drop_duplicates(subset="track_id")
other_tracks.to_csv(f"brani_scaricati_{date.today()}.csv", index=False)

df_albums = pd.DataFrame(albums)
df_albums = df_albums.drop_duplicates(subset="album_id")
df_albums.to_csv(f"albums_{date.today()}.csv", index=False)

df_artists = pd.DataFrame(artists)
df_artists = df_artists.drop_duplicates(subset="artist_id")
df_artists.to_csv(f"artists_{date.today()}.csv", index=False)
        
        