import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from os.path import exists
from knowledge_base import KB
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

path_brani_preferiti = "./datasets/brani_preferiti_2023-08-11.csv"

prolog = KB()

if exists(path=path_brani_preferiti):
    df_brani_preferiti = pd.read_csv(path_brani_preferiti)
    
    for index, row in df_brani_preferiti.iterrows():
        if bool(list(prolog.query(f"brano_ascoltato_freq(\"{row['track_id']}\")"))):
            df_brani_preferiti.at[index, 'brano_ascoltato_freq'] = 1
        else: 
            df_brani_preferiti.at[index,'brano_ascoltato_freq'] = 0
            
        if bool(list(prolog.query(f"artista_ascoltato_freq(\"{row['main_artist_id']}\")"))):
            df_brani_preferiti.at[index,'artista_ascoltato_freq'] = 1
        else: 
            df_brani_preferiti.at[index,'artista_ascoltato_freq'] = 0

        if bool(list(prolog.query(f"artista_singolare_importante(\"{row['main_artist_id']}\")"))):
            df_brani_preferiti.at[index, 'artista_singolare_importante'] = 1
        else:
            df_brani_preferiti.at[index, 'artista_singolare_importante'] = 0
            
        if bool(list(prolog.query(f"collaboratore_canzone(\"{row['track_id']}\", IdArtista), artista_ascoltato_freq(IdArtista)"))):
            df_brani_preferiti.at[index, 'coll_artista_asc_freq'] = 1
        else:
            df_brani_preferiti.at[index, 'coll_artista_asc_freq'] = 0
        
        if bool(list(prolog.query(f"simile_struttura_musicale(\"{row['track_id']}\", Canzone), brano_ascoltato_freq(Canzone)"))):
            df_brani_preferiti.at[index, 'sim_struttura_musicale_brano_asc_freq'] = 1
        else: 
            df_brani_preferiti.at[index, 'sim_struttura_musicale_brano_asc_freq'] = 0

        if bool(list(prolog.query(f"simili_emozioni(\"{row['track_id']}\", Canzone), brano_ascoltato_freq(Canzone)"))):
            df_brani_preferiti.at[index, 'sim_emozioni_brano_asc_freq'] = 1
        else: 
            df_brani_preferiti.at[index, 'sim_emozioni_brano_asc_freq'] = 0

        if bool(list(prolog.query(f"macro_categoria_artista(\"{row['main_artist_id']}\", Categoria), macro_categoria_artista(Artista, Categoria), artista_ascoltato_freq(Artista)"))):
            df_brani_preferiti.at[index, 'macro_categoria_artista_asc_freq'] = 1
        else: 
            df_brani_preferiti.at[index, 'macro_categoria_artista_asc_freq'] = 0
            
        if bool(list(prolog.query(f"genere_artista(\"{row['main_artist_id']}\", Genere), genere_ascoltato_freq(Genere, _)"))):
            df_brani_preferiti.at[index, 'genere_asc_freq'] = 1
        else:
            df_brani_preferiti.at[index, 'genere_asc_freq'] = 0
            
        if bool(list(prolog.query(f"ha_composto_canzone(\"{row['main_artist_id']}\", \"{row['track_id']}\"), brano_ascoltato_freq(\"{row['track_id']}\"), artista_ascoltato_freq(\"{row['main_artist_id']}\")"))):
            df_brani_preferiti.at[index, 'ha_composto_canzone'] = 1
        else:
            df_brani_preferiti.at[index, 'ha_composto_canzone'] = 0

        if bool(list(prolog.query(f"stesso_genere_artista(\"{row['main_artist_id']}\", Artista), artista_ascoltato_freq(Artista)"))):
            df_brani_preferiti.at[index, 'stesso_genere_artista_asc_freq'] = 1
        else:
            df_brani_preferiti.at[index, 'stesso_genere_artista_asc_freq'] = 0
        
        if bool(list(prolog.query(f"stesso_album(\"{row['track_id']}\", Canzone), brano_ascoltato_freq(Canzone)"))):
            df_brani_preferiti.at[index, 'stesso_album_brano_asc_freq'] = 1
        else:
            df_brani_preferiti.at[index, 'stesso_album_brano_asc_freq'] = 0
        
        if bool(list(prolog.query(f"stesso_artista(\"{row['track_id']}\", Canzone), brano_ascoltato_freq(Canzone)"))):
            df_brani_preferiti.at[index, 'stesso_artista_brano_asc_freq'] = 1
        else:
            df_brani_preferiti.at[index, 'stesso_artista_brano_asc_freq'] = 0
        
        if bool(list(prolog.query(f"brano_freq_importante(\"{row['track_id']}\")"))):
            df_brani_preferiti.at[index, 'brano_freq_importante'] = 1
        else: 
            df_brani_preferiti.at[index, 'brano_freq_importante'] = 0
        
        if bool(list(prolog.query(f"artista_freq_importante(\"{row['main_artist_id']}\")"))):
            df_brani_preferiti.at[index, 'artista_freq_importante'] = 1
        else:
            df_brani_preferiti.at[index, 'artista_freq_importante'] = 0
        
        if bool(list(prolog.query(f"collaboratore_canzone(\"{row['track_id']}\", IdArtista), artista_freq_importante(IdArtista)"))):
            df_brani_preferiti.at[index, 'coll_artista_freq_imp'] = 1
        else:
            df_brani_preferiti.at[index, 'coll_artista_freq_imp'] = 0
            
        if bool(list(prolog.query(f"macro_categoria_artista(\"{row['main_artist_id']}\", Categoria), macro_categoria_artista(Artista, Categoria), artista_freq_importante(Artista)"))):
            df_brani_preferiti.at[index, 'macro_categoria_artista_freq_imp'] = 1
        else: 
            df_brani_preferiti.at[index, 'macro_categoria_artista_freq_imp'] = 0
            
    selected_columns = [ "brano_ascoltato_freq"
                        , "artista_ascoltato_freq"
                        , "artista_singolare_importante"
                        , "coll_artista_asc_freq"
                        , "sim_struttura_musicale_brano_asc_freq"
                        , "sim_emozioni_brano_asc_freq"
                        , "macro_categoria_artista_asc_freq"
                        , "genere_asc_freq"
                        , "ha_composto_canzone"
                        , "stesso_genere_artista_asc_freq"
                        , "stesso_album_brano_asc_freq"
                        , "stesso_artista_brano_asc_freq"
                        , "brano_freq_importante"
                        , "artista_freq_importante"
                        , "coll_artista_freq_imp"
                        , "macro_categoria_artista_freq_imp"
                    ]
    
    inertia_values = []
    
    X = df_brani_preferiti[selected_columns].values
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    for k in range(1, 11):
        kmeans = KMeans(n_clusters=k, n_init='auto')
        kmeans.fit(X_scaled)
        inertia_values.append(kmeans.inertia_)
        
    plt.figure(figsize=(10, 10))
    plt.plot(range(1, 11), inertia_values, marker='o')
    plt.title("Analisi del gomito")
    plt.xlabel("Numero di cluster")
    plt.ylabel("Inertia")
    plt.xticks(range(1, 11))
    plt.savefig("./img/Analisi_del_gomito.png")
    
    n_cluster = 9
    kmeans = KMeans(n_clusters=n_cluster, n_init='auto')
    
    kmeans.fit(X_scaled)
    
    cluster_labels = kmeans.labels_
    
    cluster_centers = kmeans.cluster_centers_
    distances = np.linalg.norm(X_scaled - cluster_centers[cluster_labels], axis=1)
    
    anomaly_thresholt = np.percentile(distances, 95)
    anomalies = df_brani_preferiti[distances > anomaly_thresholt]
    
    anomalies.to_csv("./results/brani_preferiti_anomali.csv")
    