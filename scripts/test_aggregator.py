#!/usr/bin/env python3
"""
Test Aggregator Script
Aggregates test results and generates comprehensive reports
"""

import os
import sys
import json
import glob
from datetime import datetime
from pathlib import Path

def aggregate_test_results():
    """Aggregate all test results into a comprehensive report"""
    print("📊 Aggregating test results...")
    
    # Find all test result files
    test_result_files = glob.glob("test_results_*.json")
    
    if not test_result_files:
        print("No test result files found")
        return
    
    aggregated_results = {
        'timestamp': datetime.now().isoformat(),
        'total_test_files': len(test_result_files),
        'test_suites': [],
        'summary': {
            'total_tests': 0,
            'total_passed': 0,
            'total_failed': 0,
            'total_errors': 0,
            'success_rate': 0.0
        }
    }
    
    for result_file in test_result_files:
        try:
            with open(result_file, 'r') as f:
                test_data = json.load(f)
                aggregated_results['test_suites'].append(test_data)
                
                # Update summary
                if 'tests_run' in test_data:
                    aggregated_results['summary']['total_tests'] += test_data.get('tests_run', 0)
                    aggregated_results['summary']['total_passed'] += test_data.get('tests_run', 0) - test_data.get('failures', 0) - test_data.get('errors', 0)
                    aggregated_results['summary']['total_failed'] += test_data.get('failures', 0)
                    aggregated_results['summary']['total_errors'] += test_data.get('errors', 0)
                    
        except Exception as e:
            print(f"Error processing {result_file}: {e}")
    
    # Calculate success rate
    total_tests = aggregated_results['summary']['total_tests']
    if total_tests > 0:
        total_passed = aggregated_results['summary']['total_passed']
        aggregated_results['summary']['success_rate'] = (total_passed / total_tests) * 100
    
    # Save aggregated report
    output_file = f"aggregated_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(aggregated_results, f, indent=2)
    
    print(f"📄 Aggregated results saved to: {output_file}")
    print(f"📊 Summary: {total_tests} tests, {aggregated_results['summary']['success_rate']:.1f}% success rate")
    
    return output_file

def main():
    """Main aggregation function"""
    print("🎯 Test Result Aggregator")
    print("=" * 40)
    
    # Change to repository root
    os.chdir('/home/runner/work/Jarvis-1.0.0/Jarvis-1.0.0')
    
    aggregate_test_results()
    
    print("✅ Test aggregation completed")

if __name__ == "__main__":
    main()