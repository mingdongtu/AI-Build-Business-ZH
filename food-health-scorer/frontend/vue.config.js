module.exports = {
  publicPath: process.env.NODE_ENV === 'production'
    ? '/'
    : '/',
  outputDir: 'dist',
  assetsDir: 'static',
  productionSourceMap: false,
  devServer: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        pathRewrite: {
          '^/api': '/api'
        }
      }
    },
    client: {
      overlay: {
        warnings: false,
        errors: true
      }
    }
  },
  chainWebpack: config => {
    // Handle environment variables
    config.plugin('define').tap(args => {
      const env = args[0]['process.env'] || {}
      
      // Ensure VUE_APP_API_URL is available
      env.VUE_APP_API_URL = JSON.stringify(process.env.VUE_APP_API_URL || '/api')
      
      args[0]['process.env'] = env
      return args
    })
  }
}
