<template>
  <div>
    <h1 class="sc-page-title">Check-in</h1>
    <p class="sc-page-sub mb-5">Registra la entrada de cada persona al servicio.</p>

    <v-card class="pa-4 mb-5">
      <v-row dense align="center">
        <v-col cols="12" md="5">
          <v-select v-model="servicioId" :items="servicios" item-title="label" item-value="id"
            placeholder="Elige un servicio" prepend-inner-icon="mdi-calendar-blank-outline" hide-details
            @update:model-value="cargarRegistrados" />
        </v-col>
        <v-col cols="12" md="7">
          <v-text-field v-model="q" placeholder="Busca a la persona por nombre, teléfono o correo"
            prepend-inner-icon="mdi-magnify" clearable hide-details
            @keyup.enter="buscar" @click:clear="resultados = []" />
        </v-col>
      </v-row>
    </v-card>

    <v-card v-if="!servicioId" class="pa-10 text-center">
      <v-icon size="42" color="#cbd5e1">mdi-calendar-blank-outline</v-icon>
      <p class="sc-page-sub mt-2">Elige un servicio para empezar a registrar asistencia.</p>
    </v-card>

    <v-row v-else>
      <v-col cols="12" md="7">
        <v-card>
          <div class="sc-card-title">Resultados</div>
          <div v-if="resultados.length" class="pa-2">
            <div v-for="p in resultados" :key="p.id"
              class="d-flex align-center px-3 py-2" style="border-bottom: 1px solid var(--sc-line)">
              <v-avatar size="34" color="#eef3ff" class="me-3">
                <span style="color: var(--sc-blue-ink); font-weight: 600; font-size: 0.78rem">
                  {{ (p.nombres[0] + (p.apellidos[0] || '')).toUpperCase() }}</span>
              </v-avatar>
              <div>
                <div style="font-weight: 600; color: var(--sc-ink)">{{ p.nombres }} {{ p.apellidos }}</div>
                <div class="sc-page-sub" style="font-size: 0.78rem">{{ p.telefono || p.correo || '' }}</div>
              </div>
              <v-spacer />
              <v-btn color="primary" size="small" prepend-icon="mdi-check" :loading="registrandoId === p.id"
                @click="registrar(p.id)">Registrar</v-btn>
            </div>
          </div>
          <div v-else class="pa-8 text-center">
            <p class="sc-page-sub">{{ q ? 'Nadie coincide con esa búsqueda.' : 'Escribe un nombre y presiona Enter.' }}</p>
          </div>
        </v-card>
      </v-col>

      <v-col cols="12" md="5">
        <v-card>
          <div class="sc-card-title d-flex align-center justify-space-between">
            Registrados hoy
            <v-chip size="small" color="primary" variant="tonal">{{ registrados.length }}</v-chip>
          </div>
          <div v-if="registrados.length" class="pa-2">
            <div v-for="c in registrados" :key="c.id"
              class="d-flex align-center px-3 py-2" style="border-bottom: 1px solid var(--sc-line)">
              <v-icon size="18" color="success" class="me-3">mdi-account-check-outline</v-icon>
              <span style="color: var(--sc-ink)">{{ c.persona }}</span>
              <v-spacer />
              <span class="sc-page-sub">{{ hora(c.fecha_hora) }}</span>
            </div>
          </div>
          <div v-else class="pa-8 text-center"><p class="sc-page-sub">Aún no hay nadie registrado.</p></div>
        </v-card>
      </v-col>
    </v-row>

    <v-snackbar v-model="snack" color="success" timeout="1400">Asistencia registrada</v-snackbar>
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
  const nombres = {}
  for (const c of data) {
    if (!nombres[c.persona_id]) {
      try { const { data: p } = await api.get(`/personas/${c.persona_id}`); nombres[c.persona_id] = `${p.nombres} ${p.apellidos}` }
      catch { nombres[c.persona_id] = `#${c.persona_id}` }
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
