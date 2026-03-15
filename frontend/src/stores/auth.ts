import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

const BASE = '/api/v1'

interface User {
  id: string
  email: string
  username: string
  full_name: string | null
}

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref<string | null>(localStorage.getItem('access_token'))
  const refreshToken = ref<string | null>(localStorage.getItem('refresh_token'))
  const user = ref<User | null>(null)

  const isAuthenticated = computed(() => !!accessToken.value)

  async function register(email: string, username: string, password: string, full_name?: string) {
    const { data } = await axios.post(`${BASE}/auth/register`, {
      email, username, password, full_name,
    })
    return data
  }

  async function login(email: string, password: string) {
    const params = new URLSearchParams({ username: email, password })
    const { data } = await axios.post(`${BASE}/auth/login`, params)
    _setTokens(data.access_token, data.refresh_token)
    await fetchMe()
  }

  async function refresh(): Promise<boolean> {
    if (!refreshToken.value) return false
    try {
      const { data } = await axios.post(`${BASE}/auth/refresh`, {
        refresh_token: refreshToken.value,
      })
      _setTokens(data.access_token, data.refresh_token)
      return true
    } catch {
      return false
    }
  }

  async function fetchMe() {
    const { data } = await axios.get(`${BASE}/auth/me`, {
      headers: { Authorization: `Bearer ${accessToken.value}` },
    })
    user.value = data
  }

  function logout() {
    accessToken.value = null
    refreshToken.value = null
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  function _setTokens(access: string, refresh: string) {
    accessToken.value = access
    refreshToken.value = refresh
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
  }

  if (accessToken.value) fetchMe().catch(() => logout())

  return { accessToken, refreshToken, user, isAuthenticated, register, login, refresh, logout, fetchMe }
})