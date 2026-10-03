<template>
  <v-navigation-drawer
    v-model="drawer"
    :rail="rail && !mobile"
    :permanent="!mobile"
    :temporary="mobile"
    color="surface"
    width="256"
    border="end">
    <div class="d-flex align-center px-4" style="height: 68px">
      <div class="sc-icon-chip" style="width: 38px; height: 38px; border-radius: 10px">
        <v-icon size="22">mdi-lighthouse</v-icon>
      </div>
      <div v-if="!(rail && !mobile)" class="ms-3">
        <div class="brand-font" style="font-size: 1.05rem; font-weight: 700; color: var(--sc-ink)">
          Shoreline City
        </div>
        <div class="sc-page-sub" style="font-size: 0.72rem; line-height: 1">Gestión de personas</div>
      </div>
    </div>

    <v-divider />

    <v-list nav class="sc-nav py-2">
      <v-list-item
        v-for="item in menu" :key="item.to"
        :to="item.to" :title="item.title" exact>
        <template #prepend><v-icon size="22">{{ item.icon }}</v-icon></template>
      </v-list-item>
    </v-list>

    <template #append>
      <div v-if="!(rail && !mobile)" class="pa-3">
        <v-card flat class="pa-3" color="surface" style="border: 1px solid var(--sc-line)">
          <div class="d-flex align-center">
            <v-avatar color="primary" size="36" class="me-2">
              <span style="color: #fff; font-weight: 600; font-size: 0.85rem">{{ iniciales }}</span>
            </v-avatar>
            <div style="min-width: 0">
              <div class="text-truncate" style="font-weight: 600; font-size: 0.85rem; color: var(--sc-ink)">
                {{ auth.user?.nombre }}
              </div>
              <div class="text-truncate sc-page-sub" style="font-size: 0.72rem">{{ auth.user?.rol }}</div>
            </div>
          </div>
        </v-card>
      </div>
    </template>
  </v-navigation-drawer>

  <v-app-bar color="surface" height="68" border="b">
    <v-btn icon variant="text" class="ms-2" @click="toggleNav">
      <v-icon>{{ mobile ? 'mdi-menu' : (rail ? 'mdi-chevron-right' : 'mdi-chevron-left') }}</v-icon>
    </v-btn>
    <div class="ms-1">
      <div class="sc-page-title" style="font-size: 1.05rem; line-height: 1.1">{{ titulo }}</div>
      <div class="sc-page-sub" style="font-size: 0.75rem; line-height: 1">{{ hoy }}</div>
    </div>
    <v-spacer />
    <v-menu location="bottom end">
      <template #activator="{ props }">
        <v-btn variant="text" v-bind="props" class="me-2 text-none">
          <v-avatar color="primary" size="32" class="me-2">
            <span style="color: #fff; font-weight: 600; font-size: 0.8rem">{{ iniciales }}</span>
          </v-avatar>
          <v-icon size="18" color="secondary">mdi-chevron-down</v-icon>
        </v-btn>
      </template>
      <v-card min-width="220" class="pa-1">
        <div class="px-3 py-2">
          <div style="font-weight: 600; color: var(--sc-ink)">{{ auth.user?.nombre }}</div>
          <div class="sc-page-sub">{{ auth.user?.email }}</div>
        </div>
        <v-divider class="my-1" />
        <v-list-item rounded="lg" @click="salir">
          <template #prepend><v-icon size="20">mdi-logout-variant</v-icon></template>
          <v-list-item-title>Cerrar sesión</v-list-item-title>
        </v-list-item>
      </v-card>
    </v-menu>
  </v-app-bar>

  <v-main style="background: var(--sc-bg)">
    <div class="mx-auto px-4 px-md-6 py-5" style="max-width: 1280px">
      <router-view />
    </div>
  </v-main>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useDisplay } from 'vuetify'
import { useRoute, useRouter } from 'vue-router'
import { useAuth } from '@/stores/auth'

const { mobile } = useDisplay()
const auth = useAuth()
const route = useRoute()
const router = useRouter()

const drawer = ref(true)
const rail = ref(false)

watch(mobile, (m) => { drawer.value = !m }, { immediate: true })

const menu = [
  { title: 'Dashboard', icon: 'mdi-view-dashboard-outline', to: '/' },
  { title: 'Personas', icon: 'mdi-account-multiple-outline', to: '/personas' },
  { title: 'Check-in', icon: 'mdi-login-variant', to: '/checkin' },
  { title: 'Conteos', icon: 'mdi-calculator-variant-outline', to: '/conteos' },
  { title: 'Únete', icon: 'mdi-account-group-outline', to: '/unete' },
  { title: 'Servicios', icon: 'mdi-calendar-blank-outline', to: '/servicios' },
]

const titulo = computed(() => menu.find((m) => m.to === route.path)?.title
  || (route.path.startsWith('/personas') ? 'Personas'
    : route.path.startsWith('/nametag') ? 'Name Tag' : 'Shoreline City'))

const hoy = computed(() =>
  new Date().toLocaleDateString('es-GT', { weekday: 'long', day: 'numeric', month: 'long' }))

const iniciales = computed(() => {
  const n = auth.user?.nombre || '?'
  return n.split(' ').slice(0, 2).map((x) => x[0]).join('').toUpperCase()
})

function toggleNav() {
  if (mobile.value) drawer.value = !drawer.value
  else rail.value = !rail.value
}

function salir() {
  auth.logout()
  router.push('/login')
}
</script>
