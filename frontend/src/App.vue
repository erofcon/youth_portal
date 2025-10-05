<script setup lang="ts">
import { onMounted } from 'vue'
import { useTelegramTheme } from '@/composables/useTelegramTheme'

useTelegramTheme()

</script>

<template>
  <div class="flex flex-col min-h-screen max-w-lg mx-auto tg-bg tg-text">
    <RouterView />
  </div>
</template>
