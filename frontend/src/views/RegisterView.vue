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
        <h1>Créer un compte</h1>
        <p class="auth-subtitle">Commencez à gérer vos projets en équipe</p>
      </div>

      <form @submit.prevent="handleSubmit" novalidate>
        <div class="form-group">
          <label class="form-label" for="email">Adresse email</label>
          <input id="email" v-model="form.email" type="email" class="form-input" placeholder="vous@exemple.com" required />
        </div>

        <div class="form-row">
          <div class="form-group">
            <label class="form-label" for="username">Nom d'utilisateur</label>
            <input id="username" v-model="form.username" type="text" class="form-input" placeholder="jdupont" required />
          </div>
          <div class="form-group">
            <label class="form-label" for="full_name">Nom complet <span class="optional">(optionnel)</span></label>
            <input id="full_name" v-model="form.full_name" type="text" class="form-input" placeholder="Jean Dupont" />
          </div>
        </div>

        <div class="form-group">
          <label class="form-label" for="password">Mot de passe</label>
          <input id="password" v-model="form.password" type="password" class="form-input" placeholder="Min. 8 caractères, 1 majuscule, 1 chiffre" required />
        </div>

        <p v-if="error" class="form-error" style="margin-top: 10px;">{{ error }}</p>

        <button
          type="submit"
          class="btn btn-primary"
          style="width: 100%; margin-top: 20px; height: 40px; justify-content: center;"
          :disabled="loading"
        >
          {{ loading ? 'Création en cours…' : 'Créer mon compte' }}
        </button>
      </form>

      <p class="auth-footer">
        Déjà un compte ?
        <RouterLink to="/login">Se connecter</RouterLink>
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

const form = ref({ email: '', username: '', full_name: '', password: '' })
const error = ref('')
const loading = ref(false)

async function handleSubmit() {
  error.value = ''
  loading.value = true
  try {
    await auth.register(form.value.email, form.value.username, form.value.password, form.value.full_name || undefined)
    await auth.login(form.value.email, form.value.password)
    router.push('/')
  } catch (e: any) {
    const detail = e.response?.data?.detail
    error.value = Array.isArray(detail) ? detail[0]?.msg : (detail ?? 'Registration failed.')
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
  max-width: 420px;
  padding: 32px;
}

.auth-header {
  text-align: center;
  margin-bottom: 28px;
}

.auth-header svg { margin-bottom: 12px; }
.auth-header h1 { font-size: 1.25rem; }
.auth-subtitle { margin-top: 4px; font-size: 13px; color: var(--color-text-muted); }

.form-group { margin-top: 14px; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 14px; }
.optional { font-size: 11px; color: var(--color-text-subtle); font-weight: 400; }

.auth-footer { margin-top: 20px; text-align: center; font-size: 13px; color: var(--color-text-muted); }
.auth-footer a { color: var(--color-primary); text-decoration: none; font-weight: 500; }
</style>
