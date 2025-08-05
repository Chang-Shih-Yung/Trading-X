import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import './style.css'

// 創建應用實例
const app = createApp(App)

// 安裝插件
app.use(createPinia())
app.use(router)

// 掛載應用
app.mount('#app')
