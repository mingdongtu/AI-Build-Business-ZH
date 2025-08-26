import unittest
import tempfile
import os
import cv2
import numpy as np
from PIL import Image
import io
from unittest.mock import patch, MagicMock
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.image_processor import ImageProcessor


class TestImageProcessor(unittest.TestCase):
    """Test cases for ImageProcessor class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.processor = ImageProcessor()
        
    def create_test_image(self, text="配料表: 小麦粉, 糖, 植物油, 盐", width=400, height=200):
        """Create a test image with text for OCR testing"""
        # Create a white background image
        img = np.ones((height, width, 3), dtype=np.uint8) * 255
        
        # Add text to the image (simplified - in real tests you'd use proper text rendering)
        cv2.putText(img, text, (10, height//2), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        
        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        cv2.imwrite(temp_file.name, img)
        return temp_file.name
    
    def test_extract_text_success(self):
        """Test successful text extraction from image"""
        # Create test image
        test_image_path = self.create_test_image()
        
        try:
            # Mock pytesseract to return predictable results
            with patch('pytesseract.image_to_string') as mock_ocr:
                mock_ocr.return_value = "配料表: 小麦粉, 糖, 植物油, 盐"
                
                text, success, error = self.processor.extract_text(test_image_path)
                
                self.assertTrue(success)
                self.assertIsNone(error)
                self.assertIn("配料表", text)
                self.assertIn("小麦粉", text)
        finally:
            os.unlink(test_image_path)
    
    def test_extract_text_file_not_found(self):
        """Test text extraction with non-existent file"""
        text, success, error = self.processor.extract_text("/nonexistent/file.jpg")
        
        self.assertFalse(success)
        self.assertIsNotNone(error)
        self.assertIn("文件不存在", error)
    
    def test_extract_text_low_confidence(self):
        """Test text extraction with low confidence OCR result"""
        test_image_path = self.create_test_image()
        
        try:
            with patch('pytesseract.image_to_string') as mock_ocr, \
                 patch('pytesseract.image_to_data') as mock_data:
                
                # Mock low confidence OCR result
                mock_ocr.return_value = "unclear text"
                mock_data.return_value = {
                    'conf': [10, 15, 20]  # Low confidence scores
                }
                
                text, success, error = self.processor.extract_text(test_image_path)
                
                # Should fail due to low confidence
                self.assertFalse(success)
                self.assertIsNotNone(error)
        finally:
            os.unlink(test_image_path)
    
    def test_extract_ingredients_success(self):
        """Test successful ingredient extraction from text"""
        test_text = """
        产品名称: 某某饼干
        配料表: 小麦粉, 白砂糖, 植物油, 鸡蛋, 食用盐, 泡打粉
        净含量: 100g
        """
        
        ingredients = self.processor.extract_ingredients(test_text)
        
        self.assertGreater(len(ingredients), 0)
        self.assertIn("小麦粉", ingredients)
        self.assertIn("白砂糖", ingredients)
        self.assertIn("植物油", ingredients)
    
    def test_extract_ingredients_multiple_formats(self):
        """Test ingredient extraction with different text formats"""
        test_cases = [
            "配料: 小麦粉、糖、油",
            "原料: 面粉，糖，油",
            "成分表: 小麦粉 糖 植物油",
            "Ingredients: 小麦粉, 糖, 植物油"
        ]
        
        for test_text in test_cases:
            ingredients = self.processor.extract_ingredients(test_text)
            self.assertGreater(len(ingredients), 0, f"Failed for text: {test_text}")
    
    def test_extract_ingredients_empty_text(self):
        """Test ingredient extraction with empty text"""
        ingredients = self.processor.extract_ingredients("")
        self.assertEqual(len(ingredients), 0)
    
    def test_extract_ingredients_no_ingredient_section(self):
        """Test ingredient extraction when no ingredient section is found"""
        test_text = "这是一个没有配料表的文本"
        ingredients = self.processor.extract_ingredients(test_text)
        self.assertEqual(len(ingredients), 0)
    
    def test_preprocess_image(self):
        """Test image preprocessing functionality"""
        test_image_path = self.create_test_image()
        
        try:
            # Load test image
            image = cv2.imread(test_image_path)
            
            # Test preprocessing
            processed_image = self.processor._preprocess_image(image)
            
            # Verify it returns a PIL Image
            self.assertIsInstance(processed_image, Image.Image)
            
            # Verify image dimensions are reasonable
            self.assertGreater(processed_image.width, 0)
            self.assertGreater(processed_image.height, 0)
        finally:
            os.unlink(test_image_path)
    
    def test_alternative_preprocess(self):
        """Test alternative preprocessing method"""
        test_image_path = self.create_test_image()
        
        try:
            image = cv2.imread(test_image_path)
            processed_image = self.processor._alternative_preprocess(image)
            
            self.assertIsInstance(processed_image, Image.Image)
        finally:
            os.unlink(test_image_path)
    
    def test_calculate_confidence_score(self):
        """Test OCR confidence score calculation"""
        # Mock OCR data with various confidence levels
        mock_data = {
            'conf': [85, 90, 78, 92, 88]
        }
        
        with patch('pytesseract.image_to_data', return_value=mock_data):
            confidence = self.processor._calculate_confidence_score(None)
            
            # Should return average of valid confidence scores
            expected_confidence = sum(mock_data['conf']) / len(mock_data['conf'])
            self.assertEqual(confidence, expected_confidence)
    
    def test_assess_image_quality(self):
        """Test image quality assessment"""
        test_image_path = self.create_test_image()
        
        try:
            quality_info = self.processor.assess_image_quality(test_image_path)
            
            # Verify quality assessment returns expected fields
            self.assertIn('file_size', quality_info)
            self.assertIn('dimensions', quality_info)
            self.assertIn('blurriness_score', quality_info)
            self.assertIn('brightness', quality_info)
            self.assertIn('contrast', quality_info)
            self.assertIn('quality_issues', quality_info)
            self.assertIn('recommendations', quality_info)
        finally:
            os.unlink(test_image_path)
            
    def test_compress_image_bytes(self):
        """Test image compression with bytes input"""
        # Create a test image with known size
        test_image_path = self.create_test_image(width=800, height=600)
        
        try:
            # Read the image as bytes
            with open(test_image_path, 'rb') as f:
                image_bytes = f.read()
                
            # Get original size
            original_size = len(image_bytes)
            
            # Compress to half the original size
            target_size = original_size // 2
            compressed_bytes, success, error = self.processor.compress_image(image_bytes, target_size)
            
            # Verify compression was successful
            self.assertTrue(success)
            self.assertIsNone(error)
            self.assertIsInstance(compressed_bytes, bytes)
            
            # Verify the size is reduced
            self.assertLessEqual(len(compressed_bytes), target_size)
            
            # Verify the compressed data is valid image data
            img = Image.open(io.BytesIO(compressed_bytes))
            self.assertIsInstance(img, Image.Image)
        finally:
            os.unlink(test_image_path)
            
    def test_compress_image_file_path(self):
        """Test image compression with file path input"""
        test_image_path = self.create_test_image(width=800, height=600)
        
        try:
            # Get original file size
            original_size = os.path.getsize(test_image_path)
            
            # Compress to a smaller size
            target_size = original_size // 2
            compressed_bytes, success, error = self.processor.compress_image(test_image_path, target_size)
            
            # Verify compression was successful
            self.assertTrue(success)
            self.assertIsNone(error)
            
            # Check compressed size
            self.assertLessEqual(len(compressed_bytes), target_size)
        finally:
            os.unlink(test_image_path)
            
    def test_compress_image_file_object(self):
        """Test image compression with file-like object input"""
        test_image_path = self.create_test_image(width=800, height=600)
        
        try:
            # Open file as file-like object
            with open(test_image_path, 'rb') as f:
                # Get original size
                f.seek(0, os.SEEK_END)
                original_size = f.tell()
                f.seek(0)
                
                # Compress to smaller size
                target_size = original_size // 2
                compressed_bytes, success, error = self.processor.compress_image(f, target_size)
                
                # Verify compression was successful
                self.assertTrue(success)
                self.assertIsNone(error)
                
                # Check compressed size
                self.assertLessEqual(len(compressed_bytes), target_size)
        finally:
            os.unlink(test_image_path)
            
    def test_compress_image_invalid_input(self):
        """Test image compression with invalid input"""
        # Test with non-existent file path
        compressed_bytes, success, error = self.processor.compress_image("/nonexistent/path.jpg")
        
        self.assertFalse(success)
        self.assertIsNotNone(error)
        
        # Test with invalid image data
        invalid_data = b"This is not an image"
        compressed_bytes, success, error = self.processor.compress_image(invalid_data)
        
        self.assertFalse(success)
        self.assertIsNotNone(error)
            
    def test_compress_image_quality_limit(self):
        """Test image compression when quality limit is reached"""
        # Create a large test image
        test_image_path = self.create_test_image(width=1200, height=1200)
        
        try:
            # Get original file size
            original_size = os.path.getsize(test_image_path)
            
            # Try to compress to an extremely small size (likely impossible)
            very_small_target = 100  # 100 bytes is likely impossible while maintaining image integrity
            compressed_bytes, success, error = self.processor.compress_image(test_image_path, very_small_target)
            
            # Even though target size wasn't reached, it should still return success
            # but the compressed size will be larger than the target
            self.assertTrue(success)
            self.assertIsNone(error)
            self.assertGreater(len(compressed_bytes), very_small_target)
            
            # But it should be smaller than the original
            self.assertLess(len(compressed_bytes), original_size)
        finally:
            os.unlink(test_image_path)


if __name__ == '__main__':
    unittest.main()
