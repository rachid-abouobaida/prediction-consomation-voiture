import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'   # Forcer TensorFlow à utiliser le CPU

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.callbacks import EarlyStopping

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

import warnings
warnings.filterwarnings('ignore')

# Configuration globale des graphiques
sns.set_theme(style='whitegrid', palette='muted')
plt.rcParams['figure.figsize'] = (10, 5)
plt.rcParams['font.size'] = 12

# Reproductibilité
np.random.seed(42)
tf.random.set_seed(42)

print(f'TensorFlow version : {tf.__version__}')
print(f'Keras version      : {keras.__version__}')
print(f'GPU disponibles    : {tf.config.list_physical_devices("GPU")}')


#--2- Chargement des données ----------------------------------------------------------------

# Colonnes utiles du dataset EPA Fuel Economy
USECOLS = ['year', 'cylinders', 'displ', 'drive', 'VClass',
           'tCharger', 'sCharger', 'trany', 'fuelType1', 'comb08']

df = pd.read_csv('./data/vehicles.csv', usecols=USECOLS, low_memory=False)

# Garder uniquement les véhicules à combustion interne : essence + diesel
# (exclut électrique, hybride rechargeable, GPL, hydrogène…)
COMBUSTION = ['Regular Gasoline', 'Premium Gasoline', 'Midgrade Gasoline', 'Diesel']
df['is_diesel'] = (df['fuelType1'] == 'Diesel').astype(int)
df = df[df['fuelType1'].isin(COMBUSTION)].copy()
df = df.drop(columns=['fuelType1'])

print(f'Dimensions après filtre combustion : {df.shape}')
print(f'\nRépartition essence / diesel :')
print(f'  Essence : {(df["is_diesel"] == 0).sum():,} véhicules')
print(f'  Diesel  : {(df["is_diesel"] == 1).sum():,} véhicules')
df.head(10)

# Informations générales sur le dataset
print('=== Informations générales ===\n')
df.info()

print('\n=== Statistiques descriptives ===\n')
df.describe()

# 3. Néttoyage des données---------------------------------------------------------------
print('=== Valeurs manquantes par colonne ===\n')
print(df.isnull().sum())

print(f'\nLignes avec comb08 == 0 (invalide) : {(df["comb08"] == 0).sum()}')

# 1. Supprimer les lignes avec cylindres, cylindrée, traction, transmission ou catégorie manquants
df = df.dropna(subset=['cylinders', 'displ', 'drive', 'VClass', 'trany'])

# 2. Supprimer les lignes avec comb08 = 0 (physiquement impossible)
df = df[df['comb08'] > 0]

# 3. Conversion des types
df['cylinders'] = df['cylinders'].astype(int)
df['year']      = df['year'].astype(int)
df['displ']     = df['displ'].astype(float)
df['comb08']    = df['comb08'].astype(float)
df['is_diesel'] = df['is_diesel'].astype(int)

print(f'Dimensions après nettoyage : {df.shape}')
print('\nValeurs manquantes restantes :')
print(df.isnull().sum())
df.head()

# 4. Prétraitement des données ----------------------------------------------------------------
df['L100km'] = 235.214 / df['comb08'] # Conversion de MPG en L/100km
df = df.drop(columns=['comb08']) # On n'a plus besoin de MPG

print('Distribution de la consommation en L/100km :')
print(df['L100km'].describe())

# output
#Distribution de la consommation en L/100km :
#count    47115.000000  Nombre de véhicules
#mean        12.153893  Consommation moyenne en L/100km
#std          3.135573  Écart-type de la consommation
#min          3.986678  Consommation minimale (véhicule le plus économe)
#25%         10.226696  Consommation au 1er quartile
#50%         11.760700  Consommation médiane
#75%         13.836118  Consommation au 3e quartile
#max         33.602000  Consommation maximale (véhicule le plus gourmand)
#Name: L100km, dtype: float64'

# --- 4.2 Encodage des variables catégorielles ---

# A) Regroupement de 'drive' en 3 catégories
DRIVE_MAP = {
    'Front-Wheel Drive':           'FWD', # Traction avant
    '2-Wheel Drive':               'FWD', # Traction avant
    'Rear-Wheel Drive':            'RWD', # Propulsion ? moteur en avant et roues arrière motrices
    'All-Wheel Drive':             'AWD', # Transmission intégrale. c'est
    '4-Wheel Drive':               'AWD', # Transmission intégrale
    '4-Wheel or All-Wheel Drive':  'AWD', # Transmission intégrale
    'Part-time 4-Wheel Drive':     'AWD', # Transmission intégrale partielle (4x4 à temps partiel)
}
df['drive'] = df['drive'].map(DRIVE_MAP).fillna('FWD')

