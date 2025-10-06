import { defineStore } from 'pinia'
import { ref } from 'vue'
import apiClient from '@/api'
import type { AvailabilityResponse, BookingPayload, Room, Paginated, Booking } from '@/types'

function formatDateLocalYYYYMMDD(date: Date): string {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

export const useBookingStore = defineStore('booking', () => {
  const rooms = ref<Room[]>([])
  const isLoading = ref(false)
  const myBookings = ref<Booking[]>([])
  const error = ref<string | null>(null)

  async function fetchRooms() {
    isLoading.value = true
    error.value = null
    try {
      const result = await apiClient<Paginated<Room>>('/rooms/')
      rooms.value = result.results
    } catch (e: any) {
      error.value = e.message || 'Не удалось загрузить список помещений.'
    } finally {
      isLoading.value = false
    }
  }

  async function fetchAvailability(roomId: number, date: Date): Promise<AvailabilityResponse> {
    const dateStr = formatDateLocalYYYYMMDD(date)
    return await apiClient<AvailabilityResponse>(`/rooms/${roomId}/availability/?date=${dateStr}`)
  }

  async function createBooking(payload: BookingPayload) {
    return await apiClient('/bookings/', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  }

  async function fetchMyBookings() {
    isLoading.value = true
    error.value = null
    try {
      const result = await apiClient<Paginated<Booking>>('/bookings/my/')
      myBookings.value = result.results
    } catch (e: any) {
      error.value = e.message || 'Не удалось загрузить ваши бронирования.'
    } finally {
      isLoading.value = false
    }
  }

  return {
    rooms,
    myBookings,
    isLoading,
    error,
    fetchRooms,
    fetchAvailability,
    fetchMyBookings,
    createBooking,
  }
})
