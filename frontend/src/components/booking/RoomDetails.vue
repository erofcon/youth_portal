<script setup lang="ts">
import type { Room } from '@/types'

defineProps<{ room: Room }>()
const emit = defineEmits<{ (e: 'close'): void }>()
</script>

<template>
  <div class="flex flex-col h-full w-full tg-bg tg-text">
    <!-- Шапка -->
    <div class="sticky top-0 z-10 tg-bg border-b tg-border flex items-center p-3">
      <button @click="emit('close')" class="p-1 rounded-full hover:bg-black/10">
        <svg
            class="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
        >
          <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M15 19l-7-7 7-7"
          ></path>
        </svg>
      </button>
      <h2 class="text-lg font-semibold ml-3">О помещении</h2>
    </div>

    <!-- Контент -->
    <div class="flex-1 overflow-y-auto">
      <img
          v-if="room.image"
          class="w-full h-56 object-cover"
          :src="room.image"
          :alt="`Фото ${room.name}`"
      />
      <div class="p-4">
        <h1 class="text-2xl font-bold tg-text">{{ room.name }}</h1>
        <p class="text-md tg-hint">{{ room.center.name }}</p>

        <div class="mt-4 border-t tg-border pt-4">
          <h3 class="text-sm font-semibold tg-hint mb-2">ОПИСАНИЕ</h3>
          <p class="tg-text whitespace-pre-wrap">{{ room.description || 'Описание отсутствует.' }}</p>
        </div>

        <div class="mt-4 border-t tg-border pt-4">
          <h3 class="text-sm font-semibold tg-hint mb-2">ДЕТАЛИ</h3>
          <div class="space-y-2">
            <div class="flex items-center">
              <span class="w-24 text-sm tg-hint">Вместимость:</span>
              <span class="tg-text font-medium">до {{ room.capacity }} чел.</span>
            </div>
            <div v-if="room.responsible_phone" class="flex items-center">
              <span class="w-24 text-sm tg-hint">Телефон:</span>
              <a :href="`tel:${room.responsible_phone}`" class="tg-link font-medium">{{ room.responsible_phone }}</a>
            </div>
            <div class="flex items-center">
              <span class="w-24 text-sm tg-hint">Адрес:</span>
              <span class="tg-text font-medium">{{ room.center.address }}</span>
            </div>
          </div>
        </div>

        <div v-if="room.tags.length" class="mt-4 border-t tg-border pt-4">
          <h3 class="text-sm font-semibold tg-hint mb-2">ОСОБЕННОСТИ</h3>
          <div class="flex flex-wrap gap-2">
            <span
                v-for="tag in room.tags"
                :key="tag.id"
                class="tg-secondary-bg border tg-border text-xs font-medium px-3 py-1 rounded-full"
            >
              {{ tag.name }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>