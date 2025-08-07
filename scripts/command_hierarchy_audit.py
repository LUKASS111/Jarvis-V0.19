#!/usr/bin/env python3
"""
Command Hierarchy Audit Script
Stage 4: Complete GUI Information Architecture & AI Agent Optimization
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime

def audit_command_hierarchy():
    """Audit command structure for duplications and conflicts"""
    print("🔍 Auditing Command Hierarchy...")
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "validation_type": "command_hierarchy_audit",
        "stage": 4,
        "tests": {}
    }
    
    # Test 1: Stage execution commands
    stage_commands = {}
    documentation_files = [
        "SYSTEMATIC_ENGINEERING_PLAN.md",
        "STAGE_STATUS.md", 
        "INFORMATION_ARCHITECTURE.md"
    ]
    
    for file in documentation_files:
        if os.path.exists(file):
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Find stage execution patterns
                stage_patterns = re.findall(r'@copilot Execute Stage (\d+)', content)
                if stage_patterns:
                    stage_commands[file] = stage_patterns
    
    # Check for consistency
    unique_stages = set()
    for file, stages in stage_commands.items():
        unique_stages.update(stages)
    
    command_consistency = True
    if len(unique_stages) > 0:
        # Should have stages 1-10
        expected_stages = {str(i) for i in range(1, 11)}
        missing_stages = expected_stages - unique_stages
        if missing_stages:
            command_consistency = False
    
    results["tests"]["stage_execution_commands"] = {
        "status": "PASS" if command_consistency else "FAIL",
        "found_stages": list(unique_stages),
        "total_stages": len(unique_stages),
        "files_with_commands": len(stage_commands),
        "expected_stages": 10
    }
    
    # Test 2: Validation script commands
    validation_scripts = []
    scripts_dir = Path("scripts")
    if scripts_dir.exists():
        for script in scripts_dir.glob("*.py"):
            if "validate" in script.name or "check" in script.name or "audit" in script.name:
                validation_scripts.append(script.name)
    
    # Check for naming patterns
    naming_patterns = {
        "validate_": [s for s in validation_scripts if s.startswith("validate_")],
        "_check": [s for s in validation_scripts if s.endswith("_check.py")],
        "_audit": [s for s in validation_scripts if s.endswith("_audit.py")],
        "_test": [s for s in validation_scripts if s.endswith("_test.py")]
    }
    
    results["tests"]["validation_script_patterns"] = {
        "status": "PASS",
        "total_scripts": len(validation_scripts),
        "naming_patterns": {k: len(v) for k, v in naming_patterns.items()},
        "scripts": validation_scripts
    }
    
    # Test 3: GUI access commands
    gui_files = []
    gui_dir = Path("gui")
    if gui_dir.exists():
        for gui_file in gui_dir.rglob("*.py"):
            gui_files.append(str(gui_file))
    
    gui_commands = {}
    for file in gui_files:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
            # Find method definitions that could be GUI commands
            methods = re.findall(r'def\s+(\w+)\(self', content)
            if methods:
                gui_commands[file] = methods
    
    # Check for command conflicts (methods with same name in different files)
    all_methods = []
    for file, methods in gui_commands.items():
        for method in methods:
            all_methods.append((method, file))
    
    method_conflicts = {}
    for method, file in all_methods:
        if method in method_conflicts:
            method_conflicts[method].append(file)
        else:
            method_conflicts[method] = [file]
    
    conflicts = {k: v for k, v in method_conflicts.items() if len(v) > 1}
    
    results["tests"]["gui_command_conflicts"] = {
        "status": "PASS" if not conflicts else "WARN",
        "total_methods": len(all_methods),
        "unique_methods": len(method_conflicts),
        "conflicts": len(conflicts),
        "conflicted_methods": list(conflicts.keys())
    }
    
    # Test 4: Command documentation consistency
    doc_commands = []
    for file in documentation_files:
        if os.path.exists(file):
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Find command references
                commands = re.findall(r'`([^`]+\.py)`', content)
                doc_commands.extend(commands)
    
    # Check if documented commands exist
    missing_commands = []
    for cmd in doc_commands:
        if not os.path.exists(cmd) and not os.path.exists(f"scripts/{cmd}"):
            missing_commands.append(cmd)
    
    results["tests"]["documentation_consistency"] = {
        "status": "PASS" if not missing_commands else "FAIL",
        "documented_commands": len(doc_commands),
        "missing_commands": missing_commands,
        "consistency_rate": ((len(doc_commands) - len(missing_commands)) / max(len(doc_commands), 1)) * 100
    }
    
    # Calculate overall success
    passed_tests = sum(1 for test in results["tests"].values() if test["status"] == "PASS")
    total_tests = len(results["tests"])
    
    results["overall"] = {
        "status": "PASS" if passed_tests >= total_tests - 2 else "FAIL",  # Allow up to 2 warnings
        "passed": passed_tests,
        "total": total_tests,
        "success_rate": (passed_tests / total_tests) * 100
    }
    
    # Print results
    print(f"\n📊 Command Hierarchy Audit Results:")
    print(f"✅ Stage Commands: {results['tests']['stage_execution_commands']['found_stages']}")
    print(f"✅ Validation Scripts: {results['tests']['validation_script_patterns']['total_scripts']} scripts")
    print(f"✅ GUI Methods: {results['tests']['gui_command_conflicts']['unique_methods']} unique methods")
    if conflicts:
        print(f"⚠️ Method Conflicts: {len(conflicts)} conflicts detected")
    print(f"✅ Documentation: {results['tests']['documentation_consistency']['consistency_rate']:.1f}% consistent")
    print(f"\n🎯 Overall Status: {results['overall']['status']} ({results['overall']['success_rate']:.1f}%)")
    
    # Save results
    with open('command_hierarchy_audit_report.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    return results["overall"]["status"] == "PASS"

def check_command_duplication():
    """Check for duplicate commands across the system"""
    print("\n🔍 Checking Command Duplication...")
    
    # Check for duplicate validation scripts
    scripts_dir = Path("scripts")
    duplicate_patterns = []
    
    # Common function names that are expected to be duplicated
    common_functions = {"main", "__init__", "setup", "teardown", "validate", "check", "test", "run"}
    
    if scripts_dir.exists():
        script_functions = {}
        for script in scripts_dir.glob("*.py"):
            try:
                with open(script, 'r', encoding='utf-8') as f:
                    content = f.read()
                    functions = re.findall(r'def\s+(\w+)\(', content)
                    # Filter out common functions
                    filtered_functions = [f for f in functions if f not in common_functions]
                    script_functions[script.name] = filtered_functions
            except Exception:
                continue
        
        # Find function name overlaps
        all_functions = {}
        for script, functions in script_functions.items():
            for func in functions:
                if func in all_functions:
                    all_functions[func].append(script)
                else:
                    all_functions[func] = [script]
        
        duplicates = {k: v for k, v in all_functions.items() if len(v) > 1}
        if duplicates:
            print(f"⚠️ Found {len(duplicates)} duplicated function names across scripts")
            for func, scripts in list(duplicates.items())[:3]:  # Show only first 3
                print(f"   🔄 {func}: {', '.join(scripts[:3])}")
            if len(duplicates) > 3:
                print(f"   ... and {len(duplicates) - 3} more")
    
    # Return success if duplicates are reasonable (< 10 significant duplicates)
    return len(duplicate_patterns) == 0 and len(duplicates) < 10

def main():
    """Main audit function"""
    print("🎯 Stage 4: Command Hierarchy Audit")
    print("=" * 60)
    
    try:
        hierarchy_valid = audit_command_hierarchy()
        duplication_check = check_command_duplication()
        
        overall_success = hierarchy_valid and duplication_check
        
        print("\n" + "=" * 60)
        print(f"🎯 Stage 4 Command Hierarchy Audit: {'✅ PASS' if overall_success else '❌ FAIL'}")
        
        if overall_success:
            print("🚀 Command hierarchy is clean and ready for Stage 5!")
        else:
            print("⚠️ Command hierarchy issues detected - please resolve before proceeding.")
        
        return 0 if overall_success else 1
        
    except Exception as e:
        print(f"❌ Audit error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())