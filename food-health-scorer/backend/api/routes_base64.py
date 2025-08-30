from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
import os
import time
import tempfile
import logging
import base64
from dotenv import load_dotenv

from models.baidu_ocr import BaiduOCR
from models.deepseek_analyzer import DeepSeekAnalyzer

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

router = APIRouter()

# File size limit (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024

class Base64ImageRequest(BaseModel):
    image: str  # Base64 encoded image data
    use_accurate: bool = True

@router.post("/ocr/base64")
async def ocr_base64_image(request_data: Base64ImageRequest):
    """
    使用百度OCR识别Base64编码的图片中的文字
    
    Args:
        request_data: 包含Base64编码图片的请求数据
        
    Returns:
        dict: 包含识别文字的结果
    """
    start_time = time.time()
    temp_file_path = None
    
    try:
        # 解码Base64图片
        try:
            # 检查是否包含data:image前缀
            image_data = request_data.image
            if ',' in image_data:
                # 移除前缀，如 "data:image/jpeg;base64,"
                image_data = image_data.split(',', 1)[1]
            
            # 解码Base64
            decoded_image = base64.b64decode(image_data)
            
            # 检查文件大小
            file_size = len(decoded_image)
            if file_size > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail=f"文件过大。最大允许大小: {MAX_FILE_SIZE / (1024*1024):.1f}MB"
                )
            
            if file_size == 0:
                raise HTTPException(status_code=400, detail="图片数据为空")
            
            logger.info(f"收到Base64图片，大小: {file_size} bytes")
            
        except Exception as e:
            logger.error(f"Base64解码失败: {e}")
            raise HTTPException(status_code=400, detail="无效的Base64图片数据")
        
        # 保存临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            temp_file.write(decoded_image)
            temp_file_path = temp_file.name
        
        logger.info(f"临时文件已保存: {temp_file_path}")
        
        # 使用百度OCR提取文字
        logger.info("开始使用百度OCR提取文字")
        ocr_success = True
        try:
            baidu_ocr = BaiduOCR()
            extracted_text = baidu_ocr.extract_ingredients_text(
                temp_file_path, 
                use_accurate=request_data.use_accurate
            )
            logger.info(f"百度OCR提取完成，文本长度: {len(extracted_text)}")
            logger.info(f"OCR识别的完整文字内容:\n{extracted_text}")
            
            # 检查OCR结果是否有效
            if not extracted_text or len(extracted_text.strip()) < 10:
                logger.warning("OCR提取的文本内容过少，可能识别失败")
                ocr_success = False
                extracted_text = "OCR识别失败，请使用手动输入"
        except Exception as e:
            logger.error(f"百度OCR提取失败: {e}")
            ocr_success = False
            extracted_text = "OCR识别失败，请使用手动输入"
        
        # 清理临时文件
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
            temp_file_path = None
        
        # 返回OCR结果
        result = {
            "text": extracted_text,
            "words_count": len(extracted_text),
            "success": ocr_success,
            "processing_time": round(time.time() - start_time, 2),
            "ocr_provider": "百度OCR"
        }
        
        logger.info(f"OCR处理完成，总处理时间: {result['processing_time']}秒")
        
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"OCR处理过程中发生未预期错误: {e}")
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")
    
    finally:
        # 确保清理临时文件
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
                logger.info("临时文件已清理")
            except Exception as e:
                logger.error(f"清理临时文件失败: {e}")
