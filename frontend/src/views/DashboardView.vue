<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <div>
        <h1>Projects</h1>
        <p class="subtitle">{{ projects.projects.length }} project{{ projects.projects.length !== 1 ? 's' : '' }}</p>
      </div>
      <button class="btn btn-primary" @click="showCreate = true">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg>
        Nouveau projet
      </button>
    </div>

<div v-if="projects.loading" class="loading-state">Chargement des projets…</div>

    <div v-else-if="projects.projects.length === 0" class="empty-state">
      <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="var(--color-text-subtle)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
        <rect x="3" y="3" width="7" height="7" rx="1"/>
        <rect x="14" y="3" width="7" height="7" rx="1"/>
        <rect x="3" y="14" width="7" height="7" rx="1"/>
        <rect x="14" y="14" width="7" height="7" rx="1"/>
      </svg>
      <p>Aucun projet pour l'instant. Créez-en un pour commencer.</p>
    </div>

    <div v-else class="project-grid">
      <RouterLink
        v-for="project in projects.projects"
        :key="project.id"
        :to="`/projects/${project.id}`"
        class="project-card card"
      >
        <div class="project-card-header">
          <span class="project-avatar">{{ project.name[0].toUpperCase() }}</span>
          <span class="project-member-count">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/></svg>
            {{ project.member_count }}
          </span>
        </div>
        <h3 class="project-name">{{ project.name }}</h3>
        <p v-if="project.description" class="project-desc">{{ project.description }}</p>
        <p class="project-date">Créé le {{ formatDate(project.created_at) }}</p>
      </RouterLink>
    </div>

    <!-- modal -->
    <Teleport to="body">
      <div v-if="showCreate" class="modal-backdrop" @click.self="showCreate = false">
        <div class="modal card">
          <h2>Nouveau projet</h2>
          <form @submit.prevent="handleCreate" style="margin-top: 20px;">
            <div class="form-group">
              <label class="form-label">Nom <span style="color: var(--color-danger)">*</span></label>
              <input v-model="newProject.name" class="form-input" placeholder="ex : API Backend" required autofocus />
            </div>
            <div class="form-group" style="margin-top: 14px;">
              <label class="form-label">Description <span style="font-size: 11px; color: var(--color-text-subtle); font-weight: 400;">(optional)</span></label>
              <textarea v-model="newProject.description" class="form-textarea" placeholder="À quoi sert ce projet ?" />
            </div>
            <p v-if="createError" class="form-error" style="margin-top: 8px;">{{ createError }}</p>
            <div class="modal-actions">
              <button type="button" class="btn btn-ghost" @click="showCreate = false">Annuler</button>
              <button type="submit" class="btn btn-primary" :disabled="!newProject.name.trim() || creating">
                {{ creating ? 'Création…' : 'Créer le projet' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useProjectStore } from '@/stores/projects'

const projects = useProjectStore()

const showCreate = ref(false)
const creating = ref(false)
const createError = ref('')
const newProject = ref({ name: '', description: '' })

onMounted(() => projects.fetchAll())

async function handleCreate() {
  createError.value = ''
  creating.value = true
  try {
    await projects.create(newProject.value.name, newProject.value.description || undefined)
    showCreate.value = false
    newProject.value = { name: '', description: '' }
  } catch (e: any) {
    createError.value = e.response?.data?.detail ?? 'Failed to create project.'
  } finally {
    creating.value = false
  }
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })
}
</script>

<style scoped>
.dashboard {
  max-width: 1280px;
  margin: 0 auto;
  padding: 36px 24px;
}

.dashboard-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 32px;
}

.dashboard-header h1 { color: var(--color-text); }
.subtitle { margin-top: 3px; font-size: 13px; color: var(--color-text-muted); }

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  padding: 80px 24px;
  color: var(--color-text-muted);
  font-size: 14px;
}

.project-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 18px;
}

.project-card {
  padding: 22px;
  text-decoration: none;
  color: var(--color-text);
  transition: box-shadow 0.2s, transform 0.2s;
  display: flex;
  flex-direction: column;
  gap: 10px;
  cursor: pointer;
}

.project-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.project-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 4px;
}

.project-avatar {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, var(--color-primary-light), var(--color-primary-muted));
  color: var(--color-primary);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 16px;
}

.project-member-count {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: var(--color-text-subtle);
  background: var(--color-bg);
  padding: 3px 8px;
  border-radius: 99px;
  border: 1px solid var(--color-border);
}

.project-name { font-size: 15px; font-weight: 600; letter-spacing: -0.01em; }
.project-desc {
  font-size: 13px;
  color: var(--color-text-muted);
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.project-date {
  font-size: 12px;
  color: var(--color-text-subtle);
  margin-top: auto;
  padding-top: 8px;
  border-top: 1px solid var(--color-border);
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(16, 24, 40, 0.4);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 24px;
}

.modal {
  width: 100%;
  max-width: 460px;
  padding: 28px;
  box-shadow: var(--shadow-lg);
}

.modal h2 { font-size: 1.1rem; margin-bottom: 4px; }

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 24px;
}
</style>
