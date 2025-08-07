#!/usr/bin/env python3
"""
Comprehensive Stage Validation Script
Validates the completion status of all stages 1-5 and readiness for Stage 6

This master validation script provides:
- Complete overview of all stage completion status
- Comprehensive analysis with actionable insights
- Stage 6 readiness assessment
- Foundation repair recommendations
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
import importlib.util

def run_command(cmd):
    """Execute shell command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, "", str(e)

def run_stage_validation(stage_num):
    """Run individual stage validation script"""
    script_path = f"scripts/validate_stage{stage_num}_completion.py"
    
    if not os.path.exists(script_path):
        return {
            'status': 'MISSING',
            'message': f'Validation script for stage {stage_num} not found',
            'completion_percentage': 0,
            'details': {}
        }
    
    try:
        # Make script executable
        os.chmod(script_path, 0o755)
        
        # Run the validation script
        success, output, error = run_command(f'python3 {script_path}')
        
        # Parse the latest report for this stage
        report_pattern = f"validate_stage{stage_num}_completion_report_*.json"
        success_find, report_files, _ = run_command(f"ls -t {report_pattern} 2>/dev/null | head -1")
        
        if success_find and report_files:
            with open(report_files.strip(), 'r') as f:
                report_data = json.load(f)
            
            return {
                'status': report_data.get('overall_status', 'UNKNOWN'),
                'completion_percentage': report_data.get('summary', {}).get('completion_percentage', 0),
                'details': report_data.get('summary', {}),
                'micro_tasks': report_data.get('micro_tasks', {}),
                'message': f'Stage {stage_num} validation completed'
            }
        else:
            # Parse output for basic info
            if 'PASS' in output:
                status = 'PASS'
            elif 'PARTIAL' in output:
                status = 'PARTIAL'
            elif 'FAIL' in output:
                status = 'FAIL'
            else:
                status = 'UNKNOWN'
            
            return {
                'status': status,
                'completion_percentage': 75 if status == 'PASS' else 50 if status == 'PARTIAL' else 25,
                'details': {'output': output[:500]},
                'message': f'Stage {stage_num} validation executed'
            }
    
    except Exception as e:
        return {
            'status': 'ERROR',
            'message': f'Error running stage {stage_num} validation: {str(e)}',
            'completion_percentage': 0,
            'details': {'error': str(e)}
        }

def analyze_overall_readiness():
    """Analyze overall system readiness and foundation status"""
    print("🔍 Analyzing Overall System Readiness...")
    
    # Check basic system health
    system_health = {
        'main_executable': os.path.exists('main.py'),
        'gui_system': os.path.exists('gui/') and len(os.listdir('gui/')) > 0,
        'test_framework': os.path.exists('run_tests.py') or os.path.exists('tests/'),
        'documentation': len([f for f in os.listdir('.') if f.endswith('.md')]) >= 5,
        'validation_framework': len([f for f in os.listdir('scripts/') if 'validate' in f]) >= 5 if os.path.exists('scripts/') else False
    }
    
    health_score = sum(system_health.values()) / len(system_health) * 100
    
    # Check for critical files
    critical_files = [
        'README.md', 'SYSTEMATIC_ENGINEERING_PLAN.md', 'STAGE_STATUS.md',
        'ERROR_REGISTRY.md', 'ENGINEERING_METRICS.md', 'INFORMATION_ARCHITECTURE.md'
    ]
    
    existing_critical = [f for f in critical_files if os.path.exists(f)]
    
    return {
        'system_health': system_health,
        'health_score': health_score,
        'critical_files': {
            'required': len(critical_files),
            'existing': len(existing_critical),
            'missing': [f for f in critical_files if f not in existing_critical]
        },
        'readiness_status': 'READY' if health_score >= 80 else 'NEEDS_WORK' if health_score >= 60 else 'NOT_READY'
    }

