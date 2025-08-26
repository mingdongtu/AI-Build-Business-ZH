<template>
  <div class="home">
    <h2>食品健康评分</h2>
    <p class="subtitle">拍摄食品包装袋配料表，获取健康评分和分析</p>
    
    <image-analyzer />
    
    <div class="features-section">
      <h3>功能介绍</h3>
      <div class="features-grid">
        <div class="feature-item">
          <div class="feature-icon">📷</div>
          <div class="feature-title">拍照识别</div>
          <div class="feature-desc">直接拍摄食品包装上的配料表</div>
        </div>
        <div class="feature-item">
          <div class="feature-icon">🔍</div>
          <div class="feature-title">智能分析</div>
          <div class="feature-desc">自动识别配料成分及健康影响</div>
        </div>
        <div class="feature-item">
          <div class="feature-icon">📊</div>
          <div class="feature-title">健康评分</div>
          <div class="feature-desc">根据配料表给出0-100分健康评分</div>
        </div>
        <div class="feature-item">
          <div class="feature-icon">💡</div>
          <div class="feature-title">健康建议</div>
          <div class="feature-desc">提供个性化的健康饮食建议</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ImageAnalyzer from '@/components/ImageAnalyzer.vue';

export default {
  name: 'HomeView',
  components: {
    ImageAnalyzer
  }
}
</script>

<style scoped>
.home {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.subtitle {
  color: #666;
  margin-bottom: 30px;
  font-size: 16px;
}

.features-section {
  margin-top: 40px;
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 10px;
}

.features-section h3 {
  text-align: center;
  margin-bottom: 20px;
  color: #333;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.feature-item {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  text-align: center;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.feature-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.feature-icon {
  font-size: 28px;
  margin-bottom: 10px;
}

.feature-title {
  font-weight: bold;
  margin-bottom: 8px;
  color: #2196F3;
}

.feature-desc {
  font-size: 14px;
  color: #666;
}

/* 移动端适配 */
@media (max-width: 600px) {
  .features-grid {
    grid-template-columns: 1fr;
  }
  
  .feature-item {
    padding: 15px;
  }
}
</style>
