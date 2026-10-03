<template>
  <div>
    <h1 class="sc-page-title">Conteos</h1>
    <p class="sc-page-sub mb-5">Cuenta la asistencia por categoría; el total se calcula solo.</p>

    <v-row>
      <v-col cols="12" md="6">
        <v-card>
          <div class="sc-card-title">Nuevo conteo</div>
          <div class="pa-5">
            <v-select v-model="servicioId" :items="servicios" item-title="label" item-value="id"
              placeholder="Servicio" prepend-inner-icon="mdi-calendar-blank-outline" class="mb-4" hide-details />

            <div v-for="c in categorias" :key="c.id"
              class="d-flex align-center justify-space-between py-2">
              <span style="color: var(--sc-ink); font-weight: 500">{{ c.nombre }}</span>
              <div class="d-flex align-center" style="gap: 6px">
                <v-btn icon="mdi-minus" size="small" variant="tonal" @click="ajustar(c.id, -1)" />
                <span class="sc-metric-value" style="font-size: 1.2rem; min-width: 36px; text-align: center">
                  {{ valores[c.id] || 0 }}</span>
                <v-btn icon="mdi-plus" size="small" color="primary" @click="ajustar(c.id, 1)" />
              </div>
            </div>

            <div class="d-flex justify-space-between align-center mt-4 pt-4" style="border-top: 1px solid var(--sc-line)">
              <span style="font-weight: 600; color: var(--sc-ink)">Total</span>
              <span class="sc-metric-value" style="font-size: 2rem; color: var(--sc-blue)">{{ total }}</span>
            </div>
            <v-btn color="primary" block class="mt-4" :loading="guardando"
              :disabled="!servicioId || total === 0" @click="guardar">Guardar conteo</v-btn>
          </div>
        </v-card>
      </v-col>

      <v-col cols="12" md="6">
        <v-card>
          <div class="sc-card-title">Conteos recientes</div>
          <v-data-table :headers="headers" :items="conteos" :items-per-page="10" density="comfortable">
            <template #item.total="{ value }">
              <span class="sc-metric-value" style="font-size: 1rem">{{ value }}</span>
            </template>
            <template #item.fecha_hora="{ value }">
              <span class="sc-page-sub">{{ new Date(value).toLocaleString('es-GT') }}</span>
            </template>
            <template #no-data><div class="pa-6 text-center"><p class="sc-page-sub">Sin conteos todavía.</p></div></template>
          </v-data-table>
        </v-card>
      </v-col>
    </v-row>

    <v-snackbar v-model="snack" color="success" timeout="1400">Conteo guardado</v-snackbar>
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
function ajustar(id, delta) { valores.value[id] = Math.max(0, (valores.value[id] || 0) + delta) }

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
    const detalles = categorias.value.filter((c) => valores.value[c.id])
      .map((c) => ({ categoria_id: c.id, cantidad: valores.value[c.id] }))
    await api.post('/conteos', { servicio_id: servicioId.value, detalles })
    valores.value = {}
    snack.value = true
    await cargar()
  } finally { guardando.value = false }
}

onMounted(cargar)
</script>