def check_validation_framework_completeness():
    """Check if all validation scripts exist and are functional"""
    print("📋 Checking Validation Framework Completeness...")
    
    required_validators = [
        'validate_stage1_completion.py',
        'validate_stage2_completion.py', 
        'validate_stage3_completion.py',
        'validate_stage4_completion.py',
        'validate_stage5_completion.py'
    ]
    
    validator_status = {}
    for validator in required_validators:
        script_path = f"scripts/{validator}"
        if os.path.exists(script_path):
            # Check if script is executable and has main function
            try:
                with open(script_path, 'r') as f:
                    content = f.read()
                    has_main = 'def main(' in content
                    has_imports = 'import' in content
                    validator_status[validator] = {
                        'exists': True,
                        'functional': has_main and has_imports,
                        'size': len(content)
                    }
            except Exception as e:
                validator_status[validator] = {
                    'exists': True,
                    'functional': False,
                    'error': str(e)
                }
        else:
            validator_status[validator] = {
                'exists': False,
                'functional': False
            }
    
    functional_count = sum(1 for v in validator_status.values() if v.get('functional', False))
    
    return {
        'required_validators': len(required_validators),
        'existing_validators': sum(1 for v in validator_status.values() if v.get('exists', False)),
        'functional_validators': functional_count,
        'validator_details': validator_status,
        'framework_completeness': functional_count / len(required_validators) * 100
    }

def generate_actionable_insights(stage_results, readiness_analysis, framework_status):
    """Generate actionable insights and recommendations"""
    insights = {
        'critical_issues': [],
        'recommendations': [],
        'stage_6_blockers': [],
        'quick_wins': []
    }
    
    # Analyze stage completion
    failed_stages = [stage for stage, result in stage_results.items() if result['status'] in ['FAIL', 'ERROR']]
    partial_stages = [stage for stage, result in stage_results.items() if result['status'] == 'PARTIAL']
    
    # Critical issues
    if failed_stages:
        insights['critical_issues'].append(f"CRITICAL: Stages {', '.join(failed_stages)} have FAILED validation")
        insights['stage_6_blockers'].extend([f"Stage {stage} must be completed" for stage in failed_stages])
    
    if framework_status['functional_validators'] < 5:
        insights['critical_issues'].append("CRITICAL: Validation framework incomplete")
        insights['stage_6_blockers'].append("Complete validation framework required")
    
    if readiness_analysis['health_score'] < 60:
        insights['critical_issues'].append("CRITICAL: System health below acceptable threshold")
        insights['stage_6_blockers'].append("System health must reach 80%+")
    
    # Recommendations
    if partial_stages:
        insights['recommendations'].append(f"Address partial completion in Stages {', '.join(partial_stages)}")
        insights['quick_wins'].append("Review partial stage requirements and complete missing items")
    
    if len(readiness_analysis['critical_files']['missing']) > 0:
        insights['recommendations'].append("Create missing critical documentation files")
        insights['quick_wins'].extend([f"Create {f}" for f in readiness_analysis['critical_files']['missing']])
    
    # Stage 6 readiness
    overall_completion = sum(result['completion_percentage'] for result in stage_results.values()) / len(stage_results)
    
    if overall_completion >= 75 and not failed_stages and framework_status['functional_validators'] >= 5:
        insights['stage_6_readiness'] = 'READY'
        insights['recommendations'].append("Foundation is solid - proceed with Stage 6")
    elif overall_completion >= 60:
        insights['stage_6_readiness'] = 'NEEDS_MINOR_FIXES'
        insights['recommendations'].append("Minor fixes required before Stage 6")
    else:
        insights['stage_6_readiness'] = 'NOT_READY'
        insights['recommendations'].append("Significant foundation repair required")
    
    return insights

