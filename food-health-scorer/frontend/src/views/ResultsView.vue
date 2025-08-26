<template>
  <div class="results">
    <div v-if="results" class="results-container">
      <!-- 添加视图切换按钮 -->
      <div class="view-toggle">
        <button 
          @click="currentView = 'card'" 
          :class="{ active: currentView === 'card' }"
          class="toggle-button"
        >
          卡片视图
        </button>
        <button 
          @click="currentView = 'table'" 
          :class="{ active: currentView === 'table' }"
          class="toggle-button"
        >
          表格视图
        </button>
      </div>
      
      <!-- 卡片视图 -->
      <score-display 
        v-if="currentView === 'card'"
        :score="results.score" 
        :food-name="extractedFoodName" 
        :ingredients="results.ingredients || []" 
        :health-points="results.health_points || []" 
        :recommendation="formattedRecommendation"
        @analyze-new="goBack"
      />
      
      <!-- 表格视图 -->
      <food-info-table
        v-else
        :score="results.score" 
        :food-name="extractedFoodName" 
        :ingredients="results.ingredients || []" 
        :health-points="results.health_points || []" 
        :recommendation="formattedRecommendation"
        @analyze-new="goBack"
      />
    </div>
    
    <div v-else class="no-results">
      <div class="no-results-card">
        <div class="no-results-icon">❓</div>
        <h3>没有可用的分析结果</h3>
        <p>请先上传食品包装图片进行分析</p>
        <button class="back-button" @click="goBack">返回上传页面</button>
      </div>
    </div>
  </div>
</template>

<script>
import ScoreDisplay from '@/components/ScoreDisplay.vue';
import FoodInfoTable from '@/components/FoodInfoTable.vue';

export default {
  name: 'ResultsView',
  components: {
    ScoreDisplay,
    FoodInfoTable
  },
  data() {
    return {
      results: null,
      currentView: 'card' // 默认使用卡片视图
    }
  },
  computed: {
    // 提取或生成食品名称
    extractedFoodName() {
      // 如果后端返回了食品名称，则使用它
      if (this.results && this.results.food_name) {
        return this.results.food_name;
      }
      
      // 否则，尝试从配料表中推断食品类型
      if (this.results && this.results.ingredients && this.results.ingredients.length > 0) {
        // 这里只是一个简单示例，实际应用中可能需要更复杂的逻辑
        return '食品';
      }
      
      return '未识别食品';
    },
    
    // 格式化建议内容
    formattedRecommendation() {
      if (!this.results) return '';
      
      // 如果后端返回了单个recommendation字符串，则直接使用
      if (this.results.recommendation && typeof this.results.recommendation === 'string') {
        return this.results.recommendation;
      }
      
      // 如果后端返回了recommendations数组，则将其合并为一个字符串
      if (this.results.recommendations && Array.isArray(this.results.recommendations)) {
        return this.results.recommendations.join(' ');
      }
      
      return '无可用建议';
    }
  },
  created() {
    // Try to get results from localStorage
    const storedResults = localStorage.getItem('analysisResults');
    if (storedResults) {
      try {
        this.results = JSON.parse(storedResults);
        console.log('Analysis results loaded:', this.results);
        
        // 在结果页面也显示OCR识别的文字
        if (this.results.extracted_text) {
          console.log('=== 结果页面 - 百度OCR识别的文字 ===');
          console.log(this.results.extracted_text);
          console.log('=== 文字显示完成 ===');
        }
      } catch (e) {
        console.error('Failed to parse stored results:', e);
      }
    }
  },
  methods: {
    goBack() {
      this.$router.push('/');
    }
  }
}
</script>

<style scoped>
.results {
  padding: 20px;
}

.view-toggle {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.toggle-button {
  padding: 10px 20px;
  margin: 0 5px;
  border: 1px solid #ddd;
  background-color: #f5f5f5;
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.toggle-button.active {
  background-color: #2196F3;
  color: white;
  border-color: #2196F3;
}

.toggle-button:hover:not(.active) {
  background-color: #e0e0e0;
}

.no-results {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
}

.no-results-card {
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  padding: 30px;
  text-align: center;
  max-width: 400px;
}

.no-results-icon {
  font-size: 40px;
  margin-bottom: 20px;
  color: #9e9e9e;
}

.no-results-card h3 {
  margin-bottom: 15px;
  color: #333;
}

.no-results-card p {
  color: #666;
  margin-bottom: 25px;
}

.back-button {
  background-color: #2196F3;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.2s ease;
}

.back-button:hover {
  background-color: #0b7dda;
  transform: translateY(-2px);
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
}

/* 移动端适配 */
@media (max-width: 480px) {
  .results {
    padding: 10px;
  }
  
  .no-results-card {
    padding: 20px;
    margin: 0 10px;
  }
}
</style>
