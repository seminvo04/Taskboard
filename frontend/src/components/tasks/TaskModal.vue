<template>
  <Teleport to="body">
    <div class="modal-backdrop" @click.self="$emit('close')">
      <div class="modal card">
        <div class="modal-header">
          <h2>{{ task ? 'Modifier la tâche' : 'Nouvelle tâche' }}</h2>
          <button class="btn-icon" @click="$emit('close')">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M18 6L6 18M6 6l12 12"/></svg>
          </button>
        </div>

        <form @submit.prevent="handleSubmit" style="margin-top: 20px;">
          <div class="form-group">
            <label class="form-label">Titre <span style="color: var(--color-danger)">*</span></label>
            <input v-model="form.title" class="form-input" placeholder="Que faut-il faire ?" required autofocus />
          </div>

          <div class="form-group" style="margin-top: 14px;">
            <label class="form-label">Description</label>
            <textarea v-model="form.description" class="form-textarea" placeholder="Ajoutez du contexte…" />
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Status</label>
              <select v-model="form.status" class="form-select">
                <option v-for="s in STATUSES" :key="s.key" :value="s.key">{{ s.label }}</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Priorité</label>
              <select v-model="form.priority" class="form-select">
                <option value="low">Faible</option>
                <option value="medium">Moyenne</option>
                <option value="high">Haute</option>
                <option value="critical">Critique</option>
              </select>
            </div>
          </div>

          <div class="form-group" style="margin-top: 14px;">
            <label class="form-label">Date d'échéance</label>
            <input v-model="form.due_date" type="date" class="form-input" />
          </div>

          <div class="form-group" style="margin-top: 14px;">
            <label class="form-label">Assigné à</label>
            <select v-model="form.assignee_id" class="form-select">
              <option :value="undefined">Non assigné</option>
              <option
                v-for="member in memberStore.members"
                :key="member.user.id"
                :value="member.user.id"
              >
                {{ member.user.full_name ?? member.user.username }}
              </option>
            </select>
          </div>

          <p v-if="error" class="form-error" style="margin-top: 10px;">{{ error }}</p>

          <div class="modal-footer">
            <button
              v-if="task"
              type="button"
              class="btn btn-danger btn-sm"
              :disabled="saving"
              @click="handleDelete"
            >
              Supprimer
            </button>
            <div style="flex: 1;" />
            <button type="button" class="btn btn-ghost" @click="$emit('close')">Annuler</button>
            <button type="submit" class="btn btn-primary" :disabled="!form.title.trim() || saving">
              {{ saving ? 'Enregistrement…' : (task ? 'Enregistrer' : 'Créer la tâche') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useTaskStore, STATUSES, type Task, type TaskStatus } from '@/stores/tasks'
import { useMemberStore } from '@/stores/members'

const memberStore = useMemberStore()

const props = defineProps<{
  projectId: string
  task?: Task | null
  initialStatus?: TaskStatus
}>()

const emit = defineEmits<{
  close: []
  saved: [task: Task]
}>()

const taskStore = useTaskStore()

const form = ref({
  title: '',
  description: '',
  status: (props.initialStatus ?? 'todo') as TaskStatus,
  priority: 'medium' as string,
  due_date: '',
})

const saving = ref(false)
const error = ref('')

watch(
  () => props.task,
  (t) => {
    if (t) {
      form.value = {
        title: t.title,
        description: t.description ?? '',
        status: t.status,
        priority: t.priority,
        due_date: t.due_date ? t.due_date.substring(0, 10) : '',
        assignee_id: props.task?.assignee?.id ?? undefined,
      }
    }
  },
  { immediate: true },
)

async function handleSubmit() {
  error.value = ''
  saving.value = true
  try {
    const payload = {
      ...form.value,
      description: form.value.description || undefined,
      due_date: form.value.due_date || undefined,
    }
    let saved: Task
    if (props.task) {
      saved = await taskStore.update(props.projectId, props.task.id, payload)
    } else {
      saved = await taskStore.create(props.projectId, payload)
    }
    emit('saved', saved)
    emit('close')
  } catch (e: any) {
    error.value = e.response?.data?.detail ?? 'Something went wrong.'
  } finally {
    saving.value = false
  }
}

async function handleDelete() {
  if (!props.task) return
  saving.value = true
  try {
    await taskStore.remove(props.projectId, props.task.id)
    emit('close')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
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
  max-width: 520px;
  padding: 28px;
  max-height: calc(100vh - 48px);
  overflow-y: auto;
  box-shadow: var(--shadow-lg);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 4px;
}

.modal-header h2 { font-size: 1.05rem; }

.btn-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border: none;
  background: transparent;
  border-radius: var(--radius-sm);
  color: var(--color-text-muted);
  cursor: pointer;
  transition: background 0.12s, color 0.12s;
}

.btn-icon:hover {
  background: var(--color-bg);
  color: var(--color-text);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
  margin-top: 14px;
}

.modal-footer {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid var(--color-border);
}
</style>