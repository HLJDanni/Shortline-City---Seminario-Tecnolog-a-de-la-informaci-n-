<template>
  <div v-if="persona">
    <div class="d-flex align-center mb-4">
      <v-btn icon="mdi-arrow-left" variant="text" @click="$router.push('/personas')" />
      <div class="ms-2">
        <h2 class="text-h5 font-weight-bold">{{ persona.nombres }} {{ persona.apellidos }}</h2>
        <v-chip size="small" color="primary" variant="tonal">{{ persona.estado }}</v-chip>
      </div>
      <v-spacer />
      <v-btn color="primary" variant="tonal" prepend-icon="mdi-tag"
        @click="$router.push(`/nametag/${persona.id}`)">Name Tag</v-btn>
    </div>

    <v-row>
      <v-col cols="12" md="5">
        <v-card elevation="2">
          <v-card-title class="text-subtitle-1 font-weight-bold">Datos personales</v-card-title>
          <v-divider />
          <v-list>
            <v-list-item title="ID" :subtitle="String(persona.id)" prepend-icon="mdi-identifier" />
            <v-list-item title="Teléfono" :subtitle="persona.telefono || '—'" prepend-icon="mdi-phone" />
            <v-list-item title="Correo" :subtitle="persona.correo || '—'" prepend-icon="mdi-email" />
            <v-list-item title="Registrada" :subtitle="fecha(persona.creada_en)" prepend-icon="mdi-calendar" />
          </v-list>
        </v-card>
      </v-col>

      <v-col cols="12" md="7">
        <v-card elevation="2" class="mb-4">
          <v-card-title class="text-subtitle-1 font-weight-bold">Asistencias</v-card-title>
          <v-divider />
          <v-list v-if="checkins.length">
            <v-list-item v-for="c in checkins" :key="c.id"
              :title="`Servicio #${c.servicio_id}`" :subtitle="fecha(c.fecha_hora)">
              <template #append>
                <v-chip size="x-small" :color="c.estado === 'registrado' ? 'success' : 'error'" variant="tonal">
                  {{ c.estado }}</v-chip>
              </template>
            </v-list-item>
          </v-list>
          <v-card-text v-else class="text-medium-emphasis">Sin asistencias registradas.</v-card-text>
        </v-card>

        <v-card elevation="2">
          <v-card-title class="text-subtitle-1 font-weight-bold">Historial (RF-009)</v-card-title>
          <v-divider />
          <v-timeline v-if="historial.length" side="end" density="compact" class="pa-4">
            <v-timeline-item v-for="(h, i) in historial" :key="i" dot-color="primary" size="x-small">
              <div class="d-flex justify-space-between">
                <span><strong class="text-capitalize">{{ h.accion }}</strong> — {{ h.detalle }}</span>
              </div>
              <div class="text-caption text-medium-emphasis">{{ fecha(h.fecha) }}</div>
            </v-timeline-item>
          </v-timeline>
          <v-card-text v-else class="text-medium-emphasis">Sin historial.</v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api'

const route = useRoute()
const persona = ref(null)
const checkins = ref([])
const historial = ref([])

function fecha(iso) { return iso ? new Date(iso).toLocaleString('es-GT') : '—' }

onMounted(async () => {
  const { data } = await api.get(`/personas/${route.params.id}/perfil`)
  persona.value = data.persona
  checkins.value = data.checkins
  historial.value = data.historial
})
</script>
