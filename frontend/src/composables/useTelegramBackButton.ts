// composables/useTelegramBackButton.ts

import { onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

export function useTelegramBackButton() {
  const router = useRouter()

  // ИЗМЕНЕНО: Используем ту же надежную проверку
  const isTelegramEnvironment = (): boolean => {
    const tg = window.Telegram?.WebApp
    if (!tg) return false

    const hasInitData = !!tg.initData
    const isRealPlatform = tg.platform !== 'unknown'

    return hasInitData || isRealPlatform
  }

  const handleBackClick = () => {
    if (window.history.length > 1) {
      router.back()
    } else {
      router.push('/app')
    }
  }

  const showBackButton = () => {
    if (isTelegramEnvironment()) {
      window.Telegram?.WebApp?.BackButton.show()
    }
  }

  const hideBackButton = () => {
    if (isTelegramEnvironment()) {
      window.Telegram?.WebApp?.BackButton.hide()
    }
  }

  onMounted(() => {
    if (isTelegramEnvironment()) {
      window.Telegram?.WebApp?.BackButton.onClick(handleBackClick)
    }
  })

  onUnmounted(() => {
    if (isTelegramEnvironment()) {
      const tg = window.Telegram.WebApp
      tg.BackButton.offClick(handleBackClick)
      tg.BackButton.hide()
    }
  })

  return {
    showBackButton,
    hideBackButton,
  }
}
