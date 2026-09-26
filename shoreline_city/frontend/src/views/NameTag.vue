<template>
  <div v-if="persona">
    <div class="d-flex align-center mb-4 no-print">
      <v-btn icon="mdi-arrow-left" variant="text" @click="$router.back()" />
      <h2 class="text-h5 font-weight-bold ms-2">Name Tag</h2>
      <v-spacer />
      <v-btn color="primary" prepend-icon="mdi-printer" @click="imprimir">Imprimir (RF-018)</v-btn>
    </div>

    <v-row>
      <v-col cols="12" md="6">
        <div id="tag" class="tag mx-auto">
          <div class="tag-brand">SHORELINE CITY</div>
          <div class="tag-name">{{ persona.nombres }} {{ persona.apellidos }}</div>
          <div class="tag-role">{{ persona.estado }}</div>
          <div class="tag-date">{{ hoy }}</div>
          <div class="tag-id">ID {{ persona.id }}</div>
        </div>
      </v-col>
      <v-col cols="12" md="6" class="no-print">
        <v-alert type="info" variant="tonal" class="mb-3">
          <strong>Impresión Bluetooth (RF-019).</strong> La impresión estándar del navegador cubre RF-018.
          Para impresoras Bluetooth (Brother QL / Zebra) la arquitectura deja un punto de integración
          vía SDK del fabricante, a validar con pruebas reales antes de producción.
        </v-alert>
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
  max-width: 360px; background: #fff; border: 1px solid #ddd; border-radius: 14px;
  padding: 28px; text-align: center; box-shadow: 0 4px 18px rgba(0,0,0,.08);
}
.tag-brand { letter-spacing: 3px; color: #3a86a8; font-size: 12px; font-weight: 600; }
.tag-name { font-size: 30px; font-weight: 800; color: #0b3d5c; margin: 10px 0 4px; line-height: 1.1; }
.tag-role { text-transform: capitalize; color: #555; }
.tag-date { color: #999; font-size: 13px; margin-top: 8px; }
.tag-id { margin-top: 10px; display: inline-block; background: #0b3d5c; color: #fff;
  border-radius: 20px; padding: 2px 12px; font-size: 12px; }
@media print {
  .no-print { display: none !important; }
  .tag { box-shadow: none; border: 1px dashed #999; }
}
</style>