def main():
    """Main comprehensive validation function"""
    print("🎯 Comprehensive Stage 1-5 Validation")
    print("=" * 60)
    print("Foundation Repair & Stage 6 Readiness Assessment")
    print()
    
    # Change to repository root
    os.chdir('/home/runner/work/Jarvis-V0.19/Jarvis-V0.19')
    
    print("🔄 Running individual stage validations...")
    print("-" * 40)
    
    # Run all stage validations
    stage_results = {}
    for stage in range(1, 6):
        print(f"Running Stage {stage} validation...")
        stage_results[f"stage_{stage}"] = run_stage_validation(stage)
        status_emoji = "✅" if stage_results[f"stage_{stage}"]['status'] == 'PASS' else "⚠️" if stage_results[f"stage_{stage}"]['status'] == 'PARTIAL' else "❌"
        print(f"{status_emoji} Stage {stage}: {stage_results[f'stage_{stage}']['status']} ({stage_results[f'stage_{stage}']['completion_percentage']:.1f}%)")
    
    print("\n🔍 Analyzing system readiness...")
    readiness_analysis = analyze_overall_readiness()
    
    print("📋 Checking validation framework...")
    framework_status = check_validation_framework_completeness()
    
    print("💡 Generating actionable insights...")
    insights = generate_actionable_insights(stage_results, readiness_analysis, framework_status)
    
    # Compile comprehensive report
    comprehensive_report = {
        'timestamp': datetime.now().isoformat(),
        'validation_type': 'comprehensive_stage_1_5_validation',
        'stage_results': stage_results,
        'system_readiness': readiness_analysis,
        'validation_framework': framework_status,
        'actionable_insights': insights,
        'summary': {
            'total_stages_evaluated': 5,
            'stages_passed': sum(1 for r in stage_results.values() if r['status'] == 'PASS'),
            'stages_partial': sum(1 for r in stage_results.values() if r['status'] == 'PARTIAL'),
            'stages_failed': sum(1 for r in stage_results.values() if r['status'] in ['FAIL', 'ERROR']),
            'overall_completion': sum(r['completion_percentage'] for r in stage_results.values()) / len(stage_results),
            'stage_6_readiness': insights.get('stage_6_readiness', 'UNKNOWN'),
            'system_health_score': readiness_analysis['health_score'],
            'validation_framework_completeness': framework_status['framework_completeness']
        }
    }
    
    # Print comprehensive results
    print("\n" + "=" * 60)
    print("📊 COMPREHENSIVE VALIDATION RESULTS")
    print("=" * 60)
    
    print("\n🎯 Stage Completion Overview:")
    for stage, result in stage_results.items():
        status_emoji = "✅" if result['status'] == 'PASS' else "⚠️" if result['status'] == 'PARTIAL' else "❌"
        print(f"  {status_emoji} {stage.replace('_', ' ').title()}: {result['status']} ({result['completion_percentage']:.1f}%)")
    
    print(f"\n📈 Overall Completion: {comprehensive_report['summary']['overall_completion']:.1f}%")
    print(f"🏥 System Health Score: {readiness_analysis['health_score']:.1f}%")
    print(f"🛠️ Validation Framework: {framework_status['framework_completeness']:.1f}%")
    
    print(f"\n🚀 Stage 6 Readiness: {insights.get('stage_6_readiness', 'UNKNOWN')}")
    
    # Critical issues
    if insights['critical_issues']:
        print("\n🚨 CRITICAL ISSUES:")
        for issue in insights['critical_issues']:
            print(f"  ❌ {issue}")
    
    # Stage 6 blockers
    if insights['stage_6_blockers']:
        print("\n🛑 STAGE 6 BLOCKERS:")
        for blocker in insights['stage_6_blockers']:
            print(f"  🛑 {blocker}")
    
    # Recommendations
    if insights['recommendations']:
        print("\n💡 RECOMMENDATIONS:")
        for rec in insights['recommendations']:
            print(f"  💡 {rec}")
    
    # Quick wins
    if insights['quick_wins']:
        print("\n⚡ QUICK WINS:")
        for win in insights['quick_wins'][:5]:  # Show top 5
            print(f"  ⚡ {win}")
    
    # Save comprehensive report
    report_filename = f"comprehensive_stage_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_filename, 'w') as f:
        json.dump(comprehensive_report, f, indent=2)
    
    print(f"\n📄 Comprehensive report saved: {report_filename}")
    
    # Determine exit status
    if insights.get('stage_6_readiness') == 'READY':
        print("\n✅ FOUNDATION READY - Stage 6 can proceed")
        sys.exit(0)
    elif insights.get('stage_6_readiness') == 'NEEDS_MINOR_FIXES':
        print("\n⚠️ MINOR FIXES NEEDED - Address recommendations before Stage 6")
        sys.exit(0)
    else:
        print("\n❌ FOUNDATION REPAIR REQUIRED - Complete critical issues before Stage 6")
        sys.exit(1)

if __name__ == "__main__":
    main()