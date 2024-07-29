import Vue from 'vue'
import VueRouter from 'vue-router'
import HomeView from '../views/HomeView.vue'
import Login from '../views/Login.vue'
import Head from '../views/Head.vue'
import Test from '../views/Test.vue'
Vue.use(VueRouter)

const routes = [
  {
    path: '/conversation',
    name: 'home',
    component: HomeView
  },
  {
    path: '/login',
    name: 'login',
    component: Login
  },
  {
    path: '/',
    name: 'head',
    component: Head
  },
  {
    path:'/test',
    name:'test',
    component:Test
  }
]

const router = new VueRouter({
  routes
})

export default router
