<template>
  <v-app>
    <router-view />
  </v-app>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuth } from '@/stores/auth'

const auth = useAuth()
onMounted(() => {
  if (auth.isAuth && !auth.user) auth.fetchMe().catch(() => auth.logout())
})
</script>
