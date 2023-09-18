import pyswip
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from os.path import exists
from scipy.stats import uniform, randint

from knowledge_base import KB
from sklearn.preprocessing import MinMaxScaler

# Modelli
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier

# Valutazione
from sklearn.decomposition import PCA
from sklearn.model_selection import learning_curve
from sklearn.model_selection import cross_validate
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV, StratifiedShuffleSplit, RandomizedSearchCV
from sklearn.metrics import classification_report, accuracy_score, auc, roc_curve, confusion_matrix

import warnings
warnings.filterwarnings('ignore')

path_brani_preferiti = "./datasets/brani_preferiti_2023-08-11.csv"
path_brani_scaricati = "./datasets/brani_scaricati_2023-08-11.csv"

def cross_validation(model, _X, _y, _cv=5):
    _scoring = ['accuracy', 'precision', 'recall', 'f1']
    results = cross_validate(estimator=model
                             , X=_X
                             , y=_y
                             , cv=_cv
                             , scoring=_scoring
                             , return_train_score=True
                            )
    return {
        "Training Accuracy scores": results['train_accuracy'],
        "Mean Training Accuracy": results['train_accuracy'].mean()*100,
        "Training Precision scores": results['train_precision'],
        "Mean Training Precision": results['train_precision'].mean(),
        "Training Recall scores": results['train_recall'],
        "Mean Training Recall": results['train_recall'].mean(),
        "Training F1 scores": results['train_f1'],
        "Mean Training F1 Score": results['train_f1'].mean(),
        "Validation Accuracy scores": results['test_accuracy'],
        "Mean Validation Accuracy": results['test_accuracy'].mean()*100,
        "Validation Precision scores": results['test_precision'],
        "Mean Validation Precision": results['test_precision'].mean(),
        "Validation Recall scores": results['test_recall'],
        "Mean Validation Recall": results['test_recall'].mean(),
        "Validation F1 scores": results['test_f1'],
        "Mean Validation F1 Score": results['test_f1'].mean()
    }

def plot_results(x_label, y_label, plot_title, train_data, val_data):
    '''
        x_label: str
            Nome dell'algoritmo utilizzato nel training e.g 'Decision Tree'
            
        y_label: str
            Nome della metrica che deve essere visualzzata e.g 'Accuracy'
            
        plot_title: str
            Titolo del plot e.g 'Accuracy Plot'
            
        train_result: array
            Array che contiene la precisione di addestramento, l'accuratezza o l'f1
            
        test_result: array
            Array che contiene la precisione di valutazione, l'accuratezza o l'f1
    '''
    
    plt.figure(figsize=(12, 6))
    labels = ["1st Fold", "2nd Fold", "3rd Fold", "4th Fold", "5th Fold"]
    X_axis = np.arange(len(labels))
    ax = plt.gca()
    plt.ylim(0.40000, 1)
    plt.bar(X_axis-0.2, train_data, 0.4, color='blue', label='Training')
    plt.bar(X_axis+0.2, val_data, 0.4, color='red', label='Validation')
    plt.title(plot_title)
    plt.xticks(X_axis, labels)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.legend()
    plt.grid(True)
    plt.show()
     
