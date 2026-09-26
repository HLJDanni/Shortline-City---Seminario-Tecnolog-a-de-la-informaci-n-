<template>
  <v-navigation-drawer v-model="drawer" color="primary" theme="dark">
    <div class="pa-4 d-flex align-center">
      <v-icon size="30" class="me-2">mdi-lighthouse-on</v-icon>
      <div>
        <div class="text-h6 font-weight-bold">Shoreline City</div>
        <div class="text-caption text-medium-emphasis">Gestión de personas</div>
      </div>
    </div>
    <v-divider />
    <v-list nav density="comfortable">
      <v-list-item
        v-for="item in menu" :key="item.to"
        :to="item.to" :prepend-icon="item.icon" :title="item.title"
        color="white" rounded="lg" />
    </v-list>
  </v-navigation-drawer>

  <v-app-bar flat color="surface" border>
    <v-app-bar-nav-icon @click="drawer = !drawer" />
    <v-toolbar-title class="font-weight-medium">{{ titulo }}</v-toolbar-title>
    <v-spacer />
    <v-chip color="primary" variant="tonal" class="me-2" prepend-icon="mdi-shield-account">
      {{ auth.user?.rol }}
    </v-chip>
    <v-menu>
      <template #activator="{ props }">
        <v-btn icon v-bind="props"><v-avatar color="secondary" size="36">
          <span class="text-white">{{ iniciales }}</span></v-avatar></v-btn>
      </template>
      <v-list>
        <v-list-item :subtitle="auth.user?.email" :title="auth.user?.nombre" />
        <v-divider />
        <v-list-item prepend-icon="mdi-logout" title="Cerrar sesión" @click="salir" />
      </v-list>
    </v-menu>
  </v-app-bar>

  <v-main class="bg-background">
    <v-container fluid class="pa-4 pa-md-6">
      <router-view />
    </v-container>
  </v-main>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuth } from '@/stores/auth'

const drawer = ref(true)
const auth = useAuth()
const route = useRoute()
const router = useRouter()

const menu = [
  { title: 'Dashboard', icon: 'mdi-view-dashboard', to: '/' },
  { title: 'Personas', icon: 'mdi-account-group', to: '/personas' },
  { title: 'Check-in', icon: 'mdi-door-open', to: '/checkin' },
  { title: 'Conteos', icon: 'mdi-counter', to: '/conteos' },
  { title: 'Únete', icon: 'mdi-sitemap', to: '/unete' },
  { title: 'Servicios', icon: 'mdi-calendar-star', to: '/servicios' },
]

const titulo = computed(() => menu.find((m) => m.to === route.path)?.title || 'Shoreline City')
const iniciales = computed(() => {
  const n = auth.user?.nombre || '?'
  return n.split(' ').slice(0, 2).map((x) => x[0]).join('').toUpperCase()
})

function salir() {
  auth.logout()
  router.push('/login')
}
</script>
