import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import AboutView from '../views/AboutView.vue'
import PostView from '../views/PostView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/about',
      name: 'about',
      component: AboutView,
    },
    {
      path: '/posts/:section/:id(\\d+)',
      component: PostView,
      props: route => ({ assetPath: `content/${route.params.section}/${route.params.id}` }),
    }
  ]
})

export default router
