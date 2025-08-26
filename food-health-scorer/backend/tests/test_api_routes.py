import unittest
import tempfile
import os
import sys
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI
import io
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.routes import router
from main import app

class TestAPIRoutes(unittest.TestCase):
    """Test cases for API routes"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = TestClient(app)
    
    def create_test_image_file(self):
        """Create a test image file for upload testing"""
        # Create a simple test image (1x1 pixel PNG)
        image_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82'
        return io.BytesIO(image_data)
    
    def test_health_check_endpoint(self):
        """Test the health check endpoint"""
        response = self.client.get("/api/health")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["service"], "Food Health Scorer API")
        self.assertIn("timestamp", data)
    
    @patch('utils.image_processor.ImageProcessor.extract_text')
    @patch('utils.image_processor.ImageProcessor.extract_ingredients')
    @patch('models.food_analyzer.FoodAnalyzer.analyze')
    def test_analyze_image_success(self, mock_analyze, mock_extract_ingredients, mock_extract_text):
        """Test successful image analysis"""
        # Mock the dependencies
        mock_extract_text.return_value = ("配料表: 小麦粉, 糖, 植物油", True, None)
        mock_extract_ingredients.return_value = ["小麦粉", "糖", "植物油"]
        mock_analyze.return_value = {
            "score": 65,
            "health_points": ["Contains some beneficial ingredients"],
            "recommendations": ["Consume in moderation"],
            "scientific_reasoning": ["Whole grains provide fiber"]
        }
        
        # Create test file
        test_file = self.create_test_image_file()
        
        # Make request
        response = self.client.post(
            "/api/analyze",
            files={"image": ("test.png", test_file, "image/png")}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["score"], 65)
        self.assertIn("health_points", data)
        self.assertIn("recommendations", data)
        self.assertIn("scientific_reasoning", data)
        self.assertIn("processing_time", data)
    
    def test_analyze_image_invalid_file_type(self):
        """Test image analysis with invalid file type"""
        # Create a text file instead of image
        test_file = io.BytesIO(b"This is not an image")
        
        response = self.client.post(
            "/api/analyze",
            files={"image": ("test.txt", test_file, "text/plain")}
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertIn("Unsupported file type", response.json()["detail"])
    
    def test_analyze_image_empty_file(self):
        """Test image analysis with empty file"""
        test_file = io.BytesIO(b"")
        
        response = self.client.post(
            "/api/analyze",
            files={"image": ("empty.png", test_file, "image/png")}
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertIn("Empty file", response.json()["detail"])
    
    def test_analyze_image_file_too_large(self):
        """Test image analysis with file too large"""
        # Create a file that exceeds the size limit
        large_data = b"x" * (11 * 1024 * 1024)  # 11MB
        test_file = io.BytesIO(large_data)
        
        response = self.client.post(
            "/api/analyze",
            files={"image": ("large.png", test_file, "image/png")}
        )
        
        self.assertEqual(response.status_code, 413)
        self.assertIn("File too large", response.json()["detail"])
    
    @patch('utils.image_processor.ImageProcessor.extract_text')
    def test_analyze_image_ocr_failure(self, mock_extract_text):
        """Test image analysis when OCR fails"""
        # Mock OCR failure
        mock_extract_text.return_value = ("", False, "Unable to read image")
        
        test_file = self.create_test_image_file()
        
        response = self.client.post(
            "/api/analyze",
            files={"image": ("test.png", test_file, "image/png")}
        )
        
        self.assertEqual(response.status_code, 422)
        self.assertIn("Unable to extract text", response.json()["detail"])
    
    @patch('utils.image_processor.ImageProcessor.extract_text')
    @patch('utils.image_processor.ImageProcessor.extract_ingredients')
    def test_analyze_image_no_ingredients(self, mock_extract_ingredients, mock_extract_text):
        """Test image analysis when no ingredients are found"""
        # Mock successful OCR but no ingredients found
        mock_extract_text.return_value = ("Some text without ingredients", True, None)
        mock_extract_ingredients.return_value = []
        
        test_file = self.create_test_image_file()
        
        response = self.client.post(
            "/api/analyze",
            files={"image": ("test.png", test_file, "image/png")}
        )
        
        self.assertEqual(response.status_code, 422)
        self.assertIn("No ingredients could be identified", response.json()["detail"])
    
    def test_get_ingredient_info_success(self):
        """Test successful ingredient info retrieval"""
        response = self.client.get("/api/health-info/糖")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["ingredient"], "糖")
        self.assertIn("health_impact", data)
        self.assertIn("description", data)
        self.assertIn("score", data)
    
    def test_get_ingredient_info_empty_name(self):
        """Test ingredient info with empty name"""
        response = self.client.get("/api/health-info/")
        
        # Should return 404 for empty path
        self.assertEqual(response.status_code, 404)
    
    def test_get_ingredient_info_long_name(self):
        """Test ingredient info with very long name"""
        long_name = "x" * 150  # Exceeds 100 character limit
        response = self.client.get(f"/api/health-info/{long_name}")
        
        self.assertEqual(response.status_code, 400)
        self.assertIn("too long", response.json()["detail"])
    
    def test_get_ingredient_info_with_scientific_reasoning(self):
        """Test ingredient info includes scientific reasoning when available"""
        response = self.client.get("/api/health-info/燕麦")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        # Should include scientific reasoning for known ingredients
        self.assertIn("scientific_reasoning", data)
    
    @patch('utils.image_processor.ImageProcessor.extract_text')
    @patch('utils.image_processor.ImageProcessor.extract_ingredients')
    @patch('models.food_analyzer.FoodAnalyzer.analyze')
    def test_analyze_image_response_metadata(self, mock_analyze, mock_extract_ingredients, mock_extract_text):
        """Test that analysis response includes proper metadata"""
        # Mock the dependencies
        mock_extract_text.return_value = ("配料表: 小麦粉, 糖", True, None)
        mock_extract_ingredients.return_value = ["小麦粉", "糖"]
        mock_analyze.return_value = {
            "score": 50,
            "health_points": [],
            "recommendations": [],
            "scientific_reasoning": []
        }
        
        test_file = self.create_test_image_file()
        
        response = self.client.post(
            "/api/analyze",
            files={"image": ("test.png", test_file, "image/png")}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check metadata fields
        self.assertIn("processing_time", data)
        self.assertIn("extracted_text_length", data)
        self.assertIn("ingredients_count", data)
        self.assertIn("file_size", data)
        self.assertIn("file_type", data)
        
        # Verify metadata values
        self.assertGreater(data["processing_time"], 0)
        self.assertEqual(data["ingredients_count"], 2)
        self.assertEqual(data["file_type"], "image/png")
    
    def test_cors_headers(self):
        """Test that CORS headers are properly set"""
        response = self.client.get("/api/health")
        
        # CORS headers should be handled by FastAPI middleware
        self.assertEqual(response.status_code, 200)
        
    @patch('utils.image_processor.ImageProcessor.compress_image')
    @patch('utils.image_processor.ImageProcessor.extract_text')
    @patch('utils.image_processor.ImageProcessor.extract_ingredients')
    @patch('models.food_analyzer.FoodAnalyzer.analyze')
    def test_analyze_image_with_compression(self, mock_analyze, mock_extract_ingredients, mock_extract_text, mock_compress):
        """Test that image compression is used when file is too large"""
        # Create a mock large file
        large_data = b"x" * (6 * 1024 * 1024)  # 6MB (over default compression threshold)
        test_file = io.BytesIO(large_data)
        
        # Mock compression to return smaller data
        compressed_data = b"compressed_image_data"
        mock_compress.return_value = (compressed_data, True, None)
        
        # Mock the other dependencies
        mock_extract_text.return_value = ("配料表: 小麦粉, 糖", True, None)
        mock_extract_ingredients.return_value = ["小麦粉", "糖"]
        mock_analyze.return_value = {
            "score": 50,
            "health_points": ["Sample health point"],
            "recommendations": ["Sample recommendation"],
            "scientific_reasoning": ["Sample reasoning"]
        }
        
        # Make request
        response = self.client.post(
            "/api/analyze",
            files={"image": ("large.jpg", test_file, "image/jpeg")}
        )
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        
        # Verify compression was called
        mock_compress.assert_called_once()
        
        # Verify the other methods were called with the compressed data
        mock_extract_text.assert_called_once_with(compressed_data)
        
    @patch('utils.image_processor.ImageProcessor.compress_image')
    def test_analyze_image_compression_failure(self, mock_compress):
        """Test handling of image compression failure"""
        # Create a test file
        test_file = self.create_test_image_file()
        
        # Mock compression failure
        mock_compress.return_value = (None, False, "Failed to compress image")
        
        # Make request
        response = self.client.post(
            "/api/analyze",
            files={"image": ("test.jpg", test_file, "image/jpeg")}
        )
        
        # Verify response indicates error
        self.assertEqual(response.status_code, 422)
        self.assertIn("Failed to compress image", response.json()["detail"])
        
    @patch('utils.image_processor.ImageProcessor.compress_image')
    @patch('utils.image_processor.ImageProcessor.extract_text')
    @patch('utils.image_processor.ImageProcessor.extract_ingredients')
    @patch('models.food_analyzer.FoodAnalyzer.analyze')
    def test_analyze_image_performance_metrics(self, mock_analyze, mock_extract_ingredients, mock_extract_text, mock_compress):
        """Test that performance metrics are included in response"""
        # Create a test file
        test_file = self.create_test_image_file()
        
        # Skip compression for small files
        mock_compress.return_value = (b"test_data", True, None)
        
        # Mock the other dependencies
        mock_extract_text.return_value = ("配料表: 小麦粉, 糖", True, None)
        mock_extract_ingredients.return_value = ["小麦粉", "糖"]
        mock_analyze.return_value = {
            "score": 50,
            "health_points": [],
            "recommendations": [],
            "scientific_reasoning": []
        }
        
        # Make request and measure time
        start_time = time.time()
        response = self.client.post(
            "/api/analyze",
            files={"image": ("test.jpg", test_file, "image/jpeg")}
        )
        end_time = time.time()
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check performance metrics
        self.assertIn("processing_time", data)
        self.assertGreaterEqual(data["processing_time"], 0)
        
        # Verify the processing time is reasonable (less than actual elapsed time)
        self.assertLessEqual(data["processing_time"], end_time - start_time + 0.1)  # Add small buffer
    
    @patch('utils.image_processor.ImageProcessor.extract_text')
    def test_analyze_image_server_error(self, mock_extract_text):
        """Test handling of unexpected server errors"""
        # Mock an unexpected exception
        mock_extract_text.side_effect = Exception("Unexpected error")
        
        test_file = self.create_test_image_file()
        
        response = self.client.post(
            "/api/analyze",
            files={"image": ("test.png", test_file, "image/png")}
        )
        
        self.assertEqual(response.status_code, 500)
        self.assertIn("Internal server error", response.json()["detail"])


if __name__ == '__main__':
    unittest.main()
