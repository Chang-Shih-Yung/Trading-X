import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '@/views/Dashboard.vue'

const router = createRouter({
    history: createWebHistory(),
    routes: [
        {
            path: '/',
            name: 'Dashboard',
            component: Dashboard
        },
        {
            path: '/enhanced',
            name: 'EnhancedDashboard',
            component: () => import('@/views/EnhancedDashboard.vue')
        },
        {
            path: '/signals',
            name: 'Signals',
            component: () => import('@/views/Signals.vue')
        },
        {
            path: '/signal-history',
            name: 'SignalHistory',
            component: () => import('@/views/SignalHistory.vue')
        },
        {
            path: '/shortterm-history',
            name: 'ShortTermHistory',
            component: () => import('@/views/ShortTermHistory.vue')
        },
        {
            path: '/market',
            name: 'Market',
            component: () => import('@/views/Market.vue')
        },
        {
            path: '/news',
            name: 'NewsAnalysis',
            component: () => import('@/views/NewsAnalysis.vue')
        },
        {
            path: '/backtest',
            name: 'Backtest',
            component: () => import('@/views/Backtest.vue')
        },
        {
            path: '/strategies',
            name: 'Strategies',
            component: () => import('@/views/Strategies.vue')
        },
        {
            path: '/trading-strategy',
            name: 'TradingStrategy',
            component: () => import('@/views/TradingStrategy.vue')
        }
    ]
})

export default router
