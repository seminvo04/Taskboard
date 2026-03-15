<template>
  <nav class="nav">
    <div class="nav-inner">
      <RouterLink to="/" class="nav-logo">
        <div class="nav-logo-icon">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="3" width="7" height="7" rx="1.5"/>
            <rect x="14" y="3" width="7" height="7" rx="1.5"/>
            <rect x="3" y="14" width="7" height="7" rx="1.5"/>
            <rect x="14" y="14" width="7" height="7" rx="1.5"/>
          </svg>
        </div>
        TaskBoard
      </RouterLink>

      <div class="nav-right">
        <div class="nav-user">
          <div class="nav-avatar">{{ auth.user?.username?.[0]?.toUpperCase() }}</div>
          <span class="nav-username">{{ auth.user?.full_name ?? auth.user?.username }}</span>
        </div>
        <button class="btn btn-ghost btn-sm" @click="handleLogout">Se déconnecter</button>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.nav {
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  position: sticky;
  top: 0;
  z-index: 50;
}

.nav-inner {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 24px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.nav-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 700;
  font-size: 15px;
  color: var(--color-text);
  text-decoration: none;
  letter-spacing: -0.02em;
}

.nav-logo-icon {
  width: 30px;
  height: 30px;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-hover));
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 4px rgba(99, 102, 241, 0.3);
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.nav-user {
  display: flex;
  align-items: center;
  gap: 9px;
}

.nav-avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-primary-light), var(--color-primary-muted));
  color: var(--color-primary);
  font-size: 12px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-username {
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-muted);
}
</style>