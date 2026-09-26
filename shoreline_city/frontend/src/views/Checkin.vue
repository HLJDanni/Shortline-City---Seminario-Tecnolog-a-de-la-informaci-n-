<template>
  <div>
    <h2 class="text-h5 font-weight-bold mb-1">Check-in de asistencia</h2>
    <p class="text-medium-emphasis mb-5">Registro rápido de entrada (RF-012 / RF-013)</p>

    <v-row>
      <v-col cols="12" md="5">
        <v-select v-model="servicioId" :items="servicios" item-title="label" item-value="id"
          label="Servicio" prepend-inner-icon="mdi-calendar" @update:model-value="cargarRegistrados" />
      </v-col>
      <v-col cols="12" md="7">
        <v-text-field v-model="q" label="Buscar persona"
          prepend-inner-icon="mdi-magnify" clearable @keyup.enter="buscar" @click:clear="resultados = []" />
      </v-col>
    </v-row>

    <v-alert v-if="!servicioId" type="info" variant="tonal" class="mb-4">
      Seleccione un servicio para registrar asistencia.
    </v-alert>

    <v-row v-else>
      <v-col cols="12" md="7">
        <v-card elevation="2">
          <v-card-title class="text-subtitle-1 font-weight-bold">Resultados</v-card-title>
          <v-divider />
          <v-list v-if="resultados.length">
            <v-list-item v-for="p in resultados" :key="p.id"
              :title="`${p.nombres} ${p.apellidos}`" :subtitle="`${p.telefono || ''} ${p.correo || ''}`">
              <template #append>
                <v-btn color="success" size="small" prepend-icon="mdi-check" :loading="registrandoId === p.id"
                  @click="registrar(p.id)">Registrar</v-btn>
              </template>
            </v-list-item>
          </v-list>
          <v-card-text v-else class="text-medium-emphasis">
            {{ q ? 'Sin coincidencias.' : 'Escriba y presione Enter para buscar.' }}
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="5">
        <v-card elevation="2">
          <v-card-title class="text-subtitle-1 font-weight-bold d-flex align-center">
            Registrados <v-spacer /><v-chip color="primary" size="small">{{ registrados.length }}</v-chip>
          </v-card-title>
          <v-divider />
          <v-list v-if="registrados.length">
            <v-list-item v-for="c in registrados" :key="c.id" :title="c.persona"
              :subtitle="hora(c.fecha_hora)" prepend-icon="mdi-account-check" />
          </v-list>
          <v-card-text v-else class="text-medium-emphasis">Nadie registrado aún.</v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-snackbar v-model="snack" color="success" timeout="1500">Asistencia registrada</v-snackbar>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import api from '@/api'

const servicios = ref([])
const servicioId = ref(null)
const q = ref('')
const resultados = ref([])
const registrados = ref([])
const registrandoId = ref(null)
const snack = ref(false)

function hora(iso) { return new Date(iso).toLocaleTimeString('es-GT', { hour: '2-digit', minute: '2-digit' }) }

async function cargarServicios() {
  const { data } = await api.get('/servicios')
  servicios.value = data.map((s) => ({ ...s, label: `${s.nombre} (${s.fecha})` }))
}

async function buscar() {
  if (!q.value) return
  const { data } = await api.get('/personas', { params: { q: q.value, limit: 15 } })
  resultados.value = data
}

async function cargarRegistrados() {
  if (!servicioId.value) return
  const { data } = await api.get(`/checkin/servicio/${servicioId.value}`)
  // Enriquecer con nombre
  const nombres = {}
  for (const c of data) {
    if (!nombres[c.persona_id]) {
      try { const { data: p } = await api.get(`/personas/${c.persona_id}`); nombres[c.persona_id] = `${p.nombres} ${p.apellidos}` } catch { nombres[c.persona_id] = `#${c.persona_id}` }
    }
  }
  registrados.value = data.filter((c) => c.estado === 'registrado')
    .map((c) => ({ ...c, persona: nombres[c.persona_id] }))
}

async function registrar(personaId) {
  registrandoId.value = personaId
  try {
    await api.post('/checkin', { persona_id: personaId, servicio_id: servicioId.value })
    snack.value = true
    await cargarRegistrados()
  } finally { registrandoId.value = null }
}

onMounted(cargarServicios)
</script>
