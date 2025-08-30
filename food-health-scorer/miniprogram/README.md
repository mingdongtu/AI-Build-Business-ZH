# 食品健康评分小程序

这是食品健康评分应用的微信小程序版本，基于uni-app框架开发，从原Vue3 Web应用迁移而来。

## 项目结构

```
miniprogram/
├── components/         # 组件目录
├── pages/              # 页面目录
│   ├── home/           # 首页
│   └── results/        # 结果页
├── static/             # 静态资源
├── styles/             # 样式文件
│   ├── global.scss     # 全局样式
│   └── variables.scss  # 样式变量
├── utils/              # 工具类
│   └── request.js      # 网络请求工具
├── App.vue             # 应用入口组件
├── main.js             # 应用入口文件
├── manifest.json       # 应用配置
├── pages.json          # 页面路由配置
└── package.json        # 项目依赖
```

## 迁移指南

### 1. 路由迁移

从Vue Router迁移到uni-app页面管理：

- Vue Router的路由配置已转换为`pages.json`中的页面配置
- 页面跳转方式变更：
  - `router.push()` → `uni.navigateTo()`
  - `router.replace()` → `uni.redirectTo()`
  - `router.go(-1)` → `uni.navigateBack()`

示例：
```js
// Vue Router (原代码)
router.push({ path: '/results', query: { id: 123 } })

// uni-app (新代码)
uni.navigateTo({
  url: '/pages/results/index?id=123'
})
```

### 2. 网络请求迁移

从Axios迁移到uni-app网络请求API：

- 已创建`utils/request.js`封装uni.request API
- 支持请求/响应拦截器
- 支持Promise接口
- 文件上传使用`uni.uploadFile`

示例：
```js
// Axios (原代码)
axios.get('/api/data').then(response => {
  console.log(response.data)
})

// uni-app (新代码)
import request from '@/utils/request'
request.get('/api/data').then(result => {
  console.log(result)
})
```

### 3. 组件迁移

Vue3组件迁移到uni-app注意事项：

- HTML标签替换为uni-app组件：
  - `<div>` → `<view>`
  - `<span>` → `<text>`
  - `<img>` → `<image>`
  - `<input>` → `<input>`
  - `<button>` → `<button>`

- Web API替换为uni-app API：
  - 相机API → `uni.chooseImage`
  - 本地存储 → `uni.setStorageSync`/`uni.getStorageSync`
  - 网络请求 → `uni.request`/`uni.uploadFile`

### 4. 样式适配

从px单位转换为rpx：

- 已设置`manifest.json`中的`"transformPx": false`，避免自动转换
- 手动将px替换为rpx，比例为1px = 2rpx
- 使用`styles/variables.scss`中的变量保持样式一致性
- 使用`styles/global.scss`中的通用样式类简化开发

### 5. 生命周期对应关系

Vue3生命周期钩子与uni-app对应关系：

- `beforeCreate`/`created` → `onLoad`
- `beforeMount`/`mounted` → `onReady`
- `beforeUnmount`/`unmounted` → `onUnload`
- `activated` → `onShow`
- `deactivated` → `onHide`

### 6. 开发与调试

1. 安装依赖：
```bash
cd miniprogram
npm install
```

2. 使用HBuilderX打开项目：
   - 导入项目到HBuilderX
   - 点击“运行”→“运行到小程序模拟器”→“微信开发者工具”
   - 或点击“运行”→“运行到浏览器”→“Chrome”（H5平台）

3. 使用微信开发者工具：
   - 导入项目
   - 填入AppID（在manifest.json中配置）
   - 开启“不校验合法域名”选项（开发阶段）

4. 使用命令行运行（H5平台）：
```bash
cd miniprogram
npm run dev:h5  # 开发环境
# 或
npm run build:h5  # 生产环境
```

### 7. 发布流程

1. 在微信公众平台注册小程序并获取AppID
2. 在`manifest.json`中填入AppID
3. 使用HBuilderX构建：点击“发行”→“小程序-微信”
4. 在微信开发者工具中上传代码
5. 在微信公众平台提交审核并发布

## 注意事项

1. 小程序限制：
   - 包大小限制为2MB，超过需分包加载
   - 网络请求域名需要在微信公众平台配置
   - 部分Web API在小程序中不可用

2. 多平台兼容：
   - 使用条件编译实现平台特定代码：
   ```js
   // #ifdef MP-WEIXIN
   // 微信小程序特有代码
   // #endif

   // #ifdef H5
   // H5平台特有代码
   // #endif
   ```
   - 摄像头调用在H5和小程序中有差异，已适配
   - 文件上传在H5中使用FormData，小程序中使用uni.uploadFile

3. 性能优化：
   - 减少不必要的组件嵌套
   - 合理使用`setData`
   - 图片资源压缩
   - 分包加载

4. 兼容性：
   - 测试不同机型和微信版本
   - 遵循小程序设计规范

## 后续开发建议

1. 添加用户登录与数据同步功能
2. 实现历史记录与收藏功能
3. 优化离线使用体验
4. 添加分享功能
5. 集成数据分析

## 相关资源

- [uni-app官方文档](https://uniapp.dcloud.io/)
- [微信小程序开发文档](https://developers.weixin.qq.com/miniprogram/dev/framework/)
- [HBuilderX下载](https://www.dcloud.io/hbuilderx.html)
