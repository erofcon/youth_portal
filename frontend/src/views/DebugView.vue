<script setup lang="ts">
import { onMounted } from 'vue'
import { useTelegramTheme } from '@/composables/useTelegramTheme'
import { useTelegramBackButton } from '@/composables/useTelegramBackButton'

const { isDark, themeParams, webApp, toggleTheme, isTelegramEnvironment } = useTelegramTheme()
const { showBackButton } = useTelegramBackButton()

onMounted(() => {
  if (isTelegramEnvironment()) {
    showBackButton()
  }
})

function formatObject(obj: object) {
  return JSON.stringify(obj, null, 2)
}
</script>

<template>
  <div class="p-4 font-mono text-sm">
    <h1 class="text-xl font-bold mb-4 text-center">Debug Information</h1>

    <div class="space-y-4">
      <!-- Информация о среде -->
      <div class="p-3 rounded-lg" :style="{ backgroundColor: 'var(--tg-secondary-bg-color)' }">
        <h2 class="font-bold mb-2" :style="{ color: 'var(--tg-link-color)' }">Environment</h2>
        <p>
          In Telegram:
          <span
            class="font-bold"
            :style="{ color: isTelegramEnvironment() ? '#22c55e' : '#ef4444' }"
          >
            {{ isTelegramEnvironment() }}
          </span>
        </p>
        <template v-if="webApp">
          <p>
            Platform:
            <span class="font-bold" :style="{ color: 'var(--tg-link-color)' }">{{
              webApp.platform
            }}</span>
          </p>
          <p>
            Version:
            <span class="font-bold" :style="{ color: 'var(--tg-link-color)' }">{{
              webApp.version
            }}</span>
          </p>
        </template>
      </div>

      <!-- Информация о теме -->
      <div class="p-3 rounded-lg" :style="{ backgroundColor: 'var(--tg-secondary-bg-color)' }">
        <h2 class="font-bold mb-2" :style="{ color: 'var(--tg-link-color)' }">Theme</h2>
        <p>
          Is Dark Mode:
          <span class="font-bold" :style="{ color: isDark ? '#a78bfa' : '#f59e0b' }">{{
            isDark
          }}</span>
        </p>
        <template v-if="webApp">
          <p>
            TG Color Scheme:
            <span class="font-bold" :style="{ color: 'var(--tg-link-color)' }">{{
              webApp.colorScheme
            }}</span>
          </p>
        </template>

        <div class="mt-2">
          <h3 class="font-semibold">Theme Params:</h3>
          <pre
            class="whitespace-pre-wrap break-all p-2 rounded mt-1"
            :style="{ backgroundColor: 'rgba(0,0,0,0.06)' }"
            >{{ formatObject(themeParams) }}
          </pre>

          <!-- Визуальные “чипы” цветов -->
          <div class="mt-3 grid grid-cols-2 md:grid-cols-3 gap-2">
            <div class="p-2 rounded border" :style="{ backgroundColor: 'var(--tg-bg-color)' }">
              bg_color
            </div>
            <div
              class="p-2 rounded border"
              :style="{ backgroundColor: 'var(--tg-secondary-bg-color)' }"
            >
              secondary_bg_color
            </div>
            <div
              class="p-2 rounded border text-white"
              :style="{
                backgroundColor: 'var(--tg-button-color)',
                color: 'var(--tg-button-text-color)',
              }"
            >
              button
            </div>
            <div class="p-2 rounded border" :style="{ color: 'var(--tg-text-color)' }">
              text_color
            </div>
            <div class="p-2 rounded border" :style="{ color: 'var(--tg-hint-color)' }">
              hint_color
            </div>
            <div class="p-2 rounded border" :style="{ color: 'var(--tg-link-color)' }">
              link_color
            </div>
          </div>
        </div>
      </div>

      <!-- Управление -->
      <div
        v-if="!isTelegramEnvironment()"
        class="p-3 rounded-lg"
        :style="{ backgroundColor: 'var(--tg-secondary-bg-color)' }"
      >
        <h2 class="font-bold mb-2" :style="{ color: 'var(--tg-link-color)' }">
          Controls (Browser only)
        </h2>
        <button
          @click="toggleTheme"
          class="px-3 py-1.5 rounded-md transition-opacity hover:opacity-90"
          :style="{
            backgroundColor: 'var(--tg-button-color)',
            color: 'var(--tg-button-text-color)',
          }"
        >
          Toggle Theme
        </button>
      </div>

      <!-- initData -->
      <div
        v-if="webApp?.initData"
        class="p-3 rounded-lg"
        :style="{ backgroundColor: 'var(--tg-secondary-bg-color)' }"
      >
        <h2 class="font-bold mb-2" :style="{ color: 'var(--tg-link-color)' }">InitData</h2>
        <pre
          class="text-xs whitespace-pre-wrap break-all p-2 rounded mt-1"
          :style="{ backgroundColor: 'rgba(0,0,0,0.06)' }"
          >{{ webApp.initData }}
        </pre>
      </div>
    </div>
  </div>
</template>
