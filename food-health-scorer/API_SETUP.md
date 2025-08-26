# API 配置说明

本项目使用百度OCR和DeepSeek-V3.1 API来实现食品包装图片的文字识别和智能分析功能。

## 1. 百度OCR API 配置

### 获取API密钥
1. 访问 [百度智能云控制台](https://console.bce.baidu.com/)
2. 注册/登录账号
3. 进入"产品服务" -> "人工智能" -> "文字识别OCR"
4. 创建应用，获取API Key和Secret Key

### 配置步骤
1. 复制 `backend/.env.example` 为 `backend/.env`
2. 填入百度OCR API密钥：
```bash
BAIDU_OCR_API_KEY=your_baidu_api_key_here
BAIDU_OCR_SECRET_KEY=your_baidu_secret_key_here
```

### API调用说明
- 使用通用文字识别和高精度文字识别API
- 支持多种图片格式：JPEG、PNG、GIF、BMP等
- 自动处理访问令牌获取和刷新

## 2. DeepSeek-V3.1 API 配置

### 获取API密钥
1. 访问 [DeepSeek官网](https://www.deepseek.com/)
2. 注册账号并申请API访问权限
3. 在控制台获取API Key

### 配置步骤
在 `backend/.env` 文件中添加：
```bash
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_API_BASE=https://api.deepseek.com
```

### API调用说明
- 使用deepseek-chat模型进行食品分析
- 支持中文提示词和响应
- 自动解析JSON格式的分析结果

## 3. 环境变量完整配置示例

```bash
# 百度OCR API配置
BAIDU_OCR_API_KEY=your_baidu_api_key_here
BAIDU_OCR_SECRET_KEY=your_baidu_secret_key_here

# DeepSeek API配置
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_API_BASE=https://api.deepseek.com

# 应用配置
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

## 4. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

## 5. 启动服务

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 6. 健康检查

启动后可访问以下接口检查配置状态：
- `GET /health` - 检查API配置状态
- `GET /` - 查看API基本信息

## 7. 费用说明

### 百度OCR
- 通用文字识别：免费额度1000次/月，超出后按量计费
- 高精度文字识别：免费额度500次/月，超出后按量计费

### DeepSeek API
- 按token使用量计费
- 具体价格请参考DeepSeek官网

## 8. 错误处理

系统具备完善的错误处理机制：
- OCR失败时会返回默认结果
- AI分析失败时会提供基础建议
- 所有错误都会记录到日志中

## 9. 安全注意事项

- 不要将API密钥提交到版本控制系统
- 定期更换API密钥
- 监控API使用量，避免超出配额
- 在生产环境中设置适当的访问限制
