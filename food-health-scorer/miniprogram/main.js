import { createSSRApp } from 'vue';
import App from './App.vue';

// 添加调试信息
console.log('开始初始化应用...');

// 检测当前运行环境
const isH5 = typeof window !== 'undefined' && typeof document !== 'undefined';
const isMiniProgram = typeof wx !== 'undefined' && typeof wx.getSystemInfoSync === 'function';

console.log('当前环境检测:', { isH5, isMiniProgram });

// 添加全局错误处理
if (isH5) {
  window.addEventListener('error', (event) => {
    console.error('全局错误捕获:', event.error);
  });
  
  window.addEventListener('unhandledrejection', (event) => {
    console.error('未处理的Promise错误:', event.reason);
  });
}

export function createApp() {
  console.log('创建Vue应用...');
  
  try {
    const app = createSSRApp(App);
    
    // 添加全局错误处理
    app.config.errorHandler = (err, vm, info) => {
      console.error('应用错误:', err);
      console.error('错误信息:', info);
    };
    
    console.log('应用创建成功');
    
    // 可以在这里进行全局配置
    // 例如：注册全局组件、添加全局属性等
    
    // 控制台输出，用于调试
    console.log('应用已初始化', process.env.UNI_PLATFORM);
    
    return {
      app
    };
  } catch (error) {
    console.error('创建Vue应用失败:', error);
    throw error;
  }
}