# B) Regroupement de 'VClass' en 5 catégories
def map_vclass(v: str) -> str:
    v = str(v).lower()
    if 'suv' in v or 'sport utility' in v:
        return 'SUV'
    if 'pickup' in v:
        return 'Pickup'
    if 'van' in v or 'minivan' in v:
        return 'Van'
    if 'special' in v:
        return 'Special'
    return 'Car'

df['VClass'] = df['VClass'].apply(map_vclass)

# C) Indicateur de suralimentation (turbocompresseur ou compresseur volumétrique)
df['forced_induction'] = ((df['tCharger'] == 'T') | (df['sCharger'] == 'S')).astype(int)
df = df.drop(columns=['tCharger', 'sCharger'])

# D) Type de transmission : Automatic / CVT / Manual
def map_transmission(t: str) -> str:
    t = str(t).upper()
    if 'CVT' in t or ('AV' in t and 'VARIABLE' in t) or 'CONTINUOUSLY' in t:
        return 'CVT'
    if t.startswith('M') or 'MANUAL' in t:
        return 'Manual'
    return 'Automatic'   # A, AM, AS, AMT, etc.

df['tranny'] = df['trany'].apply(map_transmission)
df = df.drop(columns=['trany'])

print('Distribution drive    :', df['drive'].value_counts().to_dict())
print('Distribution VClass   :', df['VClass'].value_counts().to_dict())
print('Distribution tranny   :', df['tranny'].value_counts().to_dict())
print('Forced induction       :', df['forced_induction'].value_counts().to_dict())
print('Is diesel              :', df['is_diesel'].value_counts().to_dict())

# E) One-hot encoding
df = pd.get_dummies(df, columns=['drive', 'VClass', 'tranny'], drop_first=False, dtype=float)

print('\nColonnes après encodage :', df.columns.tolist())
df.head()

# --- 4.3 Séparation features / cible ---
TARGET   = 'L100km'
FEATURES = [col for col in df.columns if col != TARGET]

X = df[FEATURES].values
y = df[TARGET].values

print(f'Features ({len(FEATURES)}) : {FEATURES}')
print(f'Shape X : {X.shape}, Shape y : {y.shape}')

## 5. Analyse Exploratoire des Données (EDA)
# --- 5.1 Distribution des variables numériques continues ---
numeric_cols = ['year', 'cylinders', 'displ', 'forced_induction', 'is_diesel', 'L100km']

fig, axes = plt.subplots(1, 6, figsize=(24, 4))

for i, col in enumerate(numeric_cols):
    axes[i].hist(df[col], bins=30, color='steelblue', edgecolor='white', alpha=0.85)
    axes[i].set_title(col, fontsize=12, fontweight='bold')
    axes[i].set_xlabel('Valeur')
    axes[i].set_ylabel('Fréquence')

