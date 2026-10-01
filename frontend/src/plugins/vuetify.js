import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'

import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

export default createVuetify({
  components,
  directives,
  icons: {
    defaultSet: 'mdi',
  },
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        colors: {
          primary:   '#1565C0',
          secondary: '#42A5F5',
          accent:    '#FF6F00',
          success:   '#2E7D32',
          warning:   '#F57C00',
          error:     '#C62828',
          background: '#F5F7FA',
        },
      },
    },
  },
})
