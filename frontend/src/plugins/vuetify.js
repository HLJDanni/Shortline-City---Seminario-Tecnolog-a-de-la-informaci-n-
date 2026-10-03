import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'
import { createVuetify } from 'vuetify'
import { es } from 'vuetify/locale'

// Paleta Shoreline: blancos, grises y un único acento azul moderno.
const shoreline = {
  dark: false,
  colors: {
    background: '#F5F7FA',
    surface: '#FFFFFF',
    primary: '#2563EB',
    'primary-darken-1': '#1E40AF',
    secondary: '#475569',
    info: '#3B82F6',
    success: '#0D9488',
    warning: '#F59E0B',
    error: '#EF4444',
    'on-background': '#0F1B2D',
    'on-surface': '#0F1B2D',
  },
  variables: {
    'border-color': '#0F1B2D',
    'border-opacity': 0.09,
    'high-emphasis-opacity': 0.95,
    'medium-emphasis-opacity': 0.62,
  },
}

export default createVuetify({
  locale: { locale: 'es', messages: { es } },
  theme: {
    defaultTheme: 'shoreline',
    themes: { shoreline },
  },
  defaults: {
    VCard: { flat: true, class: 'sc-card', rounded: 'lg' },
    VBtn: {
      flat: true,
      rounded: 'lg',
      style: 'text-transform: none; font-weight: 600; letter-spacing: 0;',
    },
    VTextField: { variant: 'outlined', density: 'comfortable', color: 'primary' },
    VSelect: { variant: 'outlined', density: 'comfortable', color: 'primary' },
    VTextarea: { variant: 'outlined', density: 'comfortable', color: 'primary' },
    VDataTable: { density: 'comfortable' },
    VChip: { rounded: 'lg' },
    VAppBar: { flat: true },
  },
})
