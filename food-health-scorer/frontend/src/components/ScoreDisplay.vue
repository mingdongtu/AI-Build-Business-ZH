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
        
        <!-- 新增详细解释部分 -->
        <div class="detailed-explanation">
          <h4>详细解释</h4>
          <div class="explanation-tabs">
            <div 
              class="tab" 
              :class="{ active: activeTab === 'nutrition' }" 
              @click="activeTab = 'nutrition'"
            >
              营养成分
            </div>
            <div 
              class="tab" 
              :class="{ active: activeTab === 'health' }" 
              @click="activeTab = 'health'"
            >
              健康影响
            </div>
            <div 
              class="tab" 
              :class="{ active: activeTab === 'advice' }" 
              @click="activeTab = 'advice'"
            >
              饮食建议
            </div>
          </div>
          
          <div class="tab-content">
            <!-- 营养成分标签 -->
            <div v-if="activeTab === 'nutrition'" class="nutrition-content">
              <div class="nutrition-chart">
                <div class="chart-title">主要营养成分占比</div>
                <div class="chart-container">
                  <div 
                    v-for="(item, index) in nutritionData" 
                    :key="index" 
                    class="chart-item"
                  >
                    <div class="chart-label">{{ item.name }}</div>
                    <div class="chart-bar-container">
                      <div 
                        class="chart-bar" 
                        :style="{ width: item.percentage + '%', backgroundColor: item.color }"
                      ></div>
                      <span class="chart-value">{{ item.percentage }}%</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 健康影响标签 -->
            <div v-if="activeTab === 'health'" class="health-content">
              <div class="health-impact">
                <div v-for="(impact, index) in healthImpacts" :key="index" class="impact-item">
                  <div class="impact-icon" :class="impact.type">
                    <span v-if="impact.type === 'positive'">+</span>
                    <span v-else-if="impact.type === 'negative'">-</span>
                    <span v-else>?</span>
                  </div>
                  <div class="impact-details">
                    <div class="impact-title">{{ impact.title }}</div>
                    <div class="impact-description">{{ impact.description }}</div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 饮食建议标签 -->
            <div v-if="activeTab === 'advice'" class="advice-content">
              <div class="advice-list">
                <div v-for="(advice, index) in dietaryAdvice" :key="index" class="advice-item">
                  <div class="advice-number">{{ index + 1 }}</div>
                  <div class="advice-text">{{ advice }}</div>
                </div>
              </div>
            </div>
          </div>
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
  data() {
    return {
      activeTab: 'nutrition',  // 默认激活营养成分标签
      nutritionData: [
        { name: '碳水化合物', percentage: 45, color: '#FF9800' },
        { name: '蛋白质', percentage: 20, color: '#2196F3' },
        { name: '脂肪', percentage: 25, color: '#F44336' },
        { name: '维生素矿物质', percentage: 10, color: '#4CAF50' }
      ],
      healthImpacts: [
        {
          type: 'positive',
          title: '均衡营养',
          description: '该食品含有多种营养素，有助于维持均衡的营养摄入'
        },
        {
          type: 'negative',
          title: '糖分含量高',
          description: '过量的糖分可能导致血糖波动和增加肥胖风险'
        },
        {
          type: 'positive',
          title: '自然成分',
          description: '主要由天然食材制成，减少了人工添加剂的使用'
        },
        {
          type: 'neutral',
          title: '适度食用',
          description: '建议适量食用，作为均衡饮食的一部分'
        }
      ],
      dietaryAdvice: [
        '将该食品作为日常饮食的补充，而非主要食物',
        '建议搭配新鲜蔬菜和水果一起食用，增加自然维生素的摄入',
        '注意控制每日的摄入量，避免过量摄入糖分和脂肪',
        '如果您有特殊健康状况，如糖尿病或高血压，请在食用前咨询医生'
      ]
    };
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

/* 详细解释部分样式 */
.detailed-explanation {
  margin-top: 20px;
  border-top: 1px solid #eee;
  padding-top: 20px;
}

.explanation-tabs {
  display: flex;
  border-bottom: 1px solid #ddd;
  margin-bottom: 15px;
}

.tab {
  padding: 10px 15px;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.2s ease;
  font-weight: 500;
  color: #666;
}

.tab:hover {
  color: #2196F3;
}

.tab.active {
  color: #2196F3;
  border-bottom-color: #2196F3;
}

.tab-content {
  padding: 10px 0;
}

/* 营养成分图表样式 */
.nutrition-chart {
  margin-bottom: 20px;
}

.chart-title {
  font-weight: 500;
  margin-bottom: 15px;
  color: #333;
}

.chart-container {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.chart-item {
  display: flex;
  align-items: center;
}

.chart-label {
  width: 100px;
  font-size: 14px;
  color: #555;
}

.chart-bar-container {
  flex: 1;
  height: 20px;
  background-color: #f1f1f1;
  border-radius: 10px;
  overflow: hidden;
  position: relative;
}

.chart-bar {
  height: 100%;
  border-radius: 10px;
  transition: width 1s ease-out;
}

.chart-value {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 12px;
  color: #fff;
  font-weight: bold;
  text-shadow: 0 0 2px rgba(0, 0, 0, 0.5);
}

/* 健康影响样式 */
.health-impact {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.impact-item {
  display: flex;
  padding: 12px;
  border-radius: 8px;
  background-color: #f9f9f9;
  transition: transform 0.2s ease;
}

.impact-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.impact-icon {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  font-weight: bold;
  font-size: 18px;
}

.impact-icon.positive {
  background-color: #4CAF50;
  color: white;
}

.impact-icon.negative {
  background-color: #F44336;
  color: white;
}

.impact-icon.neutral {
  background-color: #FFC107;
  color: white;
}

.impact-details {
  flex: 1;
}

.impact-title {
  font-weight: 500;
  margin-bottom: 5px;
  color: #333;
}

.impact-description {
  font-size: 14px;
  color: #666;
}

/* 饮食建议样式 */
.advice-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.advice-item {
  display: flex;
  align-items: flex-start;
}

.advice-number {
  width: 24px;
  height: 24px;
  background-color: #2196F3;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  font-size: 14px;
  font-weight: bold;
  flex-shrink: 0;
}

.advice-text {
  flex: 1;
  padding-top: 2px;
  line-height: 1.5;
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
  
  .explanation-tabs {
    overflow-x: auto;
    padding-bottom: 5px;
  }
  
  .tab {
    padding: 10px 12px;
    font-size: 14px;
    white-space: nowrap;
  }
  
  .chart-label {
    width: 80px;
    font-size: 12px;
  }
  
  .impact-item {
    padding: 10px;
  }
  
  .impact-icon {
    width: 24px;
    height: 24px;
    font-size: 14px;
    margin-right: 10px;
  }
}
</style>
