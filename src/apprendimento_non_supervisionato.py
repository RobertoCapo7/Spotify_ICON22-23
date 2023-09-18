import ast
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from os.path import exists
from sklearn.cluster import DBSCAN
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MultiLabelBinarizer
from mapping_genres import map_genre_to_macro_category

path_artists = "./datasets/artists_2023-08-11.csv"

def get_metrics(eps, min_samples, dataset, iter_):    
    dbscan_model_ = DBSCAN( eps = eps, min_samples = min_samples)
    dbscan_model_.fit(dataset)
    
    noise_indices = dbscan_model_.labels_ == -1
    
    if True in noise_indices:
        neighboors = NearestNeighbors(n_neighbors = 6).fit(dataset)
        distances, indices = neighboors.kneighbors(dataset)
        noise_distances = distances[noise_indices, 1:]
        noise_mean_distance = round(noise_distances.mean(), 3)
    else:
        noise_mean_distance = None
        
    number_of_clusters = len(set(dbscan_model_.labels_[dbscan_model_.labels_ >= 0]))
        
    print("%3d | Tested with eps = %3s and min_samples = %3s | %5s %4s" % (iter_, eps, min_samples, str(noise_mean_distance), number_of_clusters))
        
    return(noise_mean_distance, number_of_clusters)

def ricerca_iperparametri(dataframe):
    eps_to_test = [round(esp, 1) for esp in np.arange(0.1, 2, 0.1)]
    min_samples_to_test = range(5, 50, 5)
    
    # Dataframe per la metrica sulla distanza media dei noise points dai K punti più vicini
    results_noise = pd.DataFrame(
        data=np.zeros((len(eps_to_test), len(min_samples_to_test))),
        columns=min_samples_to_test,
        index=eps_to_test
    )
    
    # Dataframe per la metrica sul numero di cluster
    results_cluster = pd.DataFrame(
        data=np.zeros((len(eps_to_test), len(min_samples_to_test))),
        columns=min_samples_to_test,
        index=eps_to_test
    )
    
    iter_ = 0
    print("ITER| INFO%s |  DIST    CLUS" % (" "*39))
    print("-"*65)
    
    for eps in eps_to_test:
        for min_samples in min_samples_to_test:
            
            iter_ += 1
            
            noise_metric, cluster_metric, = get_metrics(eps, min_samples, dataframe, iter_)
            
            results_noise.loc[eps, min_samples] = noise_metric
            results_cluster.loc[eps, min_samples] = cluster_metric 
            
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16,8) )

    sns.heatmap(results_noise, annot = True, ax = ax1, cbar = False).set_title("METRIC: Mean Noise Points Distance")
    sns.heatmap(results_cluster, annot = True, ax = ax2, cbar = False).set_title("METRIC: Number of clusters")

    ax1.set_xlabel("N"); 
    ax2.set_xlabel("N")
    ax1.set_ylabel("EPSILON"); 
    ax2.set_ylabel("EPSILON")

    plt.tight_layout(); 
    plt.savefig("parameters.png")
    
def clustering(dataframe, eps=0.3, min_samples=5):
    
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    
    labels = dbscan.fit_predict(dataframe)
    dataframe.loc[:, 'cluster'] = labels
        
    return dataframe

"""
def best_parameters_clustering(data):
    best_eps = None
    best_min_samples = None
    best_score = -1
    
    for eps in np.arange(0.1, 1.0, 0.1):
        for min_samples in range(1, 10):
            dbscan = DBSCAN(eps=eps, min_samples=min_samples)
            labels = dbscan.fit_predict(data)
            
            if len(np.unique(labels)) > 1:
                score = silhouette_score(data, labels)
                
                # print(f"eps: {eps} - min_samples: {min_samples} - score: {score}")
                
                if score > best_score:
                    best_score = score
                    best_eps = eps
                    best_min_samples = min_samples
                    
    print(f"Best Silhouette Score: {best_score}")
    print(f"Best eps: {best_eps}")
    print(f"Best min_samples: {best_min_samples}")
    
    return best_eps, best_min_samples
"""
if exists(path_artists):
    df_artists = pd.read_csv(path_artists)
    
    # trasforma le concatenazioni dei generi musicali in una lista di stringhe dei generi
    df_artists['artist_genres'] = df_artists['artist_genres'].apply(ast.literal_eval)   
      
    # ogni categoria viene smistata in una macro categoria
    for index, row in df_artists.iterrows():
        macro_genres = []
    
        for genre in row['artist_genres']:
            macro_genres.append(map_genre_to_macro_category(genre))
    
        df_artists.at[index, 'artist_genres'] = macro_genres
    
    # trasformazione dei generi in colonne booleane
    mlb = MultiLabelBinarizer()
    genre_encoded = mlb.fit_transform(df_artists['artist_genres'])
    genre_df = pd.DataFrame(genre_encoded, columns=mlb.classes_)
    df_encoded = pd.concat([df_artists.drop('artist_genres', axis=1), genre_df], axis=1)
    
    # eliminazione degli artisti per cui non è stato definito un genere
    genre_columns = df_encoded.columns[5:]
    sum_of_genres = df_encoded[genre_columns].sum(axis=1)
    df_filtered = df_encoded[sum_of_genres > 0]
    
    columns_to_drop = [
        "artist_id",
        "artist_name",
        "artist_followers",
        "artist_popularity"
    ]
    
    columns = list(df_filtered.columns)
    for column in columns_to_drop:
        columns.remove(column)
    
    ricerca_iperparametri(df_filtered[columns])
    
    # eps, min_samples = best_parameters_clustering(data=df_filtered[columns])
      
    dataframe = clustering(df_filtered[columns])
    data = pd.concat([df_filtered.drop(columns, axis=1), dataframe], axis=1)  
    data.to_csv("./datasets/clusteringDBSCAN.csv")
else: print("Non è stato possibile trovare il file inserito, ricontrolla il path")