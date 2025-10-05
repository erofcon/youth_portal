import { useTelegramTheme } from '@/composables/useTelegramTheme'

const { webApp } = useTelegramTheme()

const getApiBaseUrl = () => {
  return 'http://localhost:8000/api/v1'
}

// Базовая функция для выполнения запросов
async function apiClient<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${getApiBaseUrl()}${endpoint}`
  const headers = new Headers(options.headers || {})
  headers.append('Content-Type', 'application/json')

  const initData = webApp.value?.initData
  if (initData) {
    headers.append('Authorization', `Tma ${initData}`)
  }

  const config: RequestInit = {
    ...options,
    headers,
  }

  try {
    const response = await fetch(url, config)
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: response.statusText }))
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`)
    }

    if (response.status === 204) {
      return null as T
    }
    return (await response.json()) as T
  } catch (error) {
    console.error(`API call failed: ${endpoint}`, error)
    throw error
  }
}

export default apiClient
