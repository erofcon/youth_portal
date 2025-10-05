<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'

type Props = {
  modelValue: boolean
  closeOnBackdrop?: boolean
  closeOnEsc?: boolean
}
const props = withDefaults(defineProps<Props>(), {
  closeOnBackdrop: false,
  closeOnEsc: false,
})

const isOpen = computed(() => props.modelValue)

function lockScroll(lock: boolean) {
  const el = document.documentElement
  lock ? el.classList.add('overflow-hidden') : el.classList.remove('overflow-hidden')
}

watch(isOpen, (v) => lockScroll(v), { immediate: true })

const root = ref<HTMLElement | null>(null)
let startY = 0
let activeScrollable: HTMLElement | null = null

function isScrollable(el: HTMLElement) {
  const style = window.getComputedStyle(el)
  const canScrollY = /(auto|scroll|overlay)/.test(style.overflowY)
  return canScrollY && el.scrollHeight > el.clientHeight
}

function findScrollable(start: EventTarget | null): HTMLElement | null {
  let el = start as HTMLElement | null
  while (el && el !== root.value) {
    if (el instanceof HTMLElement && isScrollable(el)) return el
    el = el.parentElement
  }
  return null
}

function onTouchStart(e: TouchEvent) {
  if (!isOpen.value) return
  startY = e.touches[0].clientY
  activeScrollable = findScrollable(e.target)
}

function onTouchMove(e: TouchEvent) {
  if (!isOpen.value) return
  if (!activeScrollable) {
    e.preventDefault()
    return
  }
  const dy = e.touches[0].clientY - startY
  const atTop = activeScrollable.scrollTop <= 0
  const atBottom =
    activeScrollable.scrollTop + activeScrollable.clientHeight >= activeScrollable.scrollHeight
  const isVertical = Math.abs(dy) > 6
  if ((atTop && dy > 0 && isVertical) || (atBottom && dy < 0 && isVertical)) {
    e.preventDefault()
  }
}

onMounted(() => {
  root.value?.addEventListener('touchstart', onTouchStart, { passive: false })
  root.value?.addEventListener('touchmove', onTouchMove, { passive: false })
})
onBeforeUnmount(() => {
  lockScroll(false)
  root.value?.removeEventListener('touchstart', onTouchStart as any)
  root.value?.removeEventListener('touchmove', onTouchMove as any)
})
</script>

<template>
  <transition name="fade">
    <div v-if="isOpen" ref="root" class="fixed inset-0 z-50 fs-panel touch-pan-x">
      <div class="absolute inset-0" @click="props.closeOnBackdrop ? close() : undefined" />
      <div class="absolute inset-0 flex">
        <transition name="slide-in">
          <div class="flex flex-col h-full w-full p-0 m-0" v-if="isOpen">
<!--            <div class="min-h-screen max-w-lg mx-auto">-->
              <slot />
<!--            </div>-->

          </div>
        </transition>
      </div>
    </div>
  </transition>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-in-enter-active,
.slide-in-leave-active {
  transition: transform 0.22s ease;
}

.slide-in-enter-from,
.slide-in-leave-to {
  transform: translateX(12%);
}

.fs-panel {
  overscroll-behavior: none;
}

.touch-pan-x {
  touch-action: pan-x;
}
</style>
