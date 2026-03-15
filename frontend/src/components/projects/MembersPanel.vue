<template>
  <div class="members-panel">
    <!-- Header -->
    <div class="panel-header">
      <h3>Membres <span class="count">{{ memberStore.members.length }}</span></h3>
      <button class="btn btn-primary btn-sm" @click="showInvite = !showInvite">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg>
        Inviter
      </button>
    </div>

    <!-- Invite form -->
    <div v-if="showInvite" class="invite-form">
      <div class="search-row">
        <input
          v-model="searchQuery"
          class="form-input"
          placeholder="Rechercher par nom d'utilisateur…"
          @input="handleSearch"
        />
        <select v-model="selectedRole" class="form-select role-select">
          <option value="member">Membre</option>
          <option value="viewer">Lecteur</option>
          <option value="admin">Admin</option>
        </select>
      </div>

      <!-- Search results -->
      <div v-if="searchResults.length > 0" class="search-results">
        <button
          v-for="user in searchResults"
          :key="user.id"
          class="search-result"
          @click="handleInvite(user)"
        >
          <div class="result-avatar">{{ user.username[0].toUpperCase() }}</div>
          <div class="result-info">
            <span class="result-name">{{ user.full_name ?? user.username }}</span>
            <span class="result-username">@{{ user.username }}</span>
          </div>
          <span class="result-add">Ajouter</span>
        </button>
      </div>

      <p v-if="searchQuery && searchResults.length === 0 && !searching" class="no-results">
        Aucun utilisateur trouvé
      </p>

      <p v-if="inviteError" class="form-error">{{ inviteError }}</p>
    </div>

    <!-- Members list -->
    <div v-if="memberStore.loading" class="members-loading">Chargement…</div>

    <div v-else class="members-list">
      <div v-for="member in memberStore.members" :key="member.id" class="member-row">
        <div class="member-avatar">{{ member.user.username[0].toUpperCase() }}</div>
        <div class="member-info">
          <span class="member-name">{{ member.user.full_name ?? member.user.username }}</span>
          <span class="member-username">@{{ member.user.username }}</span>
        </div>
        <div class="member-actions">
          <select
            :value="member.role"
            class="role-badge"
            :class="`role-${member.role}`"
            :disabled="member.user.id === currentUserId || member.user.id === props.ownerId"
            @change="handleRoleChange(member.user.id, ($event.target as HTMLSelectElement).value)"
            >
            <option value="admin">Admin</option>
            <option value="member">Membre</option>
            <option value="viewer">Lecteur</option>
            </select>

            <button
            v-if="member.user.id !== currentUserId && member.user.id !== props.ownerId"
            class="btn-remove"
            title="Retirer du projet"
            @click="handleRemove(member.user.id)"
            >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M18 6L6 18M6 6l12 12"/></svg>
            </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useMemberStore } from '@/stores/members'
import { useAuthStore } from '@/stores/auth'

const props = defineProps<{ projectId: string; ownerId: string }>()

const memberStore = useMemberStore()
const auth = useAuthStore()
const currentUserId = auth.user?.id

const showInvite = ref(false)
const searchQuery = ref('')
const searchResults = ref<any[]>([])
const selectedRole = ref('member')
const searching = ref(false)
const inviteError = ref('')

let searchTimeout: ReturnType<typeof setTimeout> | null = null

onMounted(() => memberStore.fetchForProject(props.projectId))

function handleSearch() {
  inviteError.value = ''
  if (!searchQuery.value.trim()) {
    searchResults.value = []
    return
  }
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(async () => {
    searching.value = true
    try {
      searchResults.value = await memberStore.searchUser(searchQuery.value.trim())
    } finally {
      searching.value = false
    }
  }, 300)
}

async function handleInvite(user: any) {
  inviteError.value = ''
  try {
    await memberStore.addMember(props.projectId, user.id, selectedRole.value)
    searchQuery.value = ''
    searchResults.value = []
    showInvite.value = false
  } catch (e: any) {
    inviteError.value = e.response?.data?.detail ?? 'Impossible d\'ajouter ce membre.'
  }
}

async function handleRoleChange(userId: string, role: string) {
  await memberStore.updateRole(props.projectId, userId, role)
}

async function handleRemove(userId: string) {
  await memberStore.removeMember(props.projectId, userId)
}
</script>

<style scoped>
.members-panel {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 18px;
  border-bottom: 1px solid var(--color-border);
}

.panel-header h3 {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.count {
  font-size: 11px;
  font-weight: 600;
  color: var(--color-text-muted);
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: 99px;
  padding: 1px 7px;
}

.invite-form {
  padding: 14px 18px;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-bg);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.search-row {
  display: flex;
  gap: 8px;
}

.role-select { width: 110px; flex-shrink: 0; }

.search-results {
  display: flex;
  flex-direction: column;
  gap: 4px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.search-result {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  background: transparent;
  border: none;
  cursor: pointer;
  text-align: left;
  transition: background 0.12s;
  width: 100%;
}

.search-result:hover { background: var(--color-bg); }

.result-avatar {
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
  flex-shrink: 0;
}

.result-info { flex: 1; display: flex; flex-direction: column; }
.result-name { font-size: 13px; font-weight: 500; color: var(--color-text); }
.result-username { font-size: 11px; color: var(--color-text-muted); }
.result-add { font-size: 12px; color: var(--color-primary); font-weight: 500; }

.no-results { font-size: 13px; color: var(--color-text-muted); text-align: center; padding: 8px 0; }

.members-loading { padding: 20px; text-align: center; font-size: 13px; color: var(--color-text-muted); }

.members-list { display: flex; flex-direction: column; }

.member-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 18px;
  border-bottom: 1px solid var(--color-border);
  transition: background 0.12s;
}

.member-row:last-child { border-bottom: none; }
.member-row:hover { background: var(--color-bg); }

.member-avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-primary-light), var(--color-primary-muted));
  color: var(--color-primary);
  font-size: 13px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.member-info { flex: 1; display: flex; flex-direction: column; gap: 1px; }
.member-name { font-size: 13px; font-weight: 500; color: var(--color-text); }
.member-username { font-size: 11px; color: var(--color-text-muted); }

.member-actions { display: flex; align-items: center; gap: 8px; }

.role-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 99px;
  border: 1px solid transparent;
  cursor: pointer;
  outline: none;
  appearance: none;
  -webkit-appearance: none;
}

.role-badge:disabled { cursor: default; opacity: 0.7; }

.role-admin   { background: #eef2ff; color: #4338ca; border-color: #c7d2fe; }
.role-member  { background: #f0fdf4; color: #166534; border-color: #bbf7d0; }
.role-viewer  { background: #f8fafc; color: #475569; border-color: #e2e8f0; }

.btn-remove {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  border: none;
  background: transparent;
  border-radius: var(--radius-sm);
  color: var(--color-text-subtle);
  cursor: pointer;
  transition: background 0.12s, color 0.12s;
}

.btn-remove:hover {
  background: var(--color-danger-light);
  color: var(--color-danger);
}
</style>