import { defineStore } from 'pinia'
import api from '@/api'

export const useAuth = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('sc_token') || null,
    user: null,
  }),
  getters: {
    isAuth: (s) => !!s.token,
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
      const { data } = await api.post('/auth/login', { email, password })
      this.token = data.access_token
      localStorage.setItem('sc_token', this.token)
      await this.fetchMe()
    },
    async fetchMe() {
      const { data } = await api.get('/auth/me')
      this.user = data
    },
    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('sc_token')
    },
  },
})
