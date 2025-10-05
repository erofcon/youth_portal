import { defineStore } from 'pinia'
import { ref } from 'vue'
import apiClient from '@/api'
import type { AvailabilityResponse, BookingPayload, Room } from '@/types'

export const useBookingStore = defineStore('booking', () => {
  const rooms = ref<Room[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  async function fetchRooms() {
    isLoading.value = true
    error.value = null
    try {
      const result = await apiClient<Room[]>('/rooms/')
      rooms.value = result.results
    } catch (e: any) {
      error.value = e.message || 'Не удалось загрузить список помещений.'
    } finally {
      isLoading.value = false
    }
  }

  async function fetchAvailability(roomId: number, date: Date): Promise<AvailabilityResponse> {
    const dateStr = date.toISOString().split('T')[0] // 'YYYY-MM-DD'
    return await apiClient<AvailabilityResponse>(`/rooms/${roomId}/availability/?date=${dateStr}`)
  }

  async function createBooking(payload: BookingPayload) {
    payload.start_datetime = '2025-10-05T20:34:40.310Z'
    payload.end_datetime = '2025-10-06T20:34:40.310Z'

    return await apiClient('/bookings/', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  }

  return {
    rooms,
    isLoading,
    error,
    fetchRooms,
    fetchAvailability,
    createBooking,
  }
})
