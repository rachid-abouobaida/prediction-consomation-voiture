<template>
  <v-app :theme="theme">
    <!-- ── Barre de navigation ─────────────────────────────────── -->
    <v-app-bar color="primary" elevation="4" density="comfortable">
      <template #prepend>
        <v-app-bar-nav-icon icon="mdi-car-multiple" />
      </template>

      <v-app-bar-title class="font-weight-bold">
        Prédiction de consommation de carburant
      </v-app-bar-title>

      <template #append>
        <!-- Indicateur d'état du service -->
        <v-chip
          :color="serviceOk ? 'success' : 'error'"
          variant="tonal"
          size="small"
          class="mr-2"
        >
          <v-icon
            start
            :icon="serviceOk ? 'mdi-check-circle-outline' : 'mdi-alert-circle-outline'"
          />
          {{ serviceOk ? 'Service actif' : 'Service hors ligne' }}
        </v-chip>

        <!-- Bascule clair / sombre -->
        <v-btn
          :icon="theme === 'light' ? 'mdi-weather-night' : 'mdi-weather-sunny'"
          variant="text"
          @click="theme = theme === 'light' ? 'dark' : 'light'"
        />
      </template>
    </v-app-bar>

    <!-- ── Contenu principal ──────────────────────────────────── -->
    <v-main class="bg-background">
      <v-container class="py-8" style="max-width: 1100px">
        <PredictionForm />
      </v-container>
    </v-main>

    <!-- ── Pied de page ──────────────────────────────────────── -->
    <v-footer color="primary" class="justify-center py-2">
      <span class="text-caption text-white opacity-70">
        Modèle MLP TensorFlow · Dataset Auto MPG (UCI) · 1970 – 1982
      </span>
    </v-footer>
  </v-app>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import PredictionForm from './components/PredictionForm.vue'

const theme      = ref('light')
const serviceOk  = ref(false)

onMounted(async () => {
  try {
    const res  = await fetch('/api/health')
    const data = await res.json()
    serviceOk.value = data.api === 'ok' && data.ml_service?.status === 'ok'
  } catch {
    serviceOk.value = false
  }
})
</script>
