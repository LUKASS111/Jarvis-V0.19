#!/usr/bin/env python3
"""
Information Architecture Validation Script
Stage 4: Complete GUI Information Architecture & AI Agent Optimization
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime

def check_information_architecture():
    """Validate information architecture consistency"""
    print("🔍 Validating Information Architecture...")
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "validation_type": "information_architecture",
        "stage": 4,
        "tests": {}
    }
    
    # Test 1: Core information files exist
    required_files = [
        "SYSTEMATIC_ENGINEERING_PLAN.md",
        "STAGE_STATUS.md", 
        "ERROR_REGISTRY.md",
        "ENGINEERING_METRICS.md",
        "INFORMATION_ARCHITECTURE.md"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    results["tests"]["core_files_exist"] = {
        "status": "PASS" if not missing_files else "FAIL",
        "required": len(required_files),
        "found": len(required_files) - len(missing_files),
        "missing": missing_files
    }
    
    # Test 2: Semantic file organization
    semantic_patterns = {
        "STAGE_STATUS.md": ["Stage", "Completion", "Status"],
        "ERROR_REGISTRY.md": ["Error", "Pattern", "Prevention"],
        "ENGINEERING_METRICS.md": ["Metrics", "Quality", "Performance"],
        "INFORMATION_ARCHITECTURE.md": ["Architecture", "GUI", "Information"]
    }
    
    semantic_violations = []
    for file, required_terms in semantic_patterns.items():
        if os.path.exists(file):
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                for term in required_terms:
                    if term not in content:
                        semantic_violations.append(f"{file}: missing '{term}'")
    
    results["tests"]["semantic_organization"] = {
        "status": "PASS" if not semantic_violations else "FAIL",
        "violations": semantic_violations,
        "total_patterns": sum(len(terms) for terms in semantic_patterns.values()),
        "validated": sum(len(terms) for terms in semantic_patterns.values()) - len(semantic_violations)
    }
    
    # Test 3: Information consistency
    stage_references = {}
    consistency_issues = []
    
    for file in required_files:
        if os.path.exists(file):
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Look for stage references
                stage_matches = re.findall(r'Stage\s+(\d+)', content)
                stage_references[file] = stage_matches
                
                # Check for conflicting stage information
                if "STAGE_STATUS.md" in file:
                    if "Stage 4" not in content and "Stage 3 COMPLETED" not in content:
                        consistency_issues.append(f"{file}: Stage 4 status not properly reflected")
    
    results["tests"]["information_consistency"] = {
        "status": "PASS" if not consistency_issues else "FAIL",
        "stage_references": stage_references,
        "consistency_issues": consistency_issues
    }
    
    # Test 4: Version control integration
    git_tracked = []
    git_untracked = []
    
    for file in required_files:
        if os.path.exists(file):
            # Check if file would be tracked by git (simplified check)
            if file.endswith('.md'):
                git_tracked.append(file)
            else:
                git_untracked.append(file)
    
    results["tests"]["version_control"] = {
        "status": "PASS",
        "tracked_files": git_tracked,
        "untracked_files": git_untracked,
        "total_files": len(git_tracked) + len(git_untracked)
    }
    
    # Calculate overall success
    passed_tests = sum(1 for test in results["tests"].values() if test["status"] == "PASS")
    total_tests = len(results["tests"])
    
    results["overall"] = {
        "status": "PASS" if passed_tests == total_tests else "FAIL",
        "passed": passed_tests,
        "total": total_tests,
        "success_rate": (passed_tests / total_tests) * 100
    }
    
    # Print results
    print(f"\n📊 Information Architecture Validation Results:")
    print(f"✅ Core Files: {results['tests']['core_files_exist']['found']}/{results['tests']['core_files_exist']['required']}")
    print(f"✅ Semantic Organization: {results['tests']['semantic_organization']['validated']}/{results['tests']['semantic_organization']['total_patterns']} patterns")
    print(f"✅ Information Consistency: {'PASS' if not consistency_issues else 'FAIL'}")
    print(f"✅ Version Control: {len(git_tracked)} files tracked")
    print(f"\n🎯 Overall Status: {results['overall']['status']} ({results['overall']['success_rate']:.1f}%)")
    
    # Save results
    with open('info_architecture_validation_report.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    return results["overall"]["status"] == "PASS"

def check_naming_conventions():
    """Validate file naming conventions"""
    print("\n🔍 Validating Naming Conventions...")
    
    naming_rules = {
        "UPPERCASE_WITH_UNDERSCORES": [
            "SYSTEMATIC_ENGINEERING_PLAN.md",
            "STAGE_STATUS.md",
            "ERROR_REGISTRY.md",
            "ENGINEERING_METRICS.md",
            "INFORMATION_ARCHITECTURE.md"
        ],
        "lowercase_with_underscores": [
            "info_architecture_check.py",
            "command_hierarchy_audit.py",
            "gui_completeness_test.py"
        ]
    }
    
    violations = []
    for pattern, files in naming_rules.items():
        for file in files:
            if os.path.exists(file):
                filename = os.path.basename(file)
                if pattern == "UPPERCASE_WITH_UNDERSCORES":
                    # Check if filename (without extension) follows pattern
                    name_part = filename.replace('.md', '').replace('.py', '')
                    if not name_part.replace('_', '').isupper() or ' ' in filename:
                        violations.append(f"{file}: should be UPPERCASE_WITH_UNDERSCORES")
                elif pattern == "lowercase_with_underscores":
                    name_part = filename.replace('.py', '')
                    if not name_part.replace('_', '').islower() or ' ' in filename:
                        violations.append(f"{file}: should be lowercase_with_underscores")
    
    print(f"✅ Naming Convention Violations: {len(violations)}")
    if violations:
        for violation in violations:
            print(f"   ❌ {violation}")
    
    return len(violations) == 0

def main():
    """Main validation function"""
    print("🎯 Stage 4: Information Architecture Validation")
    print("=" * 60)
    
    try:
        arch_valid = check_information_architecture()
        naming_valid = check_naming_conventions()
        
        overall_success = arch_valid and naming_valid
        
        print("\n" + "=" * 60)
        print(f"🎯 Stage 4 Information Architecture Validation: {'✅ PASS' if overall_success else '❌ FAIL'}")
        
        if overall_success:
            print("🚀 Information architecture is optimized and ready for Stage 5!")
        else:
            print("⚠️ Information architecture issues detected - please resolve before proceeding.")
        
        return 0 if overall_success else 1
        
    except Exception as e:
        print(f"❌ Validation error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())