import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import EventsView from '@/views/EventsView.vue'
import BookingView from '@/views/BookingView.vue'
import OrganizationsView from '@/views/OrganizationsView.vue'
import LaunchView from '@/views/LaunchView.vue' // <-- Импортируем новый компонент

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/launch',
      name: 'launch',
      component: LaunchView,
    },
    {
      path: '/',
      redirect: '/launch',
    },
    {
      path: '/app',
      children: [
        {
          path: '',
          name: 'home',
          component: HomeView,
        },
        {
          path: 'events',
          name: 'events',
          component: EventsView,
        },
        {
          path: 'booking',
          name: 'booking',
          component: BookingView,
        },
        {
          path: 'organizations',
          name: 'organizations',
          component: OrganizationsView,
        },
      ],
    },
  ],
})

export default router
