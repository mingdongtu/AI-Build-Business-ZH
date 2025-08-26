<template>
  <div class="food-info-table">
    <table>
      <thead>
        <tr>
          <th>食品名称</th>
          <th>配料清单</th>
          <th>健康评估</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td class="food-name-cell">{{ foodName || '未识别' }}</td>
          <td class="ingredients-cell">
            <div class="ingredients-tags">
              <span 
                v-for="(ingredient, index) in ingredients" 
                :key="index" 
                class="ingredient-tag"
                :class="getIngredientClass(ingredient)"
              >
                {{ ingredient }}
              </span>
            </div>
          </td>
          <td class="health-assessment-cell">
            <div class="score-section">
              <div class="score-badge" :class="scoreClass">{{ score }}</div>
              <div class="score-label">{{ scoreLabel }}</div>
            </div>
            <div class="health-points">
              <div 
                v-for="(point, index) in healthPoints" 
                :key="index" 
                class="health-point"
                :class="point.type"
              >
                <span class="point-icon">{{ point.type === 'positive' ? '✓' : '✗' }}</span>
                <span class="point-text">{{ point.description }}</span>
              </div>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
    
    <div class="recommendation-section">
      <h4>建议</h4>
      <p>{{ recommendation }}</p>
    </div>
    
    <div class="table-actions">
      <button class="action-button primary" @click="shareResults">分享结果</button>
      <button class="action-button secondary" @click="$emit('analyze-new')">重新分析</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FoodInfoTable',
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
    }
  }
}
</script>

<style scoped>
.food-info-table {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
  padding: 20px 0;
}

table {
  width: 100%;
  border-collapse: collapse;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
  background-color: #fff;
}

th, td {
  padding: 15px;
  text-align: left;
  border-bottom: 1px solid #eee;
  vertical-align: top;
}

th {
  background-color: #f5f5f5;
  font-weight: bold;
  color: #333;
}

.food-name-cell {
  width: 20%;
  font-weight: bold;
}

.ingredients-cell {
  width: 35%;
}

.health-assessment-cell {
  width: 45%;
}

.ingredients-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.ingredient-tag {
  background-color: #f1f1f1;
  padding: 5px 10px;
  border-radius: 15px;
  font-size: 14px;
  color: #333;
  display: inline-block;
}

.ingredient-tag.healthy {
  background-color: rgba(76, 175, 80, 0.2);
  color: #2e7d32;
}

.ingredient-tag.unhealthy {
  background-color: rgba(244, 67, 54, 0.2);
  color: #c62828;
}

.score-section {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.score-badge {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 18px;
  margin-right: 15px;
  color: white;
}

.score-badge.excellent {
  background: linear-gradient(135deg, #4CAF50, #8BC34A);
}

.score-badge.good {
  background: linear-gradient(135deg, #8BC34A, #CDDC39);
}

.score-badge.average {
  background: linear-gradient(135deg, #FFC107, #FF9800);
}

.score-badge.poor {
  background: linear-gradient(135deg, #FF5722, #F44336);
}

.score-label {
  font-weight: bold;
  font-size: 16px;
}

.health-points {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.health-point {
  display: flex;
  align-items: flex-start;
  padding: 8px;
  border-radius: 6px;
}

.health-point.positive {
  background-color: rgba(76, 175, 80, 0.1);
}

.health-point.negative {
  background-color: rgba(244, 67, 54, 0.1);
}

.point-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  margin-right: 8px;
  flex-shrink: 0;
}

.health-point.positive .point-icon {
  background-color: #4CAF50;
  color: white;
}

.health-point.negative .point-icon {
  background-color: #F44336;
  color: white;
}

.recommendation-section {
  background-color: #f9f9f9;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.recommendation-section h4 {
  margin-top: 0;
  margin-bottom: 10px;
  color: #333;
}

.table-actions {
  display: flex;
  justify-content: space-between;
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
@media (max-width: 768px) {
  table {
    display: block;
  }
  
  thead {
    display: none;
  }
  
  tbody, tr, td {
    display: block;
    width: 100%;
  }
  
  td {
    position: relative;
    padding-left: 120px;
    min-height: 40px;
  }
  
  td:before {
    content: attr(data-label);
    position: absolute;
    left: 15px;
    font-weight: bold;
    color: #333;
  }
  
  .food-name-cell:before {
    content: "食品名称:";
  }
  
  .ingredients-cell:before {
    content: "配料清单:";
  }
  
  .health-assessment-cell:before {
    content: "健康评估:";
  }
  
  .table-actions {
    flex-direction: column;
    gap: 10px;
  }
  
  .action-button {
    margin: 5px 0;
  }
}
</style>
