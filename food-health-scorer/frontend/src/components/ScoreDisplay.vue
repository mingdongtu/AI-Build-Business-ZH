<template>
  <div class="score-display">
    <div class="score-card">
      <div class="score-header">
        <h3>健康评分</h3>
      </div>
      
      <div class="score-circle-container">
        <div class="score-circle" :class="scoreClass">
          <div class="score-value">{{ score }}</div>
          <div class="score-label">{{ scoreLabel }}</div>
        </div>
      </div>
      
      <div class="score-details">
        <div class="food-name">
          <h4>食品名称</h4>
          <p>{{ foodName || '未识别' }}</p>
        </div>
        
        <div class="ingredients-section">
          <h4>识别到的配料</h4>
          <div class="ingredients-list">
            <div 
              v-for="(ingredient, index) in ingredients" 
              :key="index" 
              class="ingredient-item"
              :class="getIngredientClass(ingredient)"
            >
              {{ ingredient }}
            </div>
          </div>
        </div>
        
        <div class="health-points">
          <h4>健康评估</h4>
          <div class="points-list">
            <div 
              v-for="(point, index) in healthPoints" 
              :key="index" 
              class="point-item"
              :class="point.type"
            >
              <div class="point-icon">
                <span v-if="point.type === 'positive'">✓</span>
                <span v-else>✗</span>
              </div>
              <div class="point-text">{{ point.description }}</div>
            </div>
          </div>
        </div>
        
        <div class="recommendation">
          <h4>建议</h4>
          <p>{{ recommendation }}</p>
        </div>
      </div>
      
      <div class="score-actions">
        <button class="action-button primary" @click="shareResults">分享结果</button>
        <button class="action-button secondary" @click="analyzeNew">重新分析</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ScoreDisplay',
  props: {
    score: {
      type: Number,
      required: true,
      default: 0
    },
    foodName: {
      type: String,
      default: ''
    },
    ingredients: {
      type: Array,
      default: () => []
    },
    healthPoints: {
      type: Array,
      default: () => []
    },
    recommendation: {
      type: String,
      default: ''
    }
  },
  computed: {
    scoreClass() {
      if (this.score >= 80) return 'excellent';
      if (this.score >= 60) return 'good';
      if (this.score >= 40) return 'average';
      return 'poor';
    },
    scoreLabel() {
      if (this.score >= 80) return '优秀';
      if (this.score >= 60) return '良好';
      if (this.score >= 40) return '一般';
      return '较差';
    }
  },
  methods: {
    getIngredientClass(ingredient) {
      // 这里可以根据配料的健康程度添加不同的类名
      // 简单示例，实际应用中可以根据后端返回的数据进行更复杂的判断
      const unhealthyIngredients = ['糖', '白砂糖', '反式脂肪', '人工色素', '防腐剂'];
      const healthyIngredients = ['全麦', '燕麦', '蔬菜', '水果', '坚果'];
      
      if (unhealthyIngredients.some(item => ingredient.includes(item))) {
        return 'unhealthy';
      } else if (healthyIngredients.some(item => ingredient.includes(item))) {
        return 'healthy';
      }
      return '';
    },
    shareResults() {
      // 实现分享功能
      if (navigator.share) {
        navigator.share({
          title: '食品健康评分结果',
          text: `我分析了"${this.foodName || '食品'}"，健康评分为${this.score}分（${this.scoreLabel}）。${this.recommendation}`,
          url: window.location.href
        }).catch(error => {
          console.error('分享失败:', error);
          this.fallbackShare();
        });
      } else {
        this.fallbackShare();
      }
    },
    fallbackShare() {
      // 复制到剪贴板的备用分享方法
      const shareText = `我分析了"${this.foodName || '食品'}"，健康评分为${this.score}分（${this.scoreLabel}）。${this.recommendation}`;
      
      try {
        const textArea = document.createElement('textarea');
        textArea.value = shareText;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        
        alert('结果已复制到剪贴板，可以粘贴分享给好友');
      } catch (err) {
        console.error('复制失败:', err);
        alert('分享功能不可用，请手动截图分享');
      }
    },
    analyzeNew() {
      this.$emit('analyze-new');
    }
  }
}
</script>

