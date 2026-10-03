import { createRouter, createWebHistory } from 'vue-router'
import { useAuth } from '@/stores/auth'

const routes = [
  { path: '/login', component: () => import('@/views/Login.vue'), meta: { public: true } },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    children: [
      { path: '', name: 'dashboard', component: () => import('@/views/Dashboard.vue') },
      { path: 'personas', name: 'personas', component: () => import('@/views/Personas.vue') },
      { path: 'personas/:id', name: 'persona', component: () => import('@/views/PersonaDetalle.vue') },
      { path: 'checkin', name: 'checkin', component: () => import('@/views/Checkin.vue') },
      { path: 'conteos', name: 'conteos', component: () => import('@/views/Conteos.vue') },
      { path: 'unete', name: 'unete', component: () => import('@/views/Unete.vue') },
      { path: 'servicios', name: 'servicios', component: () => import('@/views/Servicios.vue') },
      { path: 'nametag/:id', name: 'nametag', component: () => import('@/views/NameTag.vue') },
    ],
  },
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach(async (to) => {
  const auth = useAuth()
  if (to.meta.public) return true
  if (!auth.isAuth) return { path: '/login' }
  if (!auth.user) {
    try { await auth.fetchMe() } catch { auth.logout(); return { path: '/login' } }
  }
  return true
})

export default router
