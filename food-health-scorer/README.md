# 食品健康评分系统 (Food Health Scorer)

这是一个基于Vue3和Python FastAPI的H5应用，用于通过拍照上传食品包装袋配料表图片，对食品健康度进行打分（0-100分）并提供科学理由。

## 项目结构

```
food-health-scorer/
├── backend/                # Python FastAPI 后端
│   ├── api/                # API路由
│   ├── models/             # 数据模型和分析逻辑
│   ├── utils/              # 工具函数和图像处理
│   ├── main.py             # 主应用入口
│   └── requirements.txt    # Python依赖
└── frontend/               # Vue3 前端
    ├── src/                # 源代码
    │   ├── assets/         # 静态资源
    │   ├── components/     # 组件
    │   ├── views/          # 页面视图
    │   ├── App.vue         # 主应用组件
    │   ├── main.js         # 入口文件
    │   └── router/         # 路由配置
    └── package.json        # NPM依赖
```

## 安装说明

### 前端 (Vue3)

1. 安装Node.js和npm (如果尚未安装)
2. 进入前端目录并安装依赖:

```bash
cd food-health-scorer/frontend
npm install
```

3. 启动开发服务器:

```bash
npm run serve
```

前端将在 http://localhost:8080 运行。

### 后端 (Python FastAPI)

1. 安装Python 3.8+和pip (如果尚未安装)
2. 安装Tesseract OCR (用于图像文字识别):

```bash
# macOS
brew install tesseract
brew install tesseract-lang  # 安装中文语言包

# Ubuntu/Debian
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-chi-sim  # 中文简体语言包
```

3. 进入后端目录并安装Python依赖:

```bash
cd food-health-scorer/backend
pip install -r requirements.txt
```

4. 启动FastAPI服务器:

```bash
python main.py
```

后端API将在 http://localhost:8000 运行。

## 使用说明

1. 打开前端应用 (http://localhost:8080)
2. 点击"拍照上传"按钮，使用相机拍摄食品包装上的配料表
3. 确认图片后点击"分析配料"按钮
4. 系统将分析图片并显示健康评分结果

## 技术栈

- **前端**: Vue 3, Vue Router, Axios
- **后端**: Python, FastAPI, OpenCV, Tesseract OCR
- **图像处理**: OpenCV, Pillow, pytesseract

## 注意事项

- 确保拍摄的配料表图片清晰可读
- 系统需要连接互联网才能正常工作
- 所有使用的技术均为开源且不涉及付费SDK
