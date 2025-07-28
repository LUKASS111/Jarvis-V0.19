#!/usr/bin/env python3
"""
Master Test Runner for V0.41-black-ui
Executes all test suites and provides comprehensive reporting
"""

import sys
import os
import unittest
import time
import subprocess
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))))

def run_test_file(test_file, description):
    """Run a specific test file and capture results"""
    test_path = os.path.join(os.path.dirname(__file__), test_file)
    
    if not os.path.exists(test_path):
        return {
            "name": test_file,
            "description": description,
            "status": "SKIPPED",
            "reason": "File not found",
            "duration": 0,
            "tests_run": 0,
            "failures": 0,
            "errors": 0
        }
    
    print(f"\n{'='*60}")
    print(f"[TEST] Running {description}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            [sys.executable, test_path],
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout per test suite
            cwd=os.path.dirname(os.path.dirname(__file__))
        )
        
        duration = time.time() - start_time
        output = result.stdout
        error_output = result.stderr
        
        # Parse output for test statistics
        tests_run = 0
        failures = 0
        errors = 0
        
        # Look for test summary in output
        lines = output.split('\n')
        for line in lines:
            if 'Tests run:' in line:
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == 'run:' and i + 1 < len(parts):
                        tests_run = int(parts[i + 1])
                    elif part == 'Failures:' and i + 1 < len(parts):
                        failures = int(parts[i + 1])
                    elif part == 'Errors:' and i + 1 < len(parts):
                        errors = int(parts[i + 1])
        
        # Determine status
        if result.returncode == 0:
            status = "PASS"
        else:
            status = "FAIL"
        
        # Print output
        if output:
            print(output)
        if error_output and status == "FAIL":
            print("STDERR:")
            print(error_output)
        
        return {
            "name": test_file,
            "description": description,
            "status": status,
            "duration": duration,
            "tests_run": tests_run,
            "failures": failures,
            "errors": errors,
            "output": output,
            "error_output": error_output
        }
        
    except subprocess.TimeoutExpired:
        duration = time.time() - start_time
        print(f"⏰ Test suite timed out after {duration:.1f} seconds")
        
        return {
            "name": test_file,
            "description": description,
            "status": "TIMEOUT",
            "duration": duration,
            "tests_run": 0,
            "failures": 0,
            "errors": 1,
            "reason": "Test suite timed out"
        }
        
    except Exception as e:
        duration = time.time() - start_time
        print(f"[FAIL] Error running test suite: {e}")
        
        return {
            "name": test_file,
            "description": description,
            "status": "ERROR",
            "duration": duration,
            "tests_run": 0,
            "failures": 0,
            "errors": 1,
            "reason": str(e)
        }

