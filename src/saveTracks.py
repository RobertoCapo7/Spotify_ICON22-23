import pandas as pd
from datetime import date

def saveTracksIntoFile(sp, tracks, fileName, artists, albums, saveCSV=True):
    saved_tracks = []
    
    for track in tracks:
        added_at = track['added_at']
        track = track['track']
        
        print(f"nome brano: {track['name']}")
        
        features = sp.audio_features(track['id'])
        
        if features[0] != None:
            
            artist_result = sp.artist(track['artists'][0]['id'])                           
        
            current_artist = {
                'artist_id': track['artists'][0]['id'],
                'artist_name': track['artists'][0]['name'],
                'artist_followers': artist_result['followers']['total'],
                'artist_genres': artist_result['genres'],
                'artist_popularity': artist_result['popularity']
            }            
            artists.append(current_artist)
            
            side_artists = []
            for side_artist in track['artists'][1:]:
                artist_result = sp.artist(side_artist['id'])
                current_artist = {
                'artist_id': side_artist['id'],
                'artist_name': side_artist['name'],
                'artist_followers': artist_result['followers']['total'],
                'artist_genres': artist_result['genres'],
                'artist_popularity': artist_result['popularity']
                }
                artists.append(current_artist)
                side_artists.append(side_artist['id'])

            album_result = sp.album(track['album']['id'])
            current_album = {
                'album_id': track['album']['id'],
                'album_name': track['album']['name'],
                'album_total_tracks': track['album']['total_tracks'],
                'album_type': track['album']['album_type'],
                'album_release_date': track['album']['release_date'],
                # 'album_genres': album_result['genres'],
                'album_label': album_result['label'],
                'album_popularity': album_result['popularity']
            }    
            albums.append(current_album)
            
            current_track = {
                'track_id': track['id'],
                'track_added_at': added_at,
                'track_name': track['name'],
                'album_id': track['album']['id'],
                'main_artist_id': track['artists'][0]['id'], 
                'side_artists_id': side_artists,
                'track_duration': track['duration_ms'],
                'track_explicit': track['explicit'],
                'track_popularity': track['popularity'],
                'track_key': features[0]['key'],
                'track_bpm': features[0]['tempo'],
                'track_energy': features[0]['energy'],
                'track_danceability': features[0]['danceability'],
                'track_happiness': features[0]['valence'],
                'track_loudness': features[0]['loudness'],
                'track_acousticness': features[0]['acousticness'],
                'track_instrumentalness': features[0]['instrumentalness'],
                'track_liveness': features[0]['liveness'],
                'track_mode': features[0]['mode'],
                'track_speechiness': features[0]['speechiness'],
                'track_time_signature': features[0]['time_signature']
            }
            saved_tracks.append(current_track)
    
    df_saved_tracks = pd.DataFrame(saved_tracks)
    if(saveCSV): 
        df_saved_tracks.to_csv(f"{fileName}_{date.today()}.csv", index=False)
    
    return df_saved_tracks, artists, albums