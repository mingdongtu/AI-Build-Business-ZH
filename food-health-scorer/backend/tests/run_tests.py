#!/usr/bin/env python3
"""
Test runner script for Food Health Scorer backend tests
"""

import unittest
import sys
import os
import time

# Add parent directory to path so imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import test modules
from tests.test_api_routes import TestAPIRoutes
from tests.test_food_analyzer import TestFoodAnalyzer
from tests.test_image_processor import TestImageProcessor


def run_tests_with_coverage():
    """Run all tests with coverage reporting"""
    try:
        import coverage
    except ImportError:
        print("Coverage package not installed. Run 'pip install coverage' first.")
        return False
        
    # Start coverage measurement
    cov = coverage.Coverage(
        source=['api', 'models', 'utils'],
        omit=['*/__pycache__/*', '*/tests/*']
    )
    cov.start()
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestAPIRoutes))
    test_suite.addTest(unittest.makeSuite(TestFoodAnalyzer))
    test_suite.addTest(unittest.makeSuite(TestImageProcessor))
    
    # Run tests with timing
    start_time = time.time()
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    end_time = time.time()
    
    # Stop coverage measurement and generate report
    cov.stop()
    
    # Print test summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Ran {result.testsRun} tests in {end_time - start_time:.2f} seconds")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    # Print coverage report
    print("\n" + "=" * 70)
    print("COVERAGE REPORT")
    print("=" * 70)
    cov.report()
    
    # Generate HTML coverage report
    try:
        cov.html_report(directory='htmlcov')
        print(f"\nHTML coverage report generated in: {os.path.join(os.getcwd(), 'htmlcov')}")
    except Exception as e:
        print(f"Could not generate HTML report: {e}")
    
    # Return success status
    return result.wasSuccessful()


def run_tests_simple():
    """Run tests without coverage reporting"""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestAPIRoutes))
    test_suite.addTest(unittest.makeSuite(TestFoodAnalyzer))
    test_suite.addTest(unittest.makeSuite(TestImageProcessor))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    print("Food Health Scorer Backend Test Suite")
    print("=" * 40)
    
    # Parse command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == '--no-coverage':
        success = run_tests_simple()
    else:
        success = run_tests_with_coverage()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
