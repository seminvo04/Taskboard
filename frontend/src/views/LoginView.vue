<template>
  <div class="auth-page">
    <div class="auth-card card">
      <div class="auth-header">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect x="3" y="3" width="7" height="7" rx="1"/>
          <rect x="14" y="3" width="7" height="7" rx="1"/>
          <rect x="3" y="14" width="7" height="7" rx="1"/>
          <rect x="14" y="14" width="7" height="7" rx="1"/>
        </svg>
        <h1>TaskBoard</h1>
        <p class="auth-subtitle">Connectez-vous à votre espace de travail</p>
      </div>

      <form @submit.prevent="handleSubmit" novalidate>
        <div class="form-group">
          <label class="form-label" for="email">Adresse email</label>
          <input
            id="email"
            v-model="form.email"
            type="email"
            class="form-input"
            placeholder="vous@exemple.com"
            autocomplete="email"
            required
          />
        </div>

        <div class="form-group" style="margin-top: 14px;">
          <label class="form-label" for="password">Mot de passe</label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            class="form-input"
            placeholder="••••••••"
            autocomplete="current-password"
            required
          />
        </div>

        <p v-if="error" class="form-error" style="margin-top: 10px;">{{ error }}</p>

        <button
          type="submit"
          class="btn btn-primary"
          style="width: 100%; margin-top: 20px; height: 40px; justify-content: center;"
          :disabled="loading"
        >
          {{ loading ? 'Connexion en cours…' : 'Se connecter' }}
        </button>
      </form>

      <p class="auth-footer">
        Pas encore de compte ?
        <RouterLink to="/register">En créer un</RouterLink>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

const form = ref({ email: '', password: '' })
const error = ref('')
const loading = ref(false)

async function handleSubmit() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(form.value.email, form.value.password)
    router.push('/')
  } catch (e: any) {
    error.value = e.response?.data?.detail ?? 'Invalid credentials. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.auth-card {
  width: 100%;
  max-width: 380px;
  padding: 32px;
}

.auth-header {
  text-align: center;
  margin-bottom: 28px;
}

.auth-header svg {
  margin-bottom: 12px;
}

.auth-header h1 {
  font-size: 1.35rem;
}

.auth-subtitle {
  margin-top: 4px;
  font-size: 13px;
  color: var(--color-text-muted);
}

.auth-footer {
  margin-top: 20px;
  text-align: center;
  font-size: 13px;
  color: var(--color-text-muted);
}

.auth-footer a {
  color: var(--color-primary);
  text-decoration: none;
  font-weight: 500;
}
</style>