def main():
    """Main test runner function"""
    print("[LAUNCH] V0.41-black-ui COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Define test suites
    test_suites = [
        ("test_unit_comprehensive.py", "Unit Tests - Core functionality"),
        ("test_integration_comprehensive.py", "Integration Tests - Module interactions"),
        ("test_functional_comprehensive.py", "Functional Tests - End-user scenarios"),
        ("test_regression_comprehensive.py", "Regression Tests - Prevent old bugs"),
        ("test_performance_comprehensive.py", "Performance Tests - Speed and efficiency"),
        ("test_coverage_comprehensive.py", "Coverage Tests - Code coverage analysis")
    ]
    
    # Run all test suites
    overall_start_time = time.time()
    results = []
    
    for test_file, description in test_suites:
        result = run_test_file(test_file, description)
        results.append(result)
    
    overall_duration = time.time() - overall_start_time
    
    # Generate comprehensive summary
    print(f"\n{'='*80}")
    print("[CHART] COMPREHENSIVE TEST RESULTS SUMMARY")
    print(f"{'='*80}")
    
    total_tests = 0
    total_failures = 0
    total_errors = 0
    passed_suites = 0
    failed_suites = 0
    
    print(f"{'Test Suite':<40} {'Status':<10} {'Tests':<8} {'Fails':<8} {'Errors':<8} {'Time':<8}")
    print("-" * 80)
    
    for result in results:
        status_symbol = {
            "PASS": "✅",
            "FAIL": "[FAIL]", 
            "TIMEOUT": "⏰",
            "ERROR": "[BOOM]",
            "SKIPPED": "[SKIP]"
        }.get(result["status"], "❓")
        
        print(f"{result['description']:<40} {status_symbol} {result['status']:<7} "
              f"{result['tests_run']:<8} {result['failures']:<8} {result['errors']:<8} "
              f"{result['duration']:.1f}s")
        
        total_tests += result["tests_run"]
        total_failures += result["failures"]
        total_errors += result["errors"]
        
        if result["status"] == "PASS":
            passed_suites += 1
        elif result["status"] in ["FAIL", "TIMEOUT", "ERROR"]:
            failed_suites += 1
    
    print("-" * 80)
    print(f"{'TOTALS':<40} {'---':<10} {total_tests:<8} {total_failures:<8} {total_errors:<8} {overall_duration:.1f}s")
    
    # Calculate success rates
    total_suite_count = len([r for r in results if r["status"] != "SKIPPED"])
    suite_success_rate = (passed_suites / total_suite_count * 100) if total_suite_count > 0 else 0
    
    test_success_rate = 0
    if total_tests > 0:
        successful_tests = total_tests - total_failures - total_errors
        test_success_rate = (successful_tests / total_tests * 100)
    
    print(f"\n[TARGET] OVERALL SUMMARY:")
    print(f"   Test Suites:     {passed_suites}/{total_suite_count} passed ({suite_success_rate:.1f}%)")
    print(f"   Individual Tests: {total_tests - total_failures - total_errors}/{total_tests} passed ({test_success_rate:.1f}%)")
    print(f"   Total Duration:   {overall_duration:.1f} seconds")
    print(f"   Total Failures:   {total_failures}")
    print(f"   Total Errors:     {total_errors}")
    
    # Overall status
    if suite_success_rate >= 100:
        overall_status = "[GREEN] PERFECT"
    elif suite_success_rate >= 80:
        overall_status = "[GREEN] EXCELLENT"
    elif suite_success_rate >= 60:
        overall_status = "[YELLOW] GOOD"
    elif suite_success_rate >= 40:
        overall_status = "[ORANGE] NEEDS IMPROVEMENT"
    else:
        overall_status = "[RED] CRITICAL ISSUES"
    
    print(f"   Overall Status:   {overall_status}")
    
    # Detailed failure analysis
    failed_results = [r for r in results if r["status"] in ["FAIL", "TIMEOUT", "ERROR"]]
    if failed_results:
        print(f"\n[WARN]  FAILED TEST SUITES:")
        for result in failed_results:
            print(f"\n   [FOLDER] {result['description']} ({result['status']}):")
            if "reason" in result:
                print(f"      Reason: {result['reason']}")
            if result.get("error_output"):
                # Show last few lines of error output
                error_lines = result["error_output"].split('\n')
                relevant_errors = [line for line in error_lines[-10:] if line.strip()]
                for line in relevant_errors[:3]:  # Show max 3 error lines
                    print(f"      {line}")
    
    # Recommendations
    print(f"\n[IDEA] RECOMMENDATIONS:")
    
    if total_failures > 0:
        print(f"   - Fix {total_failures} failing test cases")
    
    if total_errors > 0:
        print(f"   - Resolve {total_errors} test errors")
    
    if suite_success_rate < 100:
        print(f"   - Investigate failed test suites for critical issues")
    
    if test_success_rate < 90:
        print(f"   - Improve test coverage and fix failing tests")
    
    if overall_duration > 300:  # 5 minutes
        print(f"   - Consider optimizing test performance (current: {overall_duration:.1f}s)")
    
    if suite_success_rate >= 80:
        print(f"   - ✅ Test suite is in good condition!")
        print(f"   - Consider running performance benchmarks")
        print(f"   - Review code coverage reports")
    
    print(f"\n[TIME1] Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Return appropriate exit code
    if suite_success_rate >= 80 and total_errors == 0:
        return 0  # Success
    else:
        return 1  # Failure

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)