<template>
  <div>
    <div class="d-flex flex-wrap align-center mb-5" style="gap: 12px">
      <div>
        <h1 class="sc-page-title">Personas</h1>
        <p class="sc-page-sub">Registro central de la comunidad.</p>
      </div>
      <v-spacer />
      <v-btn v-if="auth.can('personas:crear')" color="primary" prepend-icon="mdi-plus" @click="abrirNueva">
        Nueva persona
      </v-btn>
    </div>

    <v-card class="pa-4 mb-5">
      <v-row dense align="center">
        <v-col cols="12" md="7">
          <v-text-field v-model="q" placeholder="Busca por nombre, teléfono o correo"
            prepend-inner-icon="mdi-magnify" clearable hide-details
            @keyup.enter="cargar" @click:clear="cargar" />
        </v-col>
        <v-col cols="8" md="3">
          <v-select v-model="estado" :items="estados" placeholder="Estado" clearable hide-details
            @update:model-value="cargar" />
        </v-col>
        <v-col cols="4" md="2">
          <v-btn color="primary" variant="tonal" block height="48" @click="cargar">Filtrar</v-btn>
        </v-col>
      </v-row>
    </v-card>

    <v-card>
      <v-data-table :headers="headers" :items="personas" :loading="cargando" :items-per-page="15"
        hover @click:row="(_, { item }) => ver(item)">
        <template #item.nombre_completo="{ item }">
          <div class="d-flex align-center py-1">
            <v-avatar size="34" color="#eef3ff" class="me-3">
              <span style="color: var(--sc-blue-ink); font-weight: 600; font-size: 0.78rem">{{ ini(item) }}</span>
            </v-avatar>
            <span style="font-weight: 600; color: var(--sc-ink)">{{ item.nombres }} {{ item.apellidos }}</span>
          </div>
        </template>
        <template #item.estado="{ value }">
          <v-chip size="small" variant="tonal" :color="colorEstado(value)">{{ value }}</v-chip>
        </template>
        <template #item.acciones="{ item }">
          <v-btn icon="mdi-card-account-details-outline" size="small" variant="text"
            @click.stop="$router.push(`/nametag/${item.id}`)" />
        </template>
        <template #no-data>
          <div class="text-center py-10">
            <v-icon size="40" color="#cbd5e1">mdi-account-search-outline</v-icon>
            <p class="sc-page-sub mt-2">No encontramos personas con esos criterios.</p>
          </div>
        </template>
      </v-data-table>
    </v-card>

    <!-- Diálogo nueva persona -->
    <v-dialog v-model="dialogo" max-width="640" persistent>
      <v-card>
        <div class="sc-card-title d-flex align-center justify-space-between">
          Nueva persona
          <v-btn icon="mdi-close" size="small" variant="text" @click="dialogo = false" />
        </div>
        <div class="pa-5">
          <v-alert v-if="duplicados.length" type="warning" variant="tonal" rounded="lg" class="mb-4">
            <div style="font-weight: 600">Puede que ya exista</div>
            <div v-for="d in duplicados" :key="d.id" class="mt-1" style="font-size: 0.88rem">
              {{ d.nombre }} — {{ d.telefono || 'sin teléfono' }} · {{ d.correo || 'sin correo' }}
            </div>
            <v-checkbox v-model="forzar" label="Crear de todos modos" density="compact" hide-details class="mt-2" />
          </v-alert>
          <v-row dense>
            <v-col cols="12" md="6"><v-text-field v-model="form.nombres" label="Nombres" /></v-col>
            <v-col cols="12" md="6"><v-text-field v-model="form.apellidos" label="Apellidos" /></v-col>
            <v-col cols="12" md="6"><v-text-field v-model="form.telefono" label="Teléfono" /></v-col>
            <v-col cols="12" md="6"><v-text-field v-model="form.correo" label="Correo" type="email" /></v-col>
            <v-col cols="12" md="6"><v-select v-model="form.estado" :items="estados" label="Estado" /></v-col>
            <v-col cols="12"><v-textarea v-model="form.notas" label="Notas" rows="2" /></v-col>
          </v-row>
          <v-alert v-if="errorForm" type="error" variant="tonal" density="compact" rounded="lg">{{ errorForm }}</v-alert>
        </div>
        <v-divider />
        <div class="pa-3 d-flex justify-end" style="gap: 8px">
          <v-btn variant="text" @click="dialogo = false">Cancelar</v-btn>
          <v-btn color="primary" :loading="guardando" @click="guardar">Guardar persona</v-btn>
        </div>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api'
import { useAuth } from '@/stores/auth'

const auth = useAuth()
const router = useRouter()
const estados = ['nuevo', 'activo', 'visitante', 'miembro', 'inactivo']
const headers = [
  { title: 'Nombre', key: 'nombre_completo' },
  { title: 'Teléfono', key: 'telefono' },
  { title: 'Correo', key: 'correo' },
  { title: 'Estado', key: 'estado' },
  { title: '', key: 'acciones', sortable: false, align: 'end' },
]

const personas = ref([])
const cargando = ref(false)
const q = ref('')
const estado = ref(null)

const dialogo = ref(false)
const form = ref({})
const duplicados = ref([])
const forzar = ref(false)
const guardando = ref(false)
const errorForm = ref('')

function ini(p) { return `${(p.nombres || '?')[0]}${(p.apellidos || '')[0] || ''}`.toUpperCase() }
function colorEstado(e) {
  return { activo: 'success', miembro: 'primary', visitante: 'info', nuevo: 'secondary', inactivo: 'error' }[e] || 'secondary'
}

async function cargar() {
  cargando.value = true
  try {
    const params = {}
    if (q.value) params.q = q.value
    if (estado.value) params.estado = estado.value
    const { data } = await api.get('/personas', { params })
    personas.value = data
  } finally { cargando.value = false }
}

function ver(item) { router.push(`/personas/${item.id}`) }

function abrirNueva() {
  form.value = { nombres: '', apellidos: '', telefono: '', correo: '', estado: 'nuevo', notas: '' }
  duplicados.value = []
  forzar.value = false
  errorForm.value = ''
  dialogo.value = true
}

async function guardar() {
  errorForm.value = ''
  guardando.value = true
  try {
    const payload = { ...form.value, forzar: forzar.value }
    if (!payload.telefono) delete payload.telefono
    if (!payload.correo) delete payload.correo
    const { data } = await api.post('/personas', payload)
    dialogo.value = false
    router.push(`/personas/${data.id}`)
  } catch (e) {
    if (e.response?.status === 409) duplicados.value = e.response.data.detail.coincidencias || []
    else if (e.response?.status === 422) errorForm.value = 'Revisa los campos: el nombre es obligatorio y el correo debe ser válido.'
    else errorForm.value = 'No se pudo guardar.'
  } finally { guardando.value = false }
}

onMounted(cargar)
</script>
