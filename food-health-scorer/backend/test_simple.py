#!/usr/bin/env python3
"""
简单的API集成测试脚本
"""

import os
import sys
import logging

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """测试模块导入"""
    try:
        from models.baidu_ocr import BaiduOCR
        from models.deepseek_analyzer import DeepSeekAnalyzer
        logger.info("✓ 模块导入成功")
        return True
    except ImportError as e:
        logger.error(f"✗ 模块导入失败: {e}")
        return False

def test_config():
    """测试配置"""
    config_status = {
        "baidu_ocr": bool(os.getenv('BAIDU_OCR_API_KEY') and os.getenv('BAIDU_OCR_SECRET_KEY')),
        "deepseek": bool(os.getenv('DEEPSEEK_API_KEY'))
    }
    
    logger.info("配置状态:")
    for service, configured in config_status.items():
        status = "✓ 已配置" if configured else "✗ 未配置"
        logger.info(f"  {service}: {status}")
    
    return any(config_status.values())

def test_deepseek_fallback():
    """测试DeepSeek分析器的默认返回"""
    try:
        from models.deepseek_analyzer import DeepSeekAnalyzer
        analyzer = DeepSeekAnalyzer()
        
        # 测试默认结果
        default_result = analyzer._get_default_result()
        
        required_fields = ['food_name', 'ingredients', 'score', 'health_points', 'recommendations']
        for field in required_fields:
            if field not in default_result:
                logger.error(f"✗ 默认结果缺少字段: {field}")
                return False
        
        logger.info("✓ DeepSeek分析器默认结果格式正确")
        return True
        
    except Exception as e:
        logger.error(f"✗ DeepSeek分析器测试失败: {e}")
        return False

def main():
    """主测试函数"""
    logger.info("开始简单API集成测试")
    
    tests = [
        ("模块导入", test_imports),
        ("配置检查", test_config),
        ("DeepSeek默认结果", test_deepseek_fallback)
    ]
    
    results = {}
    for test_name, test_func in tests:
        logger.info(f"\n测试: {test_name}")
        results[test_name] = test_func()
    
    # 总结
    logger.info("\n=== 测试总结 ===")
    for test_name, result in results.items():
        status = "✓ 通过" if result else "✗ 失败"
        logger.info(f"{test_name}: {status}")
    
    if all(results.values()):
        logger.info("\n✓ 基础集成测试通过")
    else:
        logger.info("\n✗ 存在问题，请检查配置和依赖")

if __name__ == "__main__":
    main()
