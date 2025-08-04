<template>
  <div id="app">
    <nav class="bg-gray-900 shadow-lg">
      <div class="max-w-7xl mx-auto px-4">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <h1 class="text-white text-xl font-bold">Trading X</h1>
          </div>
          <div class="flex items-center space-x-4">
            <router-link v-for="item in navigation" :key="item.name" :to="item.href"
              class="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium"
              :class="{ 'bg-gray-700': $route.path === item.href }">
              {{ item.name }}
            </router-link>
          </div>
        </div>
      </div>
    </nav>

    <main class="min-h-screen bg-gray-100">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'

const navigation = reactive([
  { name: '儀表板', href: '/' },
  { name: '交易信號', href: '/signals' },
  { name: '實時策略', href: '/trading-strategy' },
  { name: '🎯 狙擊手計劃', href: '/sniper-strategy' },
  { name: '信號歷史', href: '/signal-history' },
  { name: '市場數據', href: '/market' },
  { name: '新聞分析', href: '/news' },
  { name: '回測', href: '/backtest' },
  { name: '策略', href: '/strategies' }
])
</script>

<style scoped>
/* 可以添加自定義樣式 */
</style>
