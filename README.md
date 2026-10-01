# Prédiction de consommation de carburant

Projet de prédiction de la consommation d'un véhicule en **L/100 km** à partir de caractéristiques techniques : année, cylindrée, nombre de cylindres, type de traction, catégorie du véhicule, transmission, suralimentation et type de carburant.

Le projet combine un modèle de Machine Learning entraîné en Python, une API FastAPI pour servir les prédictions, une passerelle Node.js/Express et une interface web Vue 3 avec Vuetify.

## Auteur

**Rachid ABOUOBAIDA**

## Objectif du projet

L'objectif est de construire une application complète capable de :

- nettoyer et préparer des données automobiles ;
- entraîner et comparer des modèles de prédiction ;
- sauvegarder un modèle de prédiction réutilisable ;
- exposer ce modèle via une API REST ;
- fournir une interface utilisateur simple pour tester des véhicules et obtenir une estimation de consommation.

La consommation est retournée en :

- **L/100 km** : unité principale utilisée par l'application ;
- **MPG** : conversion américaine, utile pour les jeux de données EPA ;
- **catégorie qualitative** : très économique, économique, moyenne, élevée ou très élevée.

## Fonctionnalités

- Formulaire web de simulation de consommation.
- Préréglages pour tester rapidement plusieurs types de véhicules.
- Validation des champs côté frontend et côté API.
- Prédiction via un réseau de neurones MLP TensorFlow/Keras.
- Standardisation des variables numériques avec un scaler scikit-learn.
- API Python FastAPI dédiée au modèle ML.
- API Node.js/Express servant de passerelle entre le frontend et le service ML.
- Indicateur d'état du service dans l'interface.
- Visualisations générées pendant l'analyse exploratoire.

## Architecture générale

```text
prediction-consomation-voiture/
├── predict_conso.py                         # Script d'analyse, préparation et entraînement
├── predict_service.py                       # Service FastAPI de prédiction ML
├── prediction_consommation_voiture.ipynb    # Notebook d'exploration et d'entraînement
├── requirements_api.txt                     # Dépendances Python pour l'API ML
├── models/
│   ├── mlp_consommation.keras               # Modèle Keras sauvegardé
│   ├── scaler.joblib                        # Scaler scikit-learn sauvegardé
│   └── features.json                        # Ordre des variables attendues par le modèle
├── data/
│   ├── vehicles.csv                         # Dataset principal EPA Fuel Economy
│   ├── auto-mpg.csv                         # Dataset Auto MPG
│   └── *.png                                # Graphiques d'analyse et d'évaluation
├── api/
│   ├── server.js                            # API Express
│   └── package.json                         # Dépendances Node.js de la passerelle
└── frontend/
    ├── src/
    │   ├── App.vue
    │   ├── main.js
    │   └── components/PredictionForm.vue
    ├── vite.config.js                       # Configuration Vite avec proxy /api
    └── package.json                         # Dépendances Vue/Vuetify
```

## Technologies utilisées

### Machine Learning et API Python

- Python
- pandas
- NumPy
- matplotlib
- seaborn
- scikit-learn
- TensorFlow / Keras
- FastAPI
- Uvicorn
- joblib
- Pydantic

### Backend Node.js

- Node.js
- Express
- Axios
- CORS

### Frontend

- Vue 3
- Vite
- Vuetify 3
- Material Design Icons

## Jeu de données

Le script d'entraînement `predict_conso.py` utilise principalement le fichier :

```text
data/vehicles.csv
```

Ce fichier correspond au dataset **EPA Fuel Economy**. Le script conserve les véhicules à combustion interne essence et diesel, puis convertit la consommation combinée `comb08` de MPG vers `L/100 km` avec la formule :

```text
L/100 km = 235.214 / MPG
```

Les colonnes utilisées sont :

- `year` : année du modèle ;
- `cylinders` : nombre de cylindres ;
- `displ` : cylindrée en litres ;
- `drive` : type de traction ;
- `VClass` : catégorie du véhicule ;
- `tCharger` et `sCharger` : présence d'une suralimentation ;
- `trany` : type de transmission ;
- `fuelType1` : type de carburant ;
- `comb08` : consommation combinée en MPG.

