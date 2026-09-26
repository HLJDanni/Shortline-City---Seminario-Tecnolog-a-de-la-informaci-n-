<template>
  <div>
    <h2 class="text-h5 font-weight-bold mb-1">Panel general</h2>
    <p class="text-medium-emphasis mb-5">Indicadores clave del sistema (RF-036 a RF-040)</p>

    <v-row>
      <v-col v-for="k in tarjetas" :key="k.label" cols="6" md="4" lg="2">
        <v-card class="pa-4" elevation="2">
          <v-icon :color="k.color" size="30">{{ k.icon }}</v-icon>
          <div class="text-h4 font-weight-bold mt-2">{{ k.value }}</div>
          <div class="text-caption text-medium-emphasis">{{ k.label }}</div>
        </v-card>
      </v-col>
    </v-row>

    <v-row class="mt-2">
      <v-col cols="12" lg="7">
        <v-card elevation="2">
          <v-card-title class="text-subtitle-1 font-weight-bold">
            Asistencia por servicio
          </v-card-title>
          <v-divider />
          <v-card-text>
            <div v-for="a in asistencia" :key="a.servicio + a.fecha" class="mb-3">
              <div class="d-flex justify-space-between text-body-2 mb-1">
                <span>{{ a.servicio }} <span class="text-medium-emphasis">· {{ a.fecha }}</span></span>
                <strong>{{ a.asistencia }}</strong>
              </div>
              <v-progress-linear
                :model-value="Math.min(a.asistencia * 8, 100)"
                color="primary" height="10" rounded />
            </div>
            <p v-if="!asistencia.length" class="text-medium-emphasis">
              Aún no hay check-ins registrados.
            </p>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" lg="5">
        <v-card elevation="2">
          <v-card-title class="text-subtitle-1 font-weight-bold">Embudo de Únete</v-card-title>
          <v-divider />
          <v-list>
            <v-list-item v-for="(v, etapa) in embudo" :key="etapa">
              <v-list-item-title class="text-capitalize">{{ etapa.replace('_', ' ') }}</v-list-item-title>
              <template #append><v-chip size="small" color="secondary" variant="tonal">{{ v }}</v-chip></template>
            </v-list-item>
          </v-list>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import api from '@/api'

const kpis = ref({})
const asistencia = ref([])
const embudo = ref({})
const conteos = ref(0)

const tarjetas = computed(() => [
  { label: 'Personas activas', value: kpis.value.total_personas ?? 0, icon: 'mdi-account-group', color: 'primary' },
  { label: 'Nuevas (30 días)', value: kpis.value.personas_nuevas_30d ?? 0, icon: 'mdi-account-plus', color: 'success' },
  { label: 'Servicios', value: kpis.value.total_servicios ?? 0, icon: 'mdi-calendar-star', color: 'secondary' },
  { label: 'Check-ins', value: kpis.value.total_checkins ?? 0, icon: 'mdi-door-open', color: 'accent' },
  { label: 'Cohortes Únete', value: kpis.value.cohortes_activas ?? 0, icon: 'mdi-sitemap', color: 'info' },
  { label: 'Asistencia (conteos)', value: conteos.value, icon: 'mdi-counter', color: 'error' },
])

onMounted(async () => {
  const { data } = await api.get('/analiticas/resumen')
  kpis.value = data.kpis
  asistencia.value = data.asistencia_por_servicio
  embudo.value = data.embudo_unete
  conteos.value = data.asistencia_total_conteos
})
</script>
