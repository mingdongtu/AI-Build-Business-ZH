from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from fastapi.responses import JSONResponse
import os
import time
import tempfile
import logging
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

# Allowed image types
ALLOWED_IMAGE_TYPES = {
    "image/jpeg", "image/jpg", "image/png", "image/gif", 
    "image/bmp", "image/webp", "image/tiff"
}

@router.post("/analyze")
async def analyze_food_image(request: Request, image: UploadFile = File(...)):
    """
    使用百度OCR和DeepSeek-V3.1分析食品包装图片
    
    Args:
        image: 包含食品包装配料表的上传图片文件
        
    Returns:
        dict: 包含健康评分、配料分析和建议的分析结果
    """
    start_time = time.time()
    temp_file_path = None
    
    try:
        # 验证文件类型
        if image.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=400, 
                detail=f"不支持的文件类型: {image.content_type}。支持的类型: {', '.join(ALLOWED_IMAGE_TYPES)}"
            )
        
        # 检查文件大小
        file_size = 0
        content = await image.read()
        file_size = len(content)
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"文件过大。最大允许大小: {MAX_FILE_SIZE / (1024*1024):.1f}MB"
            )
        
        if file_size == 0:
            raise HTTPException(status_code=400, detail="上传的文件为空")
        
        logger.info(f"收到图片文件: {image.filename}, 大小: {file_size} bytes, 类型: {image.content_type}")
        
        # 保存临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        logger.info(f"临时文件已保存: {temp_file_path}")
        
        # 使用百度OCR提取文字
        logger.info("开始使用百度OCR提取文字")
        try:
            baidu_ocr = BaiduOCR()
            extracted_text = baidu_ocr.extract_ingredients_text(temp_file_path, use_accurate=True)
            logger.info(f"百度OCR提取完成，文本长度: {len(extracted_text)}")
            logger.info(f"OCR识别的完整文字内容:\n{extracted_text}")
        except Exception as e:
            logger.error(f"百度OCR提取失败: {e}")
            # 如果OCR失败，使用默认文本
            extracted_text = "无法识别文字内容"
        
        # 使用DeepSeek-V3.1分析食品
        logger.info("开始使用DeepSeek-V3.1分析食品")
        try:
            deepseek_analyzer = DeepSeekAnalyzer()
            analysis_result = deepseek_analyzer.analyze_food_ingredients(extracted_text)
            logger.info(f"DeepSeek分析完成，健康评分: {analysis_result.get('score', 'N/A')}")
        except Exception as e:
            logger.error(f"DeepSeek分析失败: {e}")
            # 如果分析失败，返回默认结果
            analysis_result = {
                "food_name": "未识别食品",
                "ingredients": [],
                "score": 50,
                "health_points": ["分析服务暂时不可用"],
                "recommendations": ["建议查看食品标签，选择天然成分较多的产品"],
                "detailed_analysis": {
                    "positive_aspects": [],
                    "negative_aspects": [],
                    "nutritional_highlights": []
                }
            }
        
        # 添加元数据到响应
        analysis_result.update({
            "processing_time": round(time.time() - start_time, 2),
            "extracted_text": extracted_text,  # 添加OCR识别的完整文字
            "extracted_text_length": len(extracted_text),
            "file_size": file_size,
            "file_type": image.content_type,
            "ocr_provider": "百度OCR",
            "analysis_provider": "DeepSeek-V3.1"
        })
        
        # 清理临时文件
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
            temp_file_path = None
        
        logger.info(f"分析完成，总处理时间: {analysis_result['processing_time']}秒")
        
        return analysis_result
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"分析过程中发生未预期错误: {e}")
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")
    
    finally:
        # 确保清理临时文件
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
                logger.info("临时文件已清理")
            except Exception as e:
                logger.error(f"清理临时文件失败: {e}")

@router.get("/health")
async def health_check():
    """健康检查接口"""
    try:
        # 检查环境变量配置
        config_status = {
            "baidu_ocr_configured": bool(os.getenv('BAIDU_OCR_API_KEY') and os.getenv('BAIDU_OCR_SECRET_KEY')),
            "deepseek_configured": bool(os.getenv('DEEPSEEK_API_KEY')),
            "timestamp": time.time()
        }
        
        return {
            "status": "healthy",
            "message": "食品健康评分API运行正常",
            "config": config_status
        }
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        raise HTTPException(status_code=500, detail="服务不可用")

@router.get("/")
async def root():
    """根路径接口"""
    return {
        "message": "食品健康评分API",
        "version": "2.0.0",
        "features": ["百度OCR文字识别", "DeepSeek-V3.1智能分析"],
        "endpoints": ["/analyze", "/health"]
    }
