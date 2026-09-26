<template>
  <div>
    <div class="d-flex align-center mb-4">
      <div>
        <h2 class="text-h5 font-weight-bold">Personas</h2>
        <p class="text-medium-emphasis mb-0">Registro central de personas</p>
      </div>
      <v-spacer />
      <v-btn v-if="auth.can('personas:crear')" color="primary" prepend-icon="mdi-account-plus"
        @click="abrirNueva">Nueva persona</v-btn>
    </div>

    <v-card elevation="2" class="mb-4">
      <v-card-text>
        <v-row dense>
          <v-col cols="12" md="7">
            <v-text-field v-model="q" label="Buscar por nombre, teléfono o correo"
              prepend-inner-icon="mdi-magnify" clearable hide-details @keyup.enter="cargar" @click:clear="cargar" />
          </v-col>
          <v-col cols="8" md="3">
            <v-select v-model="estado" :items="estados" label="Estado" clearable hide-details @update:model-value="cargar" />
          </v-col>
          <v-col cols="4" md="2">
            <v-btn color="primary" variant="tonal" block height="48" @click="cargar">Filtrar</v-btn>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <v-card elevation="2">
      <v-data-table :headers="headers" :items="personas" :loading="cargando" :items-per-page="15"
        hover @click:row="(_, { item }) => ver(item)">
        <template #item.estado="{ value }">
          <v-chip size="small" :color="colorEstado(value)" variant="tonal">{{ value }}</v-chip>
        </template>
        <template #item.acciones="{ item }">
          <v-btn icon="mdi-tag" size="small" variant="text" @click.stop="$router.push(`/nametag/${item.id}`)" />
        </template>
        <template #no-data><div class="pa-4 text-medium-emphasis">Sin resultados.</div></template>
      </v-data-table>
    </v-card>

    <!-- Diálogo nueva persona -->
    <v-dialog v-model="dialogo" max-width="620" persistent>
      <v-card>
        <v-card-title class="text-h6">Nueva persona</v-card-title>
        <v-divider />
        <v-card-text>
          <v-alert v-if="duplicados.length" type="warning" variant="tonal" class="mb-3">
            <div class="font-weight-bold mb-1">Posible duplicado (RF-006)</div>
            <div v-for="d in duplicados" :key="d.id">
              {{ d.nombre }} — {{ d.telefono || 's/tel' }} · {{ d.correo || 's/correo' }}
            </div>
            <v-checkbox v-model="forzar" label="Crear de todos modos" density="compact" hide-details class="mt-2" />
          </v-alert>
          <v-row dense>
            <v-col cols="12" md="6"><v-text-field v-model="form.nombres" label="Nombres *" /></v-col>
            <v-col cols="12" md="6"><v-text-field v-model="form.apellidos" label="Apellidos" /></v-col>
            <v-col cols="12" md="6"><v-text-field v-model="form.telefono" label="Teléfono" /></v-col>
            <v-col cols="12" md="6"><v-text-field v-model="form.correo" label="Correo" type="email" /></v-col>
            <v-col cols="12" md="6">
              <v-select v-model="form.estado" :items="estados" label="Estado" />
            </v-col>
            <v-col cols="12"><v-textarea v-model="form.notas" label="Notas" rows="2" /></v-col>
          </v-row>
          <v-alert v-if="errorForm" type="error" density="compact" variant="tonal">{{ errorForm }}</v-alert>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="dialogo = false">Cancelar</v-btn>
          <v-btn color="primary" :loading="guardando" @click="guardar">Guardar</v-btn>
        </v-card-actions>
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
  { title: 'Nombre', key: 'nombre_completo', value: (i) => `${i.nombres} ${i.apellidos}` },
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

function colorEstado(e) {
  return { activo: 'success', miembro: 'primary', visitante: 'info', nuevo: 'secondary', inactivo: 'error' }[e] || 'grey'
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
    if (e.response?.status === 409) {
      duplicados.value = e.response.data.detail.coincidencias || []
    } else if (e.response?.status === 422) {
      errorForm.value = 'Revise los campos: el nombre es obligatorio y el correo debe ser válido.'
    } else {
      errorForm.value = 'No se pudo guardar.'
    }
  } finally { guardando.value = false }
}

onMounted(cargar)
</script>