<style scoped>
.score-display {
  width: 100%;
  max-width: 600px;
  margin: 0 auto;
  padding: 20px 0;
}

.score-card {
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.score-header {
  background-color: #f5f5f5;
  padding: 15px;
  text-align: center;
  border-bottom: 1px solid #eee;
}

.score-header h3 {
  margin: 0;
  color: #333;
  font-size: 18px;
}

.score-circle-container {
  display: flex;
  justify-content: center;
  padding: 30px 0;
  background: linear-gradient(to bottom, #f5f5f5, #fff);
}

.score-circle {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
  transition: transform 0.3s ease;
}

.score-circle:hover {
  transform: scale(1.05);
}

.score-circle.excellent {
  background: linear-gradient(135deg, #4CAF50, #8BC34A);
  color: white;
}

.score-circle.good {
  background: linear-gradient(135deg, #8BC34A, #CDDC39);
  color: white;
}

.score-circle.average {
  background: linear-gradient(135deg, #FFC107, #FF9800);
  color: white;
}

.score-circle.poor {
  background: linear-gradient(135deg, #FF5722, #F44336);
  color: white;
}

.score-value {
  font-size: 36px;
  font-weight: bold;
  line-height: 1;
}

.score-label {
  font-size: 16px;
  margin-top: 5px;
}

.score-details {
  padding: 20px;
}

.score-details h4 {
  color: #333;
  margin: 15px 0 10px;
  padding-bottom: 5px;
  border-bottom: 1px solid #eee;
}

.food-name {
  margin-bottom: 20px;
}

.ingredients-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 20px;
}

.ingredient-item {
  background-color: #f1f1f1;
  padding: 5px 10px;
  border-radius: 15px;
  font-size: 14px;
  color: #333;
}

.ingredient-item.healthy {
  background-color: rgba(76, 175, 80, 0.2);
  color: #2e7d32;
}

.ingredient-item.unhealthy {
  background-color: rgba(244, 67, 54, 0.2);
  color: #c62828;
}

.points-list {
  margin-bottom: 20px;
}

.point-item {
  display: flex;
  align-items: flex-start;
  margin-bottom: 10px;
  padding: 10px;
  border-radius: 8px;
}

.point-item.positive {
  background-color: rgba(76, 175, 80, 0.1);
}

.point-item.negative {
  background-color: rgba(244, 67, 54, 0.1);
}

.point-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  margin-right: 10px;
  flex-shrink: 0;
}

.point-item.positive .point-icon {
  background-color: #4CAF50;
  color: white;
}

.point-item.negative .point-icon {
  background-color: #F44336;
  color: white;
}

.point-text {
  flex: 1;
}

.recommendation {
  background-color: #f9f9f9;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.score-actions {
  display: flex;
  justify-content: space-between;
  padding: 0 20px 20px;
}

.action-button {
  padding: 12px 20px;
  border: none;
  border-radius: 5px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.2s ease;
  flex: 1;
  margin: 0 5px;
}

.action-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
}

.action-button.primary {
  background-color: #2196F3;
  color: white;
}

.action-button.secondary {
  background-color: #f5f5f5;
  color: #333;
  border: 1px solid #ddd;
}

/* 移动端适配 */
@media (max-width: 480px) {
  .score-display {
    padding: 10px;
  }
  
  .score-circle {
    width: 100px;
    height: 100px;
  }
  
  .score-value {
    font-size: 30px;
  }
  
  .score-actions {
    flex-direction: column;
    gap: 10px;
  }
  
  .action-button {
    margin: 5px 0;
  }
}
</style>
