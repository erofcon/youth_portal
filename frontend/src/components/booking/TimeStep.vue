<script setup lang="ts">
import { computed } from 'vue'

type BusyInterval = { start: string; end: string }
type Props = {
  date: Date
  start: Date | null
  end: Date | null
  busy?: BusyInterval[]
  workingHours?: { from: string; to: string } // '09:00', '18:00'
  minDurationMin?: number
}
const props = withDefaults(defineProps<Props>(), {
  busy: () => [],
  workingHours: () => ({ from: '09:00', to: '18:00' }),
  minDurationMin: 60,
})
const emit = defineEmits<{
  (e: 'update:start', v: Date | null): void
  (e: 'update:end', v: Date | null): void
}>()

const stepMin = 30
const now = () => new Date()

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

const dayStart = computed(() => toStartOfDay(props.date))
const dayEnd = computed(() => toEndOfDay(props.date))

const busyDay = computed(() => {
  const ds = dayStart.value,
    de = dayEnd.value
  const arr = props
    .busy!.map((b) => ({ start: parseISO(b.start), end: parseISO(b.end) }))
    .filter((x) => x.end > ds && x.start < de)
    .map((x) => ({
      start: x.start < ds ? ds : x.start,
      end: x.end > de ? de : x.end,
    }))
  arr.sort((a, b) => a.start.getTime() - b.start.getTime())
  return arr
})

const workStartRaw = computed(() => withHM(dayStart.value, props.workingHours!.from))
const workEnd = computed(() => withHM(dayStart.value, props.workingHours!.to))

const earliestStartMin = computed(() => {
  if (isSameDay(props.date, now())) {
    const oneHourFromNow = addMin(now(), 60)
    const base = new Date(Math.max(workStartRaw.value.getTime(), oneHourFromNow.getTime()))
    return ceilToStep(base, stepMin)
  }
  return workStartRaw.value
})

function insideBusy(dt: Date) {
  return busyDay.value.some((b) => dt >= b.start && dt < b.end)
}

function nextBusyStartAfter(dt: Date): Date | null {
  const c = busyDay.value.filter((b) => b.start > dt).map((b) => b.start)
  if (!c.length) return null
  return c.sort((a, b) => a.getTime() - b.getTime())[0]
}

const startSlots = computed(() => {
  const out: Date[] = []
  const latestStart = addMin(workEnd.value, -props.minDurationMin!)
  for (let t = new Date(earliestStartMin.value); t <= latestStart; t = addMin(t, stepMin)) {
    if (insideBusy(t)) continue
    const earliestEnd = addMin(t, props.minDurationMin!)
    const cap = nextBusyStartAfter(t) ?? workEnd.value
    if (earliestEnd <= cap) out.push(new Date(t))
  }
  return out
})

const endSlots = computed(() => {
  if (!props.start) return []
  const earliest = addMin(props.start, props.minDurationMin!)
  const cap = nextBusyStartAfter(props.start) ?? workEnd.value
  const out: Date[] = []
  for (let t = new Date(earliest); t <= cap; t = addMin(t, stepMin)) out.push(new Date(t))
  return out
})

const hasBusy = computed(() => busyDay.value.length > 0)
const noStartSlots = computed(() => startSlots.value.length === 0)

const fullDayAllowed = computed(
  () =>
    !hasBusy.value &&
    earliestStartMin.value.getTime() === workStartRaw.value.getTime() &&
    workEnd.value > workStartRaw.value,
)

function rangeBlocked(s: Date, e: Date) {
  if (s < earliestStartMin.value || e > workEnd.value) return true
  if (e.getTime() - s.getTime() < props.minDurationMin! * 60 * 1000) return true
  return busyDay.value.some((b) => s < b.end && e > b.start)
}

function pickStart(t: Date) {
  emit('update:start', t)
  const minEnd = addMin(t, props.minDurationMin!)
  const cap = nextBusyStartAfter(t) ?? workEnd.value
  emit('update:end', minEnd <= cap ? minEnd : null)
}

