<template>
  <v-main style="--v-layout-top: 0">
    <div class="d-flex" style="min-height: 100vh">
      <!-- Panel de marca (oculto en móvil) -->
      <div class="brand-panel d-none d-md-flex flex-column justify-space-between pa-10">
        <div class="d-flex align-center">
          <div class="sc-icon-chip" style="background: rgba(255,255,255,0.14); color: #fff">
            <v-icon>mdi-lighthouse</v-icon>
          </div>
          <span class="brand-font ms-3" style="color: #fff; font-size: 1.25rem; font-weight: 700">
            Shoreline City
          </span>
        </div>
        <div>
          <h1 class="brand-font" style="color: #fff; font-size: 2rem; font-weight: 700; line-height: 1.15">
            Un solo lugar para<br />conocer a tu gente.
          </h1>
          <p style="color: rgba(255,255,255,0.78); margin-top: 16px; max-width: 42ch">
            Personas, asistencia, conteos y seguimiento del proceso Únete, centralizados y al día.
          </p>
        </div>
        <div style="color: rgba(255,255,255,0.6); font-size: 0.8rem">
          Universidad Mariano Gálvez de Guatemala
        </div>
      </div>

      <!-- Formulario -->
      <div class="flex-grow-1 d-flex align-center justify-center pa-6" style="background: var(--sc-bg)">
        <div style="width: 100%; max-width: 380px">
          <div class="d-md-none d-flex align-center justify-center mb-6">
            <div class="sc-icon-chip"><v-icon>mdi-lighthouse</v-icon></div>
            <span class="brand-font ms-3" style="font-size: 1.2rem; font-weight: 700; color: var(--sc-ink)">
              Shoreline City
            </span>
          </div>

          <h2 class="brand-font" style="font-size: 1.5rem; font-weight: 700; color: var(--sc-ink)">
            Inicia sesión
          </h2>
          <p class="sc-page-sub mb-6">Accede con tu cuenta para continuar.</p>

          <v-alert v-if="error" type="error" variant="tonal" density="compact" class="mb-4" rounded="lg">
            {{ error }}
          </v-alert>

          <v-form @submit.prevent="entrar">
            <label class="d-block mb-1" style="font-size: 0.82rem; font-weight: 600; color: var(--sc-ink)">
              Correo electrónico
            </label>
            <v-text-field
              v-model="email" type="email" placeholder="tu@correo.org"
              prepend-inner-icon="mdi-email-outline" autofocus class="mb-3" hide-details />

            <label class="d-block mb-1" style="font-size: 0.82rem; font-weight: 600; color: var(--sc-ink)">
              Contraseña
            </label>
            <v-text-field
              v-model="password" :type="ver ? 'text' : 'password'" placeholder="••••••••"
              prepend-inner-icon="mdi-lock-outline"
              :append-inner-icon="ver ? 'mdi-eye-off-outline' : 'mdi-eye-outline'"
              @click:append-inner="ver = !ver" hide-details />

            <v-btn type="submit" color="primary" size="large" block :loading="cargando" class="mt-6">
              Entrar
            </v-btn>
          </v-form>
        </div>
      </div>
    </div>
  </v-main>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/stores/auth'

const email = ref('')
const password = ref('')
const ver = ref(false)
const error = ref('')
const cargando = ref(false)
const auth = useAuth()
const router = useRouter()

async function entrar() {
  error.value = ''
  cargando.value = true
  try {
    await auth.login(email.value, password.value)
    router.push('/')
  } catch (e) {
    error.value = e.response?.data?.detail || 'No pudimos iniciar sesión. Revisa tus datos.'
  } finally {
    cargando.value = false
  }
}
</script>

<style scoped>
.brand-panel {
  width: 44%;
  max-width: 560px;
  background: linear-gradient(160deg, #1e40af 0%, #2563eb 60%, #3b82f6 100%);
}
</style>
