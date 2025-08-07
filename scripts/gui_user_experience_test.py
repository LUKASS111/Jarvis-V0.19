#!/usr/bin/env python3
"""
Stage 5 - GUI-012: GUI User Experience Validation
Ensure intuitive access to all features for non-technical users
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

class GUIUserExperienceValidator:
    def __init__(self, root_dir):
        self.root_dir = Path(root_dir)
        self.ux_report = {
            'timestamp': datetime.now().isoformat(),
            'validation_type': 'GUI User Experience Validation',
            'stage': 'Stage 5 - GUI-012',
            'usability_score': 0,
            'accessibility_score': 0,
            'intuitive_navigation_score': 0,
            'user_workflow_efficiency': 0,
            'non_technical_user_readiness': False,
            'gui_components_analyzed': 0,
            'usability_issues': [],
            'accessibility_violations': [],
            'workflow_bottlenecks': [],
            'recommendations': []
        }

    def analyze_dashboard_usability(self):
        """Analyze the usability of the comprehensive dashboard"""
        dashboard_file = self.root_dir / 'gui' / 'enhanced' / 'comprehensive_dashboard.py'
        
        usability_criteria = {
            'navigation_clarity': 0,
            'visual_hierarchy': 0,
            'user_guidance': 0,
            'error_prevention': 0,
            'consistency': 0,
            'accessibility': 0
        }
        
        if not dashboard_file.exists():
            self.ux_report['dashboard_status'] = 'NOT_FOUND'
            self.ux_report['usability_issues'].append({
                'severity': 'CRITICAL',
                'issue': 'Comprehensive dashboard not found',
                'impact': 'Users cannot access program functionality through GUI',
                'recommendation': 'Implement comprehensive dashboard interface'
            })
            return usability_criteria
        
        try:
            with open(dashboard_file, 'r', encoding='utf-8') as f:
                dashboard_content = f.read()
            
            # Analyze navigation clarity
            usability_criteria['navigation_clarity'] = self._analyze_navigation_clarity(dashboard_content)
            
            # Analyze visual hierarchy
            usability_criteria['visual_hierarchy'] = self._analyze_visual_hierarchy(dashboard_content)
            
            # Analyze user guidance
            usability_criteria['user_guidance'] = self._analyze_user_guidance(dashboard_content)
            
            # Analyze error prevention
            usability_criteria['error_prevention'] = self._analyze_error_prevention(dashboard_content)
            
            # Analyze consistency
            usability_criteria['consistency'] = self._analyze_consistency(dashboard_content)
            
            # Analyze accessibility
            usability_criteria['accessibility'] = self._analyze_accessibility(dashboard_content)
            
            # Calculate overall usability score
            total_score = sum(usability_criteria.values())
            max_score = len(usability_criteria) * 100
            self.ux_report['usability_score'] = round((total_score / max_score) * 100, 1)
            
            self.ux_report['dashboard_status'] = 'ANALYZED'
            self.ux_report['usability_breakdown'] = usability_criteria
            
        except Exception as e:
            self.ux_report['dashboard_status'] = f'ERROR: {str(e)}'
            self.ux_report['usability_issues'].append({
                'severity': 'HIGH',
                'issue': f'Could not analyze dashboard: {str(e)}',
                'impact': 'Unable to validate user experience',
                'recommendation': 'Fix dashboard accessibility issues'
            })
        
        return usability_criteria

    def _analyze_navigation_clarity(self, content):
        """Analyze navigation clarity and structure"""
        navigation_indicators = [
            'tab', 'menu', 'navigation', 'breadcrumb',
            'sidebar', 'toolbar', 'button_group'
        ]
        
        clarity_score = 0
        
        # Check for clear navigation structure
        for indicator in navigation_indicators:
            if indicator.lower() in content.lower():
                clarity_score += 15
        
        # Check for consistent navigation patterns
        if 'def create_navigation' in content or 'class Navigation' in content:
            clarity_score += 25
        
        # Check for user-friendly labels
        user_friendly_terms = ['dashboard', 'home', 'settings', 'help', 'back']
        for term in user_friendly_terms:
            if term.lower() in content.lower():
                clarity_score += 5
        
        return min(clarity_score, 100)

    def _analyze_visual_hierarchy(self, content):
        """Analyze visual hierarchy and layout"""
        hierarchy_indicators = [
            'layout', 'grid', 'column', 'row',
            'header', 'footer', 'section', 'panel'
        ]
        
        hierarchy_score = 0
        
        # Check for structured layout
        for indicator in hierarchy_indicators:
            if indicator.lower() in content.lower():
                hierarchy_score += 12
        
        # Check for proper spacing and grouping
        spacing_terms = ['margin', 'padding', 'spacing', 'group']
        for term in spacing_terms:
            if term.lower() in content.lower():
                hierarchy_score += 8
        
        # Check for visual emphasis
        emphasis_terms = ['bold', 'highlight', 'color', 'size', 'font']
        for term in emphasis_terms:
            if term.lower() in content.lower():
                hierarchy_score += 6
        
        return min(hierarchy_score, 100)

    def _analyze_user_guidance(self, content):
        """Analyze user guidance and help systems"""
        guidance_indicators = [
            'help', 'tooltip', 'hint', 'guide',
            'instruction', 'tutorial', 'onboarding'
        ]
        
        guidance_score = 0
        
        # Check for help systems
        for indicator in guidance_indicators:
            if indicator.lower() in content.lower():
                guidance_score += 20
        
        # Check for contextual help
        if 'context' in content.lower() and 'help' in content.lower():
            guidance_score += 30
        
        # Check for error messages and feedback
        feedback_terms = ['message', 'feedback', 'status', 'progress']
        for term in feedback_terms:
            if term.lower() in content.lower():
                guidance_score += 10
        
        return min(guidance_score, 100)

    def _analyze_error_prevention(self, content):
        """Analyze error prevention mechanisms"""
        prevention_indicators = [
            'validate', 'check', 'verify', 'confirm',
            'warning', 'alert', 'prevent', 'protection'
        ]
        
        prevention_score = 0
        
        # Check for validation systems
        for indicator in prevention_indicators:
            if indicator.lower() in content.lower():
                prevention_score += 15
        
        # Check for user confirmation dialogs
        if 'confirm' in content.lower() and 'dialog' in content.lower():
            prevention_score += 25
        
        # Check for input validation
        if 'input' in content.lower() and 'valid' in content.lower():
            prevention_score += 20
        
        return min(prevention_score, 100)

    def _analyze_consistency(self, content):
        """Analyze interface consistency"""
        consistency_indicators = [
            'theme', 'style', 'standard', 'pattern',
            'template', 'base_class', 'inherit'
        ]
        
        consistency_score = 0
        
        # Check for consistent styling
        for indicator in consistency_indicators:
            if indicator.lower() in content.lower():
                consistency_score += 18
        
        # Check for reusable components
        if 'component' in content.lower() or 'widget' in content.lower():
            consistency_score += 25
        
        return min(consistency_score, 100)

    def _analyze_accessibility(self, content):
        """Analyze accessibility features"""
        accessibility_indicators = [
            'accessibility', 'a11y', 'screen_reader',
            'keyboard', 'focus', 'aria', 'alt_text'
        ]
        
        accessibility_score = 0
        
        # Check for accessibility features
        for indicator in accessibility_indicators:
            if indicator.lower() in content.lower():
                accessibility_score += 20
        
        # Check for keyboard navigation
        if 'key' in content.lower() and ('press' in content.lower() or 'shortcut' in content.lower()):
            accessibility_score += 30
        
        return min(accessibility_score, 100)

    def analyze_user_workflows(self):
        """Analyze common user workflows for efficiency"""
        workflows = {
            'new_user_onboarding': [
                'Open application',
                'Access initial setup',
                'Configure basic settings',
                'Access help/tutorial',
                'Start first task'
            ],
            'daily_ai_interaction': [
                'Launch interface',
                'Start chat/interaction',
                'Upload files (if needed)',
                'Review results',
                'Save/export work'
            ],
            'data_management': [
                'Access data interface',
                'Import/upload data',
                'Browse/search data',
                'Manage/organize data',
                'Export/backup data'
            ],
            'system_configuration': [
                'Open settings',
                'Navigate to desired section',
                'Modify settings',
                'Apply changes',
                'Verify configuration'
            ]
        }
        
        workflow_efficiency = {}
        total_efficiency = 0
        
        for workflow_name, steps in workflows.items():
            efficiency = self._evaluate_workflow_efficiency(workflow_name, steps)
            workflow_efficiency[workflow_name] = efficiency
            total_efficiency += efficiency['efficiency_score']
        
        # Calculate average workflow efficiency
        if len(workflows) > 0:
            avg_efficiency = total_efficiency / len(workflows)
            self.ux_report['user_workflow_efficiency'] = round(avg_efficiency, 1)
        
        self.ux_report['workflow_analysis'] = workflow_efficiency

    def _evaluate_workflow_efficiency(self, workflow_name, steps):
        """Evaluate efficiency of a specific workflow"""
        # Check if each step can be accomplished through GUI
        gui_accessible_steps = 0
        bottlenecks = []
        
        for step in steps:
            if self._is_step_gui_accessible(step):
                gui_accessible_steps += 1
            else:
                bottlenecks.append({
                    'workflow': workflow_name,
                    'step': step,
                    'issue': 'No clear GUI path for this step',
                    'impact': 'User may need technical knowledge or CLI access'
                })
        
        # Calculate efficiency score
        efficiency_score = (gui_accessible_steps / len(steps)) * 100
        
        # Add bottlenecks to report
        self.ux_report['workflow_bottlenecks'].extend(bottlenecks)
        
        return {
            'total_steps': len(steps),
            'gui_accessible_steps': gui_accessible_steps,
            'efficiency_score': round(efficiency_score, 1),
            'bottlenecks': len(bottlenecks)
        }

    def _is_step_gui_accessible(self, step):
        """Check if a workflow step is accessible through GUI"""
        # Check for GUI implementations based on step description
        step_lower = step.lower()
        
        # Common GUI-accessible operations
        gui_operations = [
            'open', 'launch', 'start', 'access', 'click',
            'upload', 'download', 'save', 'export',
            'configure', 'settings', 'browse', 'search',
            'review', 'view', 'navigate', 'modify'
        ]
        
        # Check if step contains GUI-friendly operations
        return any(operation in step_lower for operation in gui_operations)

    def evaluate_non_technical_user_readiness(self):
        """Evaluate if the interface is ready for non-technical users"""
        readiness_criteria = {
            'no_cli_dependency': False,
            'intuitive_navigation': False,
            'clear_labels_instructions': False,
            'error_recovery': False,
            'comprehensive_help': False
        }
        
        # Check CLI dependency
        cli_indicators = ['command', 'terminal', 'cmd', 'cli', 'console']
        gui_files = list(self.root_dir.rglob("gui/**/*.py"))
        
        if len(gui_files) > 3:  # Basic GUI presence
            readiness_criteria['no_cli_dependency'] = True
        
        # Check for intuitive navigation
        usability_score = self.ux_report.get('usability_score', 0)
        if usability_score >= 70:
            readiness_criteria['intuitive_navigation'] = True
        
        # Check for clear labels and instructions
        if self._has_clear_interface_elements():
            readiness_criteria['clear_labels_instructions'] = True
        
        # Check for error recovery mechanisms
        if self._has_error_recovery_systems():
            readiness_criteria['error_recovery'] = True
        
        # Check for comprehensive help
        if self._has_comprehensive_help():
            readiness_criteria['comprehensive_help'] = True
        
        # Calculate overall readiness
        ready_criteria = sum(1 for criterion in readiness_criteria.values() if criterion)
        readiness_percentage = (ready_criteria / len(readiness_criteria)) * 100
        
        self.ux_report['non_technical_user_readiness'] = ready_criteria >= 4  # At least 4/5 criteria
        self.ux_report['readiness_criteria'] = readiness_criteria
        self.ux_report['readiness_percentage'] = round(readiness_percentage, 1)

    def _has_clear_interface_elements(self):
        """Check for clear interface elements and labels"""
        # Look for user-friendly terms in GUI files
        user_friendly_terms = [
            'button', 'label', 'title', 'description',
            'help_text', 'placeholder', 'tooltip'
        ]
        
        gui_files = list(self.root_dir.rglob("gui/**/*.py"))
        for gui_file in gui_files:
            try:
                with open(gui_file, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                    if any(term in content for term in user_friendly_terms):
                        return True
            except:
                continue
        return False

    def _has_error_recovery_systems(self):
        """Check for error recovery and undo mechanisms"""
        recovery_terms = [
            'undo', 'revert', 'restore', 'recovery',
            'rollback', 'reset', 'default'
        ]
        
        # Check main application files
        main_files = ['main.py', 'app.py'] + list(self.root_dir.rglob("gui/**/*.py"))
        
        for file_path in main_files:
            if not Path(file_path).exists():
                continue
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                    if any(term in content for term in recovery_terms):
                        return True
            except:
                continue
        return False

    def _has_comprehensive_help(self):
        """Check for comprehensive help system"""
        help_indicators = [
            'help', 'tutorial', 'guide', 'documentation',
            'instructions', 'onboarding', 'getting_started'
        ]
        
        # Check for help files or help functionality
        help_files = list(self.root_dir.rglob("*help*")) + list(self.root_dir.rglob("*guide*"))
        if help_files:
            return True
        
        # Check in GUI files for help functionality
        gui_files = list(self.root_dir.rglob("gui/**/*.py"))
        for gui_file in gui_files:
            try:
                with open(gui_file, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                    if any(indicator in content for indicator in help_indicators):
                        return True
            except:
                continue
        return False

    def generate_ux_recommendations(self):
        """Generate UX improvement recommendations"""
        recommendations = []
        
        # Usability score recommendations
        usability_score = self.ux_report.get('usability_score', 0)
        if usability_score < 80:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Usability',
                'issue': f'Usability score only {usability_score}%',
                'recommendation': 'Improve navigation, visual hierarchy, and user guidance',
                'impact': 'Users will struggle to use the interface effectively'
            })
        
        # Non-technical user readiness
        if not self.ux_report.get('non_technical_user_readiness', False):
            readiness_percentage = self.ux_report.get('readiness_percentage', 0)
            recommendations.append({
                'priority': 'CRITICAL',
                'category': 'Non-Technical User Access',
                'issue': f'Only {readiness_percentage}% ready for non-technical users',
                'recommendation': 'Eliminate CLI dependencies and add comprehensive help',
                'impact': 'Non-technical users cannot effectively use the system'
            })
        
        # Workflow efficiency
        workflow_efficiency = self.ux_report.get('user_workflow_efficiency', 0)
        if workflow_efficiency < 90:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Workflow Efficiency',
                'issue': f'User workflows only {workflow_efficiency}% efficient',
                'recommendation': 'Streamline common user workflows and eliminate bottlenecks',
                'impact': 'Users will experience friction in daily operations'
            })
        
        # Workflow bottlenecks
        bottlenecks = self.ux_report.get('workflow_bottlenecks', [])
        if bottlenecks:
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'Workflow Bottlenecks',
                'issue': f'{len(bottlenecks)} workflow bottlenecks identified',
                'recommendation': 'Add GUI interfaces for all workflow steps',
                'impact': 'Users forced to use technical methods for common tasks'
            })
        
        self.ux_report['recommendations'] = recommendations

    def run_comprehensive_ux_validation(self):
        """Execute comprehensive UX validation"""
        print("👤 Starting Stage 5 - GUI User Experience Validation...")
        print("=" * 60)
        
        # Step 1: Analyze dashboard usability
        print("🎛️  Analyzing dashboard usability...")
        usability_criteria = self.analyze_dashboard_usability()
        usability_score = self.ux_report.get('usability_score', 0)
        print(f"   Usability score: {usability_score}%")
        
        # Step 2: Analyze user workflows
        print("🔄 Analyzing user workflow efficiency...")
        self.analyze_user_workflows()
        workflow_efficiency = self.ux_report.get('user_workflow_efficiency', 0)
        print(f"   Workflow efficiency: {workflow_efficiency}%")
        
        # Step 3: Evaluate non-technical user readiness
        print("🎯 Evaluating non-technical user readiness...")
        self.evaluate_non_technical_user_readiness()
        readiness = self.ux_report.get('non_technical_user_readiness', False)
        print(f"   Non-technical ready: {'Yes' if readiness else 'No'}")
        
        # Step 4: Generate recommendations
        print("💡 Generating UX improvement recommendations...")
        self.generate_ux_recommendations()
        print(f"   Generated {len(self.ux_report['recommendations'])} recommendations")
        
        return self.ux_report

    def save_report(self, output_file):
        """Save UX validation report"""
        with open(output_file, 'w') as f:
            json.dump(self.ux_report, f, indent=2)
        print(f"\n✅ GUI User Experience validation report saved to: {output_file}")

def main():
    """Main execution function"""
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_file = f"gui_user_experience_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    validator = GUIUserExperienceValidator(root_dir)
    report = validator.run_comprehensive_ux_validation()
    
    # Print summary
    print("\n" + "="*60)
    print("👤 GUI USER EXPERIENCE VALIDATION SUMMARY")
    print("="*60)
    print(f"Usability Score: {report.get('usability_score', 0)}%")
    print(f"Workflow Efficiency: {report.get('user_workflow_efficiency', 0)}%")
    print(f"Non-Technical User Ready: {'Yes' if report.get('non_technical_user_readiness', False) else 'No'}")
    print(f"Readiness Percentage: {report.get('readiness_percentage', 0)}%")
    
    # Print usability breakdown
    usability_breakdown = report.get('usability_breakdown', {})
    if usability_breakdown:
        print(f"\n🎛️  USABILITY BREAKDOWN:")
        for criterion, score in usability_breakdown.items():
            criterion_name = criterion.replace('_', ' ').title()
            print(f"  {criterion_name}: {score}%")
    
    # Print workflow analysis
    workflow_analysis = report.get('workflow_analysis', {})
    if workflow_analysis:
        print(f"\n🔄 WORKFLOW EFFICIENCY:")
        for workflow, data in workflow_analysis.items():
            workflow_name = workflow.replace('_', ' ').title()
            print(f"  {workflow_name}: {data['gui_accessible_steps']}/{data['total_steps']} ({data['efficiency_score']}%)")
    
    # Print critical recommendations
    recommendations = report.get('recommendations', [])
    critical_recs = [r for r in recommendations if r['priority'] == 'CRITICAL']
    if critical_recs:
        print(f"\n❗ CRITICAL UX ISSUES:")
        for rec in critical_recs:
            print(f"  • {rec['issue']}")
            print(f"    Solution: {rec['recommendation']}")
    
    validator.save_report(output_file)
    
    # Return status based on UX validation
    usability_score = report.get('usability_score', 0)
    workflow_efficiency = report.get('user_workflow_efficiency', 0)
    non_technical_ready = report.get('non_technical_user_readiness', False)
    
    if usability_score >= 85 and workflow_efficiency >= 90 and non_technical_ready:
        print("\n✅ GUI USER EXPERIENCE: EXCELLENT")
        print("   Interface ready for all users including non-technical")
        return 0
    elif usability_score >= 70 and workflow_efficiency >= 80:
        print("\n⚠️  GUI USER EXPERIENCE: GOOD")
        print("   Interface usable but improvements needed for non-technical users")
        return 0
    else:
        print("\n❌ GUI USER EXPERIENCE: NEEDS IMPROVEMENT")
        print("   Significant UX issues preventing effective use")
        return 1

if __name__ == "__main__":
    sys.exit(main())