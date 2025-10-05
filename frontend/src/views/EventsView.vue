<script setup lang="ts">
import { useTelegramBackButton } from '@/composables/useTelegramBackButton.ts'
import { onMounted } from 'vue'

const { showBackButton } = useTelegramBackButton()

const categories = ['Все', 'Технологии', 'Наука', 'Спорт', 'Творчество', 'Бизнес']
const events = [
  {
    id: 1,
    imageUrl:
      'https://молод07.рф/storage/uploads/events1/cover/1h3kfYmlwJeFqpthqv8X2lQlMq7BQb43E5QBq3pb.jpg',
    category: 'Образование',
    location: 'Нальчик',
    title: 'В Нальчике пройдет КВН на кабардинском языке',
    date: '19 сентября 2025, Пятница',
  },
  {
    id: 2,
    imageUrl:
      'https://images.unsplash.com/photo-1540575467063-178a50c2df87?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1470&q=80',
    category: 'Культура',
    location: 'Онлайн',
    title: 'Лекция "Современное искусство в цифровую эпоху"',
    date: '22 июля 2024, Понедельник',
  },
]

onMounted(() => {
  showBackButton()
})
</script>

<template>
  <section class="mx-6 mt-6">
    <h1 class="text-3xl font-bold tg-text">Мероприятия</h1>
    <p class="mt-1 mb-6 tg-hint text-lg">Самые актуальные события для молодежи</p>
  </section>

  <section class="mx-4">
    <div class="flex space-x-2 overflow-x-auto pb-3 -mx-4 px-4">
      <button
        v-for="(item, index) in categories"
        :key="index"
        class="tg-btn px-4 py-2 text-sm font-semibold rounded-full whitespace-nowrap shadow-sm"
      >
        {{ item }}
      </button>
    </div>
  </section>

  <section class="my-8 space-y-6">
    <div
      v-for="event in events"
      :key="event.id"
      class="tg-secondary-bg tg-tex mx-6 rounded-lg shadow-sm overflow-hidden border tg-border"
    >
      <img :src="event.imageUrl" :alt="event.title" class="w-full h-48 object-cover" />
      <div class="p-4">
        <div class="flex items-center gap-2">
          <span class="tg-btn text-xs font-semibold px-2.5 py-1 rounded-full">{{
            event.category
          }}</span>
          <span class="tg-btn text-xs font-medium px-2.5 py-1 rounded-full">{{
            event.location
          }}</span>
        </div>

        <h2 class="text-lg font-bold mt-3">{{ event.title }}</h2>

        <div class="flex items-center text-sm tg-hint mt-2">
          <svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
            ></path>
          </svg>
          <span>{{ event.date }}</span>
        </div>

        <button class="w-full mt-4 py-2.5 font-semibold tg-btn rounded-lg transition-colors">
          Подробнее
        </button>
      </div>
    </div>
  </section>

</template>

<style scoped></style>
