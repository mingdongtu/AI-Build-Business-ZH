<template>
  <div class="image-analyzer">
    <div v-if="!isAnalyzing && !analysisComplete && !analysisError" class="upload-section">
      <h3>食品配料分析</h3>
      <p class="instruction">请上传食品包装袋配料表图片进行健康评分分析</p>
      
      <camera-capture 
        @image-captured="handleImageCaptured" 
        @error="handleCaptureError"
      />
    </div>

    <div v-if="isAnalyzing" class="analyzing-section">
      <div class="loading-container">
        <div class="loading-spinner"></div>
        <div class="loading-text">
          <p>OCR识别中</p>
          <p class="loading-step">{{ loadingStep }}</p>
          <div class="loading-animation">
            <span class="dot"></span>
            <span class="dot"></span>
            <span class="dot"></span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="analysisError" class="error-section">
      <div class="error-container">
        <div class="error-icon">❌</div>
        <h3>识别失败</h3>
        <p>{{ analysisError }}</p>
        <div class="error-actions">
          <button class="retry-button" @click="resetAnalysis">重新拍摄</button>
          <button class="manual-input-button" @click="showManualInput = true">手动输入</button>
        </div>
      </div>
      
      <!-- 手动输入表单 -->
      <div v-if="showManualInput" class="manual-input-section">
        <h4>手动输入配料表</h4>
        <textarea 
          v-model="manualIngredients" 
          placeholder="请输入食品包装上的配料表内容..."
          rows="6"
          class="manual-input"
        ></textarea>
        <div class="manual-actions">
          <button class="cancel-button" @click="showManualInput = false">取消</button>
          <button class="submit-button" @click="analyzeManualInput">确认提交</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import CameraCapture from './CameraCapture.vue';
import { mockAnalysisResult, mockOcrFailureResult, mockManualInputResult } from '@/mockData.js';

export default {
  name: 'ImageAnalyzer',
  components: {
    CameraCapture
  },
  data() {
    return {
      apiBaseUrl: process.env.VUE_APP_API_URL || 'http://localhost:8000',
      capturedImage: null,
      loading: false,
      error: null,
      loadingText: '正在分析图片...',
      loadingSteps: [
        '正在识别食品包装...',
        '提取配料表信息...',
        '分析营养成分...',
        '计算健康评分...',
        '生成健康建议...'
      ],
      loadingStep: 0,
      loadingInterval: null,
      showManualInput: false,
      manualIngredients: '',
      manualFoodName: '',
      manualInputError: '',
      ocrFailed: false,
      isAnalyzing: false,
      analysisComplete: false,
      analysisError: null,
      analysisResult: null,
      imageData: null
    };
  },
  methods: {
    handleImageCaptured(imageData) {
      this.imageData = imageData;
      this.analyzeImage();
    },
    handleCaptureError(error) {
      this.analysisError = `相机错误: ${error}`;
    },
    async analyzeImage() {
      if (!this.imageData) {
        this.analysisError = '没有图片数据可供分析';
        return;
      }

      this.isAnalyzing = true;
      this.analysisError = null;
      this.analysisComplete = false;
      
      // 开始加载步骤切换
      this.startLoadingSteps();

      try {
        // 使用模拟数据进行测试
        // 随机模拟OCR成功或失败
        const useSuccessData = Math.random() > 0.3; // 70%概率成功
        
        // 模拟API延迟
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // 使用模拟数据
        this.analysisResult = useSuccessData ? mockAnalysisResult : mockOcrFailureResult;
        this.analysisComplete = true;
        
        // 检查OCR是否成功
        if (!useSuccessData || this.analysisResult.ocr_success === false) {
          // OCR失败，显示手动输入表单
          this.analysisError = 'OCR识别失败，无法识别配料表文字';
          this.showManualInput = true;
          this.isAnalyzing = false;
          this.stopLoadingSteps();
          return;
        }
        
        // 将结果存储到 localStorage
        localStorage.setItem('analysisResult', JSON.stringify(this.analysisResult));
        
        // 在跳转前确保停止加载动画
        this.isAnalyzing = false;
        this.stopLoadingSteps();
        
        // 跳转到结果页面
        this.$router.push('/results');
      } catch (error) {
        console.error('Analysis error:', error);
        this.showError('OCR识别过程中发生错误');
      } finally {
        this.isAnalyzing = false;
        this.stopLoadingSteps();
      }
    },
    async analyzeManualInput() {
      if (!this.manualIngredients || !this.manualIngredients.trim()) {
        this.manualInputError = '请输入配料文本';
        return;
      }
      
      this.manualInputError = '';
      this.isAnalyzing = true;
      this.loadingStep = '正在分析您输入的文本...';
      this.startLoadingSteps();

      try {
        // 使用模拟数据进行测试
        // 模拟API延迟
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        // 使用手动输入的模拟数据
        const result = {...mockManualInputResult};
        
        // 如果用户输入了食品名称，则使用用户输入的名称
        if (this.manualFoodName) {
          result.food_name = this.manualFoodName;
        }
        
        // 存储分析结果
        localStorage.setItem('analysisResult', JSON.stringify(result));
        
        // 在跳转前确保停止加载动画
        this.isAnalyzing = false;
        this.stopLoadingSteps();
        
        // 跳转到结果页面
        this.$router.push('/results');
      } catch (error) {
        console.error('手动输入分析错误:', error);
        this.analysisError = error.message || '分析过程中发生错误';
      } finally {
        this.isAnalyzing = false;
        this.stopLoadingSteps();
      }
    },
    
    startLoadingSteps() {
      this.loadingStepIndex = 0;
      this.loadingStep = this.loadingSteps[0];
      
      this.loadingInterval = setInterval(() => {
        this.loadingStepIndex = (this.loadingStepIndex + 1) % this.loadingSteps.length;
        this.loadingStep = this.loadingSteps[this.loadingStepIndex];
      }, 2000);
    },
    
    stopLoadingSteps() {
      if (this.loadingInterval) {
        clearInterval(this.loadingInterval);
        this.loadingInterval = null;
      }
      // Reset loading-related states to ensure no animations continue
      this.loadingStep = '';
      this.loadingStepIndex = 0;
      this.isAnalyzing = false;
    },
    
    resetAnalysis() {
      this.isAnalyzing = false;
      this.analysisComplete = false;
      this.analysisError = null;
      this.analysisResult = null;
      this.imageData = null;
      this.loadingStepIndex = 0;
      this.loadingStep = this.loadingSteps[0];
      this.showManualInput = false;
      this.manualIngredients = '';
    },
    
    showError(message) {
      this.analysisError = message;
      this.isAnalyzing = false;
      this.stopLoadingSteps();
    }
  },
  beforeUnmount() {
    // 组件销毁前清除定时器
    this.stopLoadingSteps();
  }
}
</script>

