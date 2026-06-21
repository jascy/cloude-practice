import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/HomeView.vue')
  },
  {
    path: '/qa/:id',
    name: 'Detail',
    component: () => import('../views/DetailView.vue')
  },
  {
    path: '/import',
    name: 'Import',
    component: () => import('../views/ImportView.vue')
  },
  {
    path: '/manage',
    name: 'Manage',
    component: () => import('../views/ManageView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
