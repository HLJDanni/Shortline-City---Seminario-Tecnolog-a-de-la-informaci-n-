<template>
  <div v-if="persona">
    <div class="d-flex align-center mb-5" style="gap: 12px">
      <v-btn icon="mdi-arrow-left" variant="text" @click="$router.push('/personas')" />
      <v-avatar size="52" color="#eef3ff">
        <span class="brand-font" style="color: var(--sc-blue-ink); font-weight: 700; font-size: 1.1rem">{{ ini }}</span>
      </v-avatar>
      <div>
        <h1 class="sc-page-title" style="line-height: 1.1">{{ persona.nombres }} {{ persona.apellidos }}</h1>
        <v-chip size="small" variant="tonal" color="primary" class="mt-1">{{ persona.estado }}</v-chip>
      </div>
      <v-spacer />
      <v-btn color="primary" variant="tonal" prepend-icon="mdi-card-account-details-outline"
        @click="$router.push(`/nametag/${persona.id}`)">Name Tag</v-btn>
    </div>

    <v-row>
      <v-col cols="12" md="5">
        <v-card>
          <div class="sc-card-title">Datos personales</div>
          <div class="pa-2">
            <div v-for="d in datos" :key="d.label"
              class="d-flex align-center px-3 py-3" style="border-bottom: 1px solid var(--sc-line)">
              <v-icon size="20" color="secondary" class="me-3">{{ d.icon }}</v-icon>
              <span class="sc-page-sub">{{ d.label }}</span>
              <v-spacer />
              <span style="color: var(--sc-ink); font-weight: 500">{{ d.value }}</span>
            </div>
          </div>
        </v-card>
      </v-col>

      <v-col cols="12" md="7">
        <v-card class="mb-5">
          <div class="sc-card-title d-flex align-center">
            <v-icon size="18" color="primary" class="me-2">mdi-login-variant</v-icon> Asistencias
          </div>
          <div v-if="checkins.length" class="pa-2">
            <div v-for="c in checkins" :key="c.id"
              class="d-flex align-center px-3 py-2" style="border-bottom: 1px solid var(--sc-line)">
              <v-icon size="18" color="success" class="me-3">mdi-check-circle-outline</v-icon>
              <span style="color: var(--sc-ink)">Servicio #{{ c.servicio_id }}</span>
              <v-spacer />
              <span class="sc-page-sub">{{ fecha(c.fecha_hora) }}</span>
            </div>
          </div>
          <div v-else class="pa-6 text-center">
            <p class="sc-page-sub">Todavía no tiene asistencias registradas.</p>
          </div>
        </v-card>

        <v-card>
          <div class="sc-card-title d-flex align-center">
            <v-icon size="18" color="primary" class="me-2">mdi-history</v-icon> Historial
          </div>
          <v-timeline v-if="historial.length" side="end" density="compact" truncate-line="both" class="pa-5">
            <v-timeline-item v-for="(h, i) in historial" :key="i" dot-color="primary" size="x-small">
              <div style="color: var(--sc-ink)">
                <span class="text-capitalize" style="font-weight: 600">{{ h.accion }}</span> — {{ h.detalle }}
              </div>
              <div class="sc-page-sub" style="font-size: 0.78rem">{{ fecha(h.fecha) }}</div>
            </v-timeline-item>
          </v-timeline>
          <div v-else class="pa-6 text-center"><p class="sc-page-sub">Sin movimientos aún.</p></div>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api'

const route = useRoute()
const persona = ref(null)
const checkins = ref([])
const historial = ref([])

const ini = computed(() => {
  const p = persona.value
  return p ? `${(p.nombres || '?')[0]}${(p.apellidos || '')[0] || ''}`.toUpperCase() : ''
})
const datos = computed(() => persona.value ? [
  { label: 'ID', value: persona.value.id, icon: 'mdi-pound' },
  { label: 'Teléfono', value: persona.value.telefono || '—', icon: 'mdi-phone-outline' },
  { label: 'Correo', value: persona.value.correo || '—', icon: 'mdi-email-outline' },
  { label: 'Registrada', value: fecha(persona.value.creada_en), icon: 'mdi-calendar-outline' },
] : [])

function fecha(iso) { return iso ? new Date(iso).toLocaleString('es-GT') : '—' }

onMounted(async () => {
  const { data } = await api.get(`/personas/${route.params.id}/perfil`)
  persona.value = data.persona
  checkins.value = data.checkins
  historial.value = data.historial
})
</script>
