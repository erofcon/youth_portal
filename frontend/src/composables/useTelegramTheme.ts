import { computed, onMounted, onUnmounted, readonly, ref } from 'vue'

let isInitialized = false
const isDark = ref(false)
const themeParams = ref<Record<string, any>>({})
const webApp = ref<WebApp | null>(null)

let mediaQuery: MediaQueryList | null = null

type WebApp = Window['Telegram']['WebApp']
type WebAppThemeParams = Window['Telegram']['WebApp']['themeParams']

const isTelegramUA = (): boolean =>
  /Telegram/i.test(navigator.userAgent) || /TMA/i.test(navigator.userAgent)

const isLaunchedAsMiniApp = (tg?: WebApp | null): boolean => {
  if (!tg) return false
  const hasInitData = !!tg.initData && tg.initData.length > 0
  const isRealPlatform = !!tg.platform && tg.platform !== 'unknown'
  return hasInitData || isRealPlatform
}

async function ensureTelegramWebApp(maxWaitMs = 3000): Promise<WebApp | null> {
  if (window.Telegram?.WebApp) return window.Telegram.WebApp

  const hasScript = !!document.querySelector('script[src*="telegram-web-app.js"]')
  if (!hasScript) {
    await new Promise<void>((resolve) => {
      const s = document.createElement('script')
      s.src = 'https://telegram.org/js/telegram-web-app.js'
      s.async = true
      s.onload = () => resolve()
      s.onerror = () => resolve()
      document.head.appendChild(s)
    })
  }

  const started = performance.now()
  while (performance.now() - started < maxWaitMs) {
    if (window.Telegram?.WebApp) return window.Telegram.WebApp
    await new Promise((r) => setTimeout(r, 50))
  }
  return null
}

// Базовые фолбэки
const DEFAULT_LIGHT = {
  bg_color: '#ffffff',
  text_color: '#111827',
  hint_color: '#6b7280',
  link_color: '#2481cc',
  button_color: '#2481cc',
  button_text_color: '#ffffff',
  secondary_bg_color: '#f3f4f6',
}
const DEFAULT_DARK = {
  bg_color: '#111827',
  text_color: '#f3f4f6',
  hint_color: '#9ca3af',
  link_color: '#7dd3fc',
  button_color: '#0ea5e9',
  button_text_color: '#ffffff',
  secondary_bg_color: '#1f2937',
}

const hexToRgb = (hex: string) => {
  const h = hex?.startsWith('#') ? hex.slice(1) : hex
  const v =
    h.length === 3
      ? h
          .split('')
          .map((c) => c + c)
          .join('')
      : h.padStart(6, '0').slice(0, 6)
  const r = parseInt(v.slice(0, 2), 16)
  const g = parseInt(v.slice(2, 4), 16)
  const b = parseInt(v.slice(4, 6), 16)
  return { r, g, b }
}
const rgba = (hex: string, a: number) => {
  const { r, g, b } = hexToRgb(hex || '#000000')
  return `rgba(${r}, ${g}, ${b}, ${a})`
}

const setVar = (name: string, value: string) => {
  document.documentElement.style.setProperty(name, value)
}

const applyCssVars = (params?: Partial<WebAppThemeParams>) => {
  const base = isDark.value ? DEFAULT_DARK : DEFAULT_LIGHT
  const p = { ...base, ...(params || {}) }

  setVar('--tg-bg-color', p.bg_color!)
  setVar('--tg-text-color', p.text_color!)
  setVar('--tg-hint-color', p.hint_color!)
  setVar('--tg-link-color', p.link_color!)
  setVar('--tg-button-color', p.button_color!)
  setVar('--tg-button-text-color', p.button_text_color!)
  setVar('--tg-secondary-bg-color', p.secondary_bg_color!)

  const alpha = isDark.value ? 0.18 : 0.12
  setVar('--tg-border-color', rgba(p.text_color!, alpha))
}

const checkIsTelegram = (): boolean => {
  const tg = window.Telegram?.WebApp
  if (!tg) return false
  return !!tg.initData || tg.platform !== 'unknown'
}

export function useTelegramTheme() {
  const applyTheme = (dark: boolean) => {
    document.documentElement.classList.toggle('dark', dark)
    isDark.value = dark

    if (!isLaunchedAsMiniApp(webApp.value)) {
      applyCssVars()
    }
  }

  const handleSystemThemeChange = (e: MediaQueryListEvent) => {
    applyTheme(e.matches)
  }

  const handleTelegramThemeChange = () => {
    const tg = webApp.value
    if (!tg) return
    themeParams.value = tg.themeParams as WebAppThemeParams
    applyTheme(tg.colorScheme === 'dark')
    applyCssVars(themeParams.value)
  }

  const isTelegramEnvironment = () => checkIsTelegram()

  const initTheme = async () => {
    if (isInitialized) return

    // 1) системная тема и мгновенная установка фолбэков
    mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    applyTheme(mediaQuery.matches)
    mediaQuery.addEventListener?.('change', handleSystemThemeChange)
    applyCssVars()

    // 2) пробуем подключить WebApp API
    const tg = await ensureTelegramWebApp()
    webApp.value = tg

    if (isLaunchedAsMiniApp(tg)) {
      themeParams.value = tg!.themeParams
      applyTheme(tg!.colorScheme === 'dark')
      applyCssVars(themeParams.value)
      tg!.onEvent('themeChanged', handleTelegramThemeChange)
      tg!.expand()
      tg!.ready()
    }

    isInitialized = true
  }

  const cleanup = () => {
    if (webApp.value) {
      webApp.value.offEvent('themeChanged', handleTelegramThemeChange)
    }
    if (mediaQuery) {
      mediaQuery.removeEventListener?.('change', handleSystemThemeChange)
    }
  }

  const toggleTheme = () => {
    // Тоглим только в браузере (не Mini App)
    if (isLaunchedAsMiniApp(webApp.value)) return
    applyTheme(!isDark.value)
    applyCssVars()
  }

  const unsafeUser = computed(() => {
    if (webApp.value?.initDataUnsafe?.user) {
      return webApp.value.initDataUnsafe.user
    }
    return null
  })

  onMounted(() => {
    initTheme()
  })

  onUnmounted(() => {
    cleanup()
    isInitialized = false
  })

  return {
    isDark: readonly(isDark),
    themeParams: readonly(themeParams),
    webApp: readonly(webApp),
    isTelegramUA,
    toggleTheme,
    isTelegramEnvironment,
    unsafeUser,
  }
}

declare global {
  interface Window {
    Telegram?: {
      WebApp: {
        ready: () => void
        expand: () => void
        themeParams: {
          bg_color?: string
          text_color?: string
          hint_color?: string
          link_color?: string
          button_color?: string
          button_text_color?: string
          secondary_bg_color?: string
        }
        colorScheme: 'light' | 'dark'
        platform: string
        version: string
        initData: string
        initDataUnsafe: any
        onEvent: (eventType: 'themeChanged', callback: () => void) => void
        offEvent: (eventType: 'themeChanged', callback: () => void) => void
        BackButton: {
          isVisible: boolean
          show: () => void
          hide: () => void
          onClick: (callback: () => void) => void
          offClick: (callback: () => void) => void
        }
      }
    }
  }
}
