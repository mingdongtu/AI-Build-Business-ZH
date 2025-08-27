import json
import os
import re
from typing import Dict, Any, List
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)

class DeepSeekAnalyzer:
    """DeepSeek-V3.1 API食品分析服务类"""
    
    def __init__(self):
        self.api_key = os.getenv('DEEPSEEK_API_KEY')
        self.api_base = os.getenv('DEEPSEEK_API_BASE', 'https://api.deepseek.com')
        
        if not self.api_key:
            raise ValueError("DeepSeek API密钥未配置，请检查环境变量 DEEPSEEK_API_KEY")
    
    def analyze_food_ingredients(self, extracted_text: str) -> Dict[str, Any]:
        """使用DeepSeek-V3.1分析食品配料表并给出健康评分和建议"""
        
        # 构建分析提示词
        prompt = self._build_analysis_prompt(extracted_text)
        
        try:
            response = self._call_deepseek_api(prompt)
            result = self._parse_analysis_result(response)
            
            logger.info(f"DeepSeek分析完成，健康评分: {result.get('score', 'N/A')}")
            return result
            
        except Exception as e:
            logger.error(f"DeepSeek分析失败: {e}")
            # 返回默认结果而不是抛出异常
            return self._get_default_result()
    
    def _build_analysis_prompt(self, extracted_text: str) -> str:
        """构建分析提示词"""
        prompt = f"""你是一个专业的食品营养分析师。请分析以下食品包装上的文字信息，重点关注配料表，并给出详细的健康评估。

提取的文字内容：
{extracted_text}

请按照以下JSON格式返回分析结果：
{{
    "food_name": "识别的食品名称",
    "ingredients": ["配料1", "配料2", "配料3"],
    "score": 75,
    "health_points": [
        "含有优质蛋白质 (+10分)",
        "添加糖含量较高 (-15分)",
        "含有防腐剂 (-5分)"
    ],
    "recommendations": [
        "建议适量食用，注意控制摄入量",
        "可以搭配新鲜蔬菜一起食用",
        "运动后食用效果更佳"
    ],
    "detailed_analysis": {{
        "positive_aspects": ["正面因素1", "正面因素2"],
        "negative_aspects": ["负面因素1", "负面因素2"],
        "nutritional_highlights": ["营养亮点1", "营养亮点2"]
    }}
}}

分析要求：
1. 从文字中识别食品名称
2. 提取完整的配料表，按重要性排序
3. 给出0-100分的健康评分，考虑以下因素：
   - 天然成分vs人工添加剂
   - 营养价值
   - 加工程度
   - 添加糖、盐、脂肪含量
   - 防腐剂和色素等添加剂
4. 列出具体的健康要点，说明加分或扣分原因
5. 提供实用的食用建议
6. 进行详细的营养分析

请确保返回的是有效的JSON格式。"""

        return prompt
    
    def _call_deepseek_api(self, prompt: str) -> str:
        """调用DeepSeek API，使用OpenAI客户端库"""
        try:
            # 创建OpenAI客户端，配置为使用DeepSeek API
            client = OpenAI(
                api_key=self.api_key,
                base_url=self.api_base
            )
            
            # 发送请求
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            # 提取内容
            if response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content
                logger.info("DeepSeek API调用成功")
                return content
            else:
                raise Exception("DeepSeek API返回格式异常")
                
        except Exception as e:
            logger.error(f"DeepSeek API调用失败: {e}")
            raise
    
    def _parse_analysis_result(self, response_content: str) -> Dict[str, Any]:
        """解析DeepSeek返回的分析结果"""
        try:
            # 尝试提取JSON部分
            content = response_content.strip()
            
            # 查找JSON开始和结束位置
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = content[start_idx:end_idx]
                result = json.loads(json_str)
                
                # 验证必要字段
                if not isinstance(result.get('score'), (int, float)):
                    result['score'] = 50
                
                if not isinstance(result.get('ingredients'), list):
                    result['ingredients'] = []
                
                if not isinstance(result.get('health_points'), list):
                    result['health_points'] = []
                
                if not isinstance(result.get('recommendations'), list):
                    result['recommendations'] = []
                
                if not result.get('food_name'):
                    result['food_name'] = '未识别食品'
                
                return result
            else:
                raise ValueError("未找到有效的JSON格式")
                
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"解析DeepSeek返回结果失败: {e}")
            logger.error(f"原始返回内容: {response_content}")
            
            # 尝试从文本中提取基本信息
            return self._extract_basic_info_from_text(response_content)
    
    def _extract_basic_info_from_text(self, text: str) -> Dict[str, Any]:
        """从文本中提取基本信息（备用方案）"""
        result = self._get_default_result()
        
        # 简单的文本解析逻辑
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if '评分' in line or '分数' in line:
                # 尝试提取分数
                import re
                score_match = re.search(r'(\d+)', line)
                if score_match:
                    result['score'] = int(score_match.group(1))
        
        return result
    
    def _get_default_result(self) -> Dict[str, Any]:
        """获取默认分析结果"""
        return {
            "food_name": "未识别食品",
            "ingredients": [],
            "score": 50,
            "health_points": ["无法获取详细分析"],
            "recommendations": ["建议查看食品标签，选择天然成分较多的产品"],
            "detailed_analysis": {
                "positive_aspects": [],
                "negative_aspects": [],
                "nutritional_highlights": []
            }
        }
