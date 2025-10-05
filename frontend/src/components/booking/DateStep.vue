<!-- components/steps/DateStep.vue -->
<script setup lang="ts">
import { computed, ref, watch } from 'vue'

type BusyInterval = { start: string; end: string }
type Props = {
  modelValue: Date | null
  minDate: Date
  busy?: BusyInterval[]
}
const props = withDefaults(defineProps<Props>(), { busy: () => [] })
const emit = defineEmits<{ (e: 'update:modelValue', v: Date | null): void }>()

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

const toStartOfDay = (d: Date) => new Date(d.getFullYear(), d.getMonth(), d.getDate(), 0, 0, 0, 0)
const toEndOfDay = (d: Date) =>
  new Date(d.getFullYear(), d.getMonth(), d.getDate(), 23, 59, 59, 999)
const parseISO = (s: string) => new Date(s)
const isSameDay = (a: Date, b: Date) => a.toDateString() === b.toDateString()

const busyIntervals = computed(() =>
  props.busy!.map((b) => ({ start: parseISO(b.start), end: parseISO(b.end) })),
)

function dayBusyType(day: Date): 'none' | 'partial' | 'full' {
  const s = toStartOfDay(day),
    e = toEndOfDay(day)
  let partial = false
  for (const x of busyIntervals.value) {
    if (x.start <= s && x.end >= e) return 'full'
    if (x.end > s && x.start < e) partial = true
  }
  return partial ? 'partial' : 'none'
}

const daysGrid = computed(() => {
  const first = new Date(viewMonth.value.getFullYear(), viewMonth.value.getMonth(), 1)
  const weekday = (first.getDay() + 6) % 7 // пн=0
  const start = new Date(first)
  start.setDate(first.getDate() - weekday)
  const arr: { d: Date; inMonth: boolean; disabled: boolean; busy: 'none' | 'partial' | 'full' }[] =
    []
  for (let i = 0; i < 42; i++) {
    const d = new Date(start)
    d.setDate(start.getDate() + i)
    const disabled = toEndOfDay(d) < toStartOfDay(props.minDate)
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

      <div class="mb-8">
        <div
          v-if="selectedBusy === 'full'"
          class="mt-3 rounded-lg border tg-border p-3 tg-secondary-bg text-sm"
        >
          Этот день полностью занят. Пожалуйста, выберите другой.
        </div>
        <div
          v-else-if="selectedBusy === 'partial'"
          class="mt-3 rounded-lg border tg-border p-3 tg-secondary-bg text-sm"
        >
          В этот день есть занятые интервалы. На следующем шаге будут доступны свободные слоты.
        </div>
      </div>
    </div>
  </section>
</template>
