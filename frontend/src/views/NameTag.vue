<template>
  <div v-if="persona">
    <div class="d-flex align-center mb-5 no-print" style="gap: 12px">
      <v-btn icon="mdi-arrow-left" variant="text" @click="$router.back()" />
      <div>
        <h1 class="sc-page-title" style="line-height: 1.1">Name Tag</h1>
        <p class="sc-page-sub">Vista previa e impresión del gafete.</p>
      </div>
      <v-spacer />
      <v-btn color="primary" prepend-icon="mdi-printer-outline" @click="imprimir">Imprimir</v-btn>
    </div>

    <v-row>
      <v-col cols="12" md="6">
        <div id="tag" class="tag mx-auto">
          <div class="tag-brand brand-font">SHORELINE CITY</div>
          <div class="tag-name brand-font">{{ persona.nombres }}<br />{{ persona.apellidos }}</div>
          <div class="tag-role">{{ persona.estado }}</div>
          <div class="tag-id">ID {{ persona.id }} · {{ hoy }}</div>
        </div>
      </v-col>
      <v-col cols="12" md="6" class="no-print">
        <v-card class="pa-5">
          <div class="d-flex">
            <v-icon color="primary" class="me-3">mdi-bluetooth</v-icon>
            <div>
              <div style="font-weight: 600; color: var(--sc-ink)">Impresión Bluetooth</div>
              <p class="sc-page-sub mt-1" style="max-width: 46ch">
                La impresión del navegador cubre el gafete estándar. Para impresoras Bluetooth
                (Brother QL, Zebra) la arquitectura deja un punto de integración vía el SDK del
                fabricante, por validar con pruebas reales antes de producción.
              </p>
            </div>
          </div>
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
const hoy = new Date().toLocaleDateString('es-GT')

function imprimir() { window.print() }

onMounted(async () => {
  const { data } = await api.get(`/personas/${route.params.id}`)
  persona.value = data
})
</script>

<style scoped>
.tag {
  max-width: 380px; background: #fff; border: 1px solid var(--sc-line); border-radius: 16px;
  padding: 36px 28px; text-align: center; box-shadow: 0 2px 14px rgba(15, 27, 45, 0.06);
}
.tag-brand { letter-spacing: 2px; color: var(--sc-blue); font-size: 12px; font-weight: 700; }
.tag-name { font-size: 2rem; font-weight: 800; color: var(--sc-ink); margin: 14px 0 8px; line-height: 1.08; }
.tag-role { text-transform: capitalize; color: var(--sc-muted); font-weight: 500; }
.tag-id {
  margin-top: 16px; display: inline-block; background: #eef3ff; color: var(--sc-blue-ink);
  border-radius: 999px; padding: 4px 14px; font-size: 12px; font-weight: 600;
}
@media print {
  .no-print { display: none !important; }
  .tag { box-shadow: none; border: 1px dashed #94a3b8; }
}
</style>