def plot_range_results(x_label, y_label, plot_title, train_data, val_data, range):
    plt.figure(figsize=(12, 6))
    plt.plot(range, train_data, marker='o', linestyle='-', color='blue', label='training scores')
    plt.plot(range, val_data, marker='o', linestyle='-', color='red', label='test scores')
    plt.title(plot_title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.legend()
    plt.grid(True)
    plt.savefig(f"./img/{plot_title} - Scores.png")
    
def model_report(model_name, y_pred, y_true):
    print(f"{model_name} - accuracy: {accuracy_score(y_pred, y_test) * 100}%")
    print(f"{model_name} - report completo:\n {classification_report(y_pred, y_test)}")
    
    fpr, tpr, _ = roc_curve(y_true, y_pred)  
    roc_auc = auc(fpr, tpr)
    
    plt.figure()
    plt.plot(fpr, tpr, color='darkorange', lw=2, label='Curva di ROC (area = %0.2f)' % roc_auc)
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.title(f'{model_name} - Curva di ROC')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.legend(loc="lower right")
    plt.savefig(f"./img/{model_name} - Curva di ROC.png")
    
     # Calcoliamo la matrice di confusione
    conf_matrix = confusion_matrix(y_test, y_pred)

    # Visualizziamo la matrice di confusione
    plt.figure(figsize=(8, 6))
    sns.heatmap(conf_matrix, annot=True, fmt="d", cmap="Blues", cbar=False)
    plt.xlabel('Predicted Labels')
    plt.ylabel('True Labels')
    plt.title(f'{model_name} - Confusion Matrix')
    plt.savefig(f'./img/{model_name} - Confusion Matrix.png')
    
def learning_stats(model, X, y):
    train_size_abs, train_scores, test_scores = learning_curve(model, X, y, train_sizes=[0.3, 0.6, 0.9])
    for train_size, cv_train_scores, cv_test_scores in zip(train_size_abs, train_scores, test_scores):
        print(f"{train_size} esempi sono stati utilizzati per addestrare il modello")
        print(f"La media dell'accuracy dei dati di train è di {cv_train_scores.mean():.2f}")
        print(f"La media dell'accuracy dei dati di test è di {cv_test_scores.mean():.2f}")

if exists(path_brani_preferiti) and exists(path_brani_scaricati):
    df_brani_preferiti = pd.read_csv(path_brani_preferiti)
    df_brani_scaricati = pd.read_csv(path_brani_scaricati)

df_brani_preferiti['Liked'] = 1
df_brani_scaricati['Liked'] = 0

df_brani = pd.merge(df_brani_preferiti, df_brani_scaricati, how='outer')
df_brani = df_brani.drop_duplicates(subset='track_id')

prolog = KB()

for index, row in df_brani.iterrows():
    if bool(list(prolog.query(f"brano_ascoltato_freq(\"{row['track_id']}\")"))):
        df_brani.at[index, 'brano_ascoltato_freq'] = 1
    else: 
        df_brani.at[index,'brano_ascoltato_freq'] = 0
        
    if bool(list(prolog.query(f"artista_ascoltato_freq(\"{row['main_artist_id']}\")"))):
        df_brani.at[index,'artista_ascoltato_freq'] = 1
    else: 
        df_brani.at[index,'artista_ascoltato_freq'] = 0

    if bool(list(prolog.query(f"artista_singolare_importante(\"{row['main_artist_id']}\")"))):
        df_brani.at[index, 'artista_singolare_importante'] = 1
    else:
        df_brani.at[index, 'artista_singolare_importante'] = 0
        
    if bool(list(prolog.query(f"collaboratore_canzone(\"{row['track_id']}\", IdArtista), artista_ascoltato_freq(IdArtista)"))):
        df_brani.at[index, 'coll_artista_asc_freq'] = 1
    else:
        df_brani.at[index, 'coll_artista_asc_freq'] = 0
    
    if bool(list(prolog.query(f"simile_struttura_musicale(\"{row['track_id']}\", Canzone), brano_ascoltato_freq(Canzone)"))):
        df_brani.at[index, 'sim_struttura_musicale_brano_asc_freq'] = 1
    else: 
        df_brani.at[index, 'sim_struttura_musicale_brano_asc_freq'] = 0

    if bool(list(prolog.query(f"simili_emozioni(\"{row['track_id']}\", Canzone), brano_ascoltato_freq(Canzone)"))):
        df_brani.at[index, 'sim_emozioni_brano_asc_freq'] = 1
    else: 
        df_brani.at[index, 'sim_emozioni_brano_asc_freq'] = 0

    if bool(list(prolog.query(f"macro_categoria_artista(\"{row['main_artist_id']}\", Categoria), macro_categoria_artista(Artista, Categoria), artista_ascoltato_freq(Artista)"))):
        df_brani.at[index, 'macro_categoria_artista_asc_freq'] = 1
    else: 
        df_brani.at[index, 'macro_categoria_artista_asc_freq'] = 0
        
    if bool(list(prolog.query(f"genere_artista(\"{row['main_artist_id']}\", Genere), genere_ascoltato_freq(Genere, _)"))):
        df_brani.at[index, 'genere_asc_freq'] = 1
    else:
        df_brani.at[index, 'genere_asc_freq'] = 0
        
    if bool(list(prolog.query(f"ha_composto_canzone(\"{row['main_artist_id']}\", \"{row['track_id']}\"), brano_ascoltato_freq(\"{row['track_id']}\"), artista_ascoltato_freq(\"{row['main_artist_id']}\")"))):
        df_brani.at[index, 'ha_composto_canzone'] = 1
    else:
        df_brani.at[index, 'ha_composto_canzone'] = 0

    if bool(list(prolog.query(f"stesso_genere_artista(\"{row['main_artist_id']}\", Artista), artista_ascoltato_freq(Artista)"))):
        df_brani.at[index, 'stesso_genere_artista_asc_freq'] = 1
    else:
        df_brani.at[index, 'stesso_genere_artista_asc_freq'] = 0
    
    if bool(list(prolog.query(f"stesso_album(\"{row['track_id']}\", Canzone), brano_ascoltato_freq(Canzone)"))):
        df_brani.at[index, 'stesso_album_brano_asc_freq'] = 1
    else:
        df_brani.at[index, 'stesso_album_brano_asc_freq'] = 0
    
    if bool(list(prolog.query(f"stesso_artista(\"{row['track_id']}\", Canzone), brano_ascoltato_freq(Canzone)"))):
        df_brani.at[index, 'stesso_artista_brano_asc_freq'] = 1
    else:
        df_brani.at[index, 'stesso_artista_brano_asc_freq'] = 0
    
    if bool(list(prolog.query(f"brano_freq_importante(\"{row['track_id']}\")"))):
        df_brani.at[index, 'brano_freq_importante'] = 1
    else: 
        df_brani.at[index, 'brano_freq_importante'] = 0
    
    if bool(list(prolog.query(f"artista_freq_importante(\"{row['main_artist_id']}\")"))):
        df_brani.at[index, 'artista_freq_importante'] = 1
    else:
        df_brani.at[index, 'artista_freq_importante'] = 0
    
    if bool(list(prolog.query(f"collaboratore_canzone(\"{row['track_id']}\", IdArtista), artista_freq_importante(IdArtista)"))):
        df_brani.at[index, 'coll_artista_freq_imp'] = 1
    else:
        df_brani.at[index, 'coll_artista_freq_imp'] = 0
        
    if bool(list(prolog.query(f"macro_categoria_artista(\"{row['main_artist_id']}\", Categoria), macro_categoria_artista(Artista, Categoria), artista_freq_importante(Artista)"))):
        df_brani.at[index, 'macro_categoria_artista_freq_imp'] = 1
    else: 
        df_brani.at[index, 'macro_categoria_artista_freq_imp'] = 0

df_brani['track_explicit'] = df_brani['track_explicit'].astype(int)

columns_to_scale = ['track_bpm', 'track_popularity', 'track_loudness', 'track_duration']
scaler = MinMaxScaler()
df_brani[columns_to_scale] = scaler.fit_transform(df_brani[columns_to_scale])

selected_columns = [ "track_duration"
                    , "track_explicit"
                    , "track_popularity" 
                    # , "track_key"
                    , "track_bpm"
                    , "track_energy"
                    , "track_danceability"
                    , "track_happiness"
                    , "track_loudness"
                    , "track_acousticness"
                    , "track_instrumentalness"
                    , "track_liveness"
                    # , "track_mode"
                    , "track_speechiness"
                    # , "track_time_signature"
                    , "brano_ascoltato_freq"
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

X = df_brani[selected_columns]
y = df_brani['Liked']

X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42, test_size=0.4)

# Importanza delle componenenti principali - quali componenti spiegano maggiormente la variazione dei dati
pca = PCA()
pca.fit(X_train)
variance_ratio = pca.explained_variance_ratio_

for column, variance in zip(selected_columns, variance_ratio):
    print(f"'{column}': {variance * 100:.2f};")

# Classificazione dataset con k-NN e valutazione modello
k_range = range(1, 13) #
mean_training_accuracy_scores = []
mean_validation_accuracy_scores = []
for k in k_range:
    knn = KNeighborsClassifier(n_neighbors=k)
    
    results = cross_validation(knn, X.values, y.values, 5)
    mean_training_accuracy_scores.append(results["Mean Training Accuracy"])
    mean_validation_accuracy_scores.append(results["Mean Validation Accuracy"])
plot_range_results("K", "Scores", "KNN", mean_training_accuracy_scores, mean_validation_accuracy_scores, k_range)

mean_training_accuracy_scores = []
mean_validation_accuracy_scores = []
# Classificazione dataset con Decision Tree Classifier e valutazione
for n in range(1, 16):
    decision_tree_model = DecisionTreeClassifier(max_depth=n
                                                 , criterion='entropy'
                                                 , min_samples_split=5
                                                 , random_state=42
                                                )
    
    results = cross_validation(decision_tree_model, X, y, 5)
    mean_training_accuracy_scores.append(results["Mean Training Accuracy"])
    mean_validation_accuracy_scores.append(results["Mean Validation Accuracy"])
plot_range_results("Profondità alberi", "Scores", "Decision Tree Classifier", mean_training_accuracy_scores, mean_validation_accuracy_scores, range(1, 16))

# Classificazione dataset con Random Forest Classifier e valutazione
mean_training_accuracy_scores = []
mean_validation_accuracy_scores = []
for n in range(1, 16):
    random_forest_model = RandomForestClassifier(max_depth=n
                                                 , criterion= 'entropy'
                                                 , min_samples_split=5
                                                 , random_state=42
                                                )

    results = cross_validation(random_forest_model, X, y, 5)
    mean_training_accuracy_scores.append(results["Mean Training Accuracy"])
    mean_validation_accuracy_scores.append(results["Mean Validation Accuracy"])
plot_range_results("Profondità alberi", "Scores", "Random Forest Classifier", mean_training_accuracy_scores, mean_validation_accuracy_scores, range(1, 16))
    
# Classificazione dataset con Gradient Boosting Classifier
mean_training_accuracy_scores = []
mean_validation_accuracy_scores = []
for n in range(1, 21):
    gradient_boosting_model = GradientBoostingClassifier(n_estimators=n
                                                         , learning_rate=0.5
                                                         , random_state=42
                                                         # , max_features="log2"
                                                        )
    
    results = cross_validation(gradient_boosting_model, X, y, 5)
    mean_training_accuracy_scores.append(results["Mean Training Accuracy"])
    mean_validation_accuracy_scores.append(results["Mean Validation Accuracy"])
plot_range_results("Numero alberi", "Scores", "Gradient Boosting Classifier", mean_training_accuracy_scores, mean_validation_accuracy_scores, range(1, 21))

# Classificazione dataset con Ada Boost
mean_training_accuracy_scores = []
mean_validation_accuracy_scores = []
for n in range(1, 21):
    ada_boost = AdaBoostClassifier(n_estimators=n, learning_rate=1) 
    
    results = cross_validation(ada_boost, X, y, 5)
    mean_training_accuracy_scores.append(results["Mean Training Accuracy"])
    mean_validation_accuracy_scores.append(results["Mean Validation Accuracy"])
plot_range_results("Numero alberi", "Scores", "Ada Boost Classifier", mean_training_accuracy_scores, mean_validation_accuracy_scores, range(1, 21))

# Classificazione dataset con Regressione logica e valutazione
mean_training_accuracy_scores = []
mean_validation_accuracy_scores = []
C_values = [0.001, 0.01, 0.1, 1, 10, 100]
for C in C_values:
    logistic_regression = LogisticRegression(C=C, random_state=42)
    results = cross_validation(logistic_regression, X, y, 5)
    mean_training_accuracy_scores.append(results["Mean Training Accuracy"])
    mean_validation_accuracy_scores.append(results["Mean Validation Accuracy"])
plot_range_results("C", "Scores", "Logistic Regression Classifier", mean_training_accuracy_scores, mean_validation_accuracy_scores, C_values)

# Classificazione dataset con SVM e valutazione
param_grid = {
    'C': [0.1, 1, 10],
    'kernel': ['linear', 'rbf', 'poly'],
    'gamma': [0.1, 1, 'scale']
}
svc = SVC(cache_size=1000)
grid = GridSearchCV(estimator=svc, param_grid=param_grid, cv=3, scoring='accuracy')
grid.fit(X, y)

print("I parametri migliori sono %s con lo score di %0.2f" %(grid.best_params_, grid.best_score_))

# Classificazione dataset con MLPClassifier e valutazione
param_grid = {
    'hidden_layer_sizes': [(50,), (100,), (50, 50)],
    'activation': ['logistic', 'tanh', 'relu'],
    'solver': ['adam', 'sgd'],
    'alpha': [0.0001, 0.001, 0.01]
}

param_dist = {
    'hidden_layer_sizes': [(50,), (100,), (50, 50)],
    'activation': ['logistic', 'tanh', 'relu'],
    'solver': ['adam', 'sgd'],
    'alpha': uniform(0.0001, 0.01)
}

# Creazione del classificatore MLP
clf = MLPClassifier(max_iter=10000, random_state=42)

# Ricerca a griglia con cross-validation
grid_search = GridSearchCV(clf, param_grid, cv=5, n_jobs=-1)
grid_search.fit(X, y)

# Ricerca casuale con cross-validation
random_search = RandomizedSearchCV(clf, param_distributions=param_dist, n_iter=10, cv=5, n_jobs=-1, random_state=42)
random_search.fit(X, y)

# Parametri ottimali e risultati
best_params = grid_search.best_params_
best_score = grid_search.best_score_
print("Ricerca a griglia - Best Parameters:", best_params)
print("Ricerca a griglia - Best Cross-Validation Score:", best_score)

best_params = random_search.best_params_
best_score = random_search.best_score_
print("Ricerca Casuale - Best Parameters:", best_params)
print("Ricerca Casuale - Best Cross-Validation Score:", best_score)

classifiers = [
    KNeighborsClassifier(n_neighbors=5),
    DecisionTreeClassifier(max_depth=6, criterion='entropy', min_samples_split=5, random_state=42),
    RandomForestClassifier(max_depth=8, criterion='entropy', min_samples_split=5, random_state=42),
    GradientBoostingClassifier(n_estimators=11, learning_rate=0.5, random_state=42, max_features="log2"),
    AdaBoostClassifier(n_estimators=10, learning_rate=1),
    LogisticRegression(C=10, random_state=42),
    SVC(cache_size=1000, C=0.1, gamma=1, kernel='poly'),
    MLPClassifier(max_iter=10000, random_state=42, activation='tanh', alpha=0.01, hidden_layer_sizes=(50, 50), solver='adam')
]

df_other_songs_original = df_brani[df_brani['Liked'] == 0]

for classifier in classifiers:
    classifier.fit(X_train, y_train)
    feature_importances = getattr(classifier, "feature_importances_", None)
    coef_ = getattr(classifier, "coef_", None)   

    if feature_importances is not None:
        for column, feature in zip(selected_columns, feature_importances):
            print(f"'{column}': {feature:.3f}")
    elif coef_ is not None:
        feature_weights = coef_[0]
        weights_dict = {feat: weight for feat, weight in zip(selected_columns, feature_weights)}
        print(weights_dict)

    df_other_songs = df_other_songs_original
    X_other_songs = df_other_songs[selected_columns]

    if (classifier.__class__.__name__ == "KNeighborsClassifier"):
        y_pred = y_pred = classifier.predict(X_test.values)
        prediction = classifier.predict(X_other_songs.values)
    else: 
        y_pred = classifier.predict(X_test)
        prediction = classifier.predict(X_other_songs)
    
    model_report(classifier.__class__.__name__, y_pred, y_test)
    
    df_other_songs['Liked'] = prediction
    canzoni_possibili = df_other_songs[df_other_songs['Liked'] == 1]
    canzoni_possibili.to_csv(f"./results/canzoni_possibili_{classifier.__class__.__name__}.csv", index=True)