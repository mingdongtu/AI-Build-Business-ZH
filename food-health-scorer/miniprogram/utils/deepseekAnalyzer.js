/**
 * DeepSeek V3.1 AI分析工具类
 * 用于调用DeepSeek API进行食品配料分析
 */
import request, { ENDPOINTS } from './request';

// DeepSeek分析API端点
const ANALYZE_API_ENDPOINT = ENDPOINTS.DEEPSEEK_ANALYZE;

/**
 * DeepSeek分析服务类
 */
class DeepSeekAnalyzer {
  /**
   * 分析食品配料表文本
   * @param {String} text 配料表文本
   * @param {Object} options 其他选项
   * @returns {Promise} 返回分析结果
   */
  static async analyzeText(text, options = {}) {
    if (!text || !text.trim()) {
      return Promise.reject(new Error('配料表文本不能为空'));
    }

    try {
      // 显示加载提示
      if (options.showLoading !== false) {
        uni.showLoading({
          title: '正在分析配料表...',
          mask: true
        });
      }

      // 发送文本分析请求
      const result = await request.post(ANALYZE_API_ENDPOINT, {
        text: text,
        ...options.params
      }, options);

      // 隐藏加载提示
      if (options.showLoading !== false) {
        uni.hideLoading();
      }

      return result;
    } catch (error) {
      // 隐藏加载提示
      if (options.showLoading !== false) {
        uni.hideLoading();
      }

      console.error('DeepSeek分析失败:', error);
      throw error;
    }
  }

  /**
   * 直接分析食品图片
   * @param {String} imagePath 图片路径
   * @param {Object} options 其他选项
   * @returns {Promise} 返回分析结果
   */
  static async analyzeImage(imagePath, options = {}) {
    if (!imagePath) {
      return Promise.reject(new Error('图片路径不能为空'));
    }

    try {
      // 显示加载提示
      if (options.showLoading !== false) {
        uni.showLoading({
          title: '正在分析食品图片...',
          mask: true
        });
      }

      // 上传图片并获取分析结果
      const result = await request.uploadImage(imagePath, {
        url: ANALYZE_API_ENDPOINT,
        name: 'image',
        showProgress: false, // 不显示上传进度，因为我们已经显示了加载提示
        ...options
      });

      // 隐藏加载提示
      if (options.showLoading !== false) {
        uni.hideLoading();
      }

      return result;
    } catch (error) {
      // 隐藏加载提示
      if (options.showLoading !== false) {
        uni.hideLoading();
      }

      console.error('DeepSeek图片分析失败:', error);
      throw error;
    }
  }

  /**
   * 格式化健康评分结果
   * @param {Object} result 原始分析结果
   * @returns {Object} 格式化后的结果
   */
  static formatAnalysisResult(result) {
    if (!result) {
      return {
        foodName: '未识别食品',
        score: 50,
        ingredients: [],
        healthPoints: ['无法获取详细分析'],
        recommendations: ['建议查看食品标签，选择天然成分较多的产品'],
        detailedAnalysis: {
          positiveAspects: [],
          negativeAspects: [],
          nutritionalHighlights: []
        }
      };
    }

    // 转换为前端使用的格式（驼峰命名）
    return {
      foodName: result.food_name || '未识别食品',
      score: result.score || 50,
      ingredients: result.ingredients || [],
      healthPoints: result.health_points || [],
      recommendations: result.recommendations || [],
      detailedAnalysis: {
        positiveAspects: result.detailed_analysis?.positive_aspects || [],
        negativeAspects: result.detailed_analysis?.negative_aspects || [],
        nutritionalHighlights: result.detailed_analysis?.nutritional_highlights || []
      }
    };
  }
}

export default DeepSeekAnalyzer;
