<template>
  <div>
    <!-- ══════════════════════════════════════════════════════════════ -->
    <!-- En-tête                                                        -->
    <!-- ══════════════════════════════════════════════════════════════ -->
    <v-row class="mb-2" align="center">
      <v-col>
        <h2 class="text-h5 font-weight-bold text-primary d-flex align-center ga-2">
          <v-icon icon="mdi-fuel" />
          Simulateur de consommation
        </h2>
        <p class="text-body-2 text-medium-emphasis mt-1">
          Entrez les caractéristiques techniques du véhicule pour obtenir
          une estimation de sa consommation en <strong>L/100&nbsp;km</strong>.
        </p>
      </v-col>
    </v-row>

    <v-row>
      <!-- ══════════════════════════════════════════════════════════════ -->
      <!-- Colonne gauche : formulaire                                    -->
      <!-- ══════════════════════════════════════════════════════════════ -->
      <v-col cols="12" md="7">
        <v-card elevation="3" rounded="lg">
          <!-- En-tête carte -->
          <v-card-title class="d-flex align-center pa-4 pb-2 text-body-1 font-weight-bold">
            <v-icon icon="mdi-car-info" color="primary" class="mr-2" />
            Caractéristiques du véhicule
          </v-card-title>
          <v-divider />

          <!-- Corps du formulaire -->
          <v-card-text class="pa-4">
            <v-form ref="formRef" v-model="formValid" @submit.prevent="runPredict">
              <v-row dense>
                <!-- Année du modèle -->
                <v-col cols="12" sm="6">
                  <v-text-field
                    v-model.number="form.year"
                    label="Année du modèle"
                    prepend-inner-icon="mdi-calendar"
                    type="number"
                    min="1984"
                    max="2026"
                    step="1"
                    :rules="[rules.required, rules.positive]"
                    variant="outlined"
                    density="comfortable"
                    hint="Plage disponible : 1984 – 2026"
                    persistent-hint
                  />
                </v-col>

                <!-- Cylindres -->
                <v-col cols="12" sm="6">
                  <v-select
                    v-model="form.cylinders"
                    :items="cylinderOptions"
                    label="Cylindres"
                    prepend-inner-icon="mdi-engine"
                    :rules="[rules.required]"
                    variant="outlined"
                    density="comfortable"
                    hint="Nombre de cylindres du moteur"
                    persistent-hint
                  />
                </v-col>

                <!-- Cylindrée (litres) -->
                <v-col cols="12" sm="6">
                  <v-text-field
                    v-model.number="form.displ"
                    label="Cylindrée (L)"
                    prepend-inner-icon="mdi-piston"
                    type="number"
                    min="0.5"
                    max="10"
                    step="0.1"
                    :rules="[rules.required, rules.positive]"
                    variant="outlined"
                    density="comfortable"
                    hint="Plage typique : 0.8 – 8.4 L"
                    persistent-hint
                  />
                </v-col>

                <!-- Suralimentation -->
                <v-col cols="12" sm="6" class="d-flex align-center">
                  <v-switch
                    v-model="form.forced_induction_bool"
                    color="primary"
                    hide-details
                    class="mt-2"
                  >
                    <template #label>
                      <span class="text-body-2">
                        <v-icon icon="mdi-wind-power" size="18" class="mr-1" />
                        Suralimentation
                        <v-chip size="x-small" :color="form.forced_induction_bool ? 'primary' : 'grey'" class="ml-1">
                          {{ form.forced_induction_bool ? 'Turbo / Compresseur' : 'Atmosphérique' }}
                        </v-chip>
                      </span>
                    </template>
                  </v-switch>
                </v-col>

                <!-- Type de traction -->
                <v-col cols="12">
                  <p class="text-body-2 mb-2 text-medium-emphasis">
                    <v-icon icon="mdi-car-traction-control" size="16" class="mr-1" />
                    Type de traction
                  </p>
                  <v-btn-toggle
                    v-model="form.drive"
                    mandatory
                    rounded="lg"
                    color="primary"
                    divided
                    class="w-100"
                  >
                    <v-btn value="FWD" class="flex-grow-1">
                      <v-icon start icon="mdi-arrow-up-circle-outline" />
                      FWD — Avant
                    </v-btn>
                    <v-btn value="RWD" class="flex-grow-1">
                      <v-icon start icon="mdi-arrow-down-circle-outline" />
                      RWD — Arrière
                    </v-btn>
                    <v-btn value="AWD" class="flex-grow-1">
                      <v-icon start icon="mdi-car-4wd" />
                      AWD — Intégrale
                    </v-btn>
                  </v-btn-toggle>
                </v-col>

                <!-- Catégorie de véhicule -->
                <v-col cols="12">
                  <p class="text-body-2 mb-2 text-medium-emphasis">
                    <v-icon icon="mdi-shape-outline" size="16" class="mr-1" />
                    Catégorie de véhicule
                  </p>
                  <v-btn-toggle
                    v-model="form.vclass"
                    mandatory
                    rounded="lg"
                    color="primary"
                    divided
                    class="w-100"
                  >
                    <v-btn value="Car"     class="flex-grow-1">🚗 Voiture</v-btn>
                    <v-btn value="SUV"     class="flex-grow-1">🚙 SUV</v-btn>
                    <v-btn value="Pickup"  class="flex-grow-1">🛻 Pickup</v-btn>
                    <v-btn value="Van"     class="flex-grow-1">🚐 Van</v-btn>
                    <v-btn value="Special" class="flex-grow-1">🏎️ Spécial</v-btn>
                  </v-btn-toggle>
                </v-col>

                <!-- Type de transmission -->
                <v-col cols="12">
                  <p class="text-body-2 mb-2 text-medium-emphasis">
                    <v-icon icon="mdi-transmission-tower" size="16" class="mr-1" />
                    Type de transmission
                  </p>
                  <v-btn-toggle
                    v-model="form.tranny"
                    mandatory
                    rounded="lg"
                    color="primary"
                    divided
                    class="w-100"
                  >
                    <v-btn value="Automatic" class="flex-grow-1">
                      <v-icon start icon="mdi-cog-sync-outline" />
                      Automatique
                    </v-btn>
                    <v-btn value="CVT" class="flex-grow-1">
                      <v-icon start icon="mdi-infinity" />
                      CVT
                    </v-btn>
                    <v-btn value="Manual" class="flex-grow-1">
                      <v-icon start icon="mdi-hand-back-right-outline" />
                      Manuelle
                    </v-btn>
                  </v-btn-toggle>
                </v-col>

                <!-- Type de carburant -->
                <v-col cols="12" sm="6" class="d-flex align-center">
                  <v-switch
                    v-model="form.is_diesel_bool"
                    color="amber-darken-2"
                    hide-details
                    class="mt-2"
                  >
                    <template #label>
                      <span class="text-body-2">
                        <v-icon icon="mdi-fuel" size="18" class="mr-1" />
                        Type de carburant
                        <v-chip size="x-small" :color="form.is_diesel_bool ? 'amber-darken-2' : 'green-darken-2'" class="ml-1">
                          {{ form.is_diesel_bool ? 'Diesel' : 'Essence' }}
                        </v-chip>
                      </span>
                    </template>
                  </v-switch>
                </v-col>

              </v-row>
            </v-form>
          </v-card-text>

          <v-divider />

          <!-- Actions -->
          <v-card-actions class="pa-4">
            <v-btn
              variant="tonal"
              color="secondary"
              prepend-icon="mdi-refresh"
              @click="resetForm"
            >
              Réinitialiser
            </v-btn>
            <v-spacer />
            <v-btn
              color="primary"
              size="large"
              prepend-icon="mdi-calculator"
              :loading="loading"
              :disabled="!formValid"
              variant="elevated"
              @click="runPredict"
            >
              Prédire la consommation
            </v-btn>
          </v-card-actions>
        </v-card>

        <!-- Préréglages ──────────────────────────────────────────── -->
        <v-card elevation="1" rounded="lg" class="mt-4" color="primary" variant="tonal">
          <v-card-title class="text-body-2 pa-3 pb-1 font-weight-bold">
            <v-icon icon="mdi-bookmark-multiple-outline" size="18" class="mr-1" />
            Exemples prédéfinis
          </v-card-title>
          <v-card-text class="pa-3 pt-1">
            <v-chip-group column>
              <v-chip
                v-for="p in presets"
                :key="p.label"
                color="primary"
                variant="outlined"
                size="small"
                prepend-icon="mdi-car"
                @click="applyPreset(p)"
              >
                {{ p.label }}
              </v-chip>
            </v-chip-group>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- ══════════════════════════════════════════════════════════════ -->
      <!-- Colonne droite : résultat                                      -->
      <!-- ══════════════════════════════════════════════════════════════ -->
      <v-col cols="12" md="5">
        <!-- État vide -->
        <v-card
          v-if="!result && !error"
          elevation="1"
          rounded="lg"
          class="d-flex align-center justify-center"
          style="min-height: 280px"
          color="primary"
          variant="tonal"
        >
          <div class="text-center pa-6">
            <v-icon icon="mdi-gauge-empty" size="72" color="primary" style="opacity: 0.35" />
            <p class="text-body-1 text-medium-emphasis mt-3">
              Remplissez le formulaire<br />
              puis cliquez sur <strong>Prédire</strong>.
            </p>
          </div>
        </v-card>

        <!-- Alerte erreur -->
        <v-alert
          v-if="error"
          type="error"
          rounded="lg"
          variant="tonal"
          closable
          :text="error"
          @click:close="error = null"
        />

        <!-- Carte résultat -->
        <v-card
          v-if="result"
          elevation="4"
          rounded="lg"
          :style="{ background: resultGradient }"
        >
          <v-card-text class="pa-6 text-center">
            <!-- Label -->
            <div class="text-overline text-white mb-1" style="opacity: .8">
              Consommation estimée
            </div>

            <!-- Valeur principale -->
            <div class="text-h2 font-weight-black text-white">
              {{ result.L100km }}
            </div>
            <div class="text-h6 text-white mb-4" style="opacity: .8">L / 100 km</div>

            <!-- Jauge -->
            <v-progress-linear
              :model-value="gaugePercent"
              bg-color="rgba(255,255,255,.2)"
              :color="gaugeBarColor"
              height="14"
              rounded
              class="mb-1"
            />
            <div class="d-flex justify-space-between text-caption text-white mb-4" style="opacity: .55">
              <span>0 L</span>
              <span>8 L</span>
              <span>16+ L</span>
            </div>

            <!-- Badge catégorie -->
            <v-chip color="white" size="large" class="mb-4 font-weight-bold" prepend-icon="mdi-leaf">
              {{ result.category }}
            </v-chip>

            <!-- Conversion MPG -->
            <div class="text-white text-body-2" style="opacity: .8">
              <v-icon icon="mdi-repeat" size="16" class="mr-1" />
              Soit <strong>{{ result.mpg }}&nbsp;MPG</strong>
            </div>
          </v-card-text>
        </v-card>

        <!-- Note modèle -->
        <v-card v-if="result" elevation="1" rounded="lg" class="mt-3">
          <v-card-text class="pa-3">
            <p class="text-caption text-medium-emphasis">
              <v-icon icon="mdi-information-outline" size="14" class="mr-1" />
              Prédiction réalisée par un réseau de neurones MLP entraîné sur
              <strong>~50&nbsp;000 véhicules</strong> essence & diesel (<em>EPA Fuel Economy Guide</em>).
              Données officielles US — modèles 1984–2026, 16 features (traction, transmission, cylindrée…).
            </p>
          </v-card-text>
        </v-card>

        <!-- Table de référence ──────────────────────────────────── -->
        <v-card elevation="1" rounded="lg" class="mt-3">
          <v-card-title class="text-body-2 pa-3 pb-1 font-weight-bold">
            <v-icon icon="mdi-table-check" size="18" class="mr-1" />
            Référentiel de consommation
          </v-card-title>
          <v-table density="compact">
            <tbody>
              <tr v-for="ref in consumptionRefs" :key="ref.label">
                <td class="py-1">
                  <v-icon :icon="ref.icon" :color="ref.color" size="16" class="mr-1" />
                  {{ ref.label }}
                </td>
                <td class="text-right font-weight-medium text-caption py-1">{{ ref.range }}</td>
              </tr>
            </tbody>
          </v-table>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

