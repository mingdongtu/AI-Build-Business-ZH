#!/usr/bin/env python3
"""
测试DeepSeek API配置和功能
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 手动设置API密钥
os.environ['DEEPSEEK_API_KEY'] = 'sk-a13783fe0c9c477196100416b0107f2c'
os.environ['DEEPSEEK_API_BASE'] = 'https://api.deepseek.com'

# 导入DeepSeek分析器
from models.deepseek_analyzer import DeepSeekAnalyzer

def test_deepseek_api():
    """测试DeepSeek API功能"""
    print("开始测试DeepSeek API...")
    
    # 创建分析器实例
    analyzer = DeepSeekAnalyzer()
    
    # 测试文本
    test_text = """
    配料：小麦粉、白砂糖、植物油、鸡蛋、食用盐、香精、
    防腐剂(山梨酸钾)、膨松剂(碳酸氢钠)、
    食品添加剂(焦糖色素)
    """
    
    # 分析食品配料
    print("正在分析食品配料...")
    result = analyzer.analyze_food_ingredients(test_text)
    
    # 打印结果
    print("\n分析结果:")
    print(f"食品名称: {result.get('food_name', '未知')}")
    print(f"健康评分: {result.get('score', 0)}")
    
    print("\n配料列表:")
    for ingredient in result.get('ingredients', []):
        print(f"- {ingredient}")
    
    print("\n健康要点:")
    for point in result.get('health_points', []):
        print(f"- {point}")
    
    print("\n建议:")
    for rec in result.get('recommendations', []):
        print(f"- {rec}")
    
    print("\n详细分析:")
    detailed = result.get('detailed_analysis', {})
    
    print("正面因素:")
    for pos in detailed.get('positive_aspects', []):
        print(f"- {pos}")
    
    print("负面因素:")
    for neg in detailed.get('negative_aspects', []):
        print(f"- {neg}")
    
    return result

if __name__ == "__main__":
    test_deepseek_api()
