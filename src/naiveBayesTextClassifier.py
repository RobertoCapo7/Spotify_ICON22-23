import os
import re
import pandas as pd
import numpy as np
import spotipy
from matplotlib import pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import accuracy_score, classification_report, ConfusionMatrixDisplay, confusion_matrix, \
    RocCurveDisplay, PrecisionRecallDisplay
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import BernoulliNB
import lyricsgenius as lg
from spotipy.oauth2 import SpotifyOAuth
from wordcloud import WordCloud
from yellowbrick.model_selection import learning_curve
from stop_words import get_stop_words

genius_id = "Oejkq5pM7oYgIfKI5IidSAe1qqsVCgLZ8DR4O-B3hMd3p-QNahQF79_SeFNHs09M"
genius_secret = "rWrWimfnUHCytx6e_xsEy_u6N2mBzpFp6vX-4ArQTp4Q5sUGKXNlnD2_kucXplneK5_-ozNiLjuinckCaNeBTg"
genius_access_token = "dichmTVxVdSkWt18dizB-Tia_pfS5TQC93qht-dOXLssAo5t786eeqUWfPDmEgtD"

client_id = "1572e8f11a55483ba6336cc98058160e"
client_secret = "f6e304f95c1d41d1b3f9434437e88435"
redirect_uri = "http://localhost:8888/callback"

print("Autenticazione Spotify in corso...")

auth_manager = SpotifyOAuth(client_id=client_id, client_secret=client_secret,
                            redirect_uri=redirect_uri, scope='user-library-read')
sp = spotipy.Spotify(auth_manager=auth_manager)

print("Autenticazione Spotify eseguita con successo!")

print("Autenticazione Genius in corso...")

genius = lg.Genius(genius_access_token)
genius.timeout = 15  # 15 va bene
genius.sleep_time = 1
np.random.seed(5)

print("Autenticazione Genius eseguita con successo!")

path_brani_preferiti = "./datasets/brani_preferiti_2023-08-11.csv"
path_brani_scaricati = "./datasets/brani_scaricati_2023-08-11.csv"

dfBraniPreferiti = pd.read_csv(path_brani_preferiti)
dfBraniScaricati = pd.read_csv(path_brani_scaricati)

dfBraniPreferiti['Liked'] = 1
dfBraniScaricati['Liked'] = 0

dfCombinati = pd.merge(dfBraniPreferiti, dfBraniScaricati, how='outer')

def pulisciTesto(input_string):
    indiceTestoPulito = input_string.find('\n')
    input_string = input_string[indiceTestoPulito + 1:]

    pattern = r'\[.*?\]'  # Pattern per trovare le sottostringhe tra '[' e ']'
    input_string = re.sub(pattern, '', input_string)  # Sostituisci le sottostringhe con una stringa vuota
    return input_string

def naiveBayesClassifier(dataframe):
    X = dataframe['testo']
    y = dataframe['Liked']

    vectorizer = CountVectorizer(stop_words=get_stop_words('it') + get_stop_words('en'))

    X = vectorizer.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    model = BernoulliNB()
    model.fit(X_train, y_train)

    p_train = model.predict(X_train)
    p_test = model.predict(X_test)

    acc_train = accuracy_score(y_train, p_train)
    acc_test = accuracy_score(y_test, p_test)
    report = classification_report(y_test, p_test)

    cm = confusion_matrix(y_test, p_test, labels=model.classes_)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=model.classes_)
    disp.plot()
    plt.savefig('./img/NaiveBayesClassifierConfusionMatrix.png')

    RocCurveDisplay.from_estimator(model, X_test, y_test)
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.savefig('./img/NaiveBayesClassifierRocCurve.png')

    PrecisionRecallDisplay.from_estimator(model, X_test, y_test)
    plt.savefig('./img/NaiveBayesClassifierPrecisionRecallCurve.png')

    learning_curve(model, X, y, scoring='accuracy')
    plt.savefig('./img/NaiveBayesClassifierLearningCurve.png')

    concatenated_string = dataframe['testo'].str.cat(sep='')

    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(concatenated_string)

    # Mostra il WordCloud
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.savefig('./img/WordCloud.png')

    return acc_train, acc_test, report

def recuperaTestiGenius(dataframe):
    testi = []
    for index, row in dataframe.iterrows():
     artista = sp.artist(row['main_artist_id'])
     song = genius.search_song(title=row['track_name'], artist=artista['name'])
     try:
         lyrics = song.lyrics
         lyrics = pulisciTesto(lyrics)
         testi.append(lyrics)
     except AttributeError:
         print("Canzone non trovata! Elimino")
         dataframe.drop(index, inplace=True)

    dataframe['testo'] = testi
    dataframe.to_csv('./datasets/dfGenius.csv')
    return dataframe

dfGeniusPath = "./datasets/dfGenius.csv"

if os.path.exists(dfGeniusPath):
    dfGenius = pd.read_csv(dfGeniusPath)
else:
    print("Dataframe dfGenius non trovato nella cartella datasets!.")
    print("Creo dataframe dfGenius nella directory datasets")
    print("Inizio download dei testi delle canzoni...")
    dfGenius = recuperaTestiGenius(dfCombinati)
    print("Fine download dei testi delle canzoni...")

acc_train, acc_test, report = naiveBayesClassifier(dfGenius)
print("Naive Bayes Classifier")
print(f"Training Accuracy: {acc_train}")
print(f"Test Accuracy: {acc_test}")
print(report)