// ── État du formulaire ───────────────────────────────────────────────────────
const formRef   = ref(null)
const formValid = ref(false)
const loading   = ref(false)
const result    = ref(null)
const error     = ref(null)

const form = ref({
  year:                  2020,
  cylinders:             4,
  displ:                 null,
  forced_induction_bool: false,
  is_diesel_bool:        false,
  drive:                 'FWD',
  vclass:                'Car',
  tranny:                'Automatic',
})

// ── Règles de validation ─────────────────────────────────────────────────────
const rules = {
  required: (v) => (v !== null && v !== undefined && v !== '') || 'Champ requis',
  positive:  (v) => (Number(v) > 0) || 'Doit être un nombre positif',
}

// ── Options des selects ──────────────────────────────────────────────────────
const cylinderOptions = [2, 3, 4, 5, 6, 8, 10, 12, 16]

// ── Préréglages ──────────────────────────────────────────────────────────────
const presets = [
  {
    label: 'Citadine turbo CVT (2023, 4 cyl, 1.5L)',
    year: 2023, cylinders: 4, displ: 1.5, drive: 'FWD', vclass: 'Car',
    tranny: 'CVT', forced_induction_bool: true, is_diesel_bool: false,
  },
  {
    label: 'Berline V6 (2022, 6 cyl, 3.0L)',
    year: 2022, cylinders: 6, displ: 3.0, drive: 'RWD', vclass: 'Car',
    tranny: 'Automatic', forced_induction_bool: false, is_diesel_bool: false,
  },
  {
    label: 'Pickup V8 essence (2020, 8 cyl, 5.0L)',
    year: 2020, cylinders: 8, displ: 5.0, drive: 'AWD', vclass: 'Pickup',
    tranny: 'Automatic', forced_induction_bool: false, is_diesel_bool: false,
  },
  {
    label: 'Pickup diesel V6 (2022, 6 cyl, 3.0L)',
    year: 2022, cylinders: 6, displ: 3.0, drive: 'AWD', vclass: 'Pickup',
    tranny: 'Automatic', forced_induction_bool: false, is_diesel_bool: true,
  },
  {
    label: 'SUV turbo compact (2021, 4 cyl, 2.0L)',
    year: 2021, cylinders: 4, displ: 2.0, drive: 'AWD', vclass: 'SUV',
    tranny: 'Automatic', forced_induction_bool: true, is_diesel_bool: false,
  },
  {
    label: 'Minivan V6 (2015, 6 cyl, 3.5L)',
    year: 2015, cylinders: 6, displ: 3.5, drive: 'FWD', vclass: 'Van',
    tranny: 'Automatic', forced_induction_bool: false, is_diesel_bool: false,
  },
  {
    label: 'Mini citadine manuelle (2024, 3 cyl, 1.0L)',
    year: 2024, cylinders: 3, displ: 1.0, drive: 'FWD', vclass: 'Car',
    tranny: 'Manual', forced_induction_bool: true, is_diesel_bool: false,
  },
]

