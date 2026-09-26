import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'
import { createVuetify } from 'vuetify'

// Tema de marca Shoreline City (azul profundo + acentos cálidos).
const shorelineLight = {
  dark: false,
  colors: {
    primary: '#0b3d5c',
    secondary: '#3a86a8',
    accent: '#f4a261',
    success: '#2a9d8f',
    info: '#457b9d',
    warning: '#e9c46a',
    error: '#e76f51',
    background: '#f4f6f8',
    surface: '#ffffff',
  },
}

export default createVuetify({
  theme: {
    defaultTheme: 'shorelineLight',
    themes: { shorelineLight },
  },
  defaults: {
    VCard: { rounded: 'lg' },
    VBtn: { rounded: 'lg', style: 'text-transform: none; letter-spacing: normal;' },
    VTextField: { variant: 'outlined', density: 'comfortable' },
    VSelect: { variant: 'outlined', density: 'comfortable' },
  },
})
