<template>
  <div class="project-view">
    <div v-if="loading" class="loading-state">Chargement du projet…</div>

    <template v-else-if="project">
      <!-- Header -->
      <div class="project-header">
        <div class="header-left">
          <RouterLink to="/" class="back-link">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5M12 5l-7 7 7 7"/></svg>
            Projets
          </RouterLink>
          <div class="header-title-row">
            <h1 class="project-title">{{ project.name }}</h1>
            <p v-if="project.description" class="project-desc">{{ project.description }}</p>
          </div>
        </div>

        <div class="header-actions">
          <div class="tab-group">
            <button
              :class="['tab-btn', activeTab === 'board' ? 'active' : '']"
              @click="activeTab = 'board'"
            >
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>
              Tableau
            </button>
            <button
              :class="['tab-btn', activeTab === 'members' ? 'active' : '']"
              @click="activeTab = 'members'"
            >
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="9" cy="7" r="4"/><path d="M3 21v-2a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v2"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/><path d="M21 21v-2a4 4 0 0 0-3-3.85"/></svg>
              Membres
              <span class="tab-count">{{ memberStore.members.length }}</span>
            </button>
          </div>

          <span class="ws-indicator" :class="wsConnected ? 'connected' : 'disconnected'">
            <span class="ws-dot" />
            {{ wsConnected ? 'En direct' : 'Hors ligne' }}
          </span>

          <button v-if="activeTab === 'board'" class="btn btn-primary" @click="openCreate('todo')">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg>
            Ajouter une tâche
          </button>
        </div>
      </div>

      <!-- Board tab -->
      <div v-if="activeTab === 'board'" class="kanban-wrapper">
        <KanbanBoard
          :project-id="project.id"
          @add="openCreate"
          @edit="openEdit"
        />
      </div>

      <!-- Members tab -->
      <div v-if="activeTab === 'members'" class="members-wrapper">
        <MembersPanel :project-id="project.id" :owner-id="project.owner_id" />
      </div>
    </template>

    <!-- Task modal -->
    <TaskModal
      v-if="modalOpen"
      :project-id="route.params.id as string"
      :task="editingTask"
      :initial-status="newTaskStatus"
      @close="modalOpen = false"
      @saved="modalOpen = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useProjectStore } from '@/stores/projects'
import { useTaskStore, type Task, type TaskStatus } from '@/stores/tasks'
import { useMemberStore } from '@/stores/members'
import { ProjectSocket } from '@/services/websocket'
import KanbanBoard from '@/components/tasks/KanbanBoard.vue'
import TaskModal from '@/components/tasks/TaskModal.vue'
import MembersPanel from '@/components/projects/MembersPanel.vue'
import type { Project } from '@/stores/projects'

const route = useRoute()
const projectStore = useProjectStore()
const taskStore = useTaskStore()
const memberStore = useMemberStore()

const project = ref<Project | null>(null)
const loading = ref(true)
const modalOpen = ref(false)
const editingTask = ref<Task | null>(null)
const newTaskStatus = ref<TaskStatus>('todo')
const wsConnected = ref(false)
const activeTab = ref<'board' | 'members'>('board')

let socket: ProjectSocket | null = null

onMounted(async () => {
  const id = route.params.id as string
  try {
    project.value = await projectStore.fetchOne(id)
    await taskStore.fetchForProject(id)
    await memberStore.fetchForProject(id)
  } finally {
    loading.value = false
  }

  socket = new ProjectSocket(id)
  socket.on('connected', () => { wsConnected.value = true })
  socket.on('task.created', (data) => taskStore.applyEvent('task.created', data as Task))
  socket.on('task.updated', (data) => taskStore.applyEvent('task.updated', data as Task))
  socket.on('task.deleted', (data) => taskStore.applyEvent('task.deleted', data as { id: string }))
  socket.connect()
})

onUnmounted(() => {
  socket?.disconnect()
  memberStore.reset()
})

function openCreate(status: TaskStatus) {
  editingTask.value = null
  newTaskStatus.value = status
  modalOpen.value = true
}

function openEdit(task: Task) {
  editingTask.value = task
  modalOpen.value = true
}
</script>

<style scoped>
.project-view {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 56px);
  overflow: hidden;
}

.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: var(--color-text-muted);
  font-size: 14px;
}

.project-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 24px;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface);
  flex-shrink: 0;
  gap: 16px;
}

.header-left { display: flex; flex-direction: column; gap: 2px; min-width: 0; }

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: var(--color-text-subtle);
  text-decoration: none;
  margin-bottom: 2px;
  transition: color 0.1s;
  width: fit-content;
}

.back-link:hover { color: var(--color-primary); }

.header-title-row { display: flex; align-items: baseline; gap: 12px; }
.project-title { font-size: 1.1rem; letter-spacing: -0.02em; white-space: nowrap; }
.project-desc { font-size: 13px; color: var(--color-text-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.header-actions { display: flex; align-items: center; gap: 10px; flex-shrink: 0; }

.tab-group {
  display: flex;
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 3px;
  gap: 2px;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 5px 12px;
  border: none;
  background: transparent;
  border-radius: var(--radius-sm);
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-muted);
  cursor: pointer;
  transition: all 0.15s;
}

.tab-btn:hover { color: var(--color-text); background: var(--color-surface); }

.tab-btn.active {
  background: var(--color-surface);
  color: var(--color-text);
  box-shadow: var(--shadow-xs);
}

.tab-count {
  font-size: 11px;
  font-weight: 600;
  color: var(--color-text-muted);
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: 99px;
  padding: 0px 6px;
}

.ws-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--color-text-muted);
  background: var(--color-bg);
  padding: 5px 10px;
  border-radius: 99px;
  border: 1px solid var(--color-border);
}

.ws-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--color-text-subtle);
}

.ws-indicator.connected .ws-dot {
  background: var(--color-success);
  box-shadow: 0 0 0 3px var(--color-success-light);
}

.kanban-wrapper {
  flex: 1;
  overflow: auto;
  padding: 20px 24px;
}

.members-wrapper {
  flex: 1;
  overflow: auto;
  padding: 24px;
  max-width: 680px;
}
</style>