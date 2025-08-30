<script>
import FallbackError from './components/FallbackError.vue';

export default {
  components: {
    FallbackError
  },
  data() {
    return {
      hasError: false,
      errorMessage: '',
      errorDetails: ''
    };
  },
  onLaunch: function() {
    console.log('App Launch');
    // 检查运行环境
    const platform = process.env.UNI_PLATFORM || 'unknown';
    console.log('当前运行平台:', platform);
    
    // 初始化工作
    this.initApp();
    
    // 添加全局错误处理
    // #ifdef H5
    if (typeof window !== 'undefined') {
      window.addEventListener('error', (event) => {
        this.handleGlobalError(event.error || event.message);
      });
      
      window.addEventListener('unhandledrejection', (event) => {
        this.handleGlobalError(event.reason || '未处理的Promise错误');
      });
    }
    // #endif
  },
  onShow: function() {
    console.log('App Show');
  },
  onHide: function() {
    console.log('App Hide');
  },
  onError: function(err) {
    console.error('应用错误:', err);
    this.handleGlobalError(err);
  },
  methods: {
    initApp() {
      // 在这里进行应用初始化工作
      console.log('应用初始化中...');
      
      try {
        // 检查是否是H5环境
        // #ifdef H5
        console.log('检测到H5环境');
        // 检查H5环境下的必要对象
        if (typeof window === 'undefined' || typeof document === 'undefined') {
          throw new Error('H5环境缺失必要对象');
        }
        // #endif
        
        // 检查是否是小程序环境
        // #ifdef MP-WEIXIN
        console.log('检测到微信小程序环境');
        // #endif
      } catch (error) {
        console.error('初始化错误:', error);
        this.handleGlobalError(error);
      }
    },
    handleGlobalError(error) {
      console.error('处理全局错误:', error);
      this.hasError = true;
      this.errorMessage = error?.message || '应用加载失败';
      this.errorDetails = error?.stack || JSON.stringify(error);
      
      // 可以在这里添加错误上报逻辑
    }
  }
};
</script>

<template>
  <fallback-error v-if="hasError" 
    :errorMessage="errorMessage" 
    :errorDetails="errorDetails" 
    :showDebugInfo="true" />
  <view v-else>
    <!-- 应用内容将由页面路由器加载 -->
  </view>
</template>

<style>
/* 全局样式 */
page {
  font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Helvetica, Segoe UI, Arial, Roboto, 'PingFang SC', 'miui', 'Hiragino Sans GB', 'Microsoft Yahei', sans-serif;
  font-size: 28rpx;
  line-height: 1.5;
  color: #333;
  background-color: #f8f8f8;
  box-sizing: border-box;
}

/* 适配暗黑模式 */
@media (prefers-color-scheme: dark) {
  page {
    background-color: #1a1a1a;
    color: #f5f5f5;
  }
}

/* 通用容器样式 */
.container {
  padding: 30rpx;
}

/* 按钮样式 */
button {
  margin: 20rpx 0;
}

/* 文本样式 */
.title {
  font-size: 40rpx;
  font-weight: bold;
  margin-bottom: 20rpx;
}

.subtitle {
  font-size: 32rpx;
  color: #666;
  margin-bottom: 30rpx;
}

/* 卡片样式 */
.card {
  background-color: #fff;
  border-radius: 10rpx;
  padding: 30rpx;
  margin-bottom: 30rpx;
  box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.05);
}

/* 列表样式 */
.list-item {
  padding: 20rpx 0;
  border-bottom: 1rpx solid #eee;
}

.list-item:last-child {
  border-bottom: none;
}
</style>
