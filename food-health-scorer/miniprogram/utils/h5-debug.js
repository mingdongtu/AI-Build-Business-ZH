/**
 * H5环境调试辅助工具
 * 用于在H5环境下进行调试和错误捕获
 */

// 全局错误捕获
export function setupErrorHandling() {
  if (typeof window !== 'undefined') {
    // 捕获未处理的Promise错误
    window.addEventListener('unhandledrejection', event => {
      console.error('未捕获的Promise错误:', event.reason);
      // 可以在这里添加自定义错误处理逻辑
    });

    // 捕获全局JS错误
    window.addEventListener('error', event => {
      console.error('全局JS错误:', {
        message: event.message,
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
        error: event.error
      });
      // 可以在这里添加自定义错误处理逻辑
    });

    // 添加控制台调试信息
    console.log('H5调试模式已启用');
    console.log('浏览器环境:', navigator.userAgent);
    console.log('当前URL:', window.location.href);
  }
}

// 检查H5环境
export function isH5Environment() {
  return process.env.UNI_PLATFORM === 'h5' || 
         (typeof window !== 'undefined' && typeof navigator !== 'undefined');
}

// 打印Vue应用实例信息
export function logAppInfo(app) {
  if (app && typeof app === 'object') {
    console.log('Vue应用实例:', {
      appConfig: app._context ? '已配置' : '未配置',
      components: app._context ? Object.keys(app._context.components || {}).length : 0,
      directives: app._context ? Object.keys(app._context.directives || {}).length : 0
    });
  }
}

export default {
  setupErrorHandling,
  isH5Environment,
  logAppInfo
};
