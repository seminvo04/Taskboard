import { useAuthStore } from '@/stores/auth'

type EventHandler = (data: unknown) => void

export class ProjectSocket {
  private ws: WebSocket | null = null
  private handlers: Map<string, EventHandler[]> = new Map()
  private projectId: string
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null

  constructor(projectId: string) {
    this.projectId = projectId
  }

  connect(): void {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    this.ws = new WebSocket(`${protocol}//${window.location.host}/api/v1/ws/${this.projectId}`)

    this.ws.onopen = () => {
      const auth = useAuthStore()
      this.ws!.send(JSON.stringify({ token: auth.accessToken }))
    }

    this.ws.onmessage = (event) => {
      try {
        const { event: name, data } = JSON.parse(event.data)
        this.handlers.get(name)?.forEach((h) => h(data))
      } catch {
        // message malformé
      }
    }

    this.ws.onclose = () => {
      this.reconnectTimer = setTimeout(() => this.connect(), 3000)
    }
  }

  on(event: string, handler: EventHandler): void {
    const list = this.handlers.get(event) ?? []
    this.handlers.set(event, [...list, handler])
  }

  off(event: string, handler: EventHandler): void {
    const list = this.handlers.get(event) ?? []
    this.handlers.set(event, list.filter((h) => h !== handler))
  }

  disconnect(): void {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer)
    this.ws?.close()
    this.ws = null
  }
}
