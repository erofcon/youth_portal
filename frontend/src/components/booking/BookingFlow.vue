<!-- components/BookingFlow.vue -->
<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import DateStep from '@/components/booking/DateStep.vue'
import TimeStep from '@/components/booking/TimeStep.vue'
import type { BusySlot, Room } from '@/types'
import { useBookingStore } from '@/stores/booking.ts'

const props = defineProps<{ room: Room; busy?: BusySlot[] }>()
const emit = defineEmits<{ (e: 'close'): void; (e: 'success', payload: any): void }>()

const bookingStore = useBookingStore()

const step = ref<0 | 1 | 2>(0)
const chosenDate = ref<Date | null>(new Date())
const startAt = ref<Date | null>(null)
const endAt = ref<Date | null>(null)

const internalBusy = ref<BusySlot[]>(props.busy || [])
const isBusyLoading = ref(false)

watch(chosenDate, async (newDate) => {
  startAt.value = null
  endAt.value = null
  if (!newDate) return

  isBusyLoading.value = true
  try {
    const response = await bookingStore.fetchAvailability(props.room.id, newDate)
    internalBusy.value = response.busy_slots
  } catch (e) {
    console.error('Failed to update availability', e)
    internalBusy.value = []
  } finally {
    isBusyLoading.value = false
  }
})

const now = () => new Date()
const minDurationMin = 60
const workingHours = { from: '09:00', to: '18:00' }

// utils
const toStartOfDay = (d: Date) => new Date(d.getFullYear(), d.getMonth(), d.getDate(), 0, 0, 0, 0)
const toEndOfDay = (d: Date) =>
  new Date(d.getFullYear(), d.getMonth(), d.getDate(), 23, 59, 59, 999)
const parseISO = (s: string) => new Date(s)

function hm(str: string) {
  const [h, m] = str.split(':').map(Number)
  return { h, m }
}

function withHM(base: Date, str: string) {
  const { h, m } = hm(str)
  const d = new Date(base)
  d.setHours(h, m, 0, 0)
  return d
}

function addMin(d: Date, m: number) {
  const x = new Date(d)
  x.setMinutes(x.getMinutes() + m)
  return x
}

function ceilToStep(dt: Date, step: number) {
  const d = new Date(dt)
  const mins = d.getHours() * 60 + d.getMinutes()
  const next = Math.ceil(mins / step) * step
  d.setHours(0, 0, 0, 0)
  d.setMinutes(next)
  return d
}

function isSameDay(a: Date, b: Date) {
  return a.toDateString() === b.toDateString()
}

// busy helpers
const dayBusy = computed(() => {
  if (!chosenDate.value) return []
  const s = toStartOfDay(chosenDate.value),
    e = toEndOfDay(chosenDate.value)
  // Используем internalBusy, который мы загружаем из API
  return internalBusy.value
    .map((b) => ({ start: parseISO(b.start), end: parseISO(b.end) }))
    .filter((x) => x.end > s && x.start < e)
    .sort((a, b) => a.start.getTime() - b.start.getTime())
})

const isDayFull = computed(() => {
  if (!chosenDate.value) return false
  const s = toStartOfDay(chosenDate.value),
    e = toEndOfDay(chosenDate.value)
  return dayBusy.value.some((x) => x.start <= s && x.end >= e)
})

// Есть ли хоть один доступный 1‑часовой слот в выбранный день,
// начиная не раньше max(работа с, now+1h) для сегодня
const hasFreeForDay = computed(() => {
  if (!chosenDate.value) return false
  const d = chosenDate.value
  const dayStart = toStartOfDay(d)
  const workStartRaw = withHM(dayStart, workingHours.from)
  const workEnd = withHM(dayStart, workingHours.to)

  const oneHourFromNow = addMin(now(), 60)
  const baseStart = isSameDay(d, now())
    ? ceilToStep(new Date(Math.max(workStartRaw.getTime(), oneHourFromNow.getTime())), 30)
    : workStartRaw

  const latestStart = addMin(workEnd, -minDurationMin)
  if (baseStart > latestStart) return false

  function insideBusy(t: Date) {
    return dayBusy.value.some((b) => t >= b.start && t < b.end)
  }

  function nextBusyStartAfter(t: Date) {
    const c = dayBusy.value.filter((b) => b.start > t).map((b) => b.start)
    return c.sort((a, b) => a.getTime() - b.getTime())[0] ?? null
  }

  for (let t = new Date(baseStart); t <= latestStart; t = addMin(t, 30)) {
    if (insideBusy(t)) continue
    const earliestEnd = addMin(t, minDurationMin)
    const cap = nextBusyStartAfter(t) ?? workEnd
    if (earliestEnd <= cap) return true
  }
  return false
})

watch(chosenDate, () => {
  startAt.value = null
  endAt.value = null
})

const canNext = computed(() => {
  if (step.value === 0) return !!chosenDate.value && !isDayFull.value && hasFreeForDay.value
  if (step.value === 1) return !!startAt.value && !!endAt.value && endAt.value! > startAt.value!
  return true
})

function next() {
  if (step.value < 2 && canNext.value) step.value = (step.value + 1) as any
}

function back() {
  if (step.value === 0) emit('close')
  else step.value = (step.value - 1) as any
}

const swipeEl = ref<HTMLElement | null>(null)
let startX = 0,
  startY = 0,
  dx = 0,
  dy = 0,
  swiping = false

function onTouchStart(e: TouchEvent) {
  const t = e.touches[0]
  startX = t.clientX
  startY = t.clientY
  dx = dy = 0
  swiping = true
}

