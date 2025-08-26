<template>
  <div class="image-analyzer">
    <div v-if="!isAnalyzing && !analysisComplete" class="upload-section">
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
          <p>正在分析配料表...</p>
          <p class="loading-step">{{ loadingStep }}</p>
        </div>
      </div>
    </div>

    <div v-if="analysisError" class="error-section">
      <div class="error-container">
        <div class="error-icon">❌</div>
        <h3>分析失败</h3>
        <p>{{ analysisError }}</p>
        <button class="retry-button" @click="resetAnalysis">重新上传</button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import CameraCapture from './CameraCapture.vue';

export default {
  name: 'ImageAnalyzer',
  components: {
    CameraCapture
  },
  data() {
    return {
      isAnalyzing: false,
      analysisComplete: false,
      analysisError: null,
      capturedImage: null,
      loadingStep: '识别图片中...',
      loadingSteps: [
        '识别图片中...',
        '提取配料信息...',
        '分析配料成分...',
        '计算健康评分...',
        '生成分析报告...'
      ],
      currentStepIndex: 0,
      stepInterval: null
    }
  },
  methods: {
    // 处理图片捕获
    handleImageCaptured(imageData) {
      this.capturedImage = imageData;
      this.analyzeImage(imageData.file);
    },
    
    // 处理捕获错误
    handleCaptureError(error) {
      this.analysisError = error;
    },
    
    // 分析图片
    async analyzeImage(imageFile) {
      if (!imageFile) return;
      
      this.isAnalyzing = true;
      this.analysisError = null;
      this.startLoadingAnimation();
      
      try {
        const formData = new FormData();
        formData.append('image', imageFile);
        
        // 获取API URL，优先使用环境变量中的配置
        const apiUrl = process.env.VUE_APP_API_URL || '/api';
        
        console.log('Using API URL:', apiUrl);
        
        const response = await axios.post(`${apiUrl}/analyze`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          timeout: 30000, // 30 second timeout
        });

        console.log('Analysis response:', response.data);
        
        // 打印OCR识别的文字到浏览器控制台
        if (response.data.extracted_text) {
          console.log('=== 百度OCR识别的文字内容 ===');
          console.log(response.data.extracted_text);
          console.log('=== OCR识别完成 ===');
        }
        
        // Store the results in localStorage for the results page
        localStorage.setItem('analysisResults', JSON.stringify(response.data));
        
        // 分析完成，跳转到结果页面
        this.analysisComplete = true;
        this.$router.push('/results');
      } catch (error) {
        console.error('图片分析失败:', error);
        
        // 处理不同类型的错误
        if (error.response) {
          // 服务器返回了错误状态码
          if (error.response.status === 413) {
            this.analysisError = '图片文件太大，请使用较小的图片';
          } else if (error.response.status === 415) {
            this.analysisError = '不支持的文件类型，请上传图片文件';
          } else if (error.response.status === 422) {
            this.analysisError = '无法识别图片中的配料表，请确保图片清晰且包含配料表';
          } else {
            this.analysisError = `服务器错误 (${error.response.status})，请稍后重试`;
          }
        } else if (error.request) {
          // 请求已发送但没有收到响应
          this.analysisError = '服务器无响应，请检查网络连接后重试';
        } else if (error.code === 'ECONNABORTED') {
          // 请求超时
          this.analysisError = '请求超时，服务器处理时间过长，请稍后重试';
        } else {
          // 其他错误
          this.analysisError = '图片上传或分析失败，请重试';
        }
      } finally {
        this.isAnalyzing = false;
        this.stopLoadingAnimation();
      }
    },
    
    // 开始加载动画
    startLoadingAnimation() {
      this.currentStepIndex = 0;
      this.loadingStep = this.loadingSteps[0];
      
      // 每2秒更新一次加载步骤
      this.stepInterval = setInterval(() => {
        this.currentStepIndex = (this.currentStepIndex + 1) % this.loadingSteps.length;
        this.loadingStep = this.loadingSteps[this.currentStepIndex];
      }, 2000);
    },
    
    // 停止加载动画
    stopLoadingAnimation() {
      if (this.stepInterval) {
        clearInterval(this.stepInterval);
        this.stepInterval = null;
      }
    },
    
    // 重置分析
    resetAnalysis() {
      this.isAnalyzing = false;
      this.analysisComplete = false;
      this.analysisError = null;
      this.capturedImage = null;
      this.stopLoadingAnimation();
    }
  },
  beforeUnmount() {
    // 组件销毁前清除定时器
    this.stopLoadingAnimation();
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
