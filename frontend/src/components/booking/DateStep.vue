<!-- components/booking/DateStep.vue -->
<script setup lang="ts">
import { computed, ref, watch } from 'vue'

type BusyInterval = { start: string; end: string }

type Props = {
  modelValue: Date | null
  minDate: Date
  busy?: BusyInterval[]
  workingHours?: { from: string; to: string }
  minDurationMin?: number
}

const props = withDefaults(defineProps<Props>(), {
  busy: () => [],
  workingHours: () => ({ from: '09:00', to: '18:00' }),
  minDurationMin: 60,
})

const emit = defineEmits<{
  (e: 'update:modelValue', v: Date | null): void
}>()

const selected = ref<Date>(props.modelValue ?? new Date())

watch(
    () => props.modelValue,
    (v) => {
      if (v) selected.value = v
    },
)

const viewMonth = ref(new Date(selected.value.getFullYear(), selected.value.getMonth(), 1))

function addMonths(n: number) {
  const d = new Date(viewMonth.value)
  d.setMonth(d.getMonth() + n)
  viewMonth.value = d
}

// Utils
const toStartOfDay = (d: Date) =>
    new Date(d.getFullYear(), d.getMonth(), d.getDate(), 0, 0, 0, 0)
const toEndOfDay = (d: Date) =>
    new Date(d.getFullYear(), d.getMonth(), d.getDate(), 23, 59, 59, 999)
const parseISO = (s: string) => new Date(s)
const isSameDay = (a: Date, b: Date) => a.toDateString() === b.toDateString()

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

const busyIntervals = computed(() =>
    props.busy!.map((b) => ({ start: parseISO(b.start), end: parseISO(b.end) })),
)

// Правильная проверка занятости с учетом рабочих часов
function dayBusyType(day: Date): 'none' | 'partial' | 'full' {
  const dayStart = toStartOfDay(day)
  const dayEnd = toEndOfDay(day)

  // Занятые интервалы в этот день
  const dayBusy = busyIntervals.value
      .filter((x) => x.end > dayStart && x.start < dayEnd)
      .map((x) => ({
        start: x.start < dayStart ? dayStart : x.start,
        end: x.end > dayEnd ? dayEnd : x.end,
      }))
      .sort((a, b) => a.start.getTime() - b.start.getTime())

  if (dayBusy.length === 0) return 'none'

  // Рабочие часы
  const workStartRaw = withHM(dayStart, props.workingHours!.from)
  const workEnd = withHM(dayStart, props.workingHours!.to)

  // Для сегодняшнего дня - начало не раньше чем через час
  const now = new Date()
  const earliestStartMin = isSameDay(day, now)
      ? ceilToStep(
          new Date(Math.max(workStartRaw.getTime(), addMin(now, 60).getTime())),
          30,
      )
      : workStartRaw

  // Проверяем есть ли хотя бы один свободный слот минимальной длительности
  const latestStart = addMin(workEnd, -props.minDurationMin!)

  if (earliestStartMin > latestStart) return 'full'

  function insideBusy(t: Date) {
    return dayBusy.some((b) => t >= b.start && t < b.end)
  }

  function nextBusyStartAfter(t: Date) {
    const c = dayBusy.filter((b) => b.start > t).map((b) => b.start)
    return c.sort((a, b) => a.getTime() - b.getTime())[0] ?? null
  }

  // Ищем хотя бы один свободный слот
  for (let t = new Date(earliestStartMin); t <= latestStart; t = addMin(t, 30)) {
    if (insideBusy(t)) continue

    const earliestEnd = addMin(t, props.minDurationMin!)
    const cap = nextBusyStartAfter(t) ?? workEnd

    if (earliestEnd <= cap) {
      // Есть свободный слот - день частично занят (если есть занятые интервалы)
      return 'partial'
    }
  }

  // Нет свободных слотов - день полностью занят
  return 'full'
}

const daysGrid = computed(() => {
  const first = new Date(viewMonth.value.getFullYear(), viewMonth.value.getMonth(), 1)
  const weekday = (first.getDay() + 6) % 7
  const start = new Date(first)
  start.setDate(first.getDate() - weekday)

  const arr: {
    d: Date
    inMonth: boolean
    disabled: boolean
    busy: 'none' | 'partial' | 'full'
  }[] = []

  for (let i = 0; i < 42; i++) {
    const d = new Date(start)
    d.setDate(start.getDate() + i)
    const disabled = toEndOfDay(d) < props.minDate
    arr.push({
      d,
      inMonth: d.getMonth() === viewMonth.value.getMonth(),
      disabled,
      busy: dayBusyType(d),
    })
  }
  return arr
})