## Prétraitement des données

Le pipeline de préparation applique les étapes suivantes :

1. Filtrage des véhicules essence et diesel.
2. Création de la variable `is_diesel`.
3. Suppression des lignes incomplètes sur les colonnes importantes.
4. Suppression des valeurs invalides avec `comb08 == 0`.
5. Conversion de MPG vers `L/100 km`.
6. Regroupement des tractions en `FWD`, `RWD` et `AWD`.
7. Regroupement des catégories véhicule en `Car`, `SUV`, `Pickup`, `Van` et `Special`.
8. Création de la variable `forced_induction`.
9. Regroupement des transmissions en `Automatic`, `CVT` et `Manual`.
10. Encodage one-hot des variables catégorielles.
11. Standardisation des features avant entraînement.

## Variables attendues par le modèle

L'ordre exact des variables est stocké dans :

```text
models/features.json
```

Le service FastAPI reconstruit le vecteur de prédiction dans cet ordre afin d'éviter les erreurs entre l'entraînement et l'inférence.

Variables principales saisies par l'utilisateur :

- `year`
- `cylinders`
- `displ`
- `drive`
- `vclass`
- `tranny`
- `forced_induction`
- `is_diesel`

## Installation

### Prérequis

- Python 3.10 ou version supérieure recommandée
- Node.js 18 ou version supérieure recommandée
- npm

### 1. Cloner ou ouvrir le projet

Placez-vous à la racine du projet :

```bash
cd prediction-consomation-voiture
```

### 2. Installer les dépendances Python

Il est recommandé d'utiliser un environnement virtuel :

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements_api.txt
```

Sous Windows PowerShell :

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements_api.txt
```

### 3. Installer les dépendances de l'API Node.js

```bash
cd api
npm install
cd ..
```

### 4. Installer les dépendances du frontend

```bash
cd frontend
npm install
cd ..
```

## Lancement de l'application

L'application se lance en trois services séparés.

### 1. Démarrer le service ML FastAPI

Depuis la racine du projet :

```bash
python predict_service.py
```

Par défaut, le service démarre sur :

```text
http://localhost:8001
```

Documentation interactive FastAPI :

```text
http://localhost:8001/docs
```

### 2. Démarrer l'API Express

Dans un deuxième terminal :

```bash
cd api
npm run dev
```

Par défaut, l'API Express démarre sur :

```text
http://localhost:3001
```

Elle transmet les requêtes de prédiction au service ML configuré par :

```text
ML_SERVICE_URL=http://localhost:8001
```

### 3. Démarrer le frontend Vue

Dans un troisième terminal :

```bash
cd frontend
npm run dev
```

Par défaut, Vite démarre sur :

```text
http://localhost:5174
```

Le frontend utilise un proxy Vite pour rediriger les appels `/api` vers :

```text
http://localhost:3001
```

## Utilisation de l'API

### Vérifier l'état du service ML

```bash
curl http://localhost:8001/health
```

Réponse attendue :

```json
{
  "status": "ok",
  "model_loaded": true
}
```

### Vérifier l'état de l'API Express

```bash
curl http://localhost:3001/api/health
```

### Faire une prédiction avec FastAPI

```bash
curl -X POST http://localhost:8001/predict \
  -H "Content-Type: application/json" \
  -d '{
    "year": 2022,
    "cylinders": 4,
    "displ": 2.0,
    "drive": "AWD",
    "vclass": "SUV",
    "tranny": "Automatic",
    "forced_induction": 1,
    "is_diesel": 0
  }'
```

Exemple de réponse :

```json
{
  "L100km": 8.75,
  "mpg": 26.9,
  "category": "Économique"
}
```

### Faire une prédiction via l'API Express

```bash
curl -X POST http://localhost:3001/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "year": 2022,
    "cylinders": 4,
    "displ": 2.0,
    "drive": "AWD",
    "vclass": "SUV",
    "tranny": "Automatic",
    "forced_induction": 1,
    "is_diesel": 0
  }'
```

