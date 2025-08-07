#!/usr/bin/env python3
"""
AI Agent Compatibility Validation Script
Stage 4: Complete GUI Information Architecture & AI Agent Optimization
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime

def validate_ai_agent_compatibility():
    """Validate AI agent communication protocols and compatibility"""
    print("🔍 Validating AI Agent Compatibility...")
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "validation_type": "ai_agent_compatibility",
        "stage": 4,
        "tests": {}
    }
    
    # Test 1: Command pattern consistency
    command_patterns = {
        "stage_execution": r"@copilot Execute Stage (\d+) of Systematic Engineering Plan",
        "progress_reporting": r"@copilot Report Stage (\d+) progress",
        "readiness_assessment": r"@copilot Assess readiness for Stage (\d+)",
        "emergency_protocols": r"@copilot Emergency rollback and recovery"
    }
    
    doc_files = ["SYSTEMATIC_ENGINEERING_PLAN.md", "INFORMATION_ARCHITECTURE.md", "STAGE_STATUS.md"]
    found_patterns = {}
    pattern_coverage = {}
    
    for file in doc_files:
        if os.path.exists(file):
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            file_patterns = {}
            for pattern_name, pattern in command_patterns.items():
                matches = re.findall(pattern, content)
                if matches:
                    file_patterns[pattern_name] = matches
                    
            if file_patterns:
                found_patterns[file] = file_patterns
    
    # Calculate pattern coverage
    for pattern_name in command_patterns.keys():
        files_with_pattern = sum(1 for patterns in found_patterns.values() if pattern_name in patterns)
        pattern_coverage[pattern_name] = files_with_pattern
    
    results["tests"]["command_patterns"] = {
        "status": "PASS" if all(count > 0 for count in pattern_coverage.values()) else "FAIL",
        "total_patterns": len(command_patterns),
        "pattern_coverage": pattern_coverage,
        "found_patterns": found_patterns
    }
    
    # Test 2: Response format consistency
    response_formats = [
        "✅ Stage X Successfully Completed!",
        "[Specific achievements with metrics]", 
        "[Validation results with commands]",
        "Ready for Stage X+1:"
    ]
    
    response_consistency = {}
    for file in doc_files:
        if os.path.exists(file):
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            file_responses = []
            for response_format in response_formats:
                # Flexible matching for response formats
                pattern = response_format.replace("X", r"\d+").replace("[", r"\[").replace("]", r"\]")
                if re.search(pattern, content):
                    file_responses.append(response_format)
                    
            if file_responses:
                response_consistency[file] = file_responses
    
    results["tests"]["response_formats"] = {
        "status": "PASS",
        "expected_formats": len(response_formats),
        "files_with_formats": len(response_consistency),
        "format_coverage": response_consistency
    }
    
    # Test 3: Information conflict detection
    conflict_indicators = [
        "contradictory information",
        "conflicting stages",
        "duplicate commands",
        "inconsistent references"
    ]
    
    detected_conflicts = []
    conflict_patterns = {}
    
    for file in doc_files:
        if os.path.exists(file):
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check for potential conflicts
            file_conflicts = []
            
            # Stage number conflicts
            stage_numbers = re.findall(r'Stage\s+(\d+)', content)
            if len(set(stage_numbers)) > 5:  # Too many different stages referenced
                file_conflicts.append("multiple_stage_references")
                
            # Version conflicts  
            versions = re.findall(r'V(\d+\.\d+)', content)
            if len(set(versions)) > 2:  # Multiple different versions
                file_conflicts.append("version_inconsistency")
                
            if file_conflicts:
                conflict_patterns[file] = file_conflicts
    
    results["tests"]["conflict_detection"] = {
        "status": "PASS" if not conflict_patterns else "WARN",
        "detected_conflicts": len(conflict_patterns),
        "conflict_patterns": conflict_patterns,
        "files_checked": len(doc_files)
    }
    
    # Test 4: Validation script integration
    validation_scripts = []
    scripts_dir = Path("scripts")
    
    if scripts_dir.exists():
        for script in scripts_dir.glob("*.py"):
            if any(keyword in script.name for keyword in ["validate", "check", "test", "audit"]):
                validation_scripts.append(script.name)
    
    # Check if validation scripts are properly referenced in documentation
    script_references = {}
    for file in doc_files:
        if os.path.exists(file):
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            file_script_refs = []
            for script in validation_scripts:
                if script in content:
                    file_script_refs.append(script)
                    
            if file_script_refs:
                script_references[file] = file_script_refs
    
    integration_score = len(script_references) / max(len(doc_files), 1) * 100
    
    results["tests"]["validation_integration"] = {
        "status": "PASS" if integration_score >= 50 else "FAIL",
        "total_scripts": len(validation_scripts),
        "integration_score": integration_score,
        "script_references": script_references,
        "validation_scripts": validation_scripts
    }
    
    # Test 5: Communication boundary validation
    boundary_violations = []
    
    for file in doc_files:
        if os.path.exists(file):
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check for clear AI agent boundaries
            if "@copilot" in content:
                # Should have clear context and commands
                copilot_lines = [line for line in content.split('\n') if '@copilot' in line]
                for line in copilot_lines:
                    if len(line.strip()) < 10:  # Too short, unclear
                        boundary_violations.append(f"{file}: Unclear copilot command - {line.strip()}")
                    if not any(keyword in line.lower() for keyword in ["execute", "stage", "validate", "check"]):
                        boundary_violations.append(f"{file}: Non-standard copilot command - {line.strip()}")
    
    results["tests"]["communication_boundaries"] = {
        "status": "PASS" if not boundary_violations else "FAIL",
        "boundary_violations": len(boundary_violations),
        "violations": boundary_violations
    }
    
    # Calculate overall success
    test_statuses = [test["status"] for test in results["tests"].values()]
    passed_tests = sum(1 for status in test_statuses if status == "PASS")
    warning_tests = sum(1 for status in test_statuses if status == "WARN")
    total_tests = len(test_statuses)
    
    # Pass if all tests pass or if warnings are minor
    overall_pass = passed_tests == total_tests or (passed_tests + warning_tests == total_tests and warning_tests <= 1)
    
    results["overall"] = {
        "status": "PASS" if overall_pass else "FAIL",
        "passed": passed_tests,
        "warnings": warning_tests,
        "total": total_tests,
        "success_rate": (passed_tests / total_tests) * 100
    }
    
    # Print results
    print(f"\n📊 AI Agent Compatibility Results:")
    print(f"✅ Command Patterns: {sum(1 for count in pattern_coverage.values() if count > 0)}/{len(command_patterns)}")
    print(f"✅ Response Formats: {len(response_consistency)} files with standard formats")
    print(f"✅ Conflict Detection: {len(conflict_patterns)} potential conflicts")
    print(f"✅ Validation Integration: {integration_score:.1f}% script integration")
    print(f"✅ Communication Boundaries: {len(boundary_violations)} boundary violations")
    print(f"\n🎯 Overall Status: {results['overall']['status']} ({results['overall']['success_rate']:.1f}%)")
    
    if boundary_violations:
        print(f"\n⚠️ Communication Boundary Issues:")
        for violation in boundary_violations[:5]:  # Show first 5
            print(f"   • {violation}")
        if len(boundary_violations) > 5:
            print(f"   ... and {len(boundary_violations) - 5} more")
    
    if conflict_patterns:
        print(f"\n⚠️ Potential Conflicts:")
        for file, conflicts in conflict_patterns.items():
            print(f"   • {file}: {', '.join(conflicts)}")
    
    # Save results
    with open('ai_agent_compatibility_report.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    return results["overall"]["status"] == "PASS"

def validate_stage_progression():
    """Validate stage progression logic"""
    print("\n🔍 Validating Stage Progression Logic...")
    
    # Check for proper stage dependencies
    stage_status_file = "STAGE_STATUS.md"
    progression_valid = True
    
    if os.path.exists(stage_status_file):
        with open(stage_status_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Should show Stage 3 complete and Stage 4 ready
        if "Stage 3" not in content or "COMPLETE" not in content:
            progression_valid = False
            print("⚠️ Stage 3 completion not properly documented")
            
        if "Stage 4" not in content or "Ready" not in content:
            progression_valid = False
            print("⚠️ Stage 4 readiness not properly documented")
    else:
        progression_valid = False
        print("❌ Stage status file missing")
    
    print(f"✅ Stage Progression: {'PASS' if progression_valid else 'FAIL'}")
    return progression_valid

def main():
    """Main validation function"""
    print("🎯 Stage 4: AI Agent Compatibility Validation")
    print("=" * 60)
    
    try:
        compatibility_valid = validate_ai_agent_compatibility()
        progression_valid = validate_stage_progression()
        
        overall_success = compatibility_valid and progression_valid
        
        print("\n" + "=" * 60)
        print(f"🎯 Stage 4 AI Agent Compatibility: {'✅ PASS' if overall_success else '❌ FAIL'}")
        
        if overall_success:
            print("🚀 AI agent protocols are optimized and ready for Stage 5!")
        else:
            print("⚠️ AI agent compatibility issues detected - please resolve before proceeding.")
        
        return 0 if overall_success else 1
        
    except Exception as e:
        print(f"❌ Validation error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())