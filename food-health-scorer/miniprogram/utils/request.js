// 配置基础URL
const BASE_URL = 'https://api.food-health-scorer.com'; // 实际后端API地址

// API端点配置
const API_ENDPOINTS = {
  // 图片分析端点
  ANALYZE: '/api/analyze',
  // 百度OCR端点
  BAIDU_OCR: '/api/ocr/baidu',
  // DeepSeek分析端点
  DEEPSEEK_ANALYZE: '/api/analyze/deepseek'
};

// 导出API端点，方便其他模块使用
export const ENDPOINTS = API_ENDPOINTS;

/**
 * 请求拦截器
 * @param {Object} config 请求配置
 */
const requestInterceptor = (config) => {
  // 可以在这里添加通用header，如token等
  const token = uni.getStorageSync('token');
  if (token) {
    config.header = {
      ...config.header,
      'Authorization': `Bearer ${token}`
    };
  }
  return config;
};

/**
 * 响应拦截器
 * @param {Object} response 响应结果
 */
const responseInterceptor = (response) => {
  // 这里可以对响应数据做统一处理
  if (response.statusCode >= 200 && response.statusCode < 300) {
    return response.data;
  } else {
    // 处理错误情况
    const error = new Error(response.data.message || '请求失败');
    error.response = response;
    throw error;
  }
};

/**
 * 统一请求方法
 * @param {Object} options 请求配置
 */
const request = (options) => {
  // 合并请求配置
  const config = {
    url: `${BASE_URL}${options.url}`,
    method: options.method || 'GET',
    data: options.data,
    header: {
      'content-type': 'application/json',
      ...options.header
    },
    timeout: options.timeout || 60000
  };

  // 应用请求拦截器
  const interceptedConfig = requestInterceptor(config);

  // 返回Promise
  return new Promise((resolve, reject) => {
    uni.request({
      ...interceptedConfig,
      success: (res) => {
        try {
          const result = responseInterceptor(res);
          resolve(result);
        } catch (error) {
          reject(error);
        }
      },
      fail: (err) => {
        reject(err);
      }
    });
  });
};

/**
 * GET请求
 * @param {String} url 请求地址
 * @param {Object} params 请求参数
 * @param {Object} options 其他配置
 */
const get = (url, params = {}, options = {}) => {
  return request({
    url,
    method: 'GET',
    data: params,
    ...options
  });
};

/**
 * POST请求
 * @param {String} url 请求地址
 * @param {Object} data 请求数据
 * @param {Object} options 其他配置
 */
const post = (url, data = {}, options = {}) => {
  return request({
    url,
    method: 'POST',
    data,
    ...options
  });
};

/**
 * 上传文件
 * @param {String} url 上传地址
 * @param {String} filePath 文件路径
 * @param {String} name 文件对应的key
 * @param {Object} formData 附加的表单数据
 * @param {Object} options 其他配置
 */
const uploadFile = (url, filePath, name = 'file', formData = {}, options = {}) => {
  const token = uni.getStorageSync('token');
  const header = token ? { 'Authorization': `Bearer ${token}` } : {};
  
  // 检测当前环境
  const isH5 = typeof window !== 'undefined' && typeof document !== 'undefined';
  
  return new Promise((resolve, reject) => {
    // 在H5环境下添加额外的错误处理
    if (isH5) {
      console.log('在H5环境下上传文件:', filePath);
    }
    
    uni.uploadFile({
      url: `${BASE_URL}${url}`,
      filePath,
      name,
      formData,
      header: {
        ...header,
        ...options.header
      },
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          // 上传文件成功
          let data;
          try {
            data = JSON.parse(res.data);
          } catch (e) {
            data = res.data;
          }
          resolve(data);
        } else {
          let errorMsg = '上传失败';
          try {
            const errorData = JSON.parse(res.data);
            errorMsg = errorData.message || errorData.error || errorMsg;
          } catch (e) {}
          
          reject(new Error(`${errorMsg} (${res.statusCode})`));
        }
      },
      fail: (err) => {
        console.error('上传文件失败:', err);
        // 检查是否是H5环境特有错误
        if (isH5 && err.errMsg && err.errMsg.includes('uploadFile:fail')) {
          reject(new Error('在H5环境下上传文件失败，请使用小程序或原生应用'));
        } else {
          reject(new Error(err.errMsg || '网络错误'));
        }
      }
    });
  });
};

