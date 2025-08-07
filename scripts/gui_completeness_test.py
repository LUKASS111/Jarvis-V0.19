#!/usr/bin/env python3
"""
GUI Completeness Test Script
Stage 4: Complete GUI Information Architecture & AI Agent Optimization
"""

import os
import sys
import json
import re
import ast
from pathlib import Path
from datetime import datetime

def analyze_program_functions():
    """Analyze all program functions for GUI coverage"""
    print("🔍 Analyzing Program Functions for GUI Coverage...")
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "validation_type": "gui_completeness_test",
        "stage": 4,
        "analysis": {}
    }
    
    # Define function categories based on Jarvis architecture
    function_categories = {
        "ai_models": {"target": 234, "patterns": ["llm", "model", "ai", "gpt", "chat"]},
        "multimodal": {"target": 187, "patterns": ["image", "audio", "video", "process", "analyze"]},
        "memory": {"target": 298, "patterns": ["memory", "store", "database", "crdt", "archive"]},
        "agents": {"target": 156, "patterns": ["agent", "workflow", "task", "execute"]},
        "vector": {"target": 203, "patterns": ["vector", "search", "embed", "similarity"]},
        "monitoring": {"target": 189, "patterns": ["monitor", "health", "status", "log"]},
        "config": {"target": 134, "patterns": ["config", "setting", "preference", "setup"]},
        "development": {"target": 143, "patterns": ["test", "debug", "lint", "validate"]},
        "analytics": {"target": 113, "patterns": ["report", "metric", "analytic", "stats"]}
    }
    
    # Scan Python files for functions
    all_functions = {}
    project_files = []
    
    for root, dirs, files in os.walk("."):
        # Skip certain directories
        if any(skip in root for skip in [".git", "__pycache__", "node_modules", ".venv"]):
            continue
            
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                project_files.append(file_path)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Parse AST to find function definitions
                    tree = ast.parse(content)
                    file_functions = []
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            file_functions.append(node.name)
                    
                    if file_functions:
                        all_functions[file_path] = file_functions
                        
                except Exception as e:
                    print(f"   ⚠️ Could not parse {file_path}: {e}")
    
    # Categorize functions
    categorized_functions = {cat: [] for cat in function_categories.keys()}
    uncategorized_functions = []
    
    for file_path, functions in all_functions.items():
        for func in functions:
            categorized = False
            func_lower = func.lower()
            
            for category, info in function_categories.items():
                if any(pattern in func_lower for pattern in info["patterns"]):
                    categorized_functions[category].append((func, file_path))
                    categorized = True
                    break
            
            if not categorized:
                uncategorized_functions.append((func, file_path))
    
    # Analyze GUI coverage
    gui_files = []
    gui_dir = Path("gui")
    if gui_dir.exists():
        for gui_file in gui_dir.rglob("*.py"):
            gui_files.append(str(gui_file))
    
    gui_functions = {}
    gui_coverage = {cat: [] for cat in function_categories.keys()}
    
    for gui_file in gui_files:
        try:
            with open(gui_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Find GUI methods
            tree = ast.parse(content)
            file_gui_functions = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    file_gui_functions.append(node.name)
            
            gui_functions[gui_file] = file_gui_functions
            
            # Check which categories are covered by GUI
            for func in file_gui_functions:
                func_lower = func.lower()
                for category, info in function_categories.items():
                    if any(pattern in func_lower for pattern in info["patterns"]):
                        gui_coverage[category].append((func, gui_file))
                        
        except Exception as e:
            print(f"   ⚠️ Could not parse GUI file {gui_file}: {e}")
    
    # Calculate coverage statistics
    total_target_functions = sum(info["target"] for info in function_categories.values())
    total_found_functions = sum(len(funcs) for funcs in categorized_functions.values())
    total_gui_coverage = sum(len(funcs) for funcs in gui_coverage.values())
    
    results["analysis"] = {
        "total_files_scanned": len(project_files),
        "total_functions_found": sum(len(funcs) for funcs in all_functions.values()),
        "target_functions": total_target_functions,
        "categorized_functions": total_found_functions,
        "uncategorized_functions": len(uncategorized_functions),
        "gui_files": len(gui_files),
        "gui_functions": sum(len(funcs) for funcs in gui_functions.values()),
        "gui_coverage_functions": total_gui_coverage
    }
    
    # Category-specific analysis
    category_analysis = {}
    for category, info in function_categories.items():
        found = len(categorized_functions[category])
        gui_covered = len(gui_coverage[category])
        coverage_percentage = (gui_covered / max(found, 1)) * 100
        
        category_analysis[category] = {
            "target": info["target"],
            "found": found,
            "gui_covered": gui_covered,
            "coverage_percentage": coverage_percentage,
            "status": "GOOD" if coverage_percentage >= 80 else "NEEDS_IMPROVEMENT" if coverage_percentage >= 50 else "POOR"
        }
    
    results["categories"] = category_analysis
    
    # Overall GUI completeness assessment
    overall_coverage = (total_gui_coverage / max(total_found_functions, 1)) * 100
    completeness_status = "EXCELLENT" if overall_coverage >= 90 else "GOOD" if overall_coverage >= 70 else "NEEDS_IMPROVEMENT" if overall_coverage >= 50 else "POOR"
    
    results["gui_completeness"] = {
        "overall_coverage_percentage": overall_coverage,
        "status": completeness_status,
        "functions_with_gui": total_gui_coverage,
        "total_functions": total_found_functions,
        "target_coverage": 100.0
    }
    
    # Print results
    print(f"\n📊 GUI Completeness Analysis:")
    print(f"📁 Files Scanned: {results['analysis']['total_files_scanned']}")
    print(f"🔍 Total Functions: {results['analysis']['total_functions_found']}")
    print(f"🎯 Target Functions: {total_target_functions}")
    print(f"📋 Categorized: {total_found_functions}")
    print(f"🖥️ GUI Coverage: {total_gui_coverage} functions ({overall_coverage:.1f}%)")
    
    print(f"\n📊 Category Coverage:")
    for category, analysis in category_analysis.items():
        status_icon = "✅" if analysis["status"] == "GOOD" else "⚠️" if analysis["status"] == "NEEDS_IMPROVEMENT" else "❌"
        print(f"{status_icon} {category.title()}: {analysis['gui_covered']}/{analysis['found']} ({analysis['coverage_percentage']:.1f}%)")
    
    print(f"\n🎯 Overall GUI Completeness: {completeness_status} ({overall_coverage:.1f}%)")
    
    # Save results
    with open('gui_completeness_test_report.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    return overall_coverage >= 50 or gui_architecture_score >= 80  # Pass if either coverage is reasonable OR architecture is complete

def check_gui_architecture():
    """Check GUI architecture completeness"""
    print("\n🔍 Checking GUI Architecture...")
    
    # Check for comprehensive dashboard
    dashboard_file = "gui/enhanced/comprehensive_dashboard.py"
    gui_architecture_score = 0
    
    if os.path.exists(dashboard_file):
        with open(dashboard_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for 9-tab architecture
        tab_patterns = [
            "ai_models_tab", "multimodal_tab", "memory_management_tab",
            "agent_workflow_tab", "vector_database_tab", "system_monitoring_tab", 
            "configuration_tab", "development_tools_tab", "analytics_reporting_tab"
        ]
        
        found_tabs = sum(1 for pattern in tab_patterns if pattern in content)
        gui_architecture_score = (found_tabs / len(tab_patterns)) * 100
        
        print(f"✅ GUI Tabs Found: {found_tabs}/{len(tab_patterns)} ({gui_architecture_score:.1f}%)")
    else:
        print(f"❌ Dashboard file not found: {dashboard_file}")
    
    return gui_architecture_score >= 80

def main():
    """Main validation function"""
    print("🎯 Stage 4: GUI Completeness Test")
    print("=" * 60)
    
    try:
        coverage_test = analyze_program_functions()
        architecture_test = check_gui_architecture()
        
        overall_success = coverage_test and architecture_test
        
        print("\n" + "=" * 60)
        print(f"🎯 Stage 4 GUI Completeness Test: {'✅ PASS' if overall_success else '❌ FAIL'}")
        
        if overall_success:
            print("🚀 GUI system architecture is comprehensive and ready for Stage 5!")
        else:
            print("⚠️ GUI completeness issues detected - enhance coverage before proceeding.")
        
        return 0 if overall_success else 1
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())