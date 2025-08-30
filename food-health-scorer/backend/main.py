import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import logging
import sys
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Callable
from dotenv import load_dotenv
from api.routes import router as api_router
from api.routes_base64 import router as base64_router
from utils.image_processor import ImageProcessor

# 自定义中间件类来记录请求和响应信息
class APILoggingMiddleware(CORSMiddleware):
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await super().__call__(scope, receive, send)

        # 创建请求对象
        request = Request(scope)
        path = request.url.path
        method = request.method
        
        # 获取请求头信息
        headers = dict(request.headers)
        client_host = request.client.host if request.client else "unknown"
        
        # 创建日志对象
        logger = logging.getLogger("api")
        request_id = f"{int(time.time() * 1000)}-{os.urandom(4).hex()}"
        
        # 记录请求开始
        logger.info(f"API请求开始 [{request_id}] {method} {path} - 客户端: {client_host}")
        
        # 记录请求头
        logger.debug(f"API请求头 [{request_id}]: {headers}")
        
        # 记录请求参数
        query_params = dict(request.query_params)
        if query_params:
            logger.debug(f"API查询参数 [{request_id}]: {query_params}")
        
        # 记录请求体（如果不是文件上传）
        content_type = headers.get("content-type", "")
        if method == "POST" and "multipart/form-data" not in content_type:
            try:
                # 保存原始请求体
                original_receive = receive
                
                # 创建新的receive函数来捕获请求体
                async def receive_with_body():
                    message = await original_receive()
                    if message["type"] == "http.request" and "body" in message:
                        body = message.get("body", b"")
                        if body:
                            try:
                                body_text = body.decode("utf-8")
                                logger.debug(f"API请求体 [{request_id}]: {body_text[:1000]}")
                            except UnicodeDecodeError:
                                logger.debug(f"API请求体 [{request_id}]: [二进制数据, 长度: {len(body)}]")
                    return message
                
                # 记录响应
                start_time = time.time()
                
                # 创建新的send函数来捕获响应
                original_send = send
                
                async def send_with_logging(message):
                    if message["type"] == "http.response.start":
                        status_code = message["status"]
                        process_time = time.time() - start_time
                        logger.info(
                            f"API请求完成 [{request_id}] {method} {path} "
                            f"- 状态码: {status_code} - 处理时间: {process_time:.4f}s"
                        )
                    return await original_send(message)
                
                # 使用新的receive和send函数
                return await super().__call__(scope, receive_with_body, send_with_logging)
            except Exception as e:
                logger.error(f"API日志记录异常 [{request_id}]: {str(e)}")
        
        # 如果是文件上传或其他请求，直接记录响应
        start_time = time.time()
        
        # 创建新的send函数来捕获响应
        original_send = send
        
        async def send_with_logging(message):
            if message["type"] == "http.response.start":
                status_code = message["status"]
                process_time = time.time() - start_time
                logger.info(
                    f"API请求完成 [{request_id}] {method} {path} "
                    f"- 状态码: {status_code} - 处理时间: {process_time:.4f}s"
                )
            return await original_send(message)
        
        return await super().__call__(scope, receive, send_with_logging)

def setup_logging():
    """Configure logging to both console and file"""
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Create a custom logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Create formatters
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_format)
    
    # File handler - new file for each day
    current_date = datetime.now().strftime("%Y-%m-%d")
    file_handler = logging.FileHandler(
        log_dir / f"app_{current_date}.log",
        encoding='utf-8'
    )
    file_handler.setFormatter(file_format)
    
    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    # Set logging level for specific loggers if needed
    # logging.getLogger('uvicorn').setLevel(logging.WARNING)
    # logging.getLogger('uvicorn.error').setLevel(logging.WARNING)
    
    return logger

# Initialize logging
logger = setup_logging()

# Create FastAPI app
app = FastAPI(
    title="Food Health Scorer API",
    description="API for analyzing food packaging ingredients and providing health scores",
    version="0.1.0"
)

# Configure API logging middleware with CORS support
app.add_middleware(
    APILoggingMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局初始化ImageProcessor
image_processor = None

@app.on_event("startup")
async def startup_event():
    global image_processor
    
    # 加载环境变量
    try:
        # 尝试加载.env文件
        load_dotenv()
        logger.info("环境变量加载成功")
        
        # 尝试加载config_local.py
        try:
            import config_local
            logger.info("本地配置文件加载成功")
        except ImportError:
            logger.warning("未找到本地配置文件config_local.py，将使用环境变量")
            
        # 检查关键API密钥是否已配置
        if os.getenv('BAIDU_OCR_API_KEY'):
            logger.info("百度OCR API密钥已配置")
        else:
            logger.warning("百度OCR API密钥未配置，OCR功能可能无法正常工作")
            
        if os.getenv('DEEPSEEK_API_KEY'):
            logger.info("DeepSeek API密钥已配置")
        else:
            logger.warning("DeepSeek API密钥未配置，分析功能可能无法正常工作")
    except Exception as e:
        logger.error(f"加载配置文件失败: {str(e)}")
    
    # 初始化ImageProcessor
    logger.info("Initializing ImageProcessor on startup...")
    try:
        image_processor = ImageProcessor()
        logger.info("ImageProcessor initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize ImageProcessor: {str(e)}")
        raise e

# Include API routes
app.include_router(api_router, prefix="/api")
# Include Base64 API routes
app.include_router(base64_router, prefix="/api")

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to Food Health Scorer API"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
