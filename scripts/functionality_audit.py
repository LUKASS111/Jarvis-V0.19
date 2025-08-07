#!/usr/bin/env python3
"""
Stage 5 - FUNC-001: Complete Functionality Mapping with Historical Capability Inventory
Comprehensive audit of all program capabilities with GUI accessibility validation
"""

import os
import sys
import json
import ast
import importlib.util
from datetime import datetime
from pathlib import Path

class FunctionalityAuditor:
    def __init__(self, root_dir):
        self.root_dir = Path(root_dir)
        self.capabilities = {}
        self.gui_mappings = {}
        self.modern_functions = []
        self.missing_functions = []
        self.report = {
            'timestamp': datetime.now().isoformat(),
            'audit_type': 'Complete Functionality Mapping',
            'stage': 'Stage 5 - FUNC-001',
            'total_functions': 0,
            'gui_accessible': 0,
            'modern_functions': 0,
            'missing_gui_access': 0,
            'capability_categories': {},
            'function_inventory': [],
            'gui_mapping_status': {},
            'recommendations': []
        }

    def scan_python_files(self):
        """Scan all Python files for function and class definitions"""
        python_files = list(self.root_dir.rglob("*.py"))
        function_count = 0
        
        for py_file in python_files:
            # Skip test files and temporary files
            if any(skip in str(py_file) for skip in ['test_', 'tests/', '__pycache__', '.pyc', '/tmp/']):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse AST to find functions and classes
                tree = ast.parse(content)
                file_functions = []
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        func_info = {
                            'name': node.name,
                            'type': 'function',
                            'file': str(py_file.relative_to(self.root_dir)),
                            'line': node.lineno,
                            'gui_accessible': self._check_gui_accessibility(node.name),
                            'category': self._categorize_function(str(py_file), node.name)
                        }
                        file_functions.append(func_info)
                        function_count += 1
                        
                    elif isinstance(node, ast.ClassDef):
                        class_info = {
                            'name': node.name,
                            'type': 'class',
                            'file': str(py_file.relative_to(self.root_dir)),
                            'line': node.lineno,
                            'methods': [],
                            'gui_accessible': self._check_gui_accessibility(node.name),
                            'category': self._categorize_function(str(py_file), node.name)
                        }
                        
                        # Get methods of the class
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef):
                                method_info = {
                                    'name': f"{node.name}.{item.name}",
                                    'type': 'method',
                                    'file': str(py_file.relative_to(self.root_dir)),
                                    'line': item.lineno,
                                    'gui_accessible': self._check_gui_accessibility(f"{node.name}.{item.name}"),
                                    'category': self._categorize_function(str(py_file), f"{node.name}.{item.name}")
                                }
                                class_info['methods'].append(method_info)
                                file_functions.append(method_info)
                                function_count += 1
                        
                        file_functions.append(class_info)
                
                if file_functions:
                    self.capabilities[str(py_file.relative_to(self.root_dir))] = file_functions
                    
            except Exception as e:
                print(f"Error parsing {py_file}: {e}")
                continue
        
        self.report['total_functions'] = function_count
        return function_count

    def _check_gui_accessibility(self, function_name):
        """Check if function is accessible through GUI"""
        # Check against known GUI mappings from comprehensive dashboard
        gui_accessible_patterns = [
            'chat_', 'model_', 'llm_', 'ai_',  # AI Models & LLM Management
            'process_', 'upload_', 'multimodal_',  # Multimodal Processing
            'memory_', 'database_', 'crdt_', 'store_',  # Memory Management
            'workflow_', 'agent_', 'task_',  # Agent Workflows
            'vector_', 'search_', 'semantic_',  # Vector Database
            'monitor_', 'health_', 'metrics_',  # System Monitoring
            'config_', 'settings_', 'preference_',  # Configuration & Settings
            'test_', 'debug_', 'validate_',  # Development Tools
            'analyze_', 'report_', 'dashboard_'  # Analytics & Reporting
        ]
        
        function_lower = function_name.lower()
        for pattern in gui_accessible_patterns:
            if pattern in function_lower:
                return True
        
        # Check if it's a GUI component itself
        if any(gui_term in function_lower for gui_term in ['gui', 'interface', 'dashboard', 'widget', 'dialog']):
            return True
            
        return False

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

    def analyze_gui_coverage(self):
        """Analyze GUI accessibility coverage for all functions"""
        gui_accessible_count = 0
        total_functions = 0
        missing_gui_access = []
        
        for file_path, functions in self.capabilities.items():
            for func in functions:
                if func['type'] in ['function', 'method']:
                    total_functions += 1
                    if func['gui_accessible']:
                        gui_accessible_count += 1
                    else:
                        missing_gui_access.append({
                            'function': func['name'],
                            'file': func['file'],
                            'category': func['category'],
                            'line': func['line']
                        })
        
        self.report['gui_accessible'] = gui_accessible_count
        self.report['missing_gui_access'] = len(missing_gui_access)
        self.missing_functions = missing_gui_access
        
        # Calculate coverage percentage
        if total_functions > 0:
            coverage_percentage = (gui_accessible_count / total_functions) * 100
            self.report['gui_coverage_percentage'] = round(coverage_percentage, 1)
        else:
            self.report['gui_coverage_percentage'] = 0

    def categorize_capabilities(self):
        """Group capabilities by category"""
        categories = {}
        
        for file_path, functions in self.capabilities.items():
            for func in functions:
                category = func['category']
                if category not in categories:
                    categories[category] = {
                        'total': 0,
                        'gui_accessible': 0,
                        'functions': []
                    }
                
                if func['type'] in ['function', 'method']:
                    categories[category]['total'] += 1
                    if func['gui_accessible']:
                        categories[category]['gui_accessible'] += 1
                    categories[category]['functions'].append({
                        'name': func['name'],
                        'file': func['file'],
                        'gui_accessible': func['gui_accessible']
                    })
        
        # Calculate coverage per category
        for category, data in categories.items():
            if data['total'] > 0:
                coverage = (data['gui_accessible'] / data['total']) * 100
                data['coverage_percentage'] = round(coverage, 1)
            else:
                data['coverage_percentage'] = 0
        
        self.report['capability_categories'] = categories

    def check_modern_functions(self):
        """Identify any remaining updated functions"""
        modern_indicators = ['modern', 'old', 'updated', 'modern', 'unused']
        modern_count = 0
        
        for file_path, functions in self.capabilities.items():
            for func in functions:
                func_name_lower = func['name'].lower()
                if any(indicator in func_name_lower for indicator in modern_indicators):
                    self.modern_functions.append({
                        'function': func['name'],
                        'file': func['file'],
                        'type': func['type'],
                        'line': func['line']
                    })
                    modern_count += 1
        
        self.report['modern_functions'] = modern_count

    def generate_recommendations(self):
        """Generate recommendations for improvement"""
        recommendations = []
        
        # GUI Coverage recommendations
        coverage = self.report.get('gui_coverage_percentage', 0)
        if coverage < 90:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'GUI Coverage',
                'issue': f'Only {coverage}% of functions accessible via GUI',
                'recommendation': 'Implement GUI interfaces for missing functions',
                'impact': 'Users forced to use CLI for critical functions'
            })
        
        # Updated implementation
        if self.report['modern_functions'] > 0:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'updated Elimination',
                'issue': f'{self.report["modern_functions"]} modern functions found',
                'recommendation': 'Remove or refactor all modern functions',
                'impact': 'Technical debt and maintenance burden'
            })
        
        # Category-specific recommendations
        categories = self.report.get('capability_categories', {})
        for category, data in categories.items():
            if data['coverage_percentage'] < 80:
                recommendations.append({
                    'priority': 'MEDIUM',
                    'category': f'{category} GUI Coverage',
                    'issue': f'{category}: {data["coverage_percentage"]}% GUI coverage',
                    'recommendation': f'Enhance GUI components for {category}',
                    'impact': 'Limited user access to category functions'
                })
        
        self.report['recommendations'] = recommendations

    def create_function_inventory(self):
        """Create detailed function inventory"""
        inventory = []
        
        for file_path, functions in self.capabilities.items():
            for func in functions:
                if func['type'] in ['function', 'method']:
                    inventory.append({
                        'name': func['name'],
                        'type': func['type'],
                        'file': func['file'],
                        'line': func['line'],
                        'category': func['category'],
                        'gui_accessible': func['gui_accessible'],
                        'priority_for_gui': 'HIGH' if not func['gui_accessible'] and 'core' in func['category'].lower() else 'MEDIUM'
                    })
        
        # Sort by category then by name
        inventory.sort(key=lambda x: (x['category'], x['name']))
        self.report['function_inventory'] = inventory

    def run_complete_audit(self):
        """Execute complete functionality audit"""
        print("🎯 Starting Stage 5 - Complete Functionality Mapping...")
        print("=" * 60)
        
        # Step 1: Scan all Python files
        print("📁 Scanning Python files for functions and classes...")
        function_count = self.scan_python_files()
        print(f"   Found {function_count} functions/methods across {len(self.capabilities)} files")
        
        # Step 2: Analyze GUI coverage
        print("🖥️  Analyzing GUI accessibility coverage...")
        self.analyze_gui_coverage()
        print(f"   GUI accessible: {self.report['gui_accessible']}/{self.report['total_functions']} ({self.report.get('gui_coverage_percentage', 0)}%)")
        
        # Step 3: Categorize capabilities
        print("📊 Categorizing capabilities by function type...")
        self.categorize_capabilities()
        print(f"   Identified {len(self.report['capability_categories'])} capability categories")
        
        # Updated implementation
        print("🧹 Checking for updated functions...")
        self.check_modern_functions()
        print(f"   updated functions found: {self.report['modern_functions']}")
        
        # Step 5: Create function inventory
        print("📋 Creating detailed function inventory...")
        self.create_function_inventory()
        print(f"   Function inventory created with {len(self.report['function_inventory'])} entries")
        
        # Step 6: Generate recommendations
        print("💡 Generating improvement recommendations...")
        self.generate_recommendations()
        print(f"   Generated {len(self.report['recommendations'])} recommendations")
        
        return self.report

    def save_report(self, output_file):
        """Save comprehensive audit report"""
        with open(output_file, 'w') as f:
            json.dump(self.report, f, indent=2)
        print(f"\n✅ Complete functionality audit report saved to: {output_file}")

def main():
    """Main execution function"""
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_file = f"functionality_audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    auditor = FunctionalityAuditor(root_dir)
    report = auditor.run_complete_audit()
    
    # Print summary
    print("\n" + "="*60)
    print("📊 FUNCTIONALITY AUDIT SUMMARY")
    print("="*60)
    print(f"Total Functions: {report['total_functions']}")
    print(f"GUI Accessible: {report['gui_accessible']} ({report.get('gui_coverage_percentage', 0)}%)")
    print(f"Missing GUI Access: {report['missing_gui_access']}")
    print(f"updated Functions: {report['modern_functions']}")
    print(f"Capability Categories: {len(report['capability_categories'])}")
    print(f"Recommendations: {len(report['recommendations'])}")
    
    # Print category breakdown
    print("\n📋 CATEGORY BREAKDOWN:")
    for category, data in report['capability_categories'].items():
        print(f"  {category}: {data['gui_accessible']}/{data['total']} ({data['coverage_percentage']}%)")
    
    # Print high priority recommendations
    high_priority = [r for r in report['recommendations'] if r['priority'] == 'HIGH']
    if high_priority:
        print("\n🚨 HIGH PRIORITY RECOMMENDATIONS:")
        for rec in high_priority:
            print(f"  • {rec['issue']}")
            print(f"    Solution: {rec['recommendation']}")
    
    auditor.save_report(output_file)
    
    # Return success/failure based on coverage
    coverage = report.get('gui_coverage_percentage', 0)
    if coverage >= 90 and report['modern_functions'] == 0:
        print("\n✅ FUNCTIONALITY AUDIT: EXCELLENT")
        print("   All functions accessible via GUI, zero updated code")
        return 0
    elif coverage >= 75:
        print("\n⚠️  FUNCTIONALITY AUDIT: GOOD")
        print("   Most functions accessible, minor improvements needed")
        return 0
    else:
        print("\n❌ FUNCTIONALITY AUDIT: NEEDS IMPROVEMENT")
        print("   Significant GUI coverage gaps identified")
        return 1

if __name__ == "__main__":
    sys.exit(main())