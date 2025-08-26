<template>
  <div class="camera-capture">
    <div v-if="!cameraActive && !imageData" class="camera-trigger">
      <button class="camera-button" @click="activateCamera">
        <span class="camera-icon">📷</span>
        <span>拍照上传</span>
      </button>
      <p class="camera-info">请拍摄食品包装袋上的配料表部分</p>
      
      <!-- 文件上传备选方案 -->
      <div class="file-upload-option">
        <p>或者</p>
        <label for="file-upload" class="file-upload-label">
          从相册选择图片
          <input 
            id="file-upload"
            type="file" 
            accept="image/*"
            @change="handleFileUpload" 
            class="file-input"
          />
        </label>
      </div>
    </div>

    <!-- 相机视图 -->
    <div v-if="cameraActive" class="camera-view">
      <video 
        ref="videoElement" 
        class="camera-video" 
        autoplay 
        playsinline
        @loadedmetadata="onVideoLoaded"
      ></video>
      
      <div class="camera-controls">
        <button class="control-button cancel" @click="cancelCamera">取消</button>
        <button class="control-button capture" @click="captureImage">拍照</button>
      </div>
      
      <!-- 相机引导框 -->
      <div class="camera-guide">
        <div class="guide-frame"></div>
        <p class="guide-text">请将配料表放入框内</p>
      </div>
    </div>

    <!-- 图片预览 -->
    <div v-if="imageData && !cameraActive" class="preview-container">
      <img :src="imageData" alt="食品包装图片预览" class="preview-image" />
      <div class="preview-actions">
        <button class="action-button cancel" @click="resetImage">重新拍摄</button>
        <button class="action-button confirm" @click="confirmImage">确认使用</button>
      </div>
    </div>

    <!-- 错误提示 -->
    <div v-if="errorMessage" class="error-message">
      <p>{{ errorMessage }}</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CameraCapture',
  emits: ['image-captured', 'error'],
  data() {
    return {
      cameraActive: false,
      imageData: null,
      stream: null,
      errorMessage: '',
      imageFile: null,
      cameraFacing: 'environment', // 默认使用后置相机
      cameraConstraints: {
        video: {
          facingMode: 'environment',
          width: { ideal: 1920 },
          height: { ideal: 1080 }
        }
      }
    }
  },
  methods: {
    // 激活相机
    async activateCamera() {
      this.errorMessage = '';
      try {
        this.stream = await navigator.mediaDevices.getUserMedia(this.cameraConstraints);
        this.cameraActive = true;
        
        // 延迟一点时间确保视频元素已经挂载
        this.$nextTick(() => {
          if (this.$refs.videoElement) {
            this.$refs.videoElement.srcObject = this.stream;
          }
        });
      } catch (error) {
        console.error('相机访问失败:', error);
        this.handleError('无法访问相机，请检查权限设置或尝试从相册上传');
      }
    },
    
    // 视频加载完成
    onVideoLoaded() {
      // 可以在这里添加视频加载完成后的逻辑
      console.log('相机视频流已加载');
    },
    
    // 切换前后摄像头
    switchCamera() {
      if (this.stream) {
        this.stopCamera();
        this.cameraFacing = this.cameraFacing === 'environment' ? 'user' : 'environment';
        this.cameraConstraints.video.facingMode = this.cameraFacing;
        this.activateCamera();
      }
    },
    
    // 停止相机
    stopCamera() {
      if (this.stream) {
        this.stream.getTracks().forEach(track => track.stop());
        this.stream = null;
      }
    },
    
    // 取消相机
    cancelCamera() {
      this.stopCamera();
      this.cameraActive = false;
    },
    
    // 拍照
    captureImage() {
      try {
        const video = this.$refs.videoElement;
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        // 转换为图片数据
        this.imageData = canvas.toDataURL('image/jpeg', 0.9);
        
        // 将 base64 转换为文件对象
        this.convertBase64ToFile(this.imageData);
        
        // 停止相机
        this.stopCamera();
        this.cameraActive = false;
      } catch (error) {
        console.error('拍照失败:', error);
        this.handleError('拍照失败，请重试');
      }
    },
    
    // 将 base64 转换为文件对象
    convertBase64ToFile(base64Data) {
      const byteString = atob(base64Data.split(',')[1]);
      const mimeString = base64Data.split(',')[0].split(':')[1].split(';')[0];
      const ab = new ArrayBuffer(byteString.length);
      const ia = new Uint8Array(ab);
      
      for (let i = 0; i < byteString.length; i++) {
        ia[i] = byteString.charCodeAt(i);
      }
      
      const blob = new Blob([ab], { type: mimeString });
      this.imageFile = new File([blob], "camera_capture.jpg", { type: "image/jpeg" });
    },
    
    // 处理文件上传
    handleFileUpload(event) {
      const file = event.target.files[0];
      if (!file) return;
      
      // 检查文件类型
      if (!file.type.startsWith('image/')) {
        this.handleError('请上传图片文件');
        return;
      }
      
      // 检查文件大小 (限制为 10MB)
      if (file.size > 10 * 1024 * 1024) {
        this.handleError('图片大小不能超过10MB');
        return;
      }
      
      this.imageFile = file;
      const reader = new FileReader();
      reader.onload = e => {
        this.imageData = e.target.result;
      };
      reader.onerror = () => {
        this.handleError('图片读取失败，请重试');
      };
      reader.readAsDataURL(file);
    },
    
    // 重置图片
    resetImage() {
      this.imageData = null;
      this.imageFile = null;
      this.errorMessage = '';
    },
    
    // 确认使用图片
    confirmImage() {
      if (this.imageFile) {
        this.$emit('image-captured', {
          file: this.imageFile,
          dataUrl: this.imageData
        });
      } else {
        this.handleError('图片处理失败，请重试');
      }
    },
    
    // 处理错误
    handleError(message) {
      this.errorMessage = message;
      this.$emit('error', message);
    }
  },
  beforeUnmount() {
    // 组件销毁前停止相机
    this.stopCamera();
  }
}
</script>

