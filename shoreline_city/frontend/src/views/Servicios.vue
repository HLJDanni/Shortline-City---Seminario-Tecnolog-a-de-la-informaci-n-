<template>
  <div>
    <h2 class="text-h5 font-weight-bold mb-1">Servicios</h2>
    <p class="text-medium-emphasis mb-5">Programación de servicios y eventos (RF-011 / RF-034)</p>

    <v-row>
      <v-col cols="12" md="4">
        <v-card elevation="2">
          <v-card-title class="text-subtitle-1 font-weight-bold">Nuevo servicio</v-card-title>
          <v-divider />
          <v-card-text>
            <v-text-field v-model="form.nombre" label="Nombre" />
            <v-text-field v-model="form.fecha" label="Fecha" type="date" />
            <v-text-field v-model="form.ubicacion" label="Ubicación" />
            <v-select v-model="form.tipo" :items="['regular', 'especial']" label="Tipo" />
            <v-btn color="primary" block :loading="guardando" @click="guardar">Crear</v-btn>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="8">
        <v-card elevation="2">
          <v-data-table :headers="headers" :items="servicios" :items-per-page="10">
            <template #item.tipo="{ value }">
              <v-chip size="small" :color="value === 'especial' ? 'accent' : 'secondary'" variant="tonal">{{ value }}</v-chip>
            </template>
            <template #item.acciones="{ item }">
              <v-btn size="small" variant="tonal" color="primary" prepend-icon="mdi-door-open"
                @click="$router.push({ path: '/checkin' })">Check-in</v-btn>
            </template>
          </v-data-table>
        </v-card>
      </v-col>
    </v-row>
    <v-snackbar v-model="snack" color="success" timeout="1500">Servicio creado</v-snackbar>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import api from '@/api'

const hoy = new Date().toISOString().slice(0, 10)
const servicios = ref([])
const form = ref({ nombre: '', fecha: hoy, ubicacion: '', tipo: 'regular' })
const guardando = ref(false)
const snack = ref(false)

const headers = [
  { title: 'Servicio', key: 'nombre' },
  { title: 'Fecha', key: 'fecha' },
  { title: 'Ubicación', key: 'ubicacion' },
  { title: 'Tipo', key: 'tipo' },
  { title: '', key: 'acciones', sortable: false, align: 'end' },
]

async function cargar() {
  const { data } = await api.get('/servicios')
  servicios.value = data
}

async function guardar() {
  guardando.value = true
  try {
    await api.post('/servicios', { ...form.value, especial: form.value.tipo === 'especial' })
    form.value = { nombre: '', fecha: hoy, ubicacion: '', tipo: 'regular' }
    snack.value = true
    await cargar()
  } finally { guardando.value = false }
}

onMounted(cargar)
</script>
