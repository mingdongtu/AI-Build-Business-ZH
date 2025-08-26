import requests
import base64
import json
import os
import sys
from typing import Optional, Dict, Any
import logging

# 尝试导入配置文件
try:
    # 添加项目根目录到路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    if parent_dir not in sys.path:
        sys.path.append(parent_dir)
    
    import config_local  # 导入配置文件，设置环境变量
except ImportError:
    pass  # 如果没有配置文件，继续使用环境变量

logger = logging.getLogger(__name__)

class BaiduOCR:
    """百度OCR服务类"""
    
    def __init__(self):
        self.api_key = os.getenv('BAIDU_OCR_API_KEY')
        self.secret_key = os.getenv('BAIDU_OCR_SECRET_KEY')
        self.access_token = None
        
        # 调试信息：显示获取到的密钥状态
        logger.info(f"百度OCR初始化 - API Key: {'已获取' if self.api_key else '未获取'}")
        logger.info(f"百度OCR初始化 - Secret Key: {'已获取' if self.secret_key else '未获取'}")
        
        if not self.api_key or not self.secret_key:
            raise ValueError("百度OCR API密钥未配置，请检查环境变量 BAIDU_OCR_API_KEY 和 BAIDU_OCR_SECRET_KEY")
    
    def get_access_token(self) -> str:
        """获取百度API访问令牌"""
        if self.access_token:
            return self.access_token
            
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.secret_key
        }
        
        try:
            response = requests.post(url, params=params)
            response.raise_for_status()
            result = response.json()
            
            if "access_token" in result:
                self.access_token = result["access_token"]
                logger.info("百度OCR访问令牌获取成功")
                return self.access_token
            else:
                raise Exception(f"获取访问令牌失败: {result}")
                
        except Exception as e:
            logger.error(f"获取百度OCR访问令牌失败: {e}")
            raise
    
    def image_to_base64(self, image_path: str) -> str:
        """将图片转换为base64编码"""
        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()
                base64_data = base64.b64encode(image_data).decode('utf-8')
                return base64_data
        except Exception as e:
            logger.error(f"图片转base64失败: {e}")
            raise
    
    def extract_text_general(self, image_path: str) -> Dict[str, Any]:
        """使用百度通用文字识别API提取文本"""
        try:
            logger.info(f"开始调用百度通用OCR接口，图片路径: {image_path}")
            access_token = self.get_access_token()
            url = f"https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic?access_token={access_token}"
            
            # 将图片转换为base64
            image_base64 = self.image_to_base64(image_path)
            logger.info(f"图片转换为base64成功，长度: {len(image_base64)}字符")
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'
            }
            
            data = {
                'image': image_base64
            }
            
            logger.info(f"发送请求到百度通用OCR接口: {url}")
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()
            result = response.json()
            logger.info(f"百度通用OCR接口响应状态码: {response.status_code}")
            
            if "error_code" in result:
                error_msg = result.get('error_msg', '未知错误')
                error_code = result.get('error_code', 'unknown')
                logger.error(f"百度通用OCR API错误: 代码={error_code}, 消息={error_msg}")
                raise Exception(f"百度OCR API错误: {error_msg} (代码: {error_code})")
            
            # 提取所有文字
            extracted_text = ""
            words_count = 0
            if "words_result" in result:
                words_count = len(result["words_result"])
                for item in result["words_result"]:
                    extracted_text += item["words"] + "\n"
                logger.info(f"百度通用OCR成功识别 {words_count} 个文本块")
            else:
                logger.warning("百度通用OCR响应中未找到words_result字段")
            
            logger.info(f"百度通用OCR文字识别成功，提取文本长度: {len(extracted_text)}字符")
            if extracted_text:
                # 只记录前100个字符，避免日志过长
                preview = extracted_text[:100] + "..." if len(extracted_text) > 100 else extracted_text
                logger.info(f"识别文本预览: {preview}")
            
            return {
                "text": extracted_text.strip(),
                "raw_result": result,
                "words_count": words_count
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"百度通用OCR网络请求失败: {e}")
            raise
        except Exception as e:
            logger.error(f"百度通用OCR文字识别失败: {e}")
            raise
    
    def extract_text_accurate(self, image_path: str) -> Dict[str, Any]:
        """使用百度高精度文字识别API提取文本"""
        try:
            logger.info(f"开始调用百度高精度OCR接口，图片路径: {image_path}")
            access_token = self.get_access_token()
            url = f"https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic?access_token={access_token}"
            
            # 将图片转换为base64
            image_base64 = self.image_to_base64(image_path)
            logger.info(f"图片转换为base64成功，长度: {len(image_base64)}字符")
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'
            }
            
            data = {
                'image': image_base64
            }
            
            logger.info(f"发送请求到百度高精度OCR接口: {url}")
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()
            result = response.json()
            logger.info(f"百度高精度OCR接口响应状态码: {response.status_code}")
            
            if "error_code" in result:
                error_msg = result.get('error_msg', '未知错误')
                error_code = result.get('error_code', 'unknown')
                logger.error(f"百度高精度OCR API错误: 代码={error_code}, 消息={error_msg}")
                raise Exception(f"百度OCR API错误: {error_msg} (代码: {error_code})")
            
            # 提取所有文字
            extracted_text = ""
            words_count = 0
            if "words_result" in result:
                words_count = len(result["words_result"])
                for item in result["words_result"]:
                    extracted_text += item["words"] + "\n"
                logger.info(f"百度高精度OCR成功识别 {words_count} 个文本块")
            else:
                logger.warning("百度高精度OCR响应中未找到words_result字段")
            
            logger.info(f"百度高精度OCR文字识别成功，提取文本长度: {len(extracted_text)}字符")
            if extracted_text:
                # 只记录前100个字符，避免日志过长
                preview = extracted_text[:100] + "..." if len(extracted_text) > 100 else extracted_text
                logger.info(f"识别文本预览: {preview}")
            
            return {
                "text": extracted_text.strip(),
                "raw_result": result,
                "words_count": words_count
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"百度高精度OCR网络请求失败: {e}")
            raise
        except Exception as e:
            logger.error(f"百度高精度OCR文字识别失败: {e}")
            raise
    
    def extract_ingredients_text(self, image_path: str, use_accurate: bool = True) -> str:
        """提取食品配料表文字（主要接口）
        
        Args:
            image_path: 图片文件路径
            use_accurate: 是否使用高精度OCR接口，默认为True
            
        Returns:
            str: 提取的文字内容
        """
        try:
            logger.info(f"OCR识别模式: {'高精度' if use_accurate else '通用'}")
            if use_accurate:
                result = self.extract_text_accurate(image_path)
                logger.info("使用百度高精度OCR接口提取文字")
            else:
                result = self.extract_text_general(image_path)
                logger.info("使用百度通用OCR接口提取文字")
            
            return result["text"]
            
        except Exception as e:
            logger.error(f"提取配料表文字失败: {e}")
            # 返回空字符串而不是抛出异常，让后续处理可以继续
            return ""
