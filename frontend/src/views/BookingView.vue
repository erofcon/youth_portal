<!-- src/views/BookingView.vue -->
<script setup lang="ts">
import { useTelegramBackButton } from '@/composables/useTelegramBackButton.ts'
import { onMounted, ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useBookingStore } from '@/stores/booking'
import type { BusySlot, Room } from '@/types'
import ScreenPanel from '@/components/booking/ScreenPanel.vue'
import BookingFlow from '@/components/booking/BookingFlow.vue'

const { showBackButton } = useTelegramBackButton()
const bookingStore = useBookingStore()
const { rooms, isLoading, error } = storeToRefs(bookingStore)

onMounted(() => {
  showBackButton()
  bookingStore.fetchRooms()
})

const isBookingFlowOpen = ref(false)
const activeRoom = ref<Room | null>(null)
const initialBusySlots = ref<BusySlot[]>([])

async function openBooking(room: Room) {
  activeRoom.value = room

  try {
    const today = new Date()
    const response = await bookingStore.fetchAvailability(room.id, today)
    initialBusySlots.value = response.busy_slots
  } catch (e) {
    console.error('Failed to fetch initial availability', e)
    initialBusySlots.value = []
  }
  isBookingFlowOpen.value = true
}

function onBooked(payload: any) {
  console.log('Booked successfully! Payload:', payload)
}
</script>

<template>
  <section v-if="isLoading" class="flex flex-col max-w-lg items-center justify-center">
    <div role="status">
      <svg
        aria-hidden="true"
        class="w-8 h-8 text-gray-200 animate-spin dark:text-gray-600 fill-blue-600"
        viewBox="0 0 100 101"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z"
          fill="currentColor"
        />
        <path
          d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z"
          fill="currentFill"
        />
      </svg>
      <span class="sr-only">Loading...</span>
    </div>
  </section>

  <section v-if="error" class="tg-bg tg-text">
    <div class="py-8 px-4 mx-auto max-w-screen-xl lg:py-16 lg:px-6">
      <div class="mx-auto max-w-screen-sm text-center">
        <h1 class="mb-4 text-7xl tracking-tight font-extrabold lg:text-9xl">404</h1>
        <p class="mb-4 text-3xl tracking-tight font-bold md:text-4xl">Что-то случилось</p>
        <p class="mb-4 text-lg font-light tg-hint">
          Извините, идет сервисные работы. Попробуйте зайти попозже.
        </p>
      </div>
    </div>
  </section>

  <section v-if="!isLoading && !error" class="flex flex-col max-w-lg">
    <div class="mx-6 mt-6">
      <h1 class="text-3xl font-bold tg-text">Бронирование</h1>
      <p class="mt-1 mb-6 tg-hint text-lg">Пространства для ваших идей</p>
    </div>

    <div
      v-for="room in rooms"
      :key="room.id"
      class="tg-secondary-bg mx-6 rounded-lg shadow-sm overflow-hidden border tg-border"
    >
      <div class="relative">
        <img class="w-full h-48 object-cover" :src="room.image" :alt="`Фото ${room.name}`" />
      </div>
      <div class="p-5">
        <h3 class="text-xl font-bold tg-text">{{ room.name }}</h3>
        <p class="text-sm tg-hint">{{ room.center.name }}</p>
        <div class="flex items-center text-sm tg-hint mt-2 space-x-4">
          <span class="flex items-center">
            <svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.653-.184-1.268-.5-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.653.184-1.268.5-1.857m0 0a5.002 5.002 0 019 0m-4.5 4.5a5.002 5.002 0 00-9 0m-2.25 0a5.002 5.002 0 009 0m0 0a5.002 5.002 0 009 0"
              />
            </svg>
            до {{ room.capacity }} чел.
          </span>
        </div>
        <div v-if="room.tags.length" class="mt-4 flex flex-wrap gap-2">
          <span
            v-for="tag in room.tags"
            :key="tag.id"
            class="tg-btn text-xs font-medium px-3 py-1 rounded-full"
          >
            {{ tag.name }}
          </span>
        </div>

        <button class="mt-6 w-full py-2 font-semibold tg-btn rounded-lg" @click="openBooking(room)">
          Забронировать
        </button>
      </div>
    </div>
  </section>

  <ScreenPanel v-model="isBookingFlowOpen">
    <BookingFlow
      v-if="activeRoom"
      :room="activeRoom"
      :busy="initialBusySlots"
      @close="isBookingFlowOpen = false"
      @success="onBooked"
    />
  </ScreenPanel>
</template>
