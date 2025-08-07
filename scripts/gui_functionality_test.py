#!/usr/bin/env python3
"""
Stage 5 - GUI-010: GUI Functionality Testing
Verify every program capability accessible via GUI interface
"""

import os
import sys
import json
import importlib.util
from datetime import datetime
from pathlib import Path

class GUIFunctionalityTester:
    def __init__(self, root_dir):
        self.root_dir = Path(root_dir)
        self.gui_components = {}
        self.accessibility_report = {
            'timestamp': datetime.now().isoformat(),
            'test_type': 'GUI Functionality Accessibility Test',
            'stage': 'Stage 5 - GUI-010',
            'total_functions_tested': 0,
            'gui_accessible_verified': 0,
            'gui_missing': 0,
            'gui_components_found': 0,
            'dashboard_tabs': {},
            'accessibility_score': 0,
            'test_results': [],
            'missing_gui_functions': [],
            'recommendations': []
        }

    def scan_gui_components(self):
        """Scan for existing GUI components and interfaces"""
        gui_dirs = ['gui', 'interface', 'frontend', 'ui']
        gui_files = []
        
        for gui_dir in gui_dirs:
            gui_path = self.root_dir / gui_dir
            if gui_path.exists():
                for py_file in gui_path.rglob("*.py"):
                    if not any(skip in str(py_file) for skip in ['__pycache__', '.pyc', 'test_']):
                        gui_files.append(py_file)
        
        self.accessibility_report['gui_components_found'] = len(gui_files)
        return gui_files

    def analyze_comprehensive_dashboard(self):
        """Analyze the comprehensive dashboard implementation"""
        dashboard_file = self.root_dir / 'gui' / 'enhanced' / 'comprehensive_dashboard.py'
        
        if not dashboard_file.exists():
            self.accessibility_report['dashboard_status'] = 'NOT_FOUND'
            return False
        
        try:
            with open(dashboard_file, 'r', encoding='utf-8') as f:
                dashboard_content = f.read()
            
            # Expected tabs based on Stage 4 architecture
            expected_tabs = {
                'AI Models & LLM Management': ['model_selection', 'chat_interface', 'llm_config'],
                'Multimodal Processing': ['file_upload', 'processing_controls', 'results_display'],
                'Memory Management': ['database_browser', 'crdt_operations', 'data_visualization'],
                'Agent Workflows': ['workflow_designer', 'execution_monitoring', 'task_management'],
                'Vector Database': ['semantic_search', 'collection_management', 'vector_operations'],
                'System Monitoring': ['dashboards', 'performance_metrics', 'health_status'],
                'Configuration & Settings': ['user_preferences', 'system_settings', 'customization'],
                'Development Tools': ['testing_interface', 'debugging_tools', 'quality_assurance'],
                'Analytics & Reporting': ['data_visualization', 'report_generation', 'analytics_dashboard']
            }
            
            tabs_implemented = {}
            for tab_name, components in expected_tabs.items():
                tab_found = any(comp.lower().replace('_', '') in dashboard_content.lower().replace('_', '') 
                               for comp in components)
                tabs_implemented[tab_name] = {
                    'implemented': tab_found,
                    'expected_components': components,
                    'coverage': 'PARTIAL' if tab_found else 'MISSING'
                }
            
            self.accessibility_report['dashboard_tabs'] = tabs_implemented
            self.accessibility_report['dashboard_status'] = 'FOUND'
            
            # Calculate dashboard completeness
            implemented_count = sum(1 for tab in tabs_implemented.values() if tab['implemented'])
            dashboard_completeness = (implemented_count / len(expected_tabs)) * 100
            self.accessibility_report['dashboard_completeness'] = round(dashboard_completeness, 1)
            
            return True
            
        except Exception as e:
            self.accessibility_report['dashboard_status'] = f'ERROR: {str(e)}'
            return False

    def test_function_gui_accessibility(self):
        """Test accessibility of core functions through GUI"""
        # Core function categories that must be GUI accessible
        critical_functions = {
            'AI & LLM Functions': [
                'chat_completion', 'model_selection', 'llm_configuration',
                'ai_response_generation', 'model_switching', 'chat_history'
            ],
            'Multimodal Processing': [
                'file_upload', 'image_processing', 'document_analysis',
                'audio_processing', 'video_analysis', 'data_extraction'
            ],
            'Memory Management': [
                'database_operations', 'memory_storage', 'data_retrieval',
                'crdt_sync', 'backup_restore', 'data_management'
            ],
            'System Operations': [
                'system_monitoring', 'health_check', 'performance_metrics',
                'configuration_management', 'user_settings', 'preferences'
            ],
            'Workflow Management': [
                'workflow_creation', 'task_execution', 'agent_management',
                'automation_setup', 'process_monitoring', 'workflow_editing'
            ]
        }
        
        accessibility_results = {}
        total_tested = 0
        accessible_count = 0
        
        for category, functions in critical_functions.items():
            category_results = []
            for func in functions:
                total_tested += 1
                # Check if function has GUI interface
                gui_accessible = self._check_function_gui_access(func)
                
                result = {
                    'function': func,
                    'gui_accessible': gui_accessible,
                    'access_method': self._identify_access_method(func) if gui_accessible else 'CLI_ONLY',
                    'priority': 'HIGH' if not gui_accessible else 'SATISFIED'
                }
                
                category_results.append(result)
                if gui_accessible:
                    accessible_count += 1
                else:
                    self.accessibility_report['missing_gui_functions'].append({
                        'function': func,
                        'category': category,
                        'impact': 'User forced to use CLI or technical interface'
                    })
            
            accessibility_results[category] = {
                'functions': category_results,
                'accessible_count': sum(1 for r in category_results if r['gui_accessible']),
                'total_functions': len(category_results),
                'coverage_percentage': round((sum(1 for r in category_results if r['gui_accessible']) / len(category_results)) * 100, 1)
            }
        
        self.accessibility_report['function_accessibility'] = accessibility_results
        self.accessibility_report['total_functions_tested'] = total_tested
        self.accessibility_report['gui_accessible_verified'] = accessible_count
        self.accessibility_report['gui_missing'] = total_tested - accessible_count
        
        # Calculate overall accessibility score
        if total_tested > 0:
            accessibility_score = (accessible_count / total_tested) * 100
            self.accessibility_report['accessibility_score'] = round(accessibility_score, 1)

    def _check_function_gui_access(self, function_name):
        """Check if a function has GUI access method"""
        # Look for GUI implementations in the codebase
        gui_patterns = [
            f"def {function_name}",
            f"class.*{function_name.title()}",
            f"{function_name}_gui",
            f"{function_name}_interface",
            f"gui_{function_name}",
            f"interface_{function_name}"
        ]
        
        # Check GUI directories for implementations
        gui_dirs = [self.root_dir / 'gui', self.root_dir / 'interface']
        
        for gui_dir in gui_dirs:
            if gui_dir.exists():
                for py_file in gui_dir.rglob("*.py"):
                    try:
                        with open(py_file, 'r', encoding='utf-8') as f:
                            content = f.read().lower()
                            if any(pattern.lower() in content for pattern in gui_patterns):
                                return True
                    except:
                        continue
        
        # Check main GUI files
        main_gui_files = [
            'main.py', 'app.py', 'interface.py', 'dashboard.py'
        ]
        
        for gui_file in main_gui_files:
            gui_path = self.root_dir / gui_file
            if gui_path.exists():
                try:
                    with open(gui_path, 'r', encoding='utf-8') as f:
                        content = f.read().lower()
                        if function_name.lower() in content:
                            return True
                except:
                    continue
        
        return False

    def _identify_access_method(self, function_name):
        """Identify how function is accessed through GUI"""
        access_methods = {
            'chat_': 'Chat Interface Tab',
            'model_': 'AI Models Tab',
            'file_': 'Multimodal Processing Tab',
            'upload_': 'File Upload Interface',
            'database_': 'Memory Management Tab',
            'memory_': 'Memory Management Tab',
            'workflow_': 'Workflow Designer Tab',
            'agent_': 'Agent Management Tab',
            'monitor_': 'System Monitoring Tab',
            'config_': 'Configuration Tab',
            'setting_': 'Settings Interface'
        }
        
        for pattern, method in access_methods.items():
            if function_name.lower().startswith(pattern):
                return method
        
        return 'Dashboard Interface'

    def test_user_experience_flows(self):
        """Test common user workflow accessibility"""
        user_flows = {
            'New User Onboarding': [
                'system_setup', 'initial_configuration', 'tutorial_access',
                'help_system', 'getting_started_guide'
            ],
            'Daily Operations': [
                'chat_interaction', 'file_processing', 'data_query',
                'workflow_execution', 'system_monitoring'
            ],
            'Advanced Features': [
                'custom_workflows', 'agent_configuration', 'advanced_settings',
                'system_optimization', 'debugging_tools'
            ],
            'Data Management': [
                'data_import', 'backup_creation', 'data_export',
                'database_management', 'storage_optimization'
            ]
        }
        
        flow_results = {}
        for flow_name, steps in user_flows.items():
            accessible_steps = sum(1 for step in steps if self._check_function_gui_access(step))
            flow_results[flow_name] = {
                'total_steps': len(steps),
                'gui_accessible_steps': accessible_steps,
                'coverage_percentage': round((accessible_steps / len(steps)) * 100, 1),
                'user_experience': 'EXCELLENT' if accessible_steps == len(steps) else 
                                 'GOOD' if accessible_steps >= len(steps) * 0.8 else 'POOR'
            }
        
        self.accessibility_report['user_flow_analysis'] = flow_results

    def generate_accessibility_recommendations(self):
        """Generate recommendations for improving GUI accessibility"""
        recommendations = []
        
        # Dashboard completeness
        dashboard_completeness = self.accessibility_report.get('dashboard_completeness', 0)
        if dashboard_completeness < 100:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Dashboard Implementation',
                'issue': f'Dashboard only {dashboard_completeness}% complete',
                'recommendation': 'Implement missing dashboard tabs and components',
                'impact': 'Users cannot access all program functions through GUI'
            })
        
        # Function accessibility
        accessibility_score = self.accessibility_report.get('accessibility_score', 0)
        if accessibility_score < 90:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Function Accessibility',
                'issue': f'Only {accessibility_score}% of functions GUI accessible',
                'recommendation': 'Create GUI interfaces for missing functions',
                'impact': 'Users forced to use CLI for critical operations'
            })
        
        # Missing functions
        missing_count = self.accessibility_report.get('gui_missing', 0)
        if missing_count > 0:
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'GUI Coverage',
                'issue': f'{missing_count} functions lack GUI access',
                'recommendation': 'Implement GUI controls for each missing function',
                'impact': 'Reduced user experience and accessibility'
            })
        
        # User flow accessibility
        flow_analysis = self.accessibility_report.get('user_flow_analysis', {})
        poor_flows = [name for name, data in flow_analysis.items() if data.get('user_experience') == 'POOR']
        if poor_flows:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'User Experience',
                'issue': f'Poor GUI coverage for: {", ".join(poor_flows)}',
                'recommendation': 'Enhance GUI workflows for critical user journeys',
                'impact': 'Difficult user experience for essential operations'
            })
        
        self.accessibility_report['recommendations'] = recommendations

    def run_comprehensive_test(self):
        """Execute complete GUI functionality test"""
        print("🖥️  Starting Stage 5 - GUI Functionality Testing...")
        print("=" * 60)
        
        # Step 1: Scan GUI components
        print("📁 Scanning for GUI components...")
        gui_files = self.scan_gui_components()
        print(f"   Found {len(gui_files)} GUI component files")
        
        # Step 2: Analyze comprehensive dashboard
        print("🎛️  Analyzing comprehensive dashboard implementation...")
        dashboard_found = self.analyze_comprehensive_dashboard()
        if dashboard_found:
            completeness = self.accessibility_report.get('dashboard_completeness', 0)
            print(f"   Dashboard completeness: {completeness}%")
        else:
            print("   ❌ Dashboard not found or accessible")
        
        # Step 3: Test function GUI accessibility
        print("🔍 Testing function GUI accessibility...")
        self.test_function_gui_accessibility()
        accessibility_score = self.accessibility_report.get('accessibility_score', 0)
        print(f"   Function accessibility: {accessibility_score}%")
        
        # Step 4: Test user experience flows
        print("👤 Testing user experience flows...")
        self.test_user_experience_flows()
        print(f"   User flow analysis completed")
        
        # Step 5: Generate recommendations
        print("💡 Generating accessibility recommendations...")
        self.generate_accessibility_recommendations()
        print(f"   Generated {len(self.accessibility_report['recommendations'])} recommendations")
        
        return self.accessibility_report

    def save_report(self, output_file):
        """Save GUI functionality test report"""
        with open(output_file, 'w') as f:
            json.dump(self.accessibility_report, f, indent=2)
        print(f"\n✅ GUI functionality test report saved to: {output_file}")

