<template>
  <div>
    <h2 class="text-h5 font-weight-bold mb-1">Conteo de asistencia</h2>
    <p class="text-medium-emphasis mb-5">Conteo rápido por categorías con total automático (RF-029 a RF-031)</p>

    <v-row>
      <v-col cols="12" md="6">
        <v-card elevation="2">
          <v-card-title class="text-subtitle-1 font-weight-bold">Nuevo conteo</v-card-title>
          <v-divider />
          <v-card-text>
            <v-select v-model="servicioId" :items="servicios" item-title="label" item-value="id"
              label="Servicio" prepend-inner-icon="mdi-calendar" class="mb-2" />

            <div v-for="c in categorias" :key="c.id" class="d-flex align-center justify-space-between mb-3">
              <span class="text-body-1">{{ c.nombre }}</span>
              <div class="d-flex align-center">
                <v-btn icon="mdi-minus" size="small" variant="tonal" @click="ajustar(c.id, -1)" />
                <span class="mx-4 text-h6" style="min-width:32px;text-align:center">{{ valores[c.id] || 0 }}</span>
                <v-btn icon="mdi-plus" size="small" color="primary" @click="ajustar(c.id, 1)" />
              </div>
            </div>

            <v-divider class="my-3" />
            <div class="d-flex justify-space-between align-center">
              <span class="text-subtitle-1 font-weight-bold">Total automático</span>
              <span class="text-h4 font-weight-bold text-primary">{{ total }}</span>
            </div>
            <v-btn color="primary" block class="mt-4" :loading="guardando"
              :disabled="!servicioId || total === 0" @click="guardar">Guardar conteo</v-btn>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="6">
        <v-card elevation="2">
          <v-card-title class="text-subtitle-1 font-weight-bold">Últimos conteos</v-card-title>
          <v-divider />
          <v-data-table :headers="headers" :items="conteos" :items-per-page="10" density="comfortable">
            <template #item.fecha_hora="{ value }">{{ new Date(value).toLocaleString('es-GT') }}</template>
          </v-data-table>
        </v-card>
      </v-col>
    </v-row>

    <v-snackbar v-model="snack" color="success" timeout="1500">Conteo guardado</v-snackbar>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import api from '@/api'

const servicios = ref([])
const categorias = ref([])
const conteos = ref([])
const servicioId = ref(null)
const valores = ref({})
const guardando = ref(false)
const snack = ref(false)

const headers = [
  { title: 'Servicio', key: 'servicio' },
  { title: 'Fecha', key: 'fecha_hora' },
  { title: 'Total', key: 'total', align: 'end' },
]

const total = computed(() => Object.values(valores.value).reduce((a, b) => a + (b || 0), 0))

function ajustar(id, delta) {
  valores.value[id] = Math.max(0, (valores.value[id] || 0) + delta)
}

async function cargar() {
  const [s, c, ct] = await Promise.all([
    api.get('/servicios'), api.get('/conteos/categorias'), api.get('/conteos'),
  ])
  servicios.value = s.data.map((x) => ({ ...x, label: `${x.nombre} (${x.fecha})` }))
  categorias.value = c.data
  conteos.value = ct.data.map((x) => ({ ...x, servicio: x.servicio || `#${x.servicio_id}` }))
}

async function guardar() {
  guardando.value = true
  try {
    const detalles = categorias.value
      .filter((c) => valores.value[c.id])
      .map((c) => ({ categoria_id: c.id, cantidad: valores.value[c.id] }))
    await api.post('/conteos', { servicio_id: servicioId.value, detalles })
    valores.value = {}
    snack.value = true
    await cargar()
  } finally { guardando.value = false }
}

onMounted(cargar)
</script>