function selectDay(d: Date) {
  const day = toStartOfDay(d)
  if (toEndOfDay(day) < props.minDate) return
  selected.value = day
  emit('update:modelValue', day)
}

const selectedBusy = computed(() => dayBusyType(selected.value))

const weekDays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']

function presetOffset(days: number) {
  const d = new Date()
  d.setDate(d.getDate() + days)
  selectDay(d)
}
</script>

<template>
  <section class="flex flex-col h-full mb-8">
    <div class="p-4 border-b tg-border sticky top-0 tg-bg z-10">
      <div class="flex gap-2 justify-between items-center">
        <div class="flex gap-2">
          <button class="tg-btn h-8 text-xs px-3 py-1 rounded-full" @click="presetOffset(1)">
            Завтра
          </button>
          <button class="tg-btn h-8 text-xs px-3 py-1 rounded-full" @click="presetOffset(2)">
            Послезавтра
          </button>
        </div>
        <div class="flex items-center gap-2">
          <button class="rounded tg-secondary-bg" @click="addMonths(-1)">
            <svg
                class="w-8 h-8 tg-hint"
                xmlns="http://www.w3.org/2000/svg"
                height="40px"
                viewBox="0 -960 960 960"
                width="40px"
                fill="currentColor"
            >
              <path d="M560-280 360-480l200-200v400Z" />
            </svg>
          </button>
          <div class="text-sm tg-hint">
            {{ viewMonth.toLocaleString('ru-RU', { month: 'long', year: 'numeric' }) }}
          </div>
          <button class="rounded tg-secondary-bg text-sm" @click="addMonths(1)">
            <svg
                class="w-8 h-8 tg-hint"
                xmlns="http://www.w3.org/2000/svg"
                height="40px"
                viewBox="0 -960 960 960"
                width="40px"
                fill="currentColor"
            >
              <path d="M400-280v-400l200 200-200 200Z" />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <div class="px-4 pt-4">
      <div class="grid grid-cols-7 text-center text-xs tg-hint mb-2">
        <div v-for="w in weekDays" :key="w" class="py-1">{{ w }}</div>
      </div>
      <div class="grid grid-cols-7 gap-1">
        <button
            v-for="cell in daysGrid"
            :key="cell.d.toISOString()"
            :disabled="cell.disabled"
            @click="!cell.disabled && selectDay(cell.d)"
            class="aspect-square rounded-lg border tg-border flex items-center justify-center text-sm relative"
            :class="[
            !cell.inMonth ? 'opacity-50' : '',
            cell.disabled ? 'opacity-40 cursor-not-allowed' : 'hover:bg-black/5',
            isSameDay(cell.d, selected) ? 'ring-2 ring-[var(--tg-button-color)]' : '',
          ]"
        >
          <span class="tg-text">{{ cell.d.getDate() }}</span>
          <span
              v-if="cell.busy !== 'none'"
              class="absolute bottom-1 left-1/2 -translate-x-1/2 w-1.5 h-1.5 rounded-full"
              :class="cell.busy === 'full' ? 'bg-red-500' : 'bg-amber-500'"
          />
        </button>
      </div>

      <div class="mt-4 text-xs tg-hint flex items-center gap-3">
        <div class="flex items-center gap-1">
          <span class="w-2 h-2 rounded-full bg-red-500"></span>занят целый день
        </div>
        <div class="flex items-center gap-1">
          <span class="w-2 h-2 rounded-full bg-amber-500"></span>частично занят
        </div>
      </div>

      <!-- Сообщение показывается сразу -->
      <div class="mb-8">
        <div
            v-if="selectedBusy === 'full'"
            class="mt-3 rounded-lg border border-red-200 bg-red-50 dark:bg-red-900/20 dark:border-red-800 p-3 text-sm flex items-start gap-2"
        >
          <span class="text-red-500 text-lg">⚠️</span>
          <span class="tg-text">
            Этот день полностью занят в рабочее время. Пожалуйста, выберите другую дату.
          </span>
        </div>
        <div
            v-else-if="selectedBusy === 'partial'"
            class="mt-3 rounded-lg border border-amber-200 bg-amber-50 dark:bg-amber-900/20 dark:border-amber-800 p-3 text-sm flex items-start gap-2"
        >
          <span class="text-amber-500 text-lg">ℹ️</span>
          <span class="tg-text">
            В этот день есть занятые интервалы. На следующем шаге будут доступны свободные слоты.
          </span>
        </div>
      </div>
    </div>
  </section>
</template>