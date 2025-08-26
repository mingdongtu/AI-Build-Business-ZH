#!/usr/bin/env python3
"""
测试百度OCR配置获取
"""

import os
import sys

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_config_loading():
    """测试配置文件加载"""
    print("=== 测试配置文件加载 ===")
    
    # 检查配置文件导入前的环境变量
    print("导入配置文件前:")
    print(f"BAIDU_OCR_API_KEY: {os.getenv('BAIDU_OCR_API_KEY', '未设置')}")
    print(f"BAIDU_OCR_SECRET_KEY: {os.getenv('BAIDU_OCR_SECRET_KEY', '未设置')}")
    
    # 导入配置文件
    try:
        import config_local
        print("\n✓ config_local.py 导入成功")
    except ImportError as e:
        print(f"\n✗ config_local.py 导入失败: {e}")
        return False
    
    # 检查配置文件导入后的环境变量
    print("\n导入配置文件后:")
    api_key = os.getenv('BAIDU_OCR_API_KEY')
    secret_key = os.getenv('BAIDU_OCR_SECRET_KEY')
    
    print(f"BAIDU_OCR_API_KEY: {api_key[:10] + '...' if api_key else '未设置'}")
    print(f"BAIDU_OCR_SECRET_KEY: {secret_key[:10] + '...' if secret_key else '未设置'}")
    
    return bool(api_key and secret_key)

def test_baidu_ocr_init():
    """测试百度OCR初始化"""
    print("\n=== 测试百度OCR初始化 ===")
    
    try:
        from models.baidu_ocr import BaiduOCR
        
        # 初始化百度OCR
        ocr = BaiduOCR()
        
        print("✓ 百度OCR初始化成功")
        print(f"API Key: {ocr.api_key[:10] + '...' if ocr.api_key else '未获取'}")
        print(f"Secret Key: {ocr.secret_key[:10] + '...' if ocr.secret_key else '未获取'}")
        
        return True
        
    except Exception as e:
        print(f"✗ 百度OCR初始化失败: {e}")
        return False

def main():
    """主函数"""
    print("开始测试百度OCR配置获取...")
    
    # 测试配置文件加载
    config_ok = test_config_loading()
    
    # 测试百度OCR初始化
    ocr_ok = test_baidu_ocr_init()
    
    # 总结
    print("\n=== 测试结果 ===")
    print(f"配置文件加载: {'✓ 成功' if config_ok else '✗ 失败'}")
    print(f"百度OCR初始化: {'✓ 成功' if ocr_ok else '✗ 失败'}")
    
    if config_ok and ocr_ok:
        print("\n🎉 百度OCR配置获取测试通过！")
        print("密钥已正确从配置文件中获取")
    else:
        print("\n❌ 测试失败，请检查配置文件")

if __name__ == "__main__":
    main()
