import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'

export interface Project {
  id: string
  name: string
  description: string | null
  owner_id: string
  member_count: number
  created_at: string
}

export const useProjectStore = defineStore('projects', () => {
  const projects = ref<Project[]>([])
  const current = ref<Project | null>(null)
  const loading = ref(false)

  async function fetchAll() {
    loading.value = true
    try {
      const { data } = await api.get<Project[]>('/projects/')
      projects.value = data
    } finally {
      loading.value = false
    }
  }

  async function fetchOne(id: string) {
    const { data } = await api.get<Project>(`/projects/${id}`)
    current.value = data
    return data
  }

  async function create(name: string, description?: string) {
    const { data } = await api.post<Project>('/projects/', { name, description })
    projects.value.unshift(data)
    return data
  }

  async function update(id: string, payload: Partial<Pick<Project, 'name' | 'description'>>) {
    const { data } = await api.patch<Project>(`/projects/${id}`, payload)
    const idx = projects.value.findIndex((p) => p.id === id)
    if (idx !== -1) projects.value[idx] = data
    if (current.value?.id === id) current.value = data
    return data
  }

  async function remove(id: string) {
    await api.delete(`/projects/${id}`)
    projects.value = projects.value.filter((p) => p.id !== id)
    if (current.value?.id === id) current.value = null
  }

  return { projects, current, loading, fetchAll, fetchOne, create, update, remove }
})