function pickEnd(t: Date) {
  if (!props.start) return
  if (!rangeBlocked(props.start, t)) emit('update:end', t)
}

function applyFirstHalf() {
  const s = withHM(dayStart.value, '09:00')
  const e = withHM(dayStart.value, '13:00')
  if (!rangeBlocked(s, e)) {
    emit('update:start', s)
    emit('update:end', e)
  }
}

function applySecondHalf() {
  const s = withHM(dayStart.value, '13:00')
  const e = withHM(dayStart.value, '18:00')
  if (!rangeBlocked(s, e)) {
    emit('update:start', s)
    emit('update:end', e)
  }
}

function applyFullDay() {
  if (!fullDayAllowed.value) return
  const s = withHM(dayStart.value, '09:00')
  const e = withHM(dayStart.value, '18:00')
  emit('update:start', s)
  emit('update:end', e)
}
</script>

<template>
  <div class="flex flex-col h-full">
    <div class="px-4 pt-2">
      <div class="flex items-center justify-between">
        <h2 class="text-lg font-semibold tg-text">
          {{ date.toLocaleDateString('ru-RU', { day: '2-digit', month: 'long' }) }}
        </h2>
        <div class="text-lg tg-hint">
          {{ workStartRaw.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' }) }}–{{
            workEnd.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
          }}
        </div>
      </div>

      <div class="mt-4 flex gap-2 flex-wrap">
        <button
          class="tg-btn text-xs font-medium px-3 py-1 rounded-full disabled:opacity-50"
          :disabled="rangeBlocked(withHM(dayStart, '09:00'), withHM(dayStart, '13:00'))"
          @click="applyFirstHalf"
        >
          1-я половина (09:00–13:00)
        </button>
        <button
          class="tg-btn text-xs font-medium px-3 py-1 rounded-full disabled:opacity-50"
          :disabled="rangeBlocked(withHM(dayStart, '13:00'), withHM(dayStart, '18:00'))"
          @click="applySecondHalf"
        >
          2-я половина (13:00–18:00)
        </button>
        <button
          class="tg-btn text-xs font-medium px-3 py-1 rounded-full disabled:opacity-50"
          :disabled="!fullDayAllowed"
          @click="applyFullDay"
        >
          Целый день
        </button>
      </div>

      <div v-if="hasBusy" class="mt-3 rounded-lg border tg-border p-3 tg-secondary-bg text-xs">
        В этот день есть занятые интервалы — недоступные слоты отключены.
      </div>
    </div>

    <div v-if="!noStartSlots" class="px-4 mt-5">
      <div class="text-sm tg-hint mb-2">Время начала</div>
      <div class="grid grid-cols-4 gap-2">
        <button
          v-for="t in startSlots"
          :key="t.toISOString()"
          class="px-2 py-2 rounded-lg border tg-border text-sm hover:opacity-90"
          :class="start && t.getTime() === start.getTime() ? 'tg-btn' : 'tg-secondary-bg'"
          @click="pickStart(t)"
        >
          {{ t.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' }) }}
        </button>
      </div>

      <div class="text-sm tg-hint mt-5 mb-2">Время окончания</div>
      <div class="grid grid-cols-4 gap-2 pb-4">
        <button
          v-for="t in endSlots"
          :key="t.toISOString()"
          class="px-2 py-2 rounded-lg border tg-border text-sm hover:opacity-90"
          :class="end && t.getTime() === end.getTime() ? 'tg-btn' : 'tg-secondary-bg'"
          @click="pickEnd(t)"
        >
          {{ t.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' }) }}
        </button>
      </div>
    </div>

    <div v-else class="px-4 mt-5 rounded-lg border tg-border p-3 tg-secondary-bg text-sm">
      На выбранную дату свободных слотов нет. Выберите другую дату.
    </div>
  </div>
</template>