## Valeurs acceptées par l'API

### `drive`

- `FWD` : traction avant
- `RWD` : propulsion
- `AWD` : transmission intégrale

### `vclass`

- `Car`
- `SUV`
- `Pickup`
- `Van`
- `Special`

### `tranny`

- `Automatic`
- `CVT`
- `Manual`

### Champs numériques

- `year` : de 1984 à 2026
- `cylinders` : de 2 à 16
- `displ` : supérieur à 0 et inférieur ou égal à 10.0
- `forced_induction` : `0` ou `1`
- `is_diesel` : `0` ou `1`

## Catégories de consommation

Le service classe la prédiction selon les seuils suivants :

| Consommation | Catégorie |
| --- | --- |
| `< 6 L/100 km` | Très économique |
| `6 à 9 L/100 km` | Économique |
| `9 à 12 L/100 km` | Moyenne |
| `12 à 15 L/100 km` | Élevée |
| `> 15 L/100 km` | Très élevée |

## Entraînement du modèle

Le script principal d'entraînement est :

```bash
python predict_conso.py
```

Il réalise l'analyse exploratoire, le prétraitement, l'entraînement et la génération de graphiques dans le dossier `data/`.

Les artefacts nécessaires à l'inférence sont sauvegardés dans le dossier `models/` :

- `mlp_consommation.keras`
- `scaler.joblib`
- `features.json`

Ces fichiers doivent être présents pour que `predict_service.py` démarre correctement.

## Visualisations disponibles

Le dossier `data/` contient plusieurs graphiques produits pendant l'analyse :

- `distributions.png`
- `correlation_matrix.png`
- `scatter_plots.png`
- `predictions_analysis.png`
- `learning_curves.png`
- `model_comparison.png`
- `consumption_by_origin.png`

Ces fichiers servent à comprendre la distribution des variables, les relations entre caractéristiques et consommation, et la qualité des prédictions.

## Scripts npm

### API Express

Dans `api/` :

```bash
npm start
npm run dev
```

- `npm start` lance `server.js`.
- `npm run dev` lance le serveur avec `node --watch`.

### Frontend Vue

Dans `frontend/` :

```bash
npm run dev
npm run build
npm run preview
```

- `npm run dev` lance le serveur de développement Vite.
- `npm run build` génère la version de production.
- `npm run preview` prévisualise le build de production.

## Variables d'environnement

### API Express

| Variable | Description | Valeur par défaut |
| --- | --- | --- |
| `PORT` | Port de l'API Node.js | `3001` |
| `ML_SERVICE_URL` | URL du service FastAPI | `http://localhost:8001` |

Exemple :

```bash
PORT=3001 ML_SERVICE_URL=http://localhost:8001 npm start
```

## Points d'attention

- Le modèle Keras, le scaler et le fichier `features.json` doivent rester synchronisés.
- Si le modèle est réentraîné avec de nouvelles variables, il faut régénérer `features.json`.
- Le frontend envoie les requêtes à `/api/predict`, qui est redirigé par Vite vers l'API Express.
- L'API Express appelle ensuite le service FastAPI.
- Le service FastAPI force TensorFlow à utiliser le CPU avec `CUDA_VISIBLE_DEVICES=-1`.
- Le fichier `data/vehicles.csv` est volumineux ; selon le mode de partage du projet, il peut être préférable de documenter sa source plutôt que de le versionner.

## Améliorations possibles

- Ajouter des tests unitaires pour les endpoints FastAPI et Express.
- Ajouter un fichier `.env.example` pour documenter les variables d'environnement.
- Ajouter un script unique de démarrage pour lancer les trois services.
- Corriger les libellés historiques qui mentionnent Auto MPG si le dataset principal utilisé est EPA Fuel Economy.
- Ajouter une page de documentation utilisateur dans le frontend.
- Ajouter une validation plus stricte des combinaisons véhicule, par exemple cylindrée minimale/maximale selon le nombre de cylindres.

## Licence

Licence non spécifiée pour le moment.
