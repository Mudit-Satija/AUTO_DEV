import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Login from '../views/Login.vue'
import Orders from '../views/Orders.vue'

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/orders',
    name: 'Orders',
    component: Orders
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router