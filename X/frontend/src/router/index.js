import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '@/views/Dashboard.vue'
import Signals from '@/views/Signals.vue'
import Monitoring from '@/views/Monitoring.vue'
import Configuration from '@/views/Configuration.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
    meta: {
      title: '監控儀表板',
      icon: 'BarChart3'
    }
  },
  {
    path: '/signals',
    name: 'Signals',
    component: Signals,
    meta: {
      title: '信號管理',
      icon: 'Target'
    }
  },
  {
    path: '/monitoring',
    name: 'Monitoring',
    component: Monitoring,
    meta: {
      title: '實時監控',
      icon: 'Activity'
    }
  },
  {
    path: '/configuration',
    name: 'Configuration',
    component: Configuration,
    meta: {
      title: '系統設定',
      icon: 'Settings'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 設置頁面標題
router.beforeEach((to, from, next) => {
  document.title = `${to.meta.title} | Trading X`
  next()
})

export default router
