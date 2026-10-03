<template>
  <div>
    <h1 class="sc-page-title mb-1">Hola{{ nombre ? ', ' + nombre : '' }}</h1>
    <p class="sc-page-sub mb-6">Así va la comunidad hoy.</p>

    <v-row>
      <!-- Métrica protagonista -->
      <v-col cols="12" md="5">
        <v-card class="pa-6 h-100 d-flex flex-column justify-space-between">
          <div class="d-flex justify-space-between align-start">
            <div>
              <div class="sc-metric-label">Personas activas</div>
              <div class="sc-metric-value mt-2" style="font-size: 3.4rem">{{ kpis.total_personas ?? 0 }}</div>
            </div>
            <div class="sc-icon-chip"><v-icon>mdi-account-multiple-outline</v-icon></div>
          </div>
          <div class="mt-4 d-flex align-center" style="color: var(--sc-blue-ink)">
            <v-icon size="18" class="me-1">mdi-trending-up</v-icon>
            <span style="font-weight: 600">{{ kpis.personas_nuevas_30d ?? 0 }}</span>
            <span class="sc-page-sub ms-1">nuevas en los últimos 30 días</span>
          </div>
        </v-card>
      </v-col>

      <!-- Tiles compactos -->
      <v-col cols="12" md="7">
        <v-row>
          <v-col v-for="t in tiles" :key="t.label" cols="6" lg="3">
            <v-card class="pa-4 h-100">
              <div class="sc-icon-chip mb-3" style="width: 38px; height: 38px; border-radius: 10px">
                <v-icon size="20">{{ t.icon }}</v-icon>
              </div>
              <div class="sc-metric-value" style="font-size: 1.7rem">{{ t.value }}</div>
              <div class="sc-metric-label mt-1">{{ t.label }}</div>
            </v-card>
          </v-col>
        </v-row>
      </v-col>
    </v-row>

    <v-row class="mt-1">
      <!-- Asistencia por servicio -->
      <v-col cols="12" lg="7">
        <v-card>
          <div class="sc-card-title d-flex align-center">
            <v-icon size="18" color="primary" class="me-2">mdi-chart-timeline-variant</v-icon>
            Asistencia por servicio
          </div>
          <div class="pa-5">
            <div v-for="a in asistencia" :key="a.servicio + a.fecha" class="mb-4">
              <div class="d-flex justify-space-between mb-1" style="font-size: 0.88rem">
                <span style="color: var(--sc-ink); font-weight: 500">{{ a.servicio }}</span>
                <span style="color: var(--sc-ink); font-weight: 600">{{ a.asistencia }}</span>
              </div>
              <v-progress-linear :model-value="Math.min(a.asistencia * 8, 100)"
                color="primary" bg-color="#eef3ff" height="8" rounded />
              <div class="sc-page-sub mt-1" style="font-size: 0.75rem">{{ a.fecha }}</div>
            </div>
            <div v-if="!asistencia.length" class="text-center py-6">
              <v-icon size="38" color="#cbd5e1">mdi-chart-line</v-icon>
              <p class="sc-page-sub mt-2">Registra un check-in y verás la asistencia aquí.</p>
            </div>
          </div>
        </v-card>
      </v-col>

      <!-- Embudo Únete -->
      <v-col cols="12" lg="5">
        <v-card>
          <div class="sc-card-title d-flex align-center">
            <v-icon size="18" color="primary" class="me-2">mdi-filter-variant</v-icon>
            Proceso Únete
          </div>
          <div class="pa-2">
            <div v-for="(v, etapa) in embudo" :key="etapa"
              class="d-flex align-center justify-space-between px-3 py-3"
              style="border-bottom: 1px solid var(--sc-line)">
              <div class="d-flex align-center">
                <span class="sc-dot" :style="{ background: colorEtapa(etapa) }"></span>
                <span class="ms-3 text-capitalize" style="color: var(--sc-ink)">{{ etapa.replace('_', ' ') }}</span>
              </div>
              <span style="font-weight: 700; color: var(--sc-ink); font-variant-numeric: tabular-nums">{{ v }}</span>
            </div>
          </div>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import api from '@/api'
import { useAuth } from '@/stores/auth'

const auth = useAuth()
const kpis = ref({})
const asistencia = ref([])
const embudo = ref({})
const conteos = ref(0)

const nombre = computed(() => auth.user?.nombre?.split(' ')[0] || '')

const tiles = computed(() => [
  { label: 'Servicios', value: kpis.value.total_servicios ?? 0, icon: 'mdi-calendar-blank-outline' },
  { label: 'Check-ins', value: kpis.value.total_checkins ?? 0, icon: 'mdi-login-variant' },
  { label: 'Cohortes Únete', value: kpis.value.cohortes_activas ?? 0, icon: 'mdi-account-group-outline' },
  { label: 'Asistencia conteos', value: conteos.value, icon: 'mdi-calculator-variant-outline' },
])

const etapaColors = {
  inscrito: '#3b82f6', en_proceso: '#f59e0b', completado: '#0d9488',
  integrado: '#2563eb', retirado: '#94a3b8',
}
function colorEtapa(e) { return etapaColors[e] || '#94a3b8' }

onMounted(async () => {
  const { data } = await api.get('/analiticas/resumen')
  kpis.value = data.kpis
  asistencia.value = data.asistencia_por_servicio
  embudo.value = data.embudo_unete
  conteos.value = data.asistencia_total_conteos
})
</script>

<style scoped>
.sc-dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }
</style>