plt.suptitle('Distribution des variables numériques', fontsize=15, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('./data/distributions.png', dpi=120, bbox_inches='tight')
plt.show()

# --- 5.2 Matrice de corrélation (variables numériques continues) ---
corr_cols = ['year', 'cylinders', 'displ', 'forced_induction', 'is_diesel', 'L100km']

corr_matrix = df[corr_cols].corr()

plt.figure(figsize=(9, 7))
mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
sns.heatmap(
    corr_matrix,
    mask=mask,
    annot=True,
    fmt='.2f',
    cmap='coolwarm',
    center=0,
    linewidths=0.5,
    square=True
)
plt.title('Matrice de corrélation', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('./data/correlation_matrix.png', dpi=120, bbox_inchees='tight')
plt.show()

print('\nCorrélations avec L/100km (variable cible) :')
print(corr_matrix['L100km'].sort_values(ascending=False))

# --- 5.3 Caractéristiques clés vs Consommation ---
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

scatter_pairs = [
    ('displ',    'Cylindrée (L)',        'tomato'),
    ('cylinders','Nombre de cylindres',  'steelblue'),
    ('year',     'Année du modèle',      'mediumseagreen'),
]

for ax, (feat, label, color) in zip(axes, scatter_pairs):
    # Sous-échantillon pour la lisibilité (5 000 points)
    sample = df.sample(n=min(5000, len(df)), random_state=42)
    ax.scatter(sample[feat], sample['L100km'], alpha=0.2, color=color, s=10)
    ax.set_xlabel(label, fontsize=12)
    ax.set_ylabel('Consommation (L/100km)', fontsize=12)
    ax.set_title(f'{label} vs Consommation', fontsize=13, fontweight='bold')
    z = np.polyfit(sample[feat], sample['L100km'], 1)
    p = np.poly1d(z)
    xl = np.linspace(sample[feat].min(), sample[feat].max(), 200)
    ax.plot(xl, p(xl), 'k--', linewidth=2, label='Tendance linéaire')
    ax.legend()

plt.suptitle('Relations entre caractéristiques et consommation', fontsize=15, fontweight='bold')
plt.tight_layout()
plt.savefig('./data/scatter_plots.png', dpi=120, bbox_inches='tight')
plt.show()

# --- 5.4 Consommation moyenne par type de traction, catégorie et transmission ---
fig, axes = plt.subplots(1, 3, figsize=(20, 5))

# Par type de traction
drive_cols  = [c for c in df.columns if c.startswith('drive_')]
drive_means = {c.replace('drive_', ''): df.loc[df[c] == 1.0, 'L100km'].mean() for c in drive_cols}
axes[0].bar(drive_means.keys(), drive_means.values(),
            color=['steelblue', 'coral', 'mediumseagreen'], edgecolor='white', linewidth=1.2)
axes[0].set_title('Conso. moy. par traction', fontsize=13, fontweight='bold')
axes[0].set_ylabel('L/100km')
for i, (k, v) in enumerate(drive_means.items()):
    axes[0].text(i, v + 0.1, f'{v:.2f}', ha='center', fontsize=11, fontweight='bold')

# Par catégorie de véhicule
vclass_cols  = [c for c in df.columns if c.startswith('VClass_')]
vclass_means = {c.replace('VClass_', ''): df.loc[df[c] == 1.0, 'L100km'].mean() for c in vclass_cols}
axes[1].bar(vclass_means.keys(), vclass_means.values(),
            color=plt.cm.Set2.colors[:len(vclass_means)], edgecolor='white', linewidth=1.2)
axes[1].set_title('Conso. moy. par catégorie', fontsize=13, fontweight='bold')
axes[1].set_ylabel('L/100km')
for i, (k, v) in enumerate(vclass_means.items()):
    axes[1].text(i, v + 0.1, f'{v:.2f}', ha='center', fontsize=10, fontweight='bold')

# Par type de transmission
tranny_cols  = [c for c in df.columns if c.startswith('tranny_')]
tranny_means = {c.replace('tranny_', ''): df.loc[df[c] == 1.0, 'L100km'].mean() for c in tranny_cols}
axes[2].bar(tranny_means.keys(), tranny_means.values(),
            color=['#4e79a7', '#f28e2b', '#59a14f'], edgecolor='white', linewidth=1.2)
axes[2].set_title('Conso. moy. par transmission', fontsize=13, fontweight='bold')
axes[2].set_ylabel('L/100km')
for i, (k, v) in enumerate(tranny_means.items()):
    axes[2].text(i, v + 0.1, f'{v:.2f}', ha='center', fontsize=11, fontweight='bold')

plt.suptitle('Consommation moyenne par groupe', fontsize=15, fontweight='bold')
plt.tight_layout()
plt.savefig('./data/consumption_by_origin.png', dpi=120, bbox_inches='tight')
plt.show()

n_features = X_train_scaled.shape[1]

def build_mlp(n_features: int) -> keras.Model:
    """Construit et compile le modèle MLP."""
    model = keras.Sequential(
        [
            layers.Input(shape=(n_features,), name='input'),
            layers.Dense(64, activation='relu', name='dense_1'),
            layers.Dropout(0.1, name='dropout_1'),
            layers.Dense(32, activation='relu', name='dense_2'),
            layers.Dense(1, name='output'),
        ],
        name='MLP_Consommation'
    )
    model.compile(
        optimizer='adam',
        loss='mse',
        metrics=['mae']
    )
    return model

model = build_mlp(n_features)
model.summary()

# Callback EarlyStopping (Bonus)
early_stopping = EarlyStopping(
    monitor='val_loss',
    patience=20,
    restore_best_weights=True,
    verbose=1
)

# Entraînement
history = model.fit(
    X_train_scaled, y_train,
    epochs=150,
    batch_size=32,
    validation_split=0.2,
    callbacks=[early_stopping],
    verbose=1
)

print(f'\n✅ Entraînement terminé après {len(history.history["loss"])} epochs.')