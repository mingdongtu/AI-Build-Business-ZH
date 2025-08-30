<template>
  <view class="fallback-container">
    <view class="fallback-header">
      <text class="fallback-title">应用加载异常</text>
    </view>
    <view class="fallback-content">
      <text class="fallback-message">{{ errorMessage || '应用加载过程中遇到了问题' }}</text>
      <view class="fallback-details" v-if="errorDetails">
        <text class="fallback-details-title">错误详情:</text>
        <text class="fallback-details-content">{{ errorDetails }}</text>
      </view>
    </view>
    <view class="fallback-actions">
      <button class="fallback-button" @click="reloadApp">重新加载</button>
      <button class="fallback-button secondary" @click="reportError">报告问题</button>
    </view>
    <view class="fallback-debug" v-if="showDebugInfo">
      <text class="fallback-debug-title">调试信息:</text>
      <text class="fallback-debug-info">平台: {{ platform }}</text>
      <text class="fallback-debug-info">路由: {{ currentRoute }}</text>
      <text class="fallback-debug-info">时间: {{ currentTime }}</text>
    </view>
  </view>
</template>

<script>
export default {
  name: 'FallbackError',
  props: {
    errorMessage: {
      type: String,
      default: ''
    },
    errorDetails: {
      type: String,
      default: ''
    },
    showDebugInfo: {
      type: Boolean,
      default: true
    }
  },
  data() {
    return {
      platform: '未知',
      currentRoute: '未知',
      currentTime: new Date().toLocaleString()
    }
  },
  mounted() {
    // 检测平台
    // #ifdef H5
    this.platform = 'H5';
    // #endif
    
    // #ifdef MP-WEIXIN
    this.platform = '微信小程序';
    // #endif
    
    // 获取当前路由信息
    try {
      const pages = getCurrentPages();
      if (pages && pages.length > 0) {
        const currentPage = pages[pages.length - 1];
        this.currentRoute = currentPage.route || '未知路由';
      }
    } catch (err) {
      console.error('获取路由信息失败:', err);
    }
  },
  methods: {
    reloadApp() {
      // #ifdef H5
      window.location.reload();
      // #endif
      
      // #ifdef MP-WEIXIN
      const pages = getCurrentPages();
      if (pages && pages.length > 0) {
        const currentPage = pages[pages.length - 1];
        if (currentPage && currentPage.onLoad) {
          currentPage.onLoad(currentPage.options || {});
        }
      }
      // #endif
    },
    reportError() {
      // 实现错误报告逻辑
      uni.showModal({
        title: '错误报告',
        content: '是否将此错误报告给开发者？',
        success: (res) => {
          if (res.confirm) {
            // 这里可以实现错误上报逻辑
            uni.showToast({
              title: '已报告问题',
              icon: 'success'
            });
          }
        }
      });
    }
  }
}
</script>

<style>
.fallback-container {
  padding: 40rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 80vh;
  background-color: #f8f8f8;
}

.fallback-header {
  margin-bottom: 40rpx;
  text-align: center;
}

.fallback-title {
  font-size: 40rpx;
  font-weight: bold;
  color: #333;
}

.fallback-content {
  background-color: #fff;
  border-radius: 12rpx;
  padding: 30rpx;
  width: 90%;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.1);
  margin-bottom: 40rpx;
}

.fallback-message {
  font-size: 32rpx;
  color: #333;
  line-height: 1.5;
  margin-bottom: 20rpx;
}

.fallback-details {
  margin-top: 20rpx;
  padding-top: 20rpx;
  border-top: 1px solid #eee;
}

.fallback-details-title {
  font-size: 28rpx;
  color: #666;
  margin-bottom: 10rpx;
  display: block;
}

.fallback-details-content {
  font-size: 24rpx;
  color: #999;
  background-color: #f5f5f5;
  padding: 16rpx;
  border-radius: 8rpx;
  word-break: break-all;
  display: block;
}

.fallback-actions {
  display: flex;
  flex-direction: row;
  justify-content: center;
  margin-bottom: 40rpx;
}

.fallback-button {
  margin: 0 20rpx;
  background-color: #2196F3;
  color: #fff;
  border: none;
  padding: 20rpx 40rpx;
  border-radius: 8rpx;
  font-size: 28rpx;
}

.fallback-button.secondary {
  background-color: #f5f5f5;
  color: #333;
}

.fallback-debug {
  width: 90%;
  background-color: #f5f5f5;
  padding: 20rpx;
  border-radius: 8rpx;
  margin-top: 20rpx;
}

.fallback-debug-title {
  font-size: 24rpx;
  color: #666;
  margin-bottom: 10rpx;
  display: block;
}

.fallback-debug-info {
  font-size: 22rpx;
  color: #999;
  display: block;
  margin-bottom: 6rpx;
}
</style>
