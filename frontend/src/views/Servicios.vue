<template>
  <div>
    <h1 class="sc-page-title">Servicios</h1>
    <p class="sc-page-sub mb-5">Programa los servicios y eventos de la iglesia.</p>

    <v-row>
      <v-col cols="12" md="4">
        <v-card>
          <div class="sc-card-title">Nuevo servicio</div>
          <div class="pa-5">
            <v-text-field v-model="form.nombre" label="Nombre" class="mb-1" />
            <v-text-field v-model="form.fecha" label="Fecha" type="date" class="mb-1" />
            <v-text-field v-model="form.ubicacion" label="Ubicación" class="mb-1" />
            <v-select v-model="form.tipo" :items="['regular', 'especial']" label="Tipo" class="mb-2" />
            <v-btn color="primary" block :loading="guardando" @click="guardar">Crear servicio</v-btn>
          </div>
        </v-card>
      </v-col>

      <v-col cols="12" md="8">
        <v-card>
          <div class="sc-card-title">Programación</div>
          <v-data-table :headers="headers" :items="servicios" :items-per-page="10">
            <template #item.nombre="{ item }">
              <span style="font-weight: 600; color: var(--sc-ink)">{{ item.nombre }}</span>
            </template>
            <template #item.tipo="{ value }">
              <v-chip size="small" variant="tonal" :color="value === 'especial' ? 'info' : 'secondary'">{{ value }}</v-chip>
            </template>
            <template #item.acciones="{ item }">
              <v-btn size="small" variant="tonal" color="primary" prepend-icon="mdi-login-variant"
                @click="$router.push('/checkin')">Check-in</v-btn>
            </template>
            <template #no-data><div class="pa-6 text-center"><p class="sc-page-sub">No hay servicios programados.</p></div></template>
          </v-data-table>
        </v-card>
      </v-col>
    </v-row>
    <v-snackbar v-model="snack" color="success" timeout="1400">Servicio creado</v-snackbar>
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
