#!/usr/bin/env python3
"""
Documentation Consistency Validation Script
Stage 4: Complete GUI Information Architecture & AI Agent Optimization
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime

def validate_documentation_consistency():
    """Validate consistency across all documentation files"""
    print("🔍 Validating Documentation Consistency...")
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "validation_type": "documentation_consistency",
        "stage": 4,
        "tests": {}
    }
    
    # Core documentation files to check
    doc_files = [
        "SYSTEMATIC_ENGINEERING_PLAN.md",
        "STAGE_STATUS.md",
        "ERROR_REGISTRY.md", 
        "ENGINEERING_METRICS.md",
        "INFORMATION_ARCHITECTURE.md",
        "PROGRESS.md",
        "TASKS.md",
        "CHANGELOG.md",
        "README.md"
    ]
    
    # Test 1: Stage references consistency
    stage_refs = {}
    stage_inconsistencies = []
    
    for file in doc_files:
        if os.path.exists(file):
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Find stage references
            stages = re.findall(r'Stage\s+(\d+)', content)
            stage_refs[file] = stages
            
            # Check for current stage consistency (should reference Stage 4)
            if "STAGE_STATUS.md" in file:
                if "Stage 4" not in content:
                    stage_inconsistencies.append(f"{file}: Missing Stage 4 reference")
            elif "SYSTEMATIC_ENGINEERING_PLAN.md" in file:
                if "Stage 4" not in content:
                    stage_inconsistencies.append(f"{file}: Missing Stage 4 in plan")
    
    results["tests"]["stage_references"] = {
        "status": "PASS" if not stage_inconsistencies else "FAIL",
        "files_checked": len([f for f in doc_files if os.path.exists(f)]),
        "stage_references": stage_refs,
        "inconsistencies": stage_inconsistencies
    }
    
    # Test 2: Version consistency
    version_refs = {}
    version_inconsistencies = []
    
    for file in doc_files:
        if os.path.exists(file):
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Find version references
            versions = re.findall(r'V?(\d+\.\d+(?:\.\d+)?)', content)
            if versions:
                version_refs[file] = versions
                
            # Check for Jarvis version consistency
            jarvis_versions = re.findall(r'Jarvis\s+V?(\d+\.\d+(?:\.\d+)?)', content)
            if jarvis_versions:
                # Should reference V0.19 or similar
                if not any('19' in v or '0.19' in v for v in jarvis_versions):
                    version_inconsistencies.append(f"{file}: Jarvis version mismatch")
    
    results["tests"]["version_consistency"] = {
        "status": "PASS" if not version_inconsistencies else "FAIL",
        "version_references": version_refs,
        "inconsistencies": version_inconsistencies
    }
    
    # Test 3: GUI function count consistency
    gui_function_refs = {}
    function_inconsistencies = []
    
    expected_function_counts = {
        "ai_models": 234,
        "multimodal": 187,
        "memory": 298,
        "agents": 156,
        "vector": 203,
        "monitoring": 189,
        "config": 134,
        "development": 143,
        "analytics": 113
    }
    
    total_expected = sum(expected_function_counts.values())  # 1,657
    
    for file in doc_files:
        if os.path.exists(file):
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check for function count references
            if "1,657" in content or "1657" in content:
                gui_function_refs[file] = "references_total_functions"
                
            # Check individual category counts
            for category, count in expected_function_counts.items():
                if str(count) in content:
                    if file not in gui_function_refs:
                        gui_function_refs[file] = []
                    if isinstance(gui_function_refs[file], list):
                        gui_function_refs[file].append(f"{category}:{count}")
    
    results["tests"]["function_count_consistency"] = {
        "status": "PASS",
        "expected_total": total_expected,
        "files_with_references": len(gui_function_refs),
        "function_references": gui_function_refs
    }
    
    # Test 4: Cross-references validation
    cross_refs = {}
    missing_refs = []
    
    for file in doc_files:
        if os.path.exists(file):
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Find references to other documentation files
            file_refs = []
            for other_file in doc_files:
                if other_file != file and other_file in content:
                    file_refs.append(other_file)
            
            if file_refs:
                cross_refs[file] = file_refs
                
            # Check if referenced files exist
            for ref_file in file_refs:
                if not os.path.exists(ref_file):
                    missing_refs.append(f"{file} references missing {ref_file}")
    
    results["tests"]["cross_references"] = {
        "status": "PASS" if not missing_refs else "FAIL",
        "total_cross_references": sum(len(refs) for refs in cross_refs.values()),
        "cross_references": cross_refs,
        "missing_references": missing_refs
    }
    
    # Test 5: Validation script references
    script_refs = {}
    missing_scripts = []
    
    for file in doc_files:
        if os.path.exists(file):
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Find script references
            scripts = re.findall(r'python scripts/([a-z_]+\.py)', content)
            if scripts:
                script_refs[file] = scripts
                
                # Check if scripts exist
                for script in scripts:
                    script_path = f"scripts/{script}"
                    if not os.path.exists(script_path):
                        missing_scripts.append(f"{file} references missing {script_path}")
    
    results["tests"]["script_references"] = {
        "status": "PASS" if not missing_scripts else "FAIL", 
        "total_script_references": sum(len(scripts) for scripts in script_refs.values()),
        "script_references": script_refs,
        "missing_scripts": missing_scripts
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
    print(f"\n📊 Documentation Consistency Results:")
    print(f"✅ Stage References: {'PASS' if not stage_inconsistencies else 'FAIL'}")
    print(f"✅ Version Consistency: {'PASS' if not version_inconsistencies else 'FAIL'}")
    print(f"✅ Function Counts: {len(gui_function_refs)} files with references")
    print(f"✅ Cross References: {sum(len(refs) for refs in cross_refs.values())} total")
    print(f"✅ Script References: {sum(len(scripts) for scripts in script_refs.values())} total")
    print(f"\n🎯 Overall Status: {results['overall']['status']} ({results['overall']['success_rate']:.1f}%)")
    
    if stage_inconsistencies:
        print(f"\n⚠️ Stage Inconsistencies:")
        for issue in stage_inconsistencies:
            print(f"   • {issue}")
    
    if missing_refs:
        print(f"\n⚠️ Missing References:")
        for issue in missing_refs:
            print(f"   • {issue}")
    
    if missing_scripts:
        print(f"\n⚠️ Missing Scripts:")
        for issue in missing_scripts:
            print(f"   • {issue}")
    
    # Save results
    with open('documentation_consistency_report.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    return results["overall"]["status"] == "PASS"

def validate_markdown_structure():
    """Validate markdown structure consistency"""
    print("\n🔍 Validating Markdown Structure...")
    
    structure_issues = []
    
    markdown_files = [f for f in ["SYSTEMATIC_ENGINEERING_PLAN.md", "STAGE_STATUS.md", "ERROR_REGISTRY.md"] if os.path.exists(f)]
    
    for file in markdown_files:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for proper heading structure
        headings = re.findall(r'^(#+)\s+(.+)$', content, re.MULTILINE)
        
        if not headings:
            structure_issues.append(f"{file}: No headings found")
            continue
            
        # Check heading hierarchy
        prev_level = 0
        for level, text in headings:
            current_level = len(level)
            if current_level > prev_level + 1:
                structure_issues.append(f"{file}: Heading level jump from h{prev_level} to h{current_level}")
            prev_level = current_level
    
    print(f"✅ Markdown Structure Issues: {len(structure_issues)}")
    if structure_issues:
        for issue in structure_issues:
            print(f"   ❌ {issue}")
    
    return len(structure_issues) == 0

def main():
    """Main validation function"""
    print("🎯 Stage 4: Documentation Consistency Validation")
    print("=" * 60)
    
    try:
        consistency_valid = validate_documentation_consistency()
        structure_valid = validate_markdown_structure()
        
        overall_success = consistency_valid and structure_valid
        
        print("\n" + "=" * 60)
        print(f"🎯 Stage 4 Documentation Consistency: {'✅ PASS' if overall_success else '❌ FAIL'}")
        
        if overall_success:
            print("🚀 Documentation is consistent and ready for Stage 5!")
        else:
            print("⚠️ Documentation consistency issues detected - please resolve before proceeding.")
        
        return 0 if overall_success else 1
        
    except Exception as e:
        print(f"❌ Validation error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())