<style scoped>
.camera-capture {
  width: 100%;
  max-width: 500px;
  margin: 0 auto;
}

.camera-trigger {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 0;
}

.camera-button {
  background-color: #4CAF50;
  border: none;
  color: white;
  padding: 15px 30px;
  text-align: center;
  font-size: 16px;
  margin: 10px 2px;
  cursor: pointer;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
  transition: all 0.3s ease;
}

.camera-button:hover {
  background-color: #45a049;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}

.camera-button:active {
  transform: translateY(0);
  box-shadow: 0 2px 3px rgba(0,0,0,0.2);
}

.camera-icon {
  font-size: 24px;
  margin-right: 10px;
}

.camera-info {
  margin-top: 15px;
  color: #666;
  font-size: 14px;
}

.file-upload-option {
  margin-top: 20px;
  text-align: center;
}

.file-upload-label {
  color: #2196F3;
  cursor: pointer;
  padding: 8px 16px;
  border: 1px solid #2196F3;
  border-radius: 4px;
  display: inline-block;
  margin-top: 5px;
  transition: all 0.3s ease;
}

.file-upload-label:hover {
  background-color: rgba(33, 150, 243, 0.1);
}

.file-input {
  display: none;
}

.camera-view {
  position: relative;
  width: 100%;
  height: 0;
  padding-bottom: 133.33%; /* 3:4 宽高比 */
  background-color: #000;
  border-radius: 8px;
  overflow: hidden;
}

.camera-video {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.camera-controls {
  position: absolute;
  bottom: 20px;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-around;
  padding: 0 20px;
  z-index: 10;
}

.control-button {
  padding: 12px 24px;
  border: none;
  border-radius: 30px;
  font-weight: bold;
  cursor: pointer;
  opacity: 0.9;
  transition: all 0.2s ease;
}

.control-button:hover {
  opacity: 1;
  transform: scale(1.05);
}

.cancel {
  background-color: rgba(244, 67, 54, 0.8);
  color: white;
}

.capture {
  background-color: white;
  color: #333;
}

.camera-guide {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  pointer-events: none;
}

.guide-frame {
  width: 80%;
  height: 40%;
  border: 2px dashed rgba(255, 255, 255, 0.8);
  border-radius: 8px;
}

.guide-text {
  color: white;
  background-color: rgba(0, 0, 0, 0.5);
  padding: 5px 10px;
  border-radius: 4px;
  margin-top: 10px;
  font-size: 14px;
}

.preview-container {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.preview-image {
  max-width: 100%;
  max-height: 300px;
  margin-bottom: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.preview-actions {
  display: flex;
  justify-content: space-between;
  width: 100%;
  max-width: 300px;
}

.action-button {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}

.action-button.cancel {
  background-color: #f44336;
  color: white;
}

.action-button.confirm {
  background-color: #2196F3;
  color: white;
}

.error-message {
  color: #f44336;
  margin-top: 15px;
  padding: 10px;
  background-color: rgba(244, 67, 54, 0.1);
  border-radius: 4px;
  text-align: center;
}

/* 移动端适配 */
@media (max-width: 480px) {
  .camera-button {
    padding: 12px 24px;
    font-size: 14px;
  }
  
  .camera-icon {
    font-size: 20px;
  }
  
  .preview-actions {
    flex-direction: column;
    gap: 10px;
  }
  
  .action-button {
    width: 100%;
  }
}
</style>
