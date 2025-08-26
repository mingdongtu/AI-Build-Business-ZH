<template>
  <div class="image-uploader">
    <div class="camera-container" v-if="showCamera">
      <video ref="videoElement" autoplay playsinline></video>
      <div class="camera-controls">
        <button @click="captureImage" class="capture-btn">拍照</button>
        <button @click="toggleCamera(false)" class="cancel-btn">取消</button>
      </div>
    </div>
    
    <div class="upload-container" v-else>
      <div class="preview-container" v-if="imagePreview">
        <img :src="imagePreview" alt="预览" class="image-preview" />
        <div class="preview-controls">
          <button @click="uploadImage" class="upload-btn" :disabled="isUploading">上传</button>
          <button @click="resetImage" class="reset-btn" :disabled="isUploading">重置</button>
        </div>
      </div>
      
      <div class="select-container" v-else>
        <label for="file-upload" class="file-label">
          <span>选择图片</span>
          <input
            type="file"
            id="file-upload"
            accept="image/*"
            @change="onFileSelected"
            :disabled="isUploading"
          />
        </label>
        <button @click="toggleCamera(true)" class="camera-btn">打开相机</button>
      </div>
      
      <div class="progress-container" v-if="isUploading">
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: `${uploadProgress}%` }"></div>
        </div>
        <div class="progress-text">{{ uploadProgress }}%</div>
      </div>
      
      <div class="error-message" v-if="errorMessage">
        {{ errorMessage }}
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'ImageUploader',
  data() {
    return {
      showCamera: false,
      stream: null,
      imageFile: null,
      imagePreview: null,
      isUploading: false,
      uploadProgress: 0,
      errorMessage: null,
      apiUrl: process.env.VUE_APP_API_URL || 'http://localhost:8000'
    };
  },
  methods: {
    toggleCamera(show) {
      this.showCamera = show;
      if (show) {
        this.initCamera();
      } else {
        this.stopCamera();
      }
    },
    
    async initCamera() {
      try {
        this.stream = await navigator.mediaDevices.getUserMedia({
          video: {
            facingMode: 'environment',
            width: { ideal: 1280 },
            height: { ideal: 720 }
          }
        });
        
        if (this.$refs.videoElement) {
          this.$refs.videoElement.srcObject = this.stream;
        }
      } catch (error) {
        this.errorMessage = '无法访问相机: ' + error.message;
        this.showCamera = false;
        console.error('Camera error:', error);
      }
    },
    
    stopCamera() {
      if (this.stream) {
        this.stream.getTracks().forEach(track => track.stop());
        this.stream = null;
      }
    },
    
    captureImage() {
      const video = this.$refs.videoElement;
      const canvas = document.createElement('canvas');
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      
      const ctx = canvas.getContext('2d');
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      
      // Convert to blob
      canvas.toBlob(blob => {
        this.imageFile = new File([blob], "camera-capture.jpg", { type: "image/jpeg" });
        this.imagePreview = URL.createObjectURL(blob);
        this.toggleCamera(false);
      }, 'image/jpeg', 0.9);
    },
    
    onFileSelected(event) {
      const file = event.target.files[0];
      if (!file) return;
      
      // Validate file type
      if (!file.type.match('image.*')) {
        this.errorMessage = '请选择图片文件';
        return;
      }
      
      this.imageFile = file;
      this.imagePreview = URL.createObjectURL(file);
      this.errorMessage = null;
    },
    
    resetImage() {
      this.imageFile = null;
      if (this.imagePreview) {
        URL.revokeObjectURL(this.imagePreview);
      }
      this.imagePreview = null;
      this.errorMessage = null;
      this.uploadProgress = 0;
    },
    
    async uploadImage() {
      if (!this.imageFile) {
        this.errorMessage = '请先选择或拍摄图片';
        return;
      }
      
      this.isUploading = true;
      this.uploadProgress = 0;
      this.errorMessage = null;
      
      const formData = new FormData();
      formData.append('image', this.imageFile);
      
      try {
        const response = await axios.post(
          `${this.apiUrl}/api/analyze`, 
          formData,
          {
            headers: {
              'Content-Type': 'multipart/form-data'
            },
            onUploadProgress: (progressEvent) => {
              this.uploadProgress = Math.round(
                (progressEvent.loaded * 100) / progressEvent.total
              );
            }
          }
        );
        
        this.isUploading = false;
        this.$emit('analysis-complete', response.data);
      } catch (error) {
        this.isUploading = false;
        
        if (error.response) {
          // Server responded with an error
          this.errorMessage = `服务器错误: ${error.response.data.detail || error.response.statusText}`;
        } else if (error.request) {
          // Request made but no response received
          this.errorMessage = '网络错误: 无法连接到服务器';
        } else {
          // Error in request setup
          this.errorMessage = `上传错误: ${error.message}`;
        }
        
        console.error('Upload error:', error);
      }
    }
  },
  beforeUnmount() {
    this.stopCamera();
    if (this.imagePreview) {
      URL.revokeObjectURL(this.imagePreview);
    }
  }
};
</script>

<style scoped>
.image-uploader {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  background-color: #fff;
}

.camera-container {
  position: relative;
  width: 100%;
  aspect-ratio: 4/3;
  overflow: hidden;
  border-radius: 8px;
  background-color: #000;
}

.camera-container video {
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
  justify-content: center;
  gap: 20px;
}

.capture-btn, .cancel-btn {
  padding: 10px 20px;
  border-radius: 20px;
  border: none;
  font-weight: bold;
  cursor: pointer;
}

.capture-btn {
  background-color: #4CAF50;
  color: white;
}

.cancel-btn {
  background-color: #f44336;
  color: white;
}

.upload-container {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.preview-container {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}

.image-preview {
  max-width: 100%;
  max-height: 300px;
  border-radius: 8px;
  object-fit: contain;
}

.preview-controls {
  display: flex;
  gap: 10px;
}

.upload-btn, .reset-btn {
  padding: 8px 16px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-weight: bold;
}

.upload-btn {
  background-color: #2196F3;
  color: white;
}

.upload-btn:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.reset-btn {
  background-color: #607D8B;
  color: white;
}

.reset-btn:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.select-container {
  display: flex;
  flex-direction: column;
  gap: 15px;
  align-items: center;
}

.file-label {
  display: inline-block;
  padding: 10px 20px;
  background-color: #2196F3;
  color: white;
  border-radius: 4px;
  cursor: pointer;
  text-align: center;
  width: 100%;
  max-width: 200px;
}

.file-label input {
  display: none;
}

.camera-btn {
  padding: 10px 20px;
  background-color: #9C27B0;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  width: 100%;
  max-width: 200px;
}

.progress-container {
  margin-top: 15px;
}

.progress-bar {
  height: 10px;
  background-color: #e0e0e0;
  border-radius: 5px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background-color: #4CAF50;
  transition: width 0.3s ease;
}

.progress-text {
  text-align: center;
  margin-top: 5px;
  font-size: 14px;
  color: #666;
}

.error-message {
  color: #f44336;
  text-align: center;
  margin-top: 10px;
  padding: 10px;
  background-color: #ffebee;
  border-radius: 4px;
}

/* Responsive styles */
@media (max-width: 480px) {
  .image-uploader {
    padding: 15px;
    box-shadow: none;
  }
  
  .camera-controls {
    bottom: 10px;
  }
  
  .capture-btn, .cancel-btn {
    padding: 8px 16px;
  }
}
</style>
