import { defineStore } from 'pinia'
import api from '@/api'

// Limpia tokens de versiones anteriores que se guardaban en localStorage.
try { localStorage.removeItem('sc_token') } catch { /* sin almacenamiento */ }

export const useAuth = defineStore('auth', {
  state: () => ({
    user: null,
  }),
  getters: {
    isAuth: (s) => !!s.user,
    permisos: (s) => (s.user ? s.user.permisos : []),
  },
  actions: {
    can(permiso) {
      const p = this.permisos || []
      if (p.includes('*') || p.includes(permiso)) return true
      const modulo = permiso.split(':')[0]
      return p.includes(`${modulo}:*`)
    },
    async login(email, password) {
      // El backend responde con una cookie HttpOnly; no se guarda nada aquí.
      await api.post('/auth/login', { email, password })
      await this.fetchMe()
    },
    async fetchMe() {
      const { data } = await api.get('/auth/me')
      this.user = data
      return data
    },
    async logout() {
      try { await api.post('/auth/logout') } catch { /* la sesión ya no era válida */ }
      this.user = null
    },
  },
})
