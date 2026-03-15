import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'

export type TaskStatus = 'backlog' | 'todo' | 'in_progress' | 'in_review' | 'done'
export type TaskPriority = 'low' | 'medium' | 'high' | 'critical'

export interface Task {
  id: string
  title: string
  description: string | null
  status: TaskStatus
  priority: TaskPriority
  position: number
  due_date: string | null
  project_id: string
  assignee: { id: string; username: string; full_name: string | null } | null
  created_by_id: string
  created_at: string
  updated_at: string
}

export const STATUSES: { key: TaskStatus; label: string }[] = [
  { key: 'backlog', label: 'Backlog' },
  { key: 'todo', label: 'À faire' },
  { key: 'in_progress', label: 'En cours' },
  { key: 'in_review', label: 'En revue' },
  { key: 'done', label: 'Terminé' },
]

export const useTaskStore = defineStore('tasks', () => {
  const tasks = ref<Task[]>([])
  const loading = ref(false)

  async function fetchForProject(projectId: string) {
    loading.value = true
    try {
      const { data } = await api.get<Task[]>(`/projects/${projectId}/tasks/`)
      tasks.value = data
    } finally {
      loading.value = false
    }
  }

  async function create(projectId: string, payload: Partial<Task>) {
    const { data } = await api.post<Task>(`/projects/${projectId}/tasks/`, payload)
    tasks.value.push(data)
    return data
  }

  async function update(projectId: string, taskId: string, payload: Partial<Task>) {
    const { data } = await api.patch<Task>(`/projects/${projectId}/tasks/${taskId}`, payload)
    const idx = tasks.value.findIndex((t) => t.id === taskId)
    if (idx !== -1) tasks.value[idx] = data
    return data
  }

  async function remove(projectId: string, taskId: string) {
    await api.delete(`/projects/${projectId}/tasks/${taskId}`)
    tasks.value = tasks.value.filter((t) => t.id !== taskId)
  }

  // Called by WebSocket events — mutates local state without an HTTP round-trip
  function applyEvent(event: string, data: Task | { id: string }) {
    if (event === 'task.created') {
      const task = data as Task
      if (!tasks.value.find((t) => t.id === task.id)) tasks.value.push(task)
    } else if (event === 'task.updated') {
      const task = data as Task
      const idx = tasks.value.findIndex((t) => t.id === task.id)
      if (idx !== -1) tasks.value[idx] = task
    } else if (event === 'task.deleted') {
      tasks.value = tasks.value.filter((t) => t.id !== (data as { id: string }).id)
    }
  }

  return { tasks, loading, fetchForProject, create, update, remove, applyEvent }
})
