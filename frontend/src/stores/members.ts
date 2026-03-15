import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'

export interface Member {
  id: string
  user: {
    id: string
    email: string
    username: string
    full_name: string | null
  }
  role: 'admin' | 'member' | 'viewer'
  joined_at: string
}

export const ROLE_LABELS: Record<string, string> = {
  admin: 'Admin',
  member: 'Membre',
  viewer: 'Lecteur',
}

export const useMemberStore = defineStore('members', () => {
  const members = ref<Member[]>([])
  const loading = ref(false)

  async function fetchForProject(projectId: string) {
    loading.value = true
    try {
      const { data } = await api.get<Member[]>(`/projects/${projectId}/members`)
      members.value = data
    } finally {
      loading.value = false
    }
  }

  async function addMember(projectId: string, userId: string, role: string) {
    const { data } = await api.post<Member>(`/projects/${projectId}/members`, {
      user_id: userId,
      role,
    })
    members.value.push(data)
    return data
  }

  async function updateRole(projectId: string, userId: string, role: string) {
    const { data } = await api.patch<Member>(
      `/projects/${projectId}/members/${userId}`,
      { role },
    )
    const idx = members.value.findIndex((m) => m.user.id === userId)
    if (idx !== -1) members.value[idx] = data
    return data
  }

  async function removeMember(projectId: string, userId: string) {
    await api.delete(`/projects/${projectId}/members/${userId}`)
    members.value = members.value.filter((m) => m.user.id !== userId)
  }

  async function searchUser(username: string) {
    const { data } = await api.get(`/users/search?username=${username}`)
    return data
  }

  function reset() {
    members.value = []
  }

  return { members, loading, fetchForProject, addMember, updateRole, removeMember, searchUser, reset }
})