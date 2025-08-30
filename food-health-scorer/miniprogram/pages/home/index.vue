<template>
  <view class="home-container">
    <view class="header">
      <text class="title">食品健康评分</text>
      <text class="subtitle">拍摄或上传食品配料表，获取健康评分</text>
    </view>
    
    <!-- H5环境使用专用上传组件 -->
    <block v-if="isH5Platform">
      <h5-image-uploader @analysis-complete="onAnalysisComplete"></h5-image-uploader>
    </block>
    
    <!-- 非H5环境使用原生上传 -->
    <block v-else>
      <!-- 上传区域 -->
      <view class="upload-section" v-if="!isAnalyzing && !tempFilePath">
        <button class="upload-btn" @click="chooseImage('camera')">拍摄配料表</button>
        <button class="upload-btn" @click="chooseImage('album')">从相册选择</button>
      </view>
      
      <!-- 预览区域 -->
      <view class="preview-section" v-if="tempFilePath && !isAnalyzing">
        <image class="preview-image" :src="tempFilePath" mode="aspectFit"></image>
        <button class="analyze-btn" @click="analyzeImage">分析图片</button>
      </view>
    </block>
    
    <!-- 加载区域 -->
    <view class="loading-section" v-if="isAnalyzing">
      <view class="loading-container">
        <view class="loading-spinner"></view>
        <view class="loading-text">
          <text class="loading-title">AI分析中</text>
          <text class="loading-step">{{ loadingStep }}</text>
          <view class="loading-dots">
            <text class="dot"></text>
            <text class="dot"></text>
            <text class="dot"></text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import BaiduOCR from '../../utils/baiduOcr.js';
import DeepSeekAnalyzer from '../../utils/deepseekAnalyzer.js';
import H5ImageUploader from '../../components/H5ImageUploader.vue';

export default {
  components: {
    H5ImageUploader
  },
  data() {
    return {
      tempFilePath: '',
      isAnalyzing: false,
      loadingStep: '',
      isH5Platform: false,
      loadingSteps: [
        '正在识别食品包装...',
        '提取配料表信息...',
        '分析营养成分...',
        '计算健康评分...',
        '生成健康建议...'
      ],
      loadingInterval: null
    }
  },
  created() {
    // 检测是否为H5平台
    // #ifdef H5
    this.isH5Platform = true;
    // #endif
  },
  methods: {
    // 选择图片（拍照或从相册选择）
    chooseImage(sourceType) {
      // #ifdef H5
      // H5平台特殊处理
      if (sourceType === 'camera' && navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        // 使用H5的摄像头API
        this.openH5Camera();
        return;
      }
      // #endif
      
      // 判断平台，微信小程序优先使用chooseMedia API
      if (uni.chooseMedia && sourceType === 'camera') {
        uni.chooseMedia({
          count: 1,
          mediaType: ['image'],
          sourceType: [sourceType === 'camera' ? 'camera' : 'album'],
          camera: 'back',
          sizeType: ['compressed', 'original'],
          success: (res) => {
            if (res.tempFiles && res.tempFiles.length > 0) {
              this.tempFilePath = res.tempFiles[0].tempFilePath;
              console.log('选择图片成功:', this.tempFilePath);
            }
          },
          fail: (err) => {
            console.error('选择图片失败:', err);
            uni.showToast({
              title: '选择图片失败',
              icon: 'none'
            });
          }
        });
      } else {
        // 兼容其他平台使用chooseImage
        uni.chooseImage({
          count: 1,
          sizeType: ['compressed', 'original'], // 优先使用压缩图，提高上传速度
          sourceType: sourceType === 'camera' ? ['camera'] : ['album'],
          success: (res) => {
            if (res.tempFilePaths && res.tempFilePaths.length > 0) {
              this.tempFilePath = res.tempFilePaths[0];
              console.log('选择图片成功:', this.tempFilePath);
            }
          },
          fail: (err) => {
            console.error('选择图片失败:', err);
            uni.showToast({
              title: '选择图片失败',
              icon: 'none'
            });
          }
        });
      }
    },
    
    // #ifdef H5
    // H5平台使用摄像头
    openH5Camera() {
      // 创建一个隐藏的file input元素
      const fileInput = document.createElement('input');
      fileInput.type = 'file';
      fileInput.accept = 'image/*';
      fileInput.capture = 'camera';
      
      fileInput.onchange = (event) => {
        const file = event.target.files[0];
        if (file) {
          const reader = new FileReader();
          reader.onload = (e) => {
            this.tempFilePath = e.target.result;
            console.log('H5选择图片成功');
          };
          reader.readAsDataURL(file);
        }
      };
      
      // 触发点击事件
      fileInput.click();
    },
    // #endif
    
    // 开始加载步骤切换
    startLoadingSteps() {
      this.loadingStepIndex = 0;
      this.loadingStep = this.loadingSteps[0];
      
      this.loadingInterval = setInterval(() => {
        this.loadingStepIndex = (this.loadingStepIndex + 1) % this.loadingSteps.length;
        this.loadingStep = this.loadingSteps[this.loadingStepIndex];
      }, 2000);
    },
    
    // 停止加载步骤
    stopLoadingSteps() {
      if (this.loadingInterval) {
        clearInterval(this.loadingInterval);
        this.loadingInterval = null;
      }
      this.loadingStep = '';
      this.loadingStepIndex = 0;
    },
    
    // 分析图片
    async analyzeImage() {
      if (!this.tempFilePath) {
        uni.showToast({
          title: '请先选择图片',
          icon: 'none'
        });
        return;
      }
      
      this.isAnalyzing = true;
      this.startLoadingSteps();
      
      try {
        // 第一步：使用百度OCR识别图片文字
        const ocrResult = await BaiduOCR.recognizeIngredients(this.tempFilePath);
        
        if (!ocrResult.success) {
          throw new Error(ocrResult.error || 'OCR识别失败');
        }
        
        // 第二步：使用DeepSeek分析配料表文本
        const analysisResult = await DeepSeekAnalyzer.analyzeText(ocrResult.text);
        
        // 格式化分析结果
        const formattedResult = DeepSeekAnalyzer.formatAnalysisResult(analysisResult);
        
        // 将分析结果存储到全局状态或缓存中
        uni.setStorageSync('analysisResult', formattedResult);
        
        // 停止加载动画
        this.stopLoadingSteps();
        this.isAnalyzing = false;
        
        // 跳转到结果页面
        uni.navigateTo({
          url: '/pages/results/index'
        });
      } catch (error) {
        console.error('分析失败:', error);
        this.stopLoadingSteps();
        this.isAnalyzing = false;
        
        uni.showToast({
          title: error.message || '分析失败，请重试',
          icon: 'none',
          duration: 3000
        });
      }
    },
    
    // 处理H5ImageUploader组件的分析结果
    onAnalysisComplete(result) {
      console.log('H5分析完成，结果:', result);
      
      // 停止加载动画
      this.stopLoadingSteps();
      this.isAnalyzing = false;
      
      // 将分析结果存储到全局状态或缓存中
      uni.setStorageSync('analysisResult', result);
      
      // 跳转到结果页面
      uni.navigateTo({
        url: '/pages/results/index'
      });
    }
  }
}
</script>

