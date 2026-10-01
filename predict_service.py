"""
Service de prédiction de consommation de carburant.
API REST FastAPI — charge le modèle MLP Keras et le scaler scikit-learn.

Démarrage :
    pip install -r requirements_api.txt
    python predict_service.py
"""

import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'   # Forcer TensorFlow sur CPU

import json
from contextlib import asynccontextmanager

import numpy as np
import joblib
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Chargement du modèle au démarrage (lifespan pattern FastAPI)
# ---------------------------------------------------------------------------
model = None
scaler = None
feature_names = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


@asynccontextmanager
async def lifespan(app: FastAPI):
    global model, scaler, feature_names

    # Import TF seulement au démarrage pour éviter les ralentissements d'import
    import tensorflow as tf
    from tensorflow import keras

    model_path   = os.path.join(BASE_DIR, "models", "mlp_consommation.keras")
    scaler_path  = os.path.join(BASE_DIR, "models", "scaler.joblib")
    features_path = os.path.join(BASE_DIR, "models", "features.json")

    model  = keras.models.load_model(model_path)
    scaler = joblib.load(scaler_path)

    with open(features_path) as f:
        feature_names = json.load(f)

    print(f"✅ Modèle chargé depuis : {model_path}")
    print(f"✅ Scaler chargé depuis : {scaler_path}")
    print(f"✅ Features : {feature_names}")
    yield  # L'application tourne ici


# ---------------------------------------------------------------------------
# Application FastAPI
# ---------------------------------------------------------------------------
app = FastAPI(
    title="API Prédiction Consommation Véhicule",
    description="Prédit la consommation en L/100km à partir de caractéristiques techniques.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Schéma de données d'entrée
# ---------------------------------------------------------------------------
class VehicleInput(BaseModel):
    year:             int   = Field(..., ge=1984, le=2026, description="Année du modèle (1984–2026)")
    cylinders:        int   = Field(..., ge=2,   le=16,   description="Nombre de cylindres (2–16)")
    displ:            float = Field(..., gt=0,   le=10.0, description="Cylindrée en litres (ex: 1.0–8.4)")
    drive:            str   = Field(...,                   description="Type de traction : 'FWD', 'RWD' ou 'AWD'")
    vclass:           str   = Field(...,                   description="Catégorie : 'Car', 'SUV', 'Pickup', 'Van', 'Special'")
    tranny:           str   = Field(...,                   description="Transmission : 'Automatic', 'CVT' ou 'Manual'")
    forced_induction: int   = Field(..., ge=0,   le=1,    description="1 = turbo/compresseur, 0 = atmosphérique")
    is_diesel:        int   = Field(..., ge=0,   le=1,    description="1 = diesel, 0 = essence")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.post("/predict", summary="Prédire la consommation")
def predict(vehicle: VehicleInput):
    """
    Retourne la consommation estimée en L/100km et MPG,
    ainsi qu'une catégorie qualitative.
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Modèle non chargé")

    VALID_DRIVE  = ('FWD', 'RWD', 'AWD')
    VALID_VCLASS = ('Car', 'SUV', 'Pickup', 'Van', 'Special')
    VALID_TRANNY = ('Automatic', 'CVT', 'Manual')

    if vehicle.drive not in VALID_DRIVE:
        raise HTTPException(status_code=422, detail=f"drive doit être parmi {VALID_DRIVE}")
    if vehicle.vclass not in VALID_VCLASS:
        raise HTTPException(status_code=422, detail=f"vclass doit être parmi {VALID_VCLASS}")
    if vehicle.tranny not in VALID_TRANNY:
        raise HTTPException(status_code=422, detail=f"tranny doit être parmi {VALID_TRANNY}")

    # Construction du vecteur de features dans l'ordre de features.json
    feature_lookup = {
        'year':               float(vehicle.year),
        'cylinders':          float(vehicle.cylinders),
        'displ':              float(vehicle.displ),
        'forced_induction':   float(vehicle.forced_induction),
        'is_diesel':          float(vehicle.is_diesel),
        'drive_AWD':          1.0 if vehicle.drive   == 'AWD'       else 0.0,
        'drive_FWD':          1.0 if vehicle.drive   == 'FWD'       else 0.0,
        'drive_RWD':          1.0 if vehicle.drive   == 'RWD'       else 0.0,
        'VClass_Car':         1.0 if vehicle.vclass  == 'Car'       else 0.0,
        'VClass_Pickup':      1.0 if vehicle.vclass  == 'Pickup'    else 0.0,
        'VClass_Special':     1.0 if vehicle.vclass  == 'Special'   else 0.0,
        'VClass_SUV':         1.0 if vehicle.vclass  == 'SUV'       else 0.0,
        'VClass_Van':         1.0 if vehicle.vclass  == 'Van'       else 0.0,
        'tranny_Automatic':   1.0 if vehicle.tranny  == 'Automatic' else 0.0,
        'tranny_CVT':         1.0 if vehicle.tranny  == 'CVT'       else 0.0,
        'tranny_Manual':      1.0 if vehicle.tranny  == 'Manual'    else 0.0,
    }

    feature_vector = np.array([[feature_lookup.get(f, 0.0) for f in feature_names]])
    feature_scaled = scaler.transform(feature_vector)
    prediction     = float(model.predict(feature_scaled, verbose=0)[0][0])
    prediction     = max(0.1, prediction)

    mpg = round(235.214 / prediction, 1)

    return {
        "L100km":   round(prediction, 2),
        "mpg":      mpg,
        "category": _get_category(prediction),
    }


@app.get("/health", summary="État du service")
def health():
    return {"status": "ok", "model_loaded": model is not None}


# ---------------------------------------------------------------------------
# Utilitaires
# ---------------------------------------------------------------------------
def _get_category(l100km: float) -> str:
    if l100km < 6:
        return "Très économique"
    if l100km < 9:
        return "Économique"
    if l100km < 12:
        return "Moyenne"
    if l100km < 15:
        return "Élevée"
    return "Très élevée"


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("predict_service:app", host="0.0.0.0", port=8001, reload=False)
