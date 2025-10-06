<script setup lang="ts">
import type { Booking } from '@/types'
import { computed } from 'vue'

const props = defineProps<{ booking: Booking }>()

const statusInfo = computed(() => {
  switch (props.booking.status) {
    case 'APPROVED':
      return { text: 'Одобрено', color: 'bg-green-500' }
    case 'REJECTED':
      return { text: 'Отклонено', color: 'bg-red-500' }
    case 'CANCELED':
      return { text: 'Отменено', color: 'bg-gray-500' }
    case 'PENDING':
    default:
      return { text: 'В ожидании', color: 'bg-yellow-500' }
  }
})

const formatDate = (iso: string) => {
  return new Date(iso).toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })
}

const formatTime = (iso: string) => {
  return new Date(iso).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
}
</script>

<template>
  <div class="tg-secondary-bg rounded-lg shadow-sm overflow-hidden border tg-border">
    <div class="p-4">
      <div class="flex justify-between items-start">
        <div>
          <h3 class="font-bold tg-text">{{ booking.room.name }}</h3>
          <p class="text-sm tg-hint">{{ booking.room.center.name }}</p>
        </div>
        <div class="flex items-center gap-2 text-xs font-medium">
          <span class="w-2.5 h-2.5 rounded-full" :class="statusInfo.color"></span>
          <span class="tg-text">{{ statusInfo.text }}</span>
        </div>
      </div>

      <div class="mt-4 border-t tg-border pt-3 grid grid-cols-2 gap-3">
        <div>
          <div class="text-xs tg-hint">Дата</div>
          <div class="text-sm tg-text font-medium">{{ formatDate(booking.start_at) }}</div>
        </div>
        <div>
          <div class="text-xs tg-hint">Время</div>
          <div class="text-sm tg-text font-medium">
            {{ formatTime(booking.start_at) }} – {{ formatTime(booking.end_at) }}
          </div>
        </div>
      </div>

      <div
        v-if="booking.status === 'REJECTED' && booking.rejection_reason"
        class="mt-3 text-xs tg-hint border-l-2 border-red-500 pl-2"
      >
        <b>Причина отклонения:</b> {{ booking.rejection_reason }}
      </div>
    </div>
  </div>
</template>
