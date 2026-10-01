import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vuetify from 'vite-plugin-vuetify'

export default defineConfig({
  plugins: [
    vue(),
    // autoImport : Vuetify génère automatiquement les imports des composants
    vuetify({ autoImport: true }),
  ],
  server: {
    port: 5174,
    proxy: {
      // Toutes les requêtes /api/* sont redirigées vers l'API Node.js
      '/api': {
        target: 'http://localhost:3001',
        changeOrigin: true,
      },
    },
  },
})
