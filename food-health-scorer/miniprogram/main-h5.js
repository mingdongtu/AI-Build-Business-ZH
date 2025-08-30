import { createSSRApp } from 'vue'
import App from './App.vue'
import './styles/index.css'
import { setupErrorHandling, logAppInfo } from './utils/h5-debug'

// 设置错误处理
setupErrorHandling()

// 创建Vue应用实例
const app = createSSRApp(App)

// 可以在这里注册全局组件或添加全局配置

// 记录应用信息（调试用）
logAppInfo(app)

// 挂载应用
app.mount('#app')

// 控制台输出，用于调试
console.log('H5应用已启动 - 时间:', new Date().toLocaleString())

// 导出app实例（可用于调试）
window.$app = app