<style scoped>
.image-analyzer {
  width: 100%;
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
}

.upload-section {
  text-align: center;
}

.instruction {
  color: #666;
  margin-bottom: 20px;
}

.analyzing-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 30px;
  background-color: rgba(255, 255, 255, 0.9);
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.loading-spinner {
  width: 60px;
  height: 60px;
  border: 5px solid #f3f3f3;
  border-top: 5px solid #2196F3;
  border-radius: 50%;
  animation: spin 1.5s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  text-align: center;
}

.loading-text p {
  margin: 5px 0;
}

.loading-step {
  color: #2196F3;
  font-weight: bold;
}

.error-section {
  display: flex;
  justify-content: center;
  padding: 20px;
}

.error-container {
  background-color: #fff;
  border-radius: 8px;
  padding: 30px;
  text-align: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  max-width: 400px;
}

.error-icon {
  font-size: 40px;
  margin-bottom: 15px;
}

.error-container h3 {
  color: #f44336;
  margin-bottom: 15px;
}

.retry-button {
  background-color: #2196F3;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  font-weight: bold;
  cursor: pointer;
  margin-top: 20px;
  transition: all 0.2s ease;
}

.retry-button:hover {
  background-color: #0b7dda;
  transform: translateY(-2px);
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
}

/* 手动输入按钮 */
.error-actions {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 20px;
}

.manual-input-button {
  background-color: #4CAF50;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.2s ease;
}

.manual-input-button:hover {
  background-color: #45a049;
  transform: translateY(-2px);
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
}

/* 手动输入表单 */
.manual-input-section {
  margin-top: 20px;
  background-color: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.manual-input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  margin: 10px 0;
  font-size: 14px;
  resize: vertical;
}

.manual-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 15px;
}

.cancel-button {
  background-color: #f5f5f5;
  color: #333;
  border: 1px solid #ddd;
  padding: 8px 16px;
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.submit-button {
  background-color: #2196F3;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.2s ease;
}

.submit-button:hover {
  background-color: #0b7dda;
  transform: translateY(-2px);
}

.cancel-button:hover {
  background-color: #e0e0e0;
}

/* 加载动画点 */
.loading-animation {
  display: flex;
  justify-content: center;
  margin-top: 15px;
}

.dot {
  width: 8px;
  height: 8px;
  background-color: #2196F3;
  border-radius: 50%;
  margin: 0 5px;
  display: inline-block;
  animation: bounce 1.4s infinite ease-in-out both;
}

.dot:nth-child(1) {
  animation-delay: -0.32s;
}

.dot:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes bounce {
  0%, 80%, 100% { 
    transform: scale(0);
  } 40% { 
    transform: scale(1.0);
  }
}

/* 移动端适配 */
@media (max-width: 480px) {
  .image-analyzer {
    padding: 10px;
  }
  
  .loading-container {
    padding: 20px;
  }
  
  .loading-spinner {
    width: 50px;
    height: 50px;
  }
}
</style>
