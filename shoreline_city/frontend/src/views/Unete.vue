<template>
  <div>
    <h2 class="text-h5 font-weight-bold mb-1">Proceso Únete</h2>
    <p class="text-medium-emphasis mb-5">Cohortes, inscripciones y seguimiento (RF-021 a RF-028)</p>

    <v-row>
      <v-col v-for="c in cohortes" :key="c.id" cols="12" md="6" lg="4">
        <v-card elevation="2" height="100%">
          <v-card-item>
            <template #prepend><v-avatar color="primary" variant="tonal"><v-icon>mdi-sitemap</v-icon></v-avatar></template>
            <v-card-title>{{ c.nombre }}</v-card-title>
            <v-card-subtitle>{{ c.horario || 'Sin horario' }}</v-card-subtitle>
          </v-card-item>
          <v-card-text>
            <div class="d-flex justify-space-between mb-1">
              <span class="text-medium-emphasis">Inicio</span><span>{{ c.fecha_inicio || '—' }}</span>
            </div>
            <div class="d-flex justify-space-between mb-1">
              <span class="text-medium-emphasis">Estado</span>
              <v-chip size="x-small" color="info" variant="tonal">{{ c.estado }}</v-chip>
            </div>
            <div class="d-flex justify-space-between">
              <span class="text-medium-emphasis">Inscritos</span>
              <strong>{{ c.inscritos }}</strong>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col v-if="!cohortes.length" cols="12">
        <v-alert type="info" variant="tonal">No hay cohortes creadas.</v-alert>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import api from '@/api'

const cohortes = ref([])
onMounted(async () => {
  const { data } = await api.get('/unete/cohortes')
  cohortes.value = data
})
</script>
