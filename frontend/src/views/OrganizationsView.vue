<script setup lang="ts">
import { useTelegramBackButton } from '@/composables/useTelegramBackButton.ts'
import { onMounted } from 'vue'

const { showBackButton } = useTelegramBackButton()

const items = [
  {
    id: 1,
    label: 'Министерство по делам молодежи КБР',
    icon: 'https://www.upinfo.ru/sites/default/files/styles/servcie_bgimage/public/news/2024/3-_1_.jpg?itok=BFxJ8Feq',
    header: 'Люев Азамат Хасейнович',
    phone: '+7 (967) 256-27-28',
    address: 'г. Нальчик, ул. Кулиева, 12',
  },
  {
    id: 2,
    label: 'Многофункциональный молодежный центр КБР',
    icon: 'https://www.upinfo.ru/sites/default/files/styles/servcie_bgimage/public/news/2024/3-_1_.jpg?itok=BFxJ8Feq',
    header: 'Дзагаштов Азамат Мусарбиевич',
    phone: '+7 (8662) 49-60-33',
    address: 'г. Нальчик, пр. Кулиева, 12',
  },
  {
    id: 3,
    label: 'Молодежный центр Черекского района',
    icon: 'https://images.vector-images.com/7/cherek_r_prcoa_2010.gif',
    header: 'Мокаев Ислам Кемалович',
    phone: '+7 (918) 728-55-55',
    address: 'г.п. Кашхатау, ул. Зукаева 5',
  },
  {
    id: 4,
    label: 'Молодежный центр Урванского района',
    icon: 'https://www.heraldicum.ru/russia/subjects/towns/images/urvan.gif',
    header: 'Хостов Темирлан Мухадинович',
    phone: '+7 (964) 039-03-09',
    address: 'г. Нарткала, ул. Кабардинская 115',
  },
  {
    id: 5,
    label: 'Молодежный центр Чегемского района',
    icon: 'https://images.vector-images.com/7/chegem-mr-c.gif',
    header: 'Хапова Фатима Аслановна',
    phone: '+7 (928) 690-97-50',
    address: 'г. Чегем, ул. Баксанское шоссе, 3',
  },
]

onMounted(() => {
  showBackButton()
})
</script>

<template>
  <section class="mx-6 mt-6">
    <h1 class="text-3xl font-bold tg-text">Молодежные центры</h1>
    <p class="mt-1 mb-6 tg-hint text-lg">Все доступные центры в Кабардино-Балкарии</p>
  </section>

  <section class="mx-4">
    <div class="relative mb-6">
      <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-5 w-5 text-gray-400"
          viewBox="0 0 20 20"
          fill="currentColor"
        >
          <path
            fill-rule="evenodd"
            d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z"
            clip-rule="evenodd"
          />
        </svg>
      </div>
      <input
        type="text"
        placeholder="Поиск по названию или району..."
        class="w-full rounded-xl border tg-border pl-10 pr-4 py-3 focus:border-sky-500 focus:outline focus:outline-sky-500"
      />
    </div>
  </section>

  <section class="space-y-6">
    <div
      v-for="item in items"
      :key="item.id"
      class="rounded-2xl tg-secondary-bg border tg-border p-5 mx-4 shadow-sm"
    >
      <div class="flex items-center space-x-4">
        <img :src="item.icon" class="rounded-full w-12 h-12 flex-shrink-0" alt="" />
        <div>
          <h2 class="text-lg tg-text font-semibold">{{ item.label }}</h2>
          <p class="text-md tg-hint">{{ item.header }}</p>
        </div>
      </div>
      <div class="mt-5 space-y-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <div
              class="hidden sm:grid flex h-10 w-10 items-center justify-center rounded-full tg-bg"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-5 w-5 text-slate-500"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fill-rule="evenodd"
                  d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z"
                  clip-rule="evenodd"
                />
              </svg>
            </div>
            <div>
              <p class="text-sm tg-hint">Адрес</p>
              <p class="text-sm font-medium tg-text">{{ item.address }}</p>
            </div>
          </div>
          <a
            :href="`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(item.address)}`"
            target="_blank"
            rel="noopener noreferrer"
            class="text-sm font-semibold tg-btn py-1.5 px-3 rounded-lg"
            >Маршрут</a
          >
        </div>
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <div
              class="hidden sm:grid flex h-10 w-10 items-center justify-center rounded-full tg-bg"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-5 w-5 text-slate-500"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  d="M2 3a1 1 0 011-1h2.153a1 1 0 01.986.836l.74 4.435a1 1 0 01-.54 1.06l-1.548.773a11.037 11.037 0 006.105 6.105l.774-1.548a1 1 0 011.059-.54l4.435.74a1 1 0 01.836.986V17a1 1 0 01-1 1h-2C7.82 18 2 12.18 2 5V3z"
                />
              </svg>
            </div>
            <div>
              <p class="text-sm tg-hint">Телефон</p>
              <p class="text-sm font-medium tg-text">{{ item.phone }}</p>
            </div>
          </div>
          <a
            :href="`tel:${item.phone.replace(/[\s()-]/g, '')}`"
            class="text-sm font-semibold tg-btn py-1.5 px-3 rounded-lg transition"
            >Вызов</a
          >
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped></style>
