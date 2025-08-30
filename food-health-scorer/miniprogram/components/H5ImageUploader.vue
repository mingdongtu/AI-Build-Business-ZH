<!-- H5环境下的图片上传组件 -->
<template>
  <view class="h5-image-uploader">
    <view v-if="!imageData" class="upload-area" @click="chooseImage">
      <view class="upload-icon">+</view>
      <view class="upload-text">点击上传图片</view>
    </view>
    <view v-else class="image-preview">
      <image :src="imageData" mode="aspectFit" @click="previewImage"></image>
      <view class="image-actions">
        <button type="primary" size="mini" @click="analyzeImage">分析图片</button>
        <button type="default" size="mini" @click="resetImage">重新选择</button>
      </view>
    </view>
    <input 
      ref="fileInput" 
      type="file" 
      accept="image/*" 
      style="display: none;" 
      @change="onFileChange"
    />
    <view v-if="showTextInput" class="text-input-area">
      <textarea 
        v-model="ingredientsText" 
        placeholder="无法上传图片时，请直接输入配料表文字内容" 
        class="ingredients-textarea"
      ></textarea>
      <button type="primary" @click="analyzeText">分析文字</button>
    </view>
    <view class="toggle-input-mode" @click="toggleInputMode">
      {{ showTextInput ? '使用图片上传模式' : '无法上传图片？点此输入文字' }}
    </view>
  </view>
</template>

<script>
import BaiduOCR from '../utils/baiduOcr';
import DeepSeekAnalyzer from '../utils/deepseekAnalyzer';

export default {
  name: 'H5ImageUploader',
  data() {
    return {
      imageData: '',
      showTextInput: false,
      ingredientsText: '',
      isH5: false
    };
  },
  mounted() {
    // 检测是否为H5环境
    this.isH5 = typeof window !== 'undefined' && typeof document !== 'undefined';
    console.log('H5ImageUploader mounted, isH5:', this.isH5);
  },
  methods: {
    chooseImage() {
      if (this.isH5) {
        // H5环境使用input file选择文件
        this.$refs.fileInput.click();
      } else {
        // 非H5环境使用uni API
        uni.chooseImage({
          count: 1,
          sizeType: ['compressed'],
          sourceType: ['album', 'camera'],
          success: (res) => {
            this.imageData = res.tempFilePaths[0];
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
    onFileChange(e) {
      const file = e.target.files[0];
      if (!file) return;
      
      // 检查文件类型
      if (!file.type.match('image.*')) {
        uni.showToast({
          title: '请选择图片文件',
          icon: 'none'
        });
        return;
      }
      
      // 读取文件为base64
      const reader = new FileReader();
      reader.onload = (e) => {
        this.imageData = e.target.result;
      };
      reader.onerror = (e) => {
        console.error('读取文件失败:', e);
        uni.showToast({
          title: '读取文件失败',
          icon: 'none'
        });
      };
      reader.readAsDataURL(file);
    },
    previewImage() {
      if (this.imageData) {
        uni.previewImage({
          urls: [this.imageData],
          current: this.imageData
        });
      }
    },
    resetImage() {
      this.imageData = '';
      if (this.$refs.fileInput) {
        this.$refs.fileInput.value = '';
      }
    },
    toggleInputMode() {
      this.showTextInput = !this.showTextInput;
    },
    async analyzeImage() {
      if (!this.imageData) {
        uni.showToast({
          title: '请先选择图片',
          icon: 'none'
        });
        return;
      }
      
      try {
        uni.showLoading({
          title: '正在识别文字...',
          mask: true
        });
        
        // 在H5环境下，直接使用base64数据进行OCR
        if (this.isH5) {
          // 发送base64数据到后端进行OCR识别
          const result = await this.analyzeBase64Image(this.imageData);
          this.$emit('analysis-complete', result);
        } else {
          // 非H5环境，使用常规方式
          const ocrResult = await BaiduOCR.recognizeIngredients(this.imageData);
          
          if (!ocrResult.success) {
            throw new Error(ocrResult.error || '识别失败');
          }
          
          // 使用DeepSeek分析识别出的文本
          const analysisResult = await DeepSeekAnalyzer.analyzeText(ocrResult.text);
          const formattedResult = DeepSeekAnalyzer.formatAnalysisResult(analysisResult);
          
          this.$emit('analysis-complete', formattedResult);
        }
        
        uni.hideLoading();
      } catch (error) {
        uni.hideLoading();
        console.error('分析图片失败:', error);
        uni.showToast({
          title: `分析失败: ${error.message || '未知错误'}`,
          icon: 'none',
          duration: 3000
        });
        
        // 如果在H5环境下上传失败，提示用户使用文本输入模式
        if (this.isH5) {
          this.showTextInput = true;
          uni.showModal({
            title: '提示',
            content: 'H5环境可能无法直接上传图片，请尝试使用文本输入模式',
            showCancel: false
          });
        }
      }
    },
    async analyzeText() {
      if (!this.ingredientsText.trim()) {
        uni.showToast({
          title: '请输入配料表文字',
          icon: 'none'
        });
        return;
      }
      
      try {
        uni.showLoading({
          title: '正在分析...',
          mask: true
        });
        
        // 使用DeepSeek分析文本
        const analysisResult = await DeepSeekAnalyzer.analyzeText(this.ingredientsText);
        const formattedResult = DeepSeekAnalyzer.formatAnalysisResult(analysisResult);
        
        this.$emit('analysis-complete', formattedResult);
        uni.hideLoading();
      } catch (error) {
        uni.hideLoading();
        console.error('分析文字失败:', error);
        uni.showToast({
          title: `分析失败: ${error.message || '未知错误'}`,
          icon: 'none',
          duration: 3000
        });
      }
    },
    async analyzeBase64Image(base64Data) {
      try {
        // 移除base64前缀
        const base64Content = base64Data.split(',')[1];
        
        // 使用POST请求发送base64数据
        const response = await uni.request({
          url: 'https://api.food-health-scorer.com/api/ocr/base64',
          method: 'POST',
          data: {
            image: base64Content
          },
          header: {
            'content-type': 'application/json'
          }
        });
        
        if (response.statusCode >= 200 && response.statusCode < 300) {
          const ocrResult = response.data;
          
          if (!ocrResult.text) {
            throw new Error('OCR识别失败，未返回有效文本');
          }
          
          // 使用DeepSeek分析识别出的文本
          const analysisResult = await DeepSeekAnalyzer.analyzeText(ocrResult.text);
          return DeepSeekAnalyzer.formatAnalysisResult(analysisResult);
        } else {
          throw new Error(`请求失败 (${response.statusCode})`);
        }
      } catch (error) {
        console.error('Base64图片分析失败:', error);
        throw error;
      }
    }
  }
};
</script>

<style>
.h5-image-uploader {
  width: 100%;
  padding: 20rpx;
}

.upload-area {
  width: 100%;
  height: 300rpx;
  border: 2rpx dashed #dcdfe6;
  border-radius: 8rpx;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background-color: #f8f9fa;
}

.upload-icon {
  font-size: 60rpx;
  color: #909399;
}

.upload-text {
  margin-top: 20rpx;
  color: #909399;
  font-size: 28rpx;
}

.image-preview {
  width: 100%;
}

.image-preview image {
  width: 100%;
  height: 400rpx;
  border-radius: 8rpx;
}

.image-actions {
  display: flex;
  justify-content: space-around;
  margin-top: 20rpx;
}

.text-input-area {
  margin-top: 30rpx;
}

.ingredients-textarea {
  width: 100%;
  height: 300rpx;
  border: 1rpx solid #dcdfe6;
  border-radius: 8rpx;
  padding: 20rpx;
  margin-bottom: 20rpx;
}

.toggle-input-mode {
  margin-top: 30rpx;
  text-align: center;
  color: #409eff;
  font-size: 28rpx;
}
</style>
