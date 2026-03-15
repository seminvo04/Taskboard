<template>
  <div class="kanban">
    <div
      v-for="col in STATUSES"
      :key="col.key"
      class="kanban-col"
    >
      <div class="col-header">
        <span class="col-title">{{ col.label }}</span>
        <span class="col-count">{{ tasksByStatus(col.key).length }}</span>
        <button
          class="btn btn-ghost btn-sm col-add"
          title="Add task"
          @click="$emit('add', col.key)"
        >
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg>
        </button>
      </div>

      <div class="col-tasks">
        <TaskCard
          v-for="task in tasksByStatus(col.key)"
          :key="task.id"
          :task="task"
          @click="$emit('edit', $event)"
        />

        <button
          class="add-task-inline"
          @click="$emit('add', col.key)"
        >
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg>
          Ajouter une tâche
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useTaskStore, STATUSES, type Task, type TaskStatus } from '@/stores/tasks'
import TaskCard from './TaskCard.vue'

const props = defineProps<{ projectId: string }>()
defineEmits<{
  add: [status: TaskStatus]
  edit: [task: Task]
}>()

const taskStore = useTaskStore()

function tasksByStatus(status: TaskStatus) {
  return taskStore.tasks
    .filter((t) => t.project_id === props.projectId && t.status === status)
    .sort((a, b) => a.position - b.position || a.created_at.localeCompare(b.created_at))
}
</script>

<style scoped>
.kanban {
  display: flex;
  gap: 16px;
  overflow-x: auto;
  padding-bottom: 16px;
  align-items: flex-start;
}

.kanban-col {
  flex: 0 0 272px;
  background: var(--color-bg);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
}

.col-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 14px 10px;
  border-bottom: 1px solid var(--color-border);
}

.col-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text);
  flex: 1;
  letter-spacing: -0.01em;
}

.col-count {
  font-size: 11px;
  font-weight: 600;
  color: var(--color-text-muted);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 99px;
  padding: 1px 8px;
}

.col-add {
  opacity: 0;
  transition: opacity 0.15s;
  padding: 0 7px;
  height: 26px;
}

.kanban-col:hover .col-add { opacity: 1; }

.col-tasks {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 10px;
  min-height: 60px;
}

.add-task-inline {
  display: flex;
  align-items: center;
  gap: 6px;
  width: 100%;
  padding: 8px 10px;
  border: none;
  background: transparent;
  border-radius: var(--radius-sm);
  font-size: 12px;
  color: var(--color-text-subtle);
  cursor: pointer;
  transition: background 0.12s, color 0.12s;
  text-align: left;
}

.add-task-inline:hover {
  background: var(--color-surface);
  color: var(--color-text-muted);
}
</style>
