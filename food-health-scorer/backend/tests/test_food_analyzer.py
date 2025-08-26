import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.food_analyzer import FoodAnalyzer


class TestFoodAnalyzer(unittest.TestCase):
    """Test cases for FoodAnalyzer class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = FoodAnalyzer()
    
    def test_analyze_empty_ingredients(self):
        """Test analysis with empty ingredient list"""
        result = self.analyzer.analyze([])
        
        self.assertEqual(result['score'], 0)
        self.assertIn('recommendations', result)
        self.assertIn('scientific_reasoning', result)
        self.assertIn('No ingredients provided', result['recommendations'][0])
    
    def test_analyze_healthy_ingredients(self):
        """Test analysis with healthy ingredients"""
        healthy_ingredients = ['全麦粉', '燕麦', '坚果', '橄榄油', '蔬菜']
        result = self.analyzer.analyze(healthy_ingredients)
        
        # Should have a good score for healthy ingredients
        self.assertGreater(result['score'], 60)
        self.assertIn('health_points', result)
        self.assertIn('recommendations', result)
        self.assertIn('scientific_reasoning', result)
    
    def test_analyze_unhealthy_ingredients(self):
        """Test analysis with unhealthy ingredients"""
        unhealthy_ingredients = ['白砂糖', '反式脂肪', '人工色素', '甜蜜素', '亚硝酸盐']
        result = self.analyzer.analyze(unhealthy_ingredients)
        
        # Should have a low score for unhealthy ingredients
        self.assertLess(result['score'], 40)
        self.assertIn('concerning', ''.join(result['health_points']).lower())
    
    def test_analyze_mixed_ingredients(self):
        """Test analysis with mixed healthy and unhealthy ingredients"""
        mixed_ingredients = ['小麦粉', '糖', '植物油', '全麦粉', '盐']
        result = self.analyzer.analyze(mixed_ingredients)
        
        # Should have a moderate score
        self.assertGreaterEqual(result['score'], 0)
        self.assertLessEqual(result['score'], 100)
        self.assertGreater(len(result['health_points']), 0)
    
    def test_analyze_high_sugar_content(self):
        """Test analysis with high proportion of sugar ingredients"""
        sugar_heavy_ingredients = ['糖', '白砂糖', '蔗糖', '果糖', '小麦粉']
        result = self.analyzer.analyze(sugar_heavy_ingredients)
        
        # Should penalize for high sugar content
        self.assertLess(result['score'], 50)
        sugar_mentioned = any('sugar' in point.lower() or '糖' in point for point in result['health_points'])
        self.assertTrue(sugar_mentioned)
    
    def test_analyze_artificial_additives(self):
        """Test analysis with artificial additives"""
        additive_ingredients = ['小麦粉', '人工色素', '人工香料', '甜蜜素', '防腐剂']
        result = self.analyzer.analyze(additive_ingredients)
        
        # Should penalize for artificial additives
        self.assertLess(result['score'], 60)
        additive_mentioned = any('additive' in point.lower() or '添加' in point for point in result['health_points'])
        self.assertTrue(additive_mentioned)
    
    def test_analyze_whole_foods(self):
        """Test analysis with whole food ingredients"""
        whole_food_ingredients = ['全麦粉', '燕麦', '糙米', '豆类', '坚果', '蔬菜']
        result = self.analyzer.analyze(whole_food_ingredients)
        
        # Should reward whole foods
        self.assertGreater(result['score'], 70)
        whole_food_mentioned = any('whole' in point.lower() or '全' in point for point in result['health_points'])
        self.assertTrue(whole_food_mentioned)
    
    def test_get_ingredient_info_known_ingredient(self):
        """Test getting info for a known ingredient"""
        info = self.analyzer.get_ingredient_info('糖')
        
        self.assertIn('ingredient', info)
        self.assertIn('health_impact', info)
        self.assertIn('description', info)
        self.assertIn('score', info)
        self.assertEqual(info['ingredient'], '糖')
        self.assertLess(info['score'], 0)  # Sugar should have negative score
    
    def test_get_ingredient_info_healthy_ingredient(self):
        """Test getting info for a healthy ingredient"""
        info = self.analyzer.get_ingredient_info('燕麦')
        
        self.assertEqual(info['ingredient'], '燕麦')
        self.assertGreater(info['score'], 0)  # Oats should have positive score
        self.assertIn('有益', info['health_impact'])
    
    def test_get_ingredient_info_unknown_ingredient(self):
        """Test getting info for an unknown ingredient"""
        info = self.analyzer.get_ingredient_info('未知配料')
        
        self.assertEqual(info['ingredient'], '未知配料')
        self.assertEqual(info['score'], 0)  # Unknown ingredients get neutral score
        self.assertEqual(info['health_impact'], '中性')
    
    def test_get_ingredient_info_concerning_additive(self):
        """Test getting info for a concerning additive"""
        info = self.analyzer.get_ingredient_info('甜蜜素')
        
        self.assertEqual(info['ingredient'], '甜蜜素')
        self.assertTrue(info['is_concerning'])
        self.assertEqual(info['health_impact'], '有争议')
    
    def test_ingredient_scoring_consistency(self):
        """Test that ingredient scoring is consistent"""
        # Test multiple calls return same results
        ingredients = ['糖', '全麦粉', '植物油']
        
        result1 = self.analyzer.analyze(ingredients)
        result2 = self.analyzer.analyze(ingredients)
        
        self.assertEqual(result1['score'], result2['score'])
    
    def test_score_bounds(self):
        """Test that scores are always within valid bounds (0-100)"""
        test_cases = [
            ['糖', '白砂糖', '反式脂肪', '人工色素'],  # Very unhealthy
            ['全麦粉', '燕麦', '坚果', '橄榄油'],      # Very healthy
            ['小麦粉', '盐', '水'],                    # Neutral
            []                                        # Empty
        ]
        
        for ingredients in test_cases:
            result = self.analyzer.analyze(ingredients)
            self.assertGreaterEqual(result['score'], 0)
            self.assertLessEqual(result['score'], 100)
    
    def test_scientific_reasoning_provided(self):
        """Test that scientific reasoning is provided in analysis"""
        ingredients = ['糖', '全麦粉', '反式脂肪']
        result = self.analyzer.analyze(ingredients)
        
        self.assertIn('scientific_reasoning', result)
        self.assertGreater(len(result['scientific_reasoning']), 0)
        
        # Check that reasoning contains scientific information
        reasoning_text = ' '.join(result['scientific_reasoning'])
        scientific_terms = ['血糖', '胆固醇', '心血管', '纤维', '营养']
        has_scientific_content = any(term in reasoning_text for term in scientific_terms)
        self.assertTrue(has_scientific_content)
    
    def test_recommendations_quality(self):
        """Test that recommendations are appropriate for the score"""
        # Test low score recommendations
        unhealthy_ingredients = ['糖', '反式脂肪', '人工色素']
        result = self.analyzer.analyze(unhealthy_ingredients)
        
        if result['score'] < 30:
            recommendation_text = ' '.join(result['recommendations'])
            self.assertIn('concerning', recommendation_text.lower())
        
        # Test high score recommendations
        healthy_ingredients = ['全麦粉', '燕麦', '坚果']
        result = self.analyzer.analyze(healthy_ingredients)
        
        if result['score'] > 70:
            recommendation_text = ' '.join(result['recommendations'])
            self.assertIn('good', recommendation_text.lower())
    
    def test_ingredient_distribution_analysis(self):
        """Test that ingredient distribution affects scoring"""
        # Test high sugar proportion
        high_sugar = ['糖', '白砂糖', '蔗糖', '小麦粉']  # 75% sugar
        result_high_sugar = self.analyzer.analyze(high_sugar)
        
        # Test low sugar proportion
        low_sugar = ['小麦粉', '植物油', '盐', '糖']  # 25% sugar
        result_low_sugar = self.analyzer.analyze(low_sugar)
        
        # High sugar should score lower
        self.assertLess(result_high_sugar['score'], result_low_sugar['score'])
        
    def test_ingredient_combinations(self):
        """Test that certain ingredient combinations are analyzed correctly"""
        # Test balanced combination
        balanced = ['全麦粉', '蜂蜜', '坚果', '植物油']
        result_balanced = self.analyzer.analyze(balanced)
        
        # Test unbalanced combination
        unbalanced = ['白面粉', '糖', '人工色素', '反式脂肪']
        result_unbalanced = self.analyzer.analyze(unbalanced)
        
        # Balanced should score higher
        self.assertGreater(result_balanced['score'], result_unbalanced['score'])
        
        # Check for combination-specific recommendations
        balanced_recommendations = ' '.join(result_balanced['recommendations'])
        self.assertTrue('balance' in balanced_recommendations.lower() or 
                       '平衡' in balanced_recommendations)
        
    def test_error_handling_with_invalid_input(self):
        """Test error handling with invalid input types"""
        # Test with None
        result = self.analyzer.analyze(None)
        self.assertEqual(result['score'], 0)
        self.assertIn('error', ' '.join(result['recommendations']).lower())
        
        # Test with non-list input
        result = self.analyzer.analyze("not a list")
        self.assertEqual(result['score'], 0)
        self.assertIn('error', ' '.join(result['recommendations']).lower())
        
    def test_ingredient_info_with_special_characters(self):
        """Test ingredient info with special characters"""
        # Test with ingredient containing special characters
        info = self.analyzer.get_ingredient_info('维生素E(dl-α-生育酚)')
        
        self.assertIsNotNone(info)
        self.assertEqual(info['ingredient'], '维生素E(dl-α-生育酚)')
        
    def test_performance_with_large_ingredient_list(self):
        """Test analyzer performance with a large list of ingredients"""
        # Create a large list of ingredients
        large_list = ['小麦粉', '糖', '盐', '植物油'] * 25  # 100 ingredients
        
        import time
        start_time = time.time()
        result = self.analyzer.analyze(large_list)
        end_time = time.time()
        
        # Analysis should complete in a reasonable time (less than 1 second)
        self.assertLess(end_time - start_time, 1.0)
        
        # Result should still be valid
        self.assertGreaterEqual(result['score'], 0)
        self.assertLessEqual(result['score'], 100)
        self.assertGreater(len(result['recommendations']), 0)


if __name__ == '__main__':
    unittest.main()
