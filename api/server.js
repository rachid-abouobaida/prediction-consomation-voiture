'use strict';

/**
 * API Node.js / Express
 * Passerelle entre le frontend Vue 3 et le service de prédiction Python (FastAPI).
 *
 * Variables d'environnement :
 *   PORT            : port d'écoute (défaut : 3001)
 *   ML_SERVICE_URL  : URL du service Python FastAPI (défaut : http://localhost:8000)
 */

const express = require('express');
const cors    = require('cors');
const axios   = require('axios');

const app            = express();
const PORT           = process.env.PORT           || 3001;
const ML_SERVICE_URL = process.env.ML_SERVICE_URL || 'http://localhost:8001';

// ---------------------------------------------------------------------------
// Middlewares
// ---------------------------------------------------------------------------
app.use(cors({ origin: '*' }));
app.use(express.json());

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
const REQUIRED_FIELDS = [
  'year', 'cylinders', 'displ', 'drive', 'vclass', 'tranny', 'forced_induction', 'is_diesel',
];

function validateInput(body) {
  const missing = REQUIRED_FIELDS.filter(
    (f) => body[f] === undefined || body[f] === null || body[f] === ''
  );
  return missing;
}

function sanitizePayload(body) {
  return {
    year:             parseInt(body.year, 10),
    cylinders:        parseInt(body.cylinders, 10),
    displ:            parseFloat(body.displ),
    drive:            String(body.drive).trim(),
    vclass:           String(body.vclass).trim(),
    tranny:           String(body.tranny).trim(),
    forced_induction: parseInt(body.forced_induction, 10),
    is_diesel:        parseInt(body.is_diesel, 10),
  };
}

// ---------------------------------------------------------------------------
// Routes
// ---------------------------------------------------------------------------

/**
 * POST /api/predict
 * Corps JSON : { cylinders, displacement, horsepower, weight, acceleration, model_year, origin }
 * Réponse    : { L100km, mpg, category }
 */
app.post('/api/predict', async (req, res) => {
  // Validation des champs requis
  const missing = validateInput(req.body);
  if (missing.length > 0) {
    return res.status(400).json({ error: `Champs manquants : ${missing.join(', ')}` });
  }

  const payload = sanitizePayload(req.body);

  // Vérification des valeurs numériques (string pour drive/vclass est OK)
  const numericFields = ['year', 'cylinders', 'displ', 'forced_induction', 'is_diesel'];
  for (const key of numericFields) {
    if (Number.isNaN(payload[key])) {
      return res.status(400).json({ error: `Valeur invalide pour le champ "${key}"` });
    }
  }

  try {
    const { data } = await axios.post(`${ML_SERVICE_URL}/predict`, payload, {
      timeout: 10_000,
    });
    return res.json(data);
  } catch (err) {
    if (err.response) {
      return res
        .status(err.response.status)
        .json({ error: err.response.data?.detail || 'Erreur du service ML' });
    }
    return res.status(503).json({
      error: 'Service ML indisponible. Vérifiez que predict_service.py est démarré.',
      details: err.message,
    });
  }
});

/**
 * GET /api/health
 * Vérifie l'état de l'API Node.js et du service ML Python.
 */
app.get('/api/health', async (req, res) => {
  try {
    const { data } = await axios.get(`${ML_SERVICE_URL}/health`, { timeout: 3_000 });
    return res.json({ api: 'ok', ml_service: data });
  } catch {
    return res.json({ api: 'ok', ml_service: { status: 'unavailable', model_loaded: false } });
  }
});

// ---------------------------------------------------------------------------
// Démarrage
// ---------------------------------------------------------------------------
app.listen(PORT, () => {
  console.log(`🚀 API Node.js démarrée sur    http://localhost:${PORT}`);
  console.log(`🔗 Service ML Python attendu   ${ML_SERVICE_URL}`);
});
