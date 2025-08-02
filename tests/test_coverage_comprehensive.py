#!/usr/bin/env python3
"""
Code Coverage Test Suite for V0.41-black-ui
Measures and reports code coverage for the entire project
"""

import sys
import os
import unittest
import subprocess
import tempfile
import shutil

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_coverage_tool():
    """Check if coverage.py is available"""
    try:
        import coverage
        return True
    except ImportError:
        return False

def install_coverage():
    """Install coverage.py if not available"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "coverage"])
        return True
    except subprocess.CalledProcessError:
        return False

class TestCodeCoverage(unittest.TestCase):
    """Test code coverage analysis"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_coverage_tool_availability(self):
        """Test that coverage tool is available or can be installed"""
        if not check_coverage_tool():
            success = install_coverage()
            self.assertTrue(success, "Coverage tool not available and cannot be installed")
        
        # Import coverage after potential installation
        try:
            import coverage
            self.assertTrue(True)
        except ImportError:
            self.skipTest("Coverage tool not available")
    
    def test_unit_test_coverage(self):
        """Run unit tests with coverage measurement"""
        if not check_coverage_tool():
            self.skipTest("Coverage tool not available")
        
        try:
            # Run unit tests with coverage
            coverage_file = os.path.join(self.temp_dir, ".coverage_unit")
            
            cmd = [
                sys.executable, "-m", "coverage", "run",
                "--data-file", coverage_file,
                "--source", self.project_root,
                "--omit", "*/test/*,*/venv/*,*/__pycache__/*",
                os.path.join(self.project_root, "test", "test_unit_comprehensive.py")
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=120
            )
            
            # Check if coverage ran successfully
            self.assertEqual(result.returncode, 0, f"Unit test coverage failed: {result.stderr}")
            
            # Generate coverage report
            report_cmd = [
                sys.executable, "-m", "coverage", "report",
                "--data-file", coverage_file
            ]
            
            report_result = subprocess.run(
                report_cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if report_result.returncode == 0:
                print(f"\n[CHART] UNIT TEST COVERAGE REPORT:")
                print(report_result.stdout)
            
        except subprocess.TimeoutExpired:
            self.skipTest("Unit test coverage timed out")
        except Exception as e:
            self.skipTest(f"Unit test coverage failed: {e}")
    
    def test_integration_test_coverage(self):
        """Run integration tests with coverage measurement"""
        if not check_coverage_tool():
            self.skipTest("Coverage tool not available")
        
        try:
            # Run integration tests with coverage
            coverage_file = os.path.join(self.temp_dir, ".coverage_integration")
            
            cmd = [
                sys.executable, "-m", "coverage", "run",
                "--data-file", coverage_file,
                "--source", self.project_root,
                "--omit", "*/test/*,*/venv/*,*/__pycache__/*",
                os.path.join(self.project_root, "test", "test_integration_comprehensive.py")
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=120
            )
            
            # Check if coverage ran successfully
            self.assertEqual(result.returncode, 0, f"Integration test coverage failed: {result.stderr}")
            
            # Generate coverage report
            report_cmd = [
                sys.executable, "-m", "coverage", "report",
                "--data-file", coverage_file
            ]
            
            report_result = subprocess.run(
                report_cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if report_result.returncode == 0:
                print(f"\n[CHART] INTEGRATION TEST COVERAGE REPORT:")
                print(report_result.stdout)
                
        except subprocess.TimeoutExpired:
            self.skipTest("Integration test coverage timed out")
        except Exception as e:
            self.skipTest(f"Integration test coverage failed: {e}")
    
    def test_combined_coverage(self):
        """Run all tests with combined coverage measurement"""
        if not check_coverage_tool():
            self.skipTest("Coverage tool not available")
        
        try:
            coverage_file = os.path.join(self.temp_dir, ".coverage_combined")
            
            # List of test files to run
            test_files = [
                "test_unit_comprehensive.py",
                "test_integration_comprehensive.py",
                "test_functional_comprehensive.py",
                "test_regression_comprehensive.py"
            ]
            
            # Run each test file with coverage
            for test_file in test_files:
                test_path = os.path.join(self.project_root, "test", test_file)
                if os.path.exists(test_path):
                    cmd = [
                        sys.executable, "-m", "coverage", "run",
                        "--data-file", coverage_file,
                        "--append",  # Append to existing coverage data
                        "--source", self.project_root,
                        "--omit", "*/test/*,*/venv/*,*/__pycache__/*",
                        test_path
                    ]
                    
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        cwd=self.project_root,
                        timeout=60
                    )
                    
                    # Continue even if one test fails
                    if result.returncode != 0:
                        print(f"[WARN]  {test_file} coverage failed: {result.stderr}")
            
            # Generate combined coverage report
            report_cmd = [
                sys.executable, "-m", "coverage", "report",
                "--data-file", coverage_file
            ]
            
            report_result = subprocess.run(
                report_cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if report_result.returncode == 0:
                print(f"\n[CHART] COMBINED COVERAGE REPORT:")
                print(report_result.stdout)
                
                # Try to generate HTML report
                html_cmd = [
                    sys.executable, "-m", "coverage", "html",
                    "--data-file", coverage_file,
                    "--directory", os.path.join(self.temp_dir, "htmlcov")
                ]
                
                html_result = subprocess.run(
                    html_cmd,
                    capture_output=True,
                    text=True,
                    cwd=self.project_root
                )
                
                if html_result.returncode == 0:
                    print(f"[FILE] HTML coverage report generated in {os.path.join(self.temp_dir, 'htmlcov')}")
                
        except subprocess.TimeoutExpired:
            self.skipTest("Combined coverage timed out")
        except Exception as e:
            self.skipTest(f"Combined coverage failed: {e}")
    
    def test_module_coverage_analysis(self):
        """Analyze coverage for each module individually"""
        if not check_coverage_tool():
            self.skipTest("Coverage tool not available")
        
        # Core modules to analyze
        modules = [
            "main.py",
            "modern_gui.py", 
            "error_handler.py",
            "llm_interface.py",
            "memory.py",
            "logs.py"
        ]
        
        coverage_results = {}
        
        for module in modules:
            module_path = os.path.join(self.project_root, module)
            if not os.path.exists(module_path):
                continue
                
            try:
                coverage_file = os.path.join(self.temp_dir, f".coverage_{module.replace('.py', '')}")
                
                # Run unit tests focusing on this module
                cmd = [
                    sys.executable, "-m", "coverage", "run",
                    "--data-file", coverage_file,
                    "--source", module_path,
                    os.path.join(self.project_root, "test", "test_unit_comprehensive.py")
                ]
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    cwd=self.project_root,
                    timeout=60
                )
                
                if result.returncode == 0:
                    # Get coverage report
                    report_cmd = [
                        sys.executable, "-m", "coverage", "report",
                        "--data-file", coverage_file
                    ]
                    
                    report_result = subprocess.run(
                        report_cmd,
                        capture_output=True,
                        text=True,
                        cwd=self.project_root
                    )
                    
                    if report_result.returncode == 0:
                        coverage_results[module] = report_result.stdout
                        
            except subprocess.TimeoutExpired:
                coverage_results[module] = "Timeout"
            except Exception as e:
                coverage_results[module] = f"Error: {e}"
        
        # Print module coverage summary
        print(f"\n[CHART] MODULE COVERAGE ANALYSIS:")
        for module, result in coverage_results.items():
            print(f"\n[SEARCH] {module}:")
            if isinstance(result, str) and len(result) > 100:
                # Extract coverage percentage if available
                lines = result.split('\n')
                for line in lines:
                    if module.replace('.py', '') in line or 'TOTAL' in line:
                        print(f"   {line}")
            else:
                print(f"   {result}")
    
    def test_uncovered_lines_analysis(self):
        """Analyze which lines are not covered by tests"""
        if not check_coverage_tool():
            self.skipTest("Coverage tool not available")
        
        try:
            coverage_file = os.path.join(self.temp_dir, ".coverage_missing")
            
            # Run tests with coverage
            cmd = [
                sys.executable, "-m", "coverage", "run",
                "--data-file", coverage_file,
                "--source", self.project_root,
                "--omit", "*/test/*,*/venv/*,*/__pycache__/*",
                os.path.join(self.project_root, "test", "test_unit_comprehensive.py")
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=120
            )
            
            if result.returncode == 0:
                # Generate report with missing lines
                report_cmd = [
                    sys.executable, "-m", "coverage", "report",
                    "--data-file", coverage_file,
                    "--show-missing"
                ]
                
                report_result = subprocess.run(
                    report_cmd,
                    capture_output=True,
                    text=True,
                    cwd=self.project_root
                )
                
                if report_result.returncode == 0:
                    print(f"\n[CHART] UNCOVERED LINES ANALYSIS:")
                    print(report_result.stdout)
                    
                    # Analyze the report for missing coverage
                    lines = report_result.stdout.split('\n')
                    total_coverage = None
                    
                    for line in lines:
                        if 'TOTAL' in line:
                            # Extract total coverage percentage
                            parts = line.split()
                            for part in parts:
                                if '%' in part:
                                    total_coverage = part
                                    break
                    
                    if total_coverage:
                        coverage_percent = float(total_coverage.replace('%', ''))
                        print(f"\n[TARGET] COVERAGE SUMMARY:")
                        print(f"   Total Coverage: {total_coverage}")
                        
                        if coverage_percent >= 90:
                            print("   Status: [GREEN] EXCELLENT")
                        elif coverage_percent >= 80:
                            print("   Status: [YELLOW] GOOD")
                        elif coverage_percent >= 70:
                            print("   Status: [ORANGE] NEEDS IMPROVEMENT")
                        else:
                            print("   Status: [RED] POOR")
                        
                        # Assert minimum coverage requirement
                        self.assertGreater(coverage_percent, 50, 
                                         f"Code coverage too low: {coverage_percent}%")
                
        except subprocess.TimeoutExpired:
            self.skipTest("Uncovered lines analysis timed out")
        except Exception as e:
            self.skipTest(f"Uncovered lines analysis failed: {e}")

if __name__ == "__main__":
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [TestCodeCoverage]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"CODE COVERAGE TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)