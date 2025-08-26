#!/usr/bin/env python3
"""
启动后端服务并加载配置
"""

import os
import sys

# 导入配置文件
try:
    import config_local  # 这会设置环境变量
    print("✓ 配置文件已加载")
except ImportError:
    print("⚠ 配置文件 config_local.py 不存在")
    print("请确保已创建配置文件并设置了百度OCR API密钥")

# 检查配置状态
print("\n配置状态检查:")
print(f"百度OCR API Key: {'✓ 已配置' if os.getenv('BAIDU_OCR_API_KEY') else '✗ 未配置'}")
print(f"百度OCR Secret Key: {'✓ 已配置' if os.getenv('BAIDU_OCR_SECRET_KEY') else '✗ 未配置'}")
print(f"DeepSeek API Key: {'✓ 已配置' if os.getenv('DEEPSEEK_API_KEY') else '✗ 未配置'}")

# 启动服务
if __name__ == "__main__":
    import uvicorn
    from main import app
    
    print("\n🚀 启动食品健康评分API服务...")
    print("访问地址: http://localhost:8000")
    print("API文档: http://localhost:8000/docs")
    print("健康检查: http://localhost:8000/health")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )
