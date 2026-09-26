<template>
  <div class="login-bg d-flex align-center justify-center">
    <v-card class="pa-2" width="410" elevation="10" rounded="xl">
      <v-card-text class="pa-6">
        <div class="text-center mb-6">
          <v-avatar color="primary" size="64" class="mb-3">
            <v-icon size="36">mdi-lighthouse-on</v-icon>
          </v-avatar>
          <h2 class="text-h5 font-weight-bold">Shoreline City</h2>
          <p class="text-medium-emphasis">Gestión centralizada de personas</p>
        </div>

        <v-alert v-if="error" type="error" density="compact" variant="tonal" class="mb-4">
          {{ error }}
        </v-alert>

        <v-form @submit.prevent="entrar">
          <v-text-field
            v-model="email" label="Correo electrónico" type="email"
            prepend-inner-icon="mdi-email-outline" autofocus class="mb-2" />
          <v-text-field
            v-model="password" label="Contraseña"
            :type="ver ? 'text' : 'password'"
            prepend-inner-icon="mdi-lock-outline"
            :append-inner-icon="ver ? 'mdi-eye-off' : 'mdi-eye'"
            @click:append-inner="ver = !ver" />
          <v-btn
            type="submit" color="primary" size="large" block :loading="cargando"
            class="mt-4">
            Ingresar
          </v-btn>
        </v-form>
      </v-card-text>
    </v-card>
  </div>
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
    error.value = e.response?.data?.detail || 'No se pudo iniciar sesión.'
  } finally {
    cargando.value = false
  }
}
</script>

<style scoped>
.login-bg {
  min-height: 100vh;
  background: linear-gradient(135deg, #0b3d5c 0%, #3a86a8 100%);
}
</style>