<style>
.home-container {
  padding: 30rpx;
}

.header {
  text-align: center;
  margin-bottom: 60rpx;
}

.title {
  font-size: 40rpx;
  font-weight: bold;
  display: block;
  margin-bottom: 20rpx;
}

.subtitle {
  font-size: 28rpx;
  color: #666;
  display: block;
}

.upload-section {
  display: flex;
  flex-direction: column;
  gap: 30rpx;
  margin-bottom: 40rpx;
}

.upload-btn {
  background-color: #4CAF50;
  color: white;
  border-radius: 10rpx;
  font-size: 32rpx;
}

.preview-section {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.preview-image {
  width: 100%;
  height: 400rpx;
  margin-bottom: 30rpx;
  border-radius: 10rpx;
  border: 1px solid #eee;
}

.analyze-btn {
  background-color: #2196F3;
  color: white;
  border-radius: 10rpx;
  font-size: 32rpx;
  width: 80%;
}

/* 加载区域样式 */
.loading-section {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400rpx;
  margin-top: 40rpx;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  background-color: #fff;
  border-radius: 20rpx;
  padding: 40rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.1);
  width: 80%;
}

.loading-spinner {
  width: 80rpx;
  height: 80rpx;
  border: 6rpx solid #f3f3f3;
  border-top: 6rpx solid #2196F3;
  border-radius: 50%;
  animation: spin 1.5s linear infinite;
  margin-bottom: 30rpx;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.loading-title {
  font-size: 32rpx;
  font-weight: bold;
  margin-bottom: 10rpx;
}

.loading-step {
  font-size: 28rpx;
  color: #2196F3;
  margin-bottom: 20rpx;
}

.loading-dots {
  display: flex;
  justify-content: center;
  margin-top: 20rpx;
}

.dot {
  width: 16rpx;
  height: 16rpx;
  background-color: #2196F3;
  border-radius: 50%;
  margin: 0 8rpx;
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
</style>
