#!/usr/bin/env python3
"""
测试百度OCR和DeepSeek API集成的脚本
"""

import os
import sys
import tempfile
from PIL import Image, ImageDraw, ImageFont
import logging

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.baidu_ocr import BaiduOCR
from models.deepseek_analyzer import DeepSeekAnalyzer

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_image():
    """创建一个包含食品配料表的测试图片"""
    # 创建一个白色背景的图片
    width, height = 800, 600
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # 尝试使用系统字体
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
        small_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 18)
    except:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # 绘制食品标签内容
    y_pos = 50
    
    # 标题
    draw.text((50, y_pos), "营养成分表", fill='black', font=font)
    y_pos += 60
    
    # 配料表
    draw.text((50, y_pos), "配料表：", fill='black', font=font)
    y_pos += 40
    
    ingredients = [
        "小麦粉、白砂糖、植物油、鸡蛋、",
        "食用盐、酵母、食品添加剂",
        "（碳酸氢钠、柠檬酸、香精）"
    ]
    
    for ingredient in ingredients:
        draw.text((70, y_pos), ingredient, fill='black', font=small_font)
        y_pos += 30
    
    # 保存到临时文件
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    image.save(temp_file.name)
    temp_file.close()
    
    logger.info(f"测试图片已创建: {temp_file.name}")
    return temp_file.name

def test_baidu_ocr():
    """测试百度OCR功能"""
    logger.info("=== 测试百度OCR ===")
    
    # 检查环境变量
    api_key = os.getenv('BAIDU_OCR_API_KEY')
    secret_key = os.getenv('BAIDU_OCR_SECRET_KEY')
    
    if not api_key or not secret_key:
        logger.warning("百度OCR API密钥未配置，跳过测试")
        logger.info("请设置环境变量: BAIDU_OCR_API_KEY 和 BAIDU_OCR_SECRET_KEY")
        return False
    
    try:
        # 创建测试图片
        test_image_path = create_test_image()
        
        # 初始化OCR
        ocr = BaiduOCR()
        
        # 测试文字提取
        extracted_text = ocr.extract_ingredients_text(test_image_path)
        
        logger.info(f"OCR提取结果: {extracted_text}")
        
        # 清理测试文件
        os.unlink(test_image_path)
        
        return True
        
    except Exception as e:
        logger.error(f"百度OCR测试失败: {e}")
        return False

def test_deepseek_analyzer():
    """测试DeepSeek分析功能"""
    logger.info("=== 测试DeepSeek分析 ===")
    
    # 检查环境变量
    api_key = os.getenv('DEEPSEEK_API_KEY')
    
    if not api_key:
        logger.warning("DeepSeek API密钥未配置，跳过测试")
        logger.info("请设置环境变量: DEEPSEEK_API_KEY")
        return False
    
    try:
        # 初始化分析器
        analyzer = DeepSeekAnalyzer()
        
        # 测试文本
        test_text = """
        营养成分表
        配料表：小麦粉、白砂糖、植物油、鸡蛋、食用盐、酵母、食品添加剂（碳酸氢钠、柠檬酸、香精）
        """
        
        # 进行分析
        result = analyzer.analyze_food_ingredients(test_text)
        
        logger.info("DeepSeek分析结果:")
        logger.info(f"食品名称: {result.get('food_name', 'N/A')}")
        logger.info(f"健康评分: {result.get('score', 'N/A')}")
        logger.info(f"配料数量: {len(result.get('ingredients', []))}")
        logger.info(f"健康要点数量: {len(result.get('health_points', []))}")
        logger.info(f"建议数量: {len(result.get('recommendations', []))}")
        
        return True
        
    except Exception as e:
        logger.error(f"DeepSeek分析测试失败: {e}")
        return False

def test_full_pipeline():
    """测试完整的分析流程"""
    logger.info("=== 测试完整分析流程 ===")
    
    # 检查所有API密钥
    baidu_configured = bool(os.getenv('BAIDU_OCR_API_KEY') and os.getenv('BAIDU_OCR_SECRET_KEY'))
    deepseek_configured = bool(os.getenv('DEEPSEEK_API_KEY'))
    
    if not (baidu_configured and deepseek_configured):
        logger.warning("API密钥配置不完整，无法进行完整流程测试")
        return False
    
    try:
        # 创建测试图片
        test_image_path = create_test_image()
        
        # OCR提取
        ocr = BaiduOCR()
        extracted_text = ocr.extract_ingredients_text(test_image_path)
        logger.info(f"OCR提取文本: {extracted_text}")
        
        # AI分析
        analyzer = DeepSeekAnalyzer()
        result = analyzer.analyze_food_ingredients(extracted_text)
        
        logger.info("完整分析结果:")
        logger.info(f"- 食品名称: {result.get('food_name', 'N/A')}")
        logger.info(f"- 健康评分: {result.get('score', 'N/A')}")
        logger.info(f"- 配料: {result.get('ingredients', [])}")
        logger.info(f"- 建议: {result.get('recommendations', [])}")
        
        # 清理测试文件
        os.unlink(test_image_path)
        
        return True
        
    except Exception as e:
        logger.error(f"完整流程测试失败: {e}")
        return False

def main():
    """主测试函数"""
    logger.info("开始API集成测试")
    
    # 显示配置状态
    logger.info("配置状态:")
    logger.info(f"- 百度OCR: {'✓' if os.getenv('BAIDU_OCR_API_KEY') else '✗'}")
    logger.info(f"- DeepSeek: {'✓' if os.getenv('DEEPSEEK_API_KEY') else '✗'}")
    
    # 运行测试
    tests = [
        ("百度OCR", test_baidu_ocr),
        ("DeepSeek分析", test_deepseek_analyzer),
        ("完整流程", test_full_pipeline)
    ]
    
    results = {}
    for test_name, test_func in tests:
        logger.info(f"\n开始测试: {test_name}")
        results[test_name] = test_func()
        logger.info(f"测试结果: {'通过' if results[test_name] else '失败'}")
    
    # 总结
    logger.info("\n=== 测试总结 ===")
    for test_name, result in results.items():
        status = "✓ 通过" if result else "✗ 失败"
        logger.info(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    logger.info(f"\n整体测试结果: {'全部通过' if all_passed else '存在失败'}")
    
    if not all_passed:
        logger.info("\n请检查:")
        logger.info("1. API密钥是否正确配置")
        logger.info("2. 网络连接是否正常")
        logger.info("3. API服务是否可用")

if __name__ == "__main__":
    main()
