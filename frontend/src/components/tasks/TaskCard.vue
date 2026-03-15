<template>
  <div class="task-card" @click="$emit('click', task)">
    <div class="task-top">
      <span :class="`badge badge-priority-${task.priority}`">{{ priorityLabel }}</span>
      <span v-if="task.due_date" :class="['task-due', isOverdue ? 'overdue' : '']">
        {{ formatDue(task.due_date) }}
      </span>
    </div>

    <p class="task-title">{{ task.title }}</p>

    <p v-if="task.description" class="task-description">{{ task.description }}</p>

    <div v-if="task.assignee" class="task-assignee">
      <span class="assignee-avatar">{{ task.assignee.username[0].toUpperCase() }}</span>
      <span class="assignee-name">{{ task.assignee.full_name ?? task.assignee.username }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Task } from '@/stores/tasks'

const props = defineProps<{ task: Task }>()
defineEmits<{ click: [task: Task] }>()

const isOverdue = computed(() => {
  if (!props.task.due_date || props.task.status === 'done') return false
  return new Date(props.task.due_date) < new Date()
})

const PRIORITY_LABELS: Record<string, string> = {
  low: 'Faible',
  medium: 'Moyenne',
  high: 'Haute',
  critical: 'Critique',
}
const priorityLabel = computed(() => PRIORITY_LABELS[props.task.priority] ?? props.task.priority)

function formatDue(iso: string) {
  return new Date(iso).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' })
}
</script>

<style scoped>
.task-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 13px;
  cursor: pointer;
  transition: box-shadow 0.15s, transform 0.15s;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.task-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}

.task-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.task-due { font-size: 11px; color: var(--color-text-muted); }
.task-due.overdue { color: var(--color-danger); font-weight: 600; }

.task-title {
  font-size: 13px;
  font-weight: 500;
  line-height: 1.45;
  color: var(--color-text);
  letter-spacing: -0.01em;
}

.task-description {
  font-size: 12px;
  color: var(--color-text-muted);
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.task-assignee {
  display: flex;
  align-items: center;
  gap: 7px;
  margin-top: 2px;
  padding-top: 8px;
  border-top: 1px solid var(--color-border);
}

.assignee-avatar {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-primary-light), var(--color-primary-muted));
  color: var(--color-primary);
  font-size: 10px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.assignee-name { font-size: 12px; color: var(--color-text-muted); font-weight: 500; }
</style>