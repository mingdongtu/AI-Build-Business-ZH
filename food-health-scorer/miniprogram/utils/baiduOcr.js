/**
 * 百度OCR工具类
 * 用于调用百度OCR API进行图片文字识别
 */
import request, { ENDPOINTS } from './request';

// 百度OCR API端点
const OCR_API_ENDPOINT = ENDPOINTS.BAIDU_OCR;

/**
 * 百度OCR服务类
 */
class BaiduOCR {
  /**
   * 使用百度OCR识别图片中的文字
   * @param {String} imagePath 图片路径
   * @param {Boolean} useAccurate 是否使用高精度识别，默认为true
   * @param {Object} options 其他选项
   * @returns {Promise} 返回识别结果
   */
  static async recognizeText(imagePath, useAccurate = true, options = {}) {
    if (!imagePath) {
      return Promise.reject(new Error('图片路径不能为空'));
    }

    try {
      // 显示加载提示
      if (options.showLoading !== false) {
        uni.showLoading({
          title: '正在识别文字...',
          mask: true
        });
      }

      // 构建请求参数
      const params = {
        use_accurate: useAccurate
      };

      // 上传图片并获取OCR结果
      const result = await request.uploadImage(imagePath, {
        url: OCR_API_ENDPOINT,
        name: 'image',
        params,
        showProgress: false, // 不显示上传进度，因为我们已经显示了加载提示
        ...options
      });

      // 隐藏加载提示
      if (options.showLoading !== false) {
        uni.hideLoading();
      }

      // 检查OCR结果
      if (!result || !result.text) {
        throw new Error('OCR识别失败，未返回有效文本');
      }

      return {
        text: result.text,
        wordsCount: result.words_count || 0,
        success: true
      };
    } catch (error) {
      // 隐藏加载提示
      if (options.showLoading !== false) {
        uni.hideLoading();
      }

      console.error('百度OCR识别失败:', error);
      
      // 返回错误结果
      return {
        text: '',
        wordsCount: 0,
        success: false,
        error: error.message || '识别失败'
      };
    }
  }

  /**
   * 识别食品配料表
   * @param {String} imagePath 图片路径
   * @param {Object} options 其他选项
   * @returns {Promise} 返回识别结果
   */
  static async recognizeIngredients(imagePath, options = {}) {
    // 默认使用高精度识别配料表
    return this.recognizeText(imagePath, true, options);
  }
}

export default BaiduOCR;
