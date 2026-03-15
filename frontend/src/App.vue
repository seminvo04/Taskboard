<template>
  <div id="app">
    <AppNav v-if="auth.isAuthenticated" />
    <main class="main-content">
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import AppNav from '@/components/common/AppNav.vue'

const auth = useAuthStore()
</script>
