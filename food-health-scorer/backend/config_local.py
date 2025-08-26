#!/usr/bin/env python3
"""
本地API配置文件
使用前请将此文件重命名为 config.py 并设置环境变量
"""

import os

# 设置百度OCR API密钥
os.environ['BAIDU_OCR_API_KEY'] = 'qxIAKpmsAIFADM695cssGsac'
os.environ['BAIDU_OCR_SECRET_KEY'] = 'K8IkjGzpIvJJobaUBaqhaHTlFfqmODCl'

# DeepSeek API密钥（需要您提供）
# os.environ['DEEPSEEK_API_KEY'] = 'your_deepseek_api_key_here'
# os.environ['DEEPSEEK_API_BASE'] = 'https://api.deepseek.com'

# 应用配置
os.environ['DEBUG'] = 'True'
os.environ['HOST'] = '0.0.0.0'
os.environ['PORT'] = '8000'

print("✓ 百度OCR API密钥已配置")
if not os.getenv('DEEPSEEK_API_KEY'):
    print("⚠ DeepSeek API密钥尚未配置，请添加后完整测试")