// ── Table de référence ───────────────────────────────────────────────────────
const consumptionRefs = [
  { label: 'Très économique', range: '< 6 L/100km',    icon: 'mdi-leaf',               color: 'success'    },
  { label: 'Économique',      range: '6 – 9 L/100km',  icon: 'mdi-leaf-circle-outline', color: 'light-green'},
  { label: 'Moyenne',         range: '9 – 12 L/100km', icon: 'mdi-gas-station-outline', color: 'warning'    },
  { label: 'Élevée',          range: '12 – 15 L/100km',icon: 'mdi-gas-station',         color: 'deep-orange'},
  { label: 'Très élevée',     range: '> 15 L/100km',   icon: 'mdi-fire',                color: 'error'      },
]

// ── Computed pour la visualisation ──────────────────────────────────────────
const resultGradient = computed(() => {
  if (!result.value) return ''
  const v = result.value.L100km
  if (v < 6)  return 'linear-gradient(135deg, #1B5E20, #2E7D32)'
  if (v < 9)  return 'linear-gradient(135deg, #33691E, #558B2F)'
  if (v < 12) return 'linear-gradient(135deg, #E65100, #F57C00)'
  if (v < 15) return 'linear-gradient(135deg, #BF360C, #D84315)'
  return              'linear-gradient(135deg, #B71C1C, #C62828)'
})

const gaugePercent = computed(() =>
  result.value ? Math.min((result.value.L100km / 16) * 100, 100) : 0
)

const gaugeBarColor = computed(() => {
  if (!result.value) return 'success'
  const v = result.value.L100km
  if (v < 6)  return 'light-green-lighten-2'
  if (v < 9)  return 'yellow-lighten-1'
  if (v < 12) return 'orange-lighten-1'
  if (v < 15) return 'deep-orange-lighten-1'
  return              'red-lighten-1'
})

// ── Actions ──────────────────────────────────────────────────────────────────
async function runPredict() {
  const { valid } = await formRef.value.validate()
  if (!valid) return

  loading.value = true
  error.value   = null
  result.value  = null

  try {
    const { forced_induction_bool, is_diesel_bool, ...rest } = form.value
    const payload = {
      ...rest,
      forced_induction: forced_induction_bool ? 1 : 0,
      is_diesel:        is_diesel_bool        ? 1 : 0,
    }
    const res  = await fetch('/api/predict', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify(payload),
    })
    const data = await res.json()
    if (!res.ok) {
      error.value = data.error || 'Erreur lors de la prédiction'
    } else {
      result.value = data
    }
  } catch {
    error.value = "Impossible de contacter le serveur. Vérifiez que l'API est démarrée."
  } finally {
    loading.value = false
  }
}

function resetForm() {
  formRef.value?.reset()
  result.value                     = null
  error.value                      = null
  form.value.drive                 = 'FWD'
  form.value.vclass                = 'Car'
  form.value.tranny                = 'Automatic'
  form.value.forced_induction_bool = false
  form.value.is_diesel_bool        = false
}

function applyPreset(preset) {
  const { label, ...values } = preset
  Object.assign(form.value, values)
  result.value = null
  error.value  = null
}
</script>
