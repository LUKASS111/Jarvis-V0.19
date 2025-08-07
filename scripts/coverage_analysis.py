#!/usr/bin/env python3
"""
Stage 5 - FUNC-004: Coverage Analysis
Test coverage assessment for all capabilities including GUI
"""

import os
import sys
import json
import subprocess
import ast
from datetime import datetime
from pathlib import Path

class CoverageAnalyzer:
    def __init__(self, root_dir):
        self.root_dir = Path(root_dir)
        self.coverage_report = {
            'timestamp': datetime.now().isoformat(),
            'analysis_type': 'Comprehensive Test Coverage Analysis',
            'stage': 'Stage 5 - FUNC-004',
            'total_functions': 0,
            'tested_functions': 0,
            'coverage_percentage': 0,
            'gui_coverage': 0,
            'uncovered_functions': [],
            'test_files_found': 0,
            'coverage_by_category': {},
            'recommendations': []
        }

    def discover_test_files(self):
        """Discover all test files in the repository"""
        test_patterns = ['test_*.py', '*_test.py', 'tests/*.py']
        test_files = []
        
        for pattern in test_patterns:
            test_files.extend(list(self.root_dir.rglob(pattern)))
        
        # Also check for dedicated test directories
        test_dirs = ['tests', 'test', 'testing']
        for test_dir in test_dirs:
            test_path = self.root_dir / test_dir
            if test_path.exists():
                test_files.extend(list(test_path.rglob("*.py")))
        
        # Remove duplicates and filter out __pycache__
        unique_test_files = []
        seen = set()
        for test_file in test_files:
            if '__pycache__' not in str(test_file) and str(test_file) not in seen:
                unique_test_files.append(test_file)
                seen.add(str(test_file))
        
        self.coverage_report['test_files_found'] = len(unique_test_files)
        return unique_test_files

    def analyze_function_coverage(self):
        """Analyze test coverage for all functions"""
        # Discover all functions in the codebase
        all_functions = self._discover_all_functions()
        tested_functions = self._discover_tested_functions()
        
        self.coverage_report['total_functions'] = len(all_functions)
        self.coverage_report['tested_functions'] = len(tested_functions)
        
        if len(all_functions) > 0:
            coverage_percentage = (len(tested_functions) / len(all_functions)) * 100
            self.coverage_report['coverage_percentage'] = round(coverage_percentage, 1)
        
        # Find uncovered functions
        uncovered = []
        for func in all_functions:
            if func['name'] not in tested_functions:
                uncovered.append({
                    'function': func['name'],
                    'file': func['file'],
                    'category': func['category'],
                    'line': func['line'],
                    'priority': self._determine_test_priority(func)
                })
        
        self.coverage_report['uncovered_functions'] = uncovered
        return all_functions, tested_functions

    def _discover_all_functions(self):
        """Discover all functions in the codebase"""
        functions = []
        python_files = list(self.root_dir.rglob("*.py"))
        
        for py_file in python_files:
            # Skip test files and cache
            if any(skip in str(py_file) for skip in ['test_', '__pycache__', '.pyc', '/tmp/']):
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Skip private functions and special methods
                        if not node.name.startswith('_'):
                            functions.append({
                                'name': node.name,
                                'file': str(py_file.relative_to(self.root_dir)),
                                'line': node.lineno,
                                'category': self._categorize_function(str(py_file), node.name)
                            })
                    elif isinstance(node, ast.ClassDef):
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef) and not item.name.startswith('_'):
                                functions.append({
                                    'name': f"{node.name}.{item.name}",
                                    'file': str(py_file.relative_to(self.root_dir)),
                                    'line': item.lineno,
                                    'category': self._categorize_function(str(py_file), f"{node.name}.{item.name}")
                                })
            
            except Exception as e:
                continue
        
        return functions

    def _discover_tested_functions(self):
        """Discover functions that have tests"""
        tested_functions = set()
        test_files = self.discover_test_files()
        
        for test_file in test_files:
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Look for test function patterns
                import re
                
                # Find test functions
                test_function_pattern = r'def\s+test_(\w+)'
                test_matches = re.findall(test_function_pattern, content)
                
                for match in test_matches:
                    tested_functions.add(match)
                
                # Look for function calls in tests
                function_call_pattern = r'(\w+)\s*\('
                call_matches = re.findall(function_call_pattern, content)
                
                for match in call_matches:
                    if not match.startswith(('test_', 'assert', 'print', 'self')):
                        tested_functions.add(match)
                
            except Exception as e:
                continue
        
        return tested_functions

    def _categorize_function(self, file_path, function_name):
        """Categorize function based on file path and name"""
        file_path_lower = file_path.lower()
        function_lower = function_name.lower()
        
        if 'gui' in file_path_lower or 'interface' in file_path_lower:
            return 'GUI Components'
        elif any(term in file_path_lower for term in ['ai', 'llm', 'model', 'chat']):
            return 'AI Models & LLM Management'
        elif any(term in file_path_lower for term in ['multimodal', 'process', 'upload']):
            return 'Multimodal Processing'
        elif any(term in file_path_lower for term in ['memory', 'database', 'crdt', 'storage']):
            return 'Memory Management'
        elif any(term in file_path_lower for term in ['workflow', 'agent', 'task']):
            return 'Agent Workflows'
        elif any(term in file_path_lower for term in ['vector', 'search', 'semantic']):
            return 'Vector Database'
        elif any(term in file_path_lower for term in ['monitor', 'health', 'metrics']):
            return 'System Monitoring'
        elif any(term in file_path_lower for term in ['config', 'settings', 'preference']):
            return 'Configuration & Settings'
        elif any(term in file_path_lower for term in ['test', 'debug', 'validate']):
            return 'Development Tools'
        elif any(term in file_path_lower for term in ['analyze', 'report', 'dashboard']):
            return 'Analytics & Reporting'
        else:
            return 'Core System'

    def _determine_test_priority(self, func):
        """Determine testing priority for a function"""
        high_priority_categories = [
            'AI Models & LLM Management', 'Memory Management', 'Core System'
        ]
        medium_priority_categories = [
            'Multimodal Processing', 'Agent Workflows', 'Vector Database'
        ]
        
        if func['category'] in high_priority_categories:
            return 'HIGH'
        elif func['category'] in medium_priority_categories:
            return 'MEDIUM'
        else:
            return 'LOW'

    def analyze_gui_test_coverage(self):
        """Specifically analyze GUI component test coverage"""
        gui_functions = [f for f in self._discover_all_functions() 
                        if f['category'] == 'GUI Components']
        
        gui_tested = 0
        gui_test_files = []
        
        # Look for GUI-specific test files
        test_files = self.discover_test_files()
        for test_file in test_files:
            if 'gui' in str(test_file).lower() or 'interface' in str(test_file).lower():
                gui_test_files.append(test_file)
        
        # Check if GUI functions are tested
        for gui_func in gui_functions:
            if self._is_function_tested(gui_func['name'], gui_test_files):
                gui_tested += 1
        
        if len(gui_functions) > 0:
            gui_coverage = (gui_tested / len(gui_functions)) * 100
            self.coverage_report['gui_coverage'] = round(gui_coverage, 1)
        else:
            self.coverage_report['gui_coverage'] = 100  # No GUI functions to test
        
        self.coverage_report['gui_functions_total'] = len(gui_functions)
        self.coverage_report['gui_functions_tested'] = gui_tested
        self.coverage_report['gui_test_files'] = len(gui_test_files)

    def _is_function_tested(self, function_name, test_files):
        """Check if a specific function is tested"""
        for test_file in test_files:
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if function_name in content:
                        return True
            except:
                continue
        return False

    def analyze_coverage_by_category(self):
        """Analyze test coverage by function category"""
        all_functions = self._discover_all_functions()
        tested_functions = self._discover_tested_functions()
        
        category_stats = {}
        
        for func in all_functions:
            category = func['category']
            if category not in category_stats:
                category_stats[category] = {
                    'total': 0,
                    'tested': 0,
                    'coverage_percentage': 0
                }
            
            category_stats[category]['total'] += 1
            if func['name'] in tested_functions:
                category_stats[category]['tested'] += 1
        
        # Calculate coverage percentages
        for category, stats in category_stats.items():
            if stats['total'] > 0:
                coverage = (stats['tested'] / stats['total']) * 100
                stats['coverage_percentage'] = round(coverage, 1)
        
        self.coverage_report['coverage_by_category'] = category_stats

    def run_pytest_coverage(self):
        """Run pytest with coverage if available"""
        try:
            # Check if pytest and coverage are available
            result = subprocess.run(['python', '-m', 'pytest', '--version'], 
                                   capture_output=True, text=True, cwd=self.root_dir)
            
            if result.returncode == 0:
                # Run pytest with coverage
                coverage_result = subprocess.run([
                    'python', '-m', 'pytest', '--cov=.', '--cov-report=json',
                    '--cov-report=term-missing', '-v'
                ], capture_output=True, text=True, cwd=self.root_dir, timeout=300)
                
                self.coverage_report['pytest_available'] = True
                self.coverage_report['pytest_output'] = coverage_result.stdout
                
                # Try to read coverage.json if it exists
                coverage_json_path = self.root_dir / 'coverage.json'
                if coverage_json_path.exists():
                    with open(coverage_json_path, 'r') as f:
                        coverage_data = json.load(f)
                        self.coverage_report['detailed_coverage'] = coverage_data
                
                return True
            else:
                self.coverage_report['pytest_available'] = False
                return False
                
        except Exception as e:
            self.coverage_report['pytest_available'] = False
            self.coverage_report['pytest_error'] = str(e)
            return False

    def generate_coverage_recommendations(self):
        """Generate recommendations for improving test coverage"""
        recommendations = []
        
        # Overall coverage
        coverage_percentage = self.coverage_report.get('coverage_percentage', 0)
        if coverage_percentage < 80:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Overall Coverage',
                'issue': f'Test coverage only {coverage_percentage}%',
                'recommendation': 'Increase test coverage to at least 80%',
                'impact': 'Insufficient testing may lead to undetected bugs'
            })
        
        # GUI coverage
        gui_coverage = self.coverage_report.get('gui_coverage', 0)
        if gui_coverage < 70:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'GUI Testing',
                'issue': f'GUI test coverage only {gui_coverage}%',
                'recommendation': 'Implement comprehensive GUI testing suite',
                'impact': 'User interface issues may go undetected'
            })
        
        # Category-specific recommendations
        category_coverage = self.coverage_report.get('coverage_by_category', {})
        for category, stats in category_coverage.items():
            if stats['coverage_percentage'] < 60:
                recommendations.append({
                    'priority': 'MEDIUM',
                    'category': f'{category} Testing',
                    'issue': f'{category}: {stats["coverage_percentage"]}% coverage',
                    'recommendation': f'Add comprehensive tests for {category}',
                    'impact': f'Critical {category.lower()} functionality undertested'
                })
        
        # High priority uncovered functions
        uncovered = self.coverage_report.get('uncovered_functions', [])
        high_priority_uncovered = [f for f in uncovered if f['priority'] == 'HIGH']
        
        if high_priority_uncovered:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Critical Function Testing',
                'issue': f'{len(high_priority_uncovered)} high-priority functions untested',
                'recommendation': 'Create tests for all high-priority functions',
                'impact': 'Core functionality may have undetected issues',
                'functions': [f['function'] for f in high_priority_uncovered[:10]]
            })
        
        self.coverage_report['recommendations'] = recommendations

    def run_comprehensive_coverage_analysis(self):
        """Execute comprehensive coverage analysis"""
        print("📊 Starting Stage 5 - Coverage Analysis...")
        print("=" * 60)
        
        # Step 1: Discover test files
        print("🔍 Discovering test files...")
        test_files = self.discover_test_files()
        print(f"   Found {len(test_files)} test files")
        
        # Step 2: Analyze function coverage
        print("📝 Analyzing function test coverage...")
        all_functions, tested_functions = self.analyze_function_coverage()
        coverage = self.coverage_report.get('coverage_percentage', 0)
        print(f"   Overall coverage: {coverage}% ({len(tested_functions)}/{len(all_functions)})")
        
        # Step 3: Analyze GUI coverage
        print("🖥️  Analyzing GUI test coverage...")
        self.analyze_gui_test_coverage()
        gui_coverage = self.coverage_report.get('gui_coverage', 0)
        print(f"   GUI coverage: {gui_coverage}%")
        
        # Step 4: Analyze by category
        print("📋 Analyzing coverage by category...")
        self.analyze_coverage_by_category()
        categories = len(self.coverage_report.get('coverage_by_category', {}))
        print(f"   Analyzed {categories} function categories")
        
        # Step 5: Run pytest coverage if available
        print("🧪 Running pytest coverage analysis...")
        pytest_success = self.run_pytest_coverage()
        if pytest_success:
            print("   Pytest coverage analysis completed")
        else:
            print("   Pytest not available, using manual analysis")
        
        # Step 6: Generate recommendations
        print("💡 Generating coverage improvement recommendations...")
        self.generate_coverage_recommendations()
        print(f"   Generated {len(self.coverage_report['recommendations'])} recommendations")
        
        return self.coverage_report

    def save_report(self, output_file):
        """Save coverage analysis report"""
        with open(output_file, 'w') as f:
            json.dump(self.coverage_report, f, indent=2)
        print(f"\n✅ Coverage analysis report saved to: {output_file}")

def main():
    """Main execution function"""
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_file = f"coverage_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    analyzer = CoverageAnalyzer(root_dir)
    report = analyzer.run_comprehensive_coverage_analysis()
    
    # Print summary
    print("\n" + "="*60)
    print("📊 COVERAGE ANALYSIS SUMMARY")
    print("="*60)
    print(f"Total Functions: {report['total_functions']}")
    print(f"Tested Functions: {report['tested_functions']}")
    print(f"Overall Coverage: {report.get('coverage_percentage', 0)}%")
    print(f"GUI Coverage: {report.get('gui_coverage', 0)}%")
    print(f"Test Files Found: {report['test_files_found']}")
    print(f"Uncovered Functions: {len(report.get('uncovered_functions', []))}")
    
    # Print category breakdown
    category_coverage = report.get('coverage_by_category', {})
    if category_coverage:
        print(f"\n📋 COVERAGE BY CATEGORY:")
        for category, stats in category_coverage.items():
            print(f"  {category}: {stats['tested']}/{stats['total']} ({stats['coverage_percentage']}%)")
    
    # Print high priority recommendations
    recommendations = report.get('recommendations', [])
    high_priority = [r for r in recommendations if r['priority'] == 'HIGH']
    if high_priority:
        print(f"\n🚨 HIGH PRIORITY RECOMMENDATIONS:")
        for rec in high_priority:
            print(f"  • {rec['issue']}")
            print(f"    Action: {rec['recommendation']}")
    
    analyzer.save_report(output_file)
    
    # Return status based on coverage
    overall_coverage = report.get('coverage_percentage', 0)
    gui_coverage = report.get('gui_coverage', 0)
    
    if overall_coverage >= 80 and gui_coverage >= 70:
        print("\n✅ COVERAGE ANALYSIS: EXCELLENT")
        print("   Comprehensive test coverage achieved")
        return 0
    elif overall_coverage >= 60 and gui_coverage >= 50:
        print("\n⚠️  COVERAGE ANALYSIS: GOOD")
        print("   Adequate coverage, improvements recommended")
        return 0
    else:
        print("\n❌ COVERAGE ANALYSIS: INSUFFICIENT")
        print("   Significant test coverage gaps identified")
        return 1

if __name__ == "__main__":
    sys.exit(main())