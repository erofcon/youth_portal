<script setup lang="ts">
import { useRouter } from 'vue-router'

const items = [
  {
    label: 'Мероприятия',
    description: 'Главные события республики',
    icon: 'https://smart-estet.ru/datas/users/1-1683720101_eaglr3.jpg',
    route: '/app/events',
  },
  {
    label: 'Бронирование',
    description: 'Пространства для ваших идей',
    icon: 'https://молцентр-пермкрай.рф/storage/upload/spaces/01JG1JDMTSVZ2ERSC6D33WJV2Z.jpg',
    route: '/app/booking',
  },
  {
    label: 'МолЦентры',
    description: 'Точки притяжения молодежи',
    icon: 'https://www.upinfo.ru/sites/default/files/styles/servcie_bgimage/public/news/2024/3-_1_.jpg?itok=BFxJ8Feq',
    route: '/app/organizations',
  },
]

const router = useRouter()

const navigateTo = (route: string) => {
  router.push(route)
}
</script>

<template>
  <section class="flex flex-col mt-4 text-center items-center justify-center">
    <img class="w-18 h-18 rounded-full" src="@/assets/images/logo.png" alt="Rounded avatar" />

    <h1 class="text-3xl font-extrabold tg-text">
      Молодёжь
      <span class="tg-link">КБР</span>
    </h1>

    <p class="mt-2 max-w-xs tg-hint">
      Ваш проводник в мир возможностей: от ярких мероприятий до карьерного роста.
    </p>
  </section>

  <section class="mt-6">
    <div class="grid grid-cols-1 gap-4 px-8 sm:px-18">
      <a
        v-for="item in items"
        :key="item.route"
        @click.prevent="navigateTo(item.route)"
        class="relative block rounded-2xl overflow-hidden aspect-[5/2] group cursor-pointer transition-transform duration-200 active:scale-[0.97]"
      >
        <img
          :src="item.icon"
          :alt="item.label"
          class="absolute inset-0 w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
        />

        <div class="absolute inset-0 bg-gradient-to-t from-black/70 to-black/10"></div>

        <div class="relative h-full flex flex-col justify-end p-4 text-white">
          <h3 class="text-xl font-bold">{{ item.label }}</h3>
          <p class="text-sm opacity-90 mt-1">{{ item.description }}</p>
        </div>

        <i
          class="pi pi-arrow-right absolute top-4 right-4 text-white text-xl opacity-70 group-hover:opacity-100 transition-opacity"
        ></i>
      </a>
    </div>
  </section>

  <footer class="text-center mt-8 mb-4 text-xs" :style="{ color: 'var(--tg-theme-hint-color)' }">
    © Министерство по делам молодежи КБР
  </footer>
</template>
