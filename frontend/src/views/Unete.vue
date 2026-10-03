<template>
  <div>
    <h1 class="sc-page-title">Proceso Únete</h1>
    <p class="sc-page-sub mb-5">Cohortes, inscripciones y seguimiento de cada participante.</p>

    <v-row>
      <v-col v-for="c in cohortes" :key="c.id" cols="12" sm="6" lg="4">
        <v-card class="pa-5 h-100">
          <div class="d-flex align-center justify-space-between mb-3">
            <div class="sc-icon-chip" style="width: 40px; height: 40px; border-radius: 10px">
              <v-icon size="20">mdi-account-group-outline</v-icon>
            </div>
            <v-chip size="small" variant="tonal" :color="colorEstado(c.estado)">{{ c.estado }}</v-chip>
          </div>
          <div class="brand-font" style="font-weight: 700; font-size: 1.05rem; color: var(--sc-ink)">{{ c.nombre }}</div>
          <div class="sc-page-sub mb-4">{{ c.horario || 'Horario por definir' }}</div>

          <div class="d-flex align-center justify-space-between py-2" style="border-top: 1px solid var(--sc-line)">
            <span class="sc-page-sub">Inicio</span>
            <span style="color: var(--sc-ink)">{{ c.fecha_inicio || '—' }}</span>
          </div>
          <div class="d-flex align-center justify-space-between py-2" style="border-top: 1px solid var(--sc-line)">
            <span class="sc-page-sub">Inscritos</span>
            <span class="sc-metric-value" style="font-size: 1.1rem">{{ c.inscritos }}</span>
          </div>
        </v-card>
      </v-col>

      <v-col v-if="!cohortes.length" cols="12">
        <v-card class="pa-10 text-center">
          <v-icon size="42" color="#cbd5e1">mdi-account-group-outline</v-icon>
          <p class="sc-page-sub mt-2">Aún no hay cohortes. Crea una para empezar a inscribir personas.</p>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import api from '@/api'

const cohortes = ref([])
function colorEstado(e) {
  return { abierta: 'info', en_curso: 'primary', finalizada: 'success', cancelada: 'error' }[e] || 'secondary'
}
onMounted(async () => {
  const { data } = await api.get('/unete/cohortes')
  cohortes.value = data
})
</script>