function onTouchMove(e: TouchEvent) {
  if (!swiping) return
  const t = e.touches[0]
  dx = t.clientX - startX
  dy = t.clientY - startY
  if (Math.abs(dx) > Math.abs(dy) && Math.abs(dx) > 12) e.preventDefault()
}

function onTouchEnd() {
  if (!swiping) return
  const thr = 60
  if (Math.abs(dx) > Math.abs(dy) && Math.abs(dx) > thr) {
    if (dx < 0 && canNext.value) next()
    if (dx > 0 && step.value > 0) back()
  }
  swiping = false
  dx = dy = 0
}

onMounted(() => {
  const el = swipeEl.value
  el?.addEventListener('touchstart', onTouchStart, { passive: false })
  el?.addEventListener('touchmove', onTouchMove, { passive: false })
  el?.addEventListener('touchend', onTouchEnd, { passive: true })
  const tg = (window as any)?.Telegram?.WebApp
  if (tg?.BackButton) {
    tg.BackButton.show()
    const handler = () => back()
    tg.BackButton.onClick(handler)
    onBeforeUnmount(() => {
      try {
        tg.BackButton.offClick(handler)
      } catch {}
      tg.BackButton.hide()
    })
  }
})
onBeforeUnmount(() => {
  const el = swipeEl.value
  el?.removeEventListener('touchstart', onTouchStart as any)
  el?.removeEventListener('touchmove', onTouchMove as any)
  el?.removeEventListener('touchend', onTouchEnd as any)
})

const loading = ref(false)
const error = ref<string | null>(null)

async function confirm() {
  if (!chosenDate.value || !startAt.value || !endAt.value) return
  loading.value = true
  error.value = null
  try {
    const payload = {
      room_id: props.room.id,
      start_datetime: startAt.value.toISOString(),
      end_datetime: endAt.value.toISOString(),
      // Можно добавить поле для комментария
    }
    const result = await bookingStore.createBooking(payload)

    emit('success', result)
    emit('close')
  } catch (e: any) {
    error.value = e.message || 'Не удалось создать бронь. Пожалуйста, попробуйте ещё раз.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div
    class="flex flex-col p-0 m-0 h-full max-w-lg mx-auto w-full tg-bg tg-text px-4"
    ref="swipeEl"
  >
    <div class="sticky top-0 z-20 tg-bg border-b tg-border mt-4">
      <div class="px-4 pt-2 pb-3 flex items-center justify-between">
        <div class="tg-hint">{{ room.name }}</div>
        <div class="tg-hint">{{ step + 1 }}/3</div>
      </div>
    </div>

    <div class="relative flex-1 overflow-hidden">
      <div
        class="absolute inset-0 flex transition-transform duration-200"
        :style="{ transform: `translateX(-${step * 100}%)` }"
      >
        <!-- Step 1 -->
        <div class="min-w-full overflow-y-auto">
          <DateStep v-model="chosenDate" :min-date="now()" :busy="busy" />
        </div>
        <!-- Step 2 -->
        <div class="min-w-full overflow-y-auto">
          <TimeStep
            v-if="chosenDate"
            :date="chosenDate"
            :busy="busy"
            :start="startAt"
            :end="endAt"
            @update:start="startAt = $event"
            @update:end="endAt = $event"
          />
        </div>
        <!-- Step 3 -->
        <div class="min-w-full overflow-y-auto">
          <div class="p-4">
            <h3 class="text-lg font-semibold tg-text">Подтверждение</h3>
            <div class="mt-3 rounded-lg border tg-border p-3 tg-secondary-bg">
              <div class="grid grid-cols-2 gap-3">
                <div>
                  <div class="text-sm tg-hint">Помещение</div>
                  <div class="tg-text font-medium">{{ room.name }}</div>
                </div>
                <div>
                  <div class="text-sm tg-hint">Дата</div>
                  <div class="tg-text font-medium">
                    {{ chosenDate?.toLocaleDateString('ru-RU', { dateStyle: 'medium' }) }}
                  </div>
                </div>
                <div>
                  <div class="text-sm tg-hint">Начало</div>
                  <div class="tg-text font-medium">
                    {{
                      startAt?.toLocaleTimeString('ru-RU', {
                        hour: '2-digit',
                        minute: '2-digit',
                      })
                    }}
                  </div>
                </div>
                <div>
                  <div class="text-sm tg-hинt">Окончание</div>
                  <div class="tg-text font-medium">
                    {{
                      endAt?.toLocaleTimeString('ru-RU', {
                        hour: '2-digit',
                        minute: '2-digit',
                      })
                    }}
                  </div>
                </div>
              </div>
            </div>

            <div class="mt-3 rounded-lg border tg-border p-3 tg-secondary-bg tg-text">
              Ваш запрос будет отправлен администратору. После одобрения вы получите уведомление
            </div>

            <div v-if="error" class="mt-3 text-sm text-red-600">{{ error }}</div>
          </div>
        </div>
      </div>
    </div>

    <div class="sticky flex gap-4 bottom-0 tg-bg border-t tg-border p-4">
      <button
        v-if="step < 2"
        class="w-full py-2 font-semibold tg-btn rounded-lg disabled:opacity-50"
        :disabled="!canNext"
        @click="next"
      >
        Далее
      </button>
      <button
        v-else
        class="w-full py-2 font-semibold tg-btn rounded-lg disabled:opacity-50"
        :disabled="loading"
        @click="confirm"
      >
        {{ loading ? 'Отправка...' : 'Подтвердить' }}
      </button>
      <button
        class="w-full py-2 border tg-border font-semibold tg-btn-invert rounded-lg disabled:opacity-50"
        @click="back"
      >
        Назад
      </button>
    </div>
  </div>
</template>
