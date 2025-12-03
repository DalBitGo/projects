import { io } from 'socket.io-client'

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000'

class WebSocketService {
  constructor() {
    this.socket = null
    this.clientId = this.generateClientId()
    this.listeners = new Map()
  }

  generateClientId() {
    return `client-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
  }

  connect() {
    if (this.socket?.connected) {
      return
    }

    this.socket = io(WS_URL, {
      path: `/ws/${this.clientId}`,
      transports: ['websocket'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 5,
    })

    this.socket.on('connect', () => {
      console.log('WebSocket connected:', this.clientId)
    })

    this.socket.on('disconnect', () => {
      console.log('WebSocket disconnected')
    })

    this.socket.on('error', (error) => {
      console.error('WebSocket error:', error)
    })

    // 메시지 수신
    this.socket.on('message', (data) => {
      this.handleMessage(data)
    })
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
    }
  }

  send(data) {
    if (this.socket?.connected) {
      this.socket.emit('message', data)
    } else {
      console.warn('WebSocket not connected')
    }
  }

  subscribeTask(taskId, callback) {
    this.send({
      type: 'subscribe_task',
      task_id: taskId,
    })

    this.listeners.set(taskId, callback)
  }

  unsubscribeTask(taskId) {
    this.send({
      type: 'unsubscribe_task',
      task_id: taskId,
    })

    this.listeners.delete(taskId)
  }

  handleMessage(data) {
    const { type, task_id, state, info } = data

    if (type === 'task_update' && task_id) {
      const callback = this.listeners.get(task_id)
      if (callback) {
        callback({ state, info })
      }

      // 작업 완료 시 자동으로 구독 해제
      if (state === 'SUCCESS' || state === 'FAILURE' || state === 'REVOKED') {
        this.listeners.delete(task_id)
      }
    }
  }

  ping() {
    this.send({
      type: 'ping',
      timestamp: Date.now(),
    })
  }
}

// Singleton instance
const wsService = new WebSocketService()

export default wsService
