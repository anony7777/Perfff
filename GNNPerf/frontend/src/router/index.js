import Vue from 'vue'
import VueRouter from 'vue-router'

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../components/Main')
  },
  {
    path: '/main/',
    name: 'Main',
    component: () => import('../components/Main')
  },
  {
    path: '/chart/',
    name: 'Chart',
    component: () => import('../components/Chart')
  },
  {
    path: '/resultlist/',
    name: 'ResultList',
    component: () => import('../components/ResultList')
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