def main():
    """Main execution function"""
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_file = f"gui_functionality_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    tester = GUIFunctionalityTester(root_dir)
    report = tester.run_comprehensive_test()
    
    # Print summary
    print("\n" + "="*60)
    print("🖥️  GUI FUNCTIONALITY TEST SUMMARY")
    print("="*60)
    print(f"Functions Tested: {report['total_functions_tested']}")
    print(f"GUI Accessible: {report['gui_accessible_verified']}")
    print(f"Missing GUI Access: {report['gui_missing']}")
    print(f"Accessibility Score: {report.get('accessibility_score', 0)}%")
    print(f"Dashboard Completeness: {report.get('dashboard_completeness', 0)}%")
    print(f"GUI Components Found: {report['gui_components_found']}")
    
    # Print dashboard tab status
    dashboard_tabs = report.get('dashboard_tabs', {})
    if dashboard_tabs:
        print("\n📋 DASHBOARD TAB STATUS:")
        for tab, status in dashboard_tabs.items():
            status_icon = "✅" if status['implemented'] else "❌"
            print(f"  {status_icon} {tab}: {status['coverage']}")
    
    # Print user flow analysis
    flow_analysis = report.get('user_flow_analysis', {})
    if flow_analysis:
        print("\n👤 USER FLOW ANALYSIS:")
        for flow, data in flow_analysis.items():
            ux_icon = "✅" if data['user_experience'] == 'EXCELLENT' else "⚠️" if data['user_experience'] == 'GOOD' else "❌"
            print(f"  {ux_icon} {flow}: {data['gui_accessible_steps']}/{data['total_steps']} ({data['coverage_percentage']}%)")
    
    # Print high priority recommendations
    high_priority = [r for r in report['recommendations'] if r['priority'] == 'HIGH']
    if high_priority:
        print("\n🚨 HIGH PRIORITY RECOMMENDATIONS:")
        for rec in high_priority:
            print(f"  • {rec['issue']}")
            print(f"    Solution: {rec['recommendation']}")
    
    tester.save_report(output_file)
    
    # Return success based on accessibility score
    accessibility_score = report.get('accessibility_score', 0)
    dashboard_completeness = report.get('dashboard_completeness', 0)
    
    if accessibility_score >= 95 and dashboard_completeness >= 100:
        print("\n✅ GUI FUNCTIONALITY TEST: EXCELLENT")
        print("   All functions accessible via professional GUI interface")
        return 0
    elif accessibility_score >= 80 and dashboard_completeness >= 80:
        print("\n⚠️  GUI FUNCTIONALITY TEST: GOOD")
        print("   Most functions accessible, minor improvements needed")
        return 0
    else:
        print("\n❌ GUI FUNCTIONALITY TEST: NEEDS IMPROVEMENT")
        print("   Significant GUI accessibility gaps identified")
        return 1

if __name__ == "__main__":
    sys.exit(main())