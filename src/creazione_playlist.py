import ast
import random
import pandas as pd

from mapping_genres import map_genre_to_macro_category

def check_genere(brano1, brano2):    
    for genre1 in brano1['artist_genres']:
        for genre2 in brano2['artist_genres']:
            if genre1 == genre2:
                return False
    
    return True

def check_durata_totale(playlist):
    durata_totale = sum(brano['track_duration'] for brano in playlist)
    return durata_totale <= 3600000

"""
def check_artista_emergente(playlist):
    num_artisti_emergenti = sum(1 for brano in playlist if brano["emergente"])
    return num_artisti_emergenti >= 1
"""

def evaluate_playlist(playlist):
    num_violations = 0
    
    for i, brano in enumerate(playlist):
        for prev_brano in playlist[:i]:
            if not check_genere(brano, prev_brano):
                num_violations += 1
       
    
    if not check_durata_totale(playlist):
        num_violations += 1
    
    """
    if not check_artista_emergente(playlist):
        num_violations += 1
    """
    return num_violations

def most_improving_step(current_playlist, brani):
    best_playlist = current_playlist
    best_evaluation = evaluate_playlist(current_playlist)
    
    for i, brano in enumerate(current_playlist):
        for j in range(len(current_playlist)):
            if i != j:
                new_playlist = current_playlist[:]                
                new_playlist[j] = random.choice(brani)
                new_evaluation = evaluate_playlist(new_playlist)
                
                if new_evaluation < best_evaluation:
                    best_evaluation = new_evaluation
                    best_playlist = new_playlist
    
    return best_playlist
    
df_brani = pd.read_csv("./results/canzoni_possibili_AdaBoostClassifier.csv")
df_artisti = pd.read_csv("./datasets/artists_2023-08-11.csv")

df_artisti['artist_genres'] = df_artisti['artist_genres'].apply(ast.literal_eval)  

for index, row in df_artisti.iterrows():
    macro_genres = []
    for genre in row['artist_genres']:
        macro_genres.append(map_genre_to_macro_category(genre))
    df_artisti.at[index, 'artist_genres'] = list(set(macro_genres))
    
df_brani['artist_id'] = df_brani['main_artist_id']
df = pd.merge(df_brani, df_artisti, on="artist_id")

selected_columns = [
    "track_id",
    "artist_id",
    "track_duration",
    "track_name",
    "artist_popularity",
    "artist_genres"
]

df = df[selected_columns]
df = df[df['artist_genres'].apply(lambda x: len(x) > 0)]

brani = df.to_dict(orient='records')
playlist = random.sample(brani, 10)

num_iterations = 1000
for _ in range(num_iterations):
    new_playlist = most_improving_step(playlist, brani)
    if evaluate_playlist(new_playlist) < evaluate_playlist(playlist):
        playlist = new_playlist

pd.DataFrame(playlist).to_csv("./results/playlist.csv")