/**
 * 专用于上传食品图片并获取分析结果
 * @param {String} filePath 图片文件路径
 * @param {Object} options 额外配置选项
 * @returns {Promise} 返回分析结果的Promise
 */
const uploadImage = (filePath, options = {}) => {
  if (!filePath) {
    return Promise.reject(new Error('图片路径不能为空'));
  }

  // 检测当前环境
  const isH5 = typeof window !== 'undefined' && typeof document !== 'undefined';
  
  // 显示压缩进度
  const showProgress = options.showProgress !== false;
  if (showProgress) {
    uni.showLoading({
      title: '正在上传...',
      mask: true
    });
  }

  // 判断是否需要压缩图片
  const compressImage = (path) => {
    // 如果指定了不压缩或者平台不支持，直接返回原路径
    if (options.noCompress || !uni.compressImage) {
      return Promise.resolve(path);
    }

    return new Promise((resolve, reject) => {
      uni.compressImage({
        src: path,
        quality: options.quality || 80, // 压缩质量 0-100
        success: (res) => {
          resolve(res.tempFilePath);
        },
        fail: (err) => {
          console.warn('图片压缩失败，使用原图:', err);
          resolve(path); // 失败时使用原图
        }
      });
    });
  };

  // 先压缩图片，再上传
  return compressImage(filePath).then(compressedPath => {
    return new Promise((resolve, reject) => {
      const formData = options.formData || {};
      
      // 添加请求参数
      if (options.params) {
        Object.keys(options.params).forEach(key => {
          formData[key] = options.params[key];
        });
      }
      
      // 在H5环境下的特殊处理
      if (isH5) {
        console.log('H5环境上传图片:', compressedPath);
        
        // 如果是H5环境，检查是否是本地文件路径而非base64
        if (compressedPath.indexOf('data:image') !== 0 && compressedPath.indexOf('blob:') !== 0) {
          // 在H5环境下，如果是本地文件路径，需要转换为base64或blob
          if (showProgress) {
            uni.hideLoading();
          }
          reject(new Error('H5环境不支持直接上传本地文件路径，请使用小程序或原生应用'));
          return;
        }
      }

      uni.uploadFile({
        url: `${BASE_URL}${options.url || API_ENDPOINTS.ANALYZE}`,
        filePath: compressedPath,
        name: options.name || 'image',
        formData: formData,
        header: {
          ...requestInterceptor({}).header,
          ...options.header
        },
        success: (res) => {
          if (showProgress) {
            uni.hideLoading();
          }

          if (res.statusCode >= 200 && res.statusCode < 300) {
            try {
              // 尝试解析JSON响应
              const data = JSON.parse(res.data);
              resolve(data);
            } catch (e) {
              console.error('解析响应数据失败:', e);
              reject(new Error('解析响应数据失败'));
            }
          } else {
            let errorMsg = '上传失败';
            try {
              const errorData = JSON.parse(res.data);
              errorMsg = errorData.message || errorData.error || errorMsg;
            } catch (e) {}
            
            reject(new Error(`${errorMsg} (${res.statusCode})`));
          }
        },
        fail: (err) => {
          if (showProgress) {
            uni.hideLoading();
          }
          console.error('上传失败:', err);
          
          // 检查是否是H5环境特有错误
          if (isH5 && err.errMsg && err.errMsg.includes('uploadFile:fail')) {
            reject(new Error('H5环境不支持直接上传文件，请使用小程序或原生应用。如需在H5环境测试，请使用文本输入模式'));
          } else {
            reject(new Error(err.errMsg || '网络错误，请检查网络连接'));
          }
        }
      });
    });
  }).catch(err => {
    if (showProgress) {
      uni.hideLoading();
    }
    throw err;
  });
};

// 导出API
export default {
  request,
  get,
  post,
  uploadFile,
  uploadImage
};
