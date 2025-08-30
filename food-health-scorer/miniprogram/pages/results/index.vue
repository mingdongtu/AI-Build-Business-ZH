<template>
  <view class="results-container">
    <view class="header">
      <text class="title">健康评分结果</text>
    </view>
    
    <view class="score-section">
      <view class="score-circle" :style="{ backgroundColor: scoreColor }">
        <text class="score-text">{{ result.score }}</text>
      </view>
      <text class="score-label">{{ scoreLabel }}</text>
    </view>
    
    <view class="details-section">
      <view class="section-title">
        <text>食品详情</text>
      </view>
      
      <view class="food-info">
        <view class="info-item" v-for="(value, key) in result.details" :key="key">
          <text class="info-label">{{ formatLabel(key) }}:</text>
          <text class="info-value">{{ value }}</text>
        </view>
      </view>
    </view>
    
    <view class="ingredients-section">
      <view class="section-title">
        <text>配料表分析</text>
      </view>
      
      <view class="ingredients-list">
        <view class="ingredient-item" v-for="(ingredient, index) in result.ingredients" :key="index" 
              :class="{ 'healthy': ingredient.health_index > 70, 'warning': ingredient.health_index > 30 && ingredient.health_index <= 70, 'danger': ingredient.health_index <= 30 }">
          <text class="ingredient-name">{{ ingredient.name }}</text>
          <text class="ingredient-health">{{ ingredient.health_index }}</text>
        </view>
      </view>
    </view>
    
    <view class="recommendations-section">
      <view class="section-title">
        <text>健康建议</text>
      </view>
      
      <view class="recommendations-list">
        <text class="recommendation-item" v-for="(recommendation, index) in result.recommendations" :key="index">
          {{ index + 1 }}. {{ recommendation }}
        </text>
      </view>
    </view>
    
    <button class="back-btn" @click="goBack">返回首页</button>
  </view>
</template>

<script>
export default {
  data() {
    return {
      result: {
        score: 0,
        details: {},
        ingredients: [],
        recommendations: []
      }
    }
  },
  computed: {
    scoreColor() {
      const score = this.result.score;
      if (score > 70) return '#4CAF50'; // 绿色 - 健康
      if (score > 30) return '#FFC107'; // 黄色 - 中等
      return '#F44336'; // 红色 - 不健康
    },
    scoreLabel() {
      const score = this.result.score;
      if (score > 70) return '健康';
      if (score > 30) return '中等';
      return '不健康';
    }
  },
  onLoad() {
    // 从缓存中获取分析结果
    try {
      const analysisResult = uni.getStorageSync('analysisResult');
      if (analysisResult) {
        this.result = analysisResult;
      } else {
        uni.showToast({
          title: '未找到分析结果',
          icon: 'none'
        });
        setTimeout(() => {
          this.goBack();
        }, 1500);
      }
    } catch (e) {
      console.error('获取分析结果失败:', e);
      uni.showToast({
        title: '获取分析结果失败',
        icon: 'none'
      });
    }
  },
  methods: {
    formatLabel(key) {
      // 将下划线分隔的字符串转换为可读的标签
      return key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
    },
    goBack() {
      uni.navigateBack({
        delta: 1
      });
    }
  }
}
</script>

<style>
.results-container {
  padding: 30rpx;
}

.header {
  text-align: center;
  margin-bottom: 40rpx;
}

.title {
  font-size: 40rpx;
  font-weight: bold;
}

.score-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 50rpx;
}

.score-circle {
  width: 200rpx;
  height: 200rpx;
  border-radius: 100rpx;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 20rpx;
}

.score-text {
  font-size: 60rpx;
  font-weight: bold;
  color: white;
}

.score-label {
  font-size: 36rpx;
  font-weight: bold;
}

.section-title {
  font-size: 34rpx;
  font-weight: bold;
  margin-bottom: 20rpx;
  padding-bottom: 10rpx;
  border-bottom: 1px solid #eee;
}

.details-section, .ingredients-section, .recommendations-section {
  margin-bottom: 40rpx;
}

.food-info {
  background-color: #f9f9f9;
  border-radius: 10rpx;
  padding: 20rpx;
}

.info-item {
  display: flex;
  margin-bottom: 10rpx;
}

.info-label {
  font-weight: bold;
  width: 200rpx;
}

.ingredients-list {
  background-color: #f9f9f9;
  border-radius: 10rpx;
  padding: 20rpx;
}

.ingredient-item {
  display: flex;
  justify-content: space-between;
  padding: 10rpx;
  margin-bottom: 10rpx;
  border-radius: 5rpx;
}

.healthy {
  background-color: rgba(76, 175, 80, 0.1);
}

.warning {
  background-color: rgba(255, 193, 7, 0.1);
}

.danger {
  background-color: rgba(244, 67, 54, 0.1);
}

.recommendations-list {
  background-color: #f9f9f9;
  border-radius: 10rpx;
  padding: 20rpx;
}

.recommendation-item {
  display: block;
  margin-bottom: 15rpx;
}

.back-btn {
  background-color: #2196F3;
  color: white;
  border-radius: 10rpx;
  font-size: 32rpx;
  margin-top: 30rpx;
}
</style>
