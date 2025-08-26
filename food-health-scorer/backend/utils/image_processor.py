import cv2
import numpy as np
import re
import logging
import os
import io
import math
import time
from PIL import Image
from typing import List, Dict, Tuple, Optional, Union, BinaryIO

# 导入EasyOCR替代PaddleOCR
import easyocr

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

class ImageProcessor:
    """
    Class for processing food packaging images and extracting ingredients
    with enhanced OCR capabilities and error handling
    """
    
    def __init__(self):
        # Set up logger
        self.logger = logging.getLogger('ImageProcessor')
        
        # Common ingredient list markers in Chinese
        self.ingredient_markers = [
            "配料表", "配料", "成分", "原料", "原材料", "ingredients", "配料组成",
            "配 料", "配  料", "配   料", "成 分", "ingredient list"
        ]
        
        # Common ingredient separators
        self.separators = [
            "，", ",", "、", ";", "；", "/", "：", ":"
        ]
        
        # Minimum confidence threshold for OCR
        self.min_confidence = 0.4  # EasyOCR uses 0-1 range for confidence
        
        # Maximum image size for processing (1MB in bytes)
        self.max_image_size = 1 * 1024 * 1024
        
        # Initialize EasyOCR with Chinese and English support
        try:
            # 使用EasyOCR，设置使用中英文识别
            self.logger.info("Initializing EasyOCR, this may take a moment...")
            
            # 创建EasyOCR实例 - 支持中文和英文
            self.ocr = easyocr.Reader(['ch_sim', 'en'], gpu=False)
            
            # 预热模型，确保它在服务启动时就加载
            test_img_path = os.path.join(os.path.dirname(__file__), "../static/test_img.jpg")
            if not os.path.exists(test_img_path):
                # 如果测试图片不存在，创建一个简单的图片
                from PIL import Image, ImageDraw, ImageFont
                img = Image.new('RGB', (100, 40), color = (255, 255, 255))
                d = ImageDraw.Draw(img)
                d.text((10,10), "测试文字", fill=(0,0,0))
                os.makedirs(os.path.dirname(test_img_path), exist_ok=True)
                img.save(test_img_path)
            
            # 运行一次OCR来预热模型
            self.logger.info(f"Warming up EasyOCR with test image: {test_img_path}")
            _ = self.ocr.readtext(test_img_path)
            self.logger.info("EasyOCR initialized and warmed up successfully")
        except Exception as e:
            self.logger.error(f"EasyOCR initialization failed: {str(e)}")
            self.logger.error("Please check EasyOCR installation")
            self.ocr = None
    
    def extract_text(self, image_path: str) -> Tuple[str, bool, Optional[str]]:
        """
        Extract text from an image using EasyOCR with enhanced error handling
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            Tuple[str, bool, Optional[str]]: 
                - Extracted text
                - Success flag
                - Error message if any
        """
        self.logger.info(f"Starting OCR text extraction on image: {os.path.basename(image_path)}")
        
        try:
            # Check if EasyOCR was initialized successfully
            if self.ocr is None:
                self.logger.error("EasyOCR not initialized properly")
                return "", False, "OCR引擎未正确初始化"
            
            # Check if file exists
            if not os.path.exists(image_path):
                self.logger.error(f"Image file not found: {image_path}")
                return "", False, "图片文件不存在"
            
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                self.logger.error(f"Could not read image file: {image_path}")
                return "", False, "无法读取图片文件，格式可能不支持"
            
            # Check image dimensions
            height, width = image.shape[:2]
            if width < 100 or height < 100:
                self.logger.warning(f"Image is too small: {width}x{height}")
                return "", False, "图片尺寸太小，无法识别"
            
            # Check if image is too blurry
            laplacian_var = cv2.Laplacian(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY), cv2.CV_64F).var()
            if laplacian_var < 100:  # Threshold for blurriness
                self.logger.warning(f"Image is too blurry: {laplacian_var}")
                return "", False, "图片不清晰，请重拍"
            
            self.logger.info("Processing image with EasyOCR")
            
            # Try multiple preprocessing methods for better results
            results = []
            confidence_scores = []
            
            # Method 1: Original image
            start_time = time.time()
            result = self.ocr.readtext(image_path)
            self.logger.info(f"EasyOCR processing time: {time.time() - start_time:.2f}s")
            
            # Method 2: Preprocessed image with better contrast
            preprocessed_path = image_path + "_preprocessed.jpg"
            preprocessed = self._alternative_preprocess(image)
            cv2.imwrite(preprocessed_path, np.array(preprocessed))
            result_preprocessed = self.ocr.readtext(preprocessed_path)
            
            # Clean up temporary file
            if os.path.exists(preprocessed_path):
                os.unlink(preprocessed_path)
            
            # Extract text and confidence from results - EasyOCR结果解析
            for res in [result, result_preprocessed]:
                try:
                    # 调试输出，了解EasyOCR返回的结果结构
                    self.logger.info(f"EasyOCR result type: {type(res)}, length: {len(res) if res else 0}")
                    
                    text_lines = []
                    conf_scores = []
                    
                    # EasyOCR格式: [[bbox, text, confidence], ...]
                    if isinstance(res, list) and len(res) > 0:
                        for detection in res:
                            if len(detection) >= 3:
                                # 格式: [bbox, text, confidence]
                                bbox = detection[0]  # 边界框坐标
                                text = detection[1]  # 文本
                                confidence = detection[2]  # 置信度
                                
                                # 过滤掉置信度太低或无意义的文本
                                if confidence > 0.3 and text.strip() and text.strip() != '口口口':
                                    text_lines.append(text.strip())
                                    conf_scores.append(confidence)
                                    self.logger.info(f"Extracted text: '{text}' with confidence: {confidence:.3f}")
                    
                    if text_lines:
                        self.logger.info(f"Successfully extracted {len(text_lines)} text lines")
                        results.append("\n".join(text_lines))
                        avg_confidence = sum(conf_scores) / len(conf_scores) if conf_scores else 0
                        confidence_scores.append(avg_confidence)
                    else:
                        self.logger.warning("No valid text extracted from OCR result")
                        
                except Exception as e:
                    self.logger.error(f"Error parsing OCR result: {str(e)}")
                    # 继续处理下一个结果
            
            # If no results were found
            if not results:
                self.logger.warning("No text detected in the image")
                return "", False, "未能在图片中检测到文字"
            
            # Choose the result with highest confidence
            best_index = confidence_scores.index(max(confidence_scores)) if confidence_scores else 0
            text = results[best_index]
            confidence = confidence_scores[best_index] if confidence_scores else 0
            
            self.logger.info(f"OCR completed with confidence: {confidence:.4f}")
            
            # Check if OCR confidence is too low
            if confidence < self.min_confidence:
                self.logger.warning(f"OCR confidence too low: {confidence:.4f}")
                return text, False, "图片文字识别度低，请提供更清晰的图片"
            
            # Check if extracted text is too short
            if len(text.strip()) < 10:
                self.logger.warning(f"Extracted text too short: {len(text.strip())} chars")
                return text, False, "识别的文字内容太少，请确保图片包含配料表"
            
            return text, True, None
            
        except Exception as e:
            self.logger.error(f"Error extracting text: {str(e)}")
            return "", False, f"图片处理错误: {str(e)}"
    
    def _preprocess_image(self, image: np.ndarray) -> Image.Image:
        """
        Preprocess image to improve OCR accuracy
        
        Args:
            image (numpy.ndarray): Input image
            
        Returns:
            PIL.Image: Preprocessed image
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        equalized = clahe.apply(gray)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            equalized, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(thresh, None, 10, 7, 21)
        
        # Dilate to connect nearby text
        kernel = np.ones((1, 1), np.uint8)
        dilated = cv2.dilate(denoised, kernel, iterations=1)
        
        # Convert to PIL Image for EasyOCR
        pil_image = Image.fromarray(dilated)
        
        return pil_image
        
    def _alternative_preprocess(self, image: np.ndarray) -> Image.Image:
        """
        Alternative preprocessing method with higher contrast
        
        Args:
            image (numpy.ndarray): Input image
            
        Returns:
            PIL.Image: Preprocessed image
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Increase contrast
        alpha = 1.8  # Contrast control (increased from 1.5)
        beta = 15    # Brightness control (increased from 10)
        adjusted = cv2.convertScaleAbs(gray, alpha=alpha, beta=beta)
        
        # Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(adjusted, (3, 3), 0)  # Reduced kernel size for sharper text
        
        # Otsu's thresholding
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Convert to PIL Image for EasyOCR
        pil_image = Image.fromarray(thresh)
        
        return pil_image
    
    def extract_ingredients(self, text: str) -> List[str]:
        """
        Extract ingredients list from OCR text
        
        Args:
            text (str): OCR extracted text
            
        Returns:
            list: List of ingredients
        """
        self.logger.info("Starting ingredient extraction from OCR text")
        
        if not text:
            self.logger.warning("Empty text provided for ingredient extraction")
            return []
        
        # Convert text to lowercase for case-insensitive matching
        text_lower = text.lower()
        
        # Find the ingredients section
        ingredients_section = ""
        lines = text.split('\n')
        
        # Try to find the ingredients section
        found_ingredients = False
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # Check if this line contains an ingredient marker
            if any(marker.lower() in line_lower for marker in self.ingredient_markers):
                found_ingredients = True
                # Start with this line and include several following lines
                ingredients_section = line
                
                # Include up to 5 more lines or until a new section starts
                for j in range(1, 6):
                    if i + j < len(lines) and not any(marker.lower() in lines[i + j].lower() for marker in ["营养成分", "保质期", "储存条件", "生产日期", "保存方法"]):
                        ingredients_section += " " + lines[i + j]
                    else:
                        break
                
                break
        
        # If no specific ingredients section found, use the entire text
        if not found_ingredients:
            ingredients_section = text
        
        # Extract ingredients from the section
        ingredients = []
        
        # Try to find ingredients after a marker
        for marker in self.ingredient_markers:
            if marker.lower() in ingredients_section.lower():
                # Get text after the marker
                marker_index = ingredients_section.lower().find(marker.lower())
                ingredients_text = ingredients_section[marker_index + len(marker):]
                
                # Split by common separators
                for separator in self.separators:
                    if separator in ingredients_text:
                        ingredients = [item.strip() for item in ingredients_text.split(separator) if item.strip()]
                        break
                
                if ingredients:
                    break
        
        # If no ingredients found using markers and separators, try to extract using regex patterns
        if not ingredients:
            # Look for patterns like Chinese characters followed by percentages
            percentage_pattern = r'([^\d%]+)(\d+(?:\.\d+)?%)'
            matches = re.findall(percentage_pattern, ingredients_section)
            if matches:
                ingredients = [match[0].strip() for match in matches]
        
        # If still no ingredients found, split by common separators
        if not ingredients:
            for separator in self.separators:
                if separator in ingredients_section:
                    ingredients = [item.strip() for item in ingredients_section.split(separator) if item.strip()]
                    break
        
        # Clean up ingredients
        cleaned_ingredients = []
        for item in ingredients:
            # Remove percentages and other non-ingredient text
            cleaned = re.sub(r'\d+(?:\.\d+)?%', '', item).strip()
            cleaned = re.sub(r'^\W+|\W+$', '', cleaned).strip()  # Remove leading/trailing non-word chars
            
            # Remove common non-ingredient text patterns
            cleaned = re.sub(r'保质期.*', '', cleaned)
            cleaned = re.sub(r'生产日期.*', '', cleaned)
            cleaned = re.sub(r'储存条件.*', '', cleaned)
            cleaned = re.sub(r'营养成分.*', '', cleaned)
            cleaned = re.sub(r'[\(\)（）\[\]【】]', '', cleaned)  # Remove brackets
            
            if cleaned and len(cleaned) < 30:  # Avoid very long strings that are likely not ingredients
                cleaned_ingredients.append(cleaned)
        
        self.logger.info(f"Extracted {len(cleaned_ingredients)} ingredients")
        if cleaned_ingredients:
            self.logger.debug(f"First few ingredients: {', '.join(cleaned_ingredients[:3])}")
        else:
            self.logger.warning("No ingredients were extracted")
            
        return cleaned_ingredients
        
    def assess_image_quality(self, image_path: str) -> Dict[str, Union[bool, str, float]]:
        """
        Assess the quality of an image for OCR processing
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            Dict: Assessment results including quality metrics
        """
        self.logger.info(f"Assessing image quality: {os.path.basename(image_path)}")
        
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                return {
                    "is_suitable": False,
                    "reason": "无法读取图片文件",
                    "metrics": {}
                }
                
            # Get dimensions
            height, width = image.shape[:2]
            
            # Calculate blurriness (Laplacian variance)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Calculate brightness
            brightness = np.mean(gray)
            
            # Calculate contrast
            contrast = np.std(gray)
            
            metrics = {
                "width": width,
                "height": height,
                "aspect_ratio": width / height if height > 0 else 0,
                "resolution": width * height,
                "blurriness": laplacian_var,
                "brightness": brightness,
                "contrast": contrast
            }
            
            # Determine if image is suitable for OCR
            is_suitable = True
            reason = "图片质量良好"
            
            if width < 300 or height < 300:
                is_suitable = False
                reason = "图片分辨率太低"
            elif laplacian_var < 100:
                is_suitable = False
                reason = "图片不清晰，请重拍"
            elif brightness < 30:
                is_suitable = False
                reason = "图片太暗，请在光线充足的环境下重拍"
            elif brightness > 220:
                is_suitable = False
                reason = "图片太亮，请避免强光反射"
            elif contrast < 20:
                is_suitable = False
                reason = "图片对比度太低，文字难以识别"
                
            self.logger.info(f"Image quality assessment: suitable={is_suitable}, reason={reason}")
            
            return {
                "is_suitable": is_suitable,
                "reason": reason,
                "metrics": metrics
            }
        except Exception as e:
            self.logger.error(f"Error assessing image quality: {str(e)}")
            return {
                "is_suitable": False,
                "reason": f"图片评估错误: {str(e)}",
                "metrics": {}
            }
            
    def compress_image(self, image_data: Union[bytes, BinaryIO, str], max_size: int = None) -> Tuple[bytes, bool, str]:
        """
        Compress an image to reduce its file size while maintaining readability for OCR
        
        Args:
            image_data: Image data as bytes, file-like object, or file path
            max_size: Maximum size in bytes (defaults to self.max_image_size if None)
            
        Returns:
            Tuple[bytes, bool, str]: Compressed image data, success flag, and error message if any
        """
        if max_size is None:
            max_size = self.max_image_size
            
        self.logger.info(f"Compressing image to target size: {max_size/1024:.1f}KB")
        
        try:
            # Handle different input types
            if isinstance(image_data, str):
                # It's a file path
                img = Image.open(image_data)
            elif isinstance(image_data, bytes):
                # It's bytes data
                img = Image.open(io.BytesIO(image_data))
            else:
                # It's a file-like object
                img = Image.open(image_data)
                
            # Convert to RGB if needed (removes alpha channel)
            if img.mode == 'RGBA':
                img = img.convert('RGB')
                
            # Get original format or default to JPEG
            img_format = img.format if img.format else 'JPEG'
            
            # Initial quality
            quality = 95
            output = io.BytesIO()
            
            # Save with initial quality
            img.save(output, format=img_format, quality=quality, optimize=True)
            img_size = output.tell()
            
            # Compress iteratively if needed
            while img_size > max_size and quality > 30:
                output = io.BytesIO()
                quality -= 10
                img.save(output, format=img_format, quality=quality, optimize=True)
                img_size = output.tell()
                self.logger.debug(f"Compressed to quality={quality}, size={img_size/1024:.1f}KB")
                
            # If still too large, resize the image
            if img_size > max_size:
                # Calculate new dimensions to maintain aspect ratio
                ratio = math.sqrt(max_size / img_size) * 0.9  # 0.9 as safety factor
                new_width = int(img.width * ratio)
                new_height = int(img.height * ratio)
                
                # Resize and compress again
                img = img.resize((new_width, new_height), Image.LANCZOS)
                output = io.BytesIO()
                img.save(output, format=img_format, quality=quality, optimize=True)
                img_size = output.tell()
                
                self.logger.info(f"Resized image to {new_width}x{new_height}, final size={img_size/1024:.1f}KB")
            else:
                self.logger.info(f"Compressed image with quality={quality}, final size={img_size/1024:.1f}KB")
                
            # Get the compressed image data
            compressed_data = output.getvalue()
            
            return compressed_data, True, ""
            
        except Exception as e:
            self.logger.error(f"Error compressing image: {str(e)}")
            return b"", False, f"图片压缩错误: {str(e)}"
