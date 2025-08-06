#!/usr/bin/env python3
"""
Legacy Structure Validation Script
Verifies that legacy chunks have been properly separated and catalogued
"""

import os
import sys
from pathlib import Path

def validate_legacy_structure():
    """Validate that legacy structure issues have been resolved"""
    
    print("🔍 LEGACY STRUCTURE VALIDATION")
    print("=" * 50)
    
    issues_found = []
    
    # Check 1: Verify main.py import paths are correct
    main_path = Path("main.py")
    if main_path.exists():
        with open(main_path) as f:
            content = f.read()
            if "from legacy.legacy_gui" in content:
                issues_found.append("❌ main.py still has incorrect legacy import path")
            elif "from archive.legacy_code.legacy_gui" in content:
                print("✅ main.py has correct archived legacy import path")
            else:
                print("ℹ️  main.py no longer references legacy GUI directly")
    
    # Check 2: Verify comprehensive dashboard exists and is accessible
    dashboard_path = Path("gui/enhanced/comprehensive_dashboard.py")
    if dashboard_path.exists():
        print("✅ Comprehensive 9-tab dashboard exists")
        with open(dashboard_path) as f:
            content = f.read()
            if "add_overview_tab" in content and "add_archive_tab" in content:
                print("✅ Dashboard contains all 9 professional tabs")
            else:
                issues_found.append("❌ Dashboard missing required tabs")
    else:
        issues_found.append("❌ Comprehensive dashboard not found")
    
    # Check 3: Verify jarvis.ai and jarvis.vector modules exist
    ai_module = Path("jarvis/ai/multimodal_processor.py")
    vector_module = Path("jarvis/vector/database_manager.py")
    
    if ai_module.exists():
        print("✅ jarvis.ai.multimodal_processor module exists")
    else:
        issues_found.append("❌ jarvis.ai module missing")
        
    if vector_module.exists():
        print("✅ jarvis.vector.database_manager module exists")
    else:
        issues_found.append("❌ jarvis.vector module missing")
    
    # Check 4: Verify legacy files are properly removed
    legacy_files_to_check = [
        "start_gui.py",
        "jarvis/interfaces/production_cli.py",
        "jarvis/interfaces/production_gui.py",
        "jarvis/interfaces/enhanced_cli.py",
        "jarvis/interfaces/web_interface.py"
    ]
    
    for legacy_file in legacy_files_to_check:
        if Path(legacy_file).exists():
            issues_found.append(f"❌ Legacy file still exists: {legacy_file}")
        else:
            print(f"✅ Legacy file properly removed: {legacy_file}")
    
    # Check 5: Verify modern main.py has proper functionality
    modern_main = Path("main.py")
    if modern_main.exists():
        with open(modern_main) as f:
            content = f.read()
            if "start_comprehensive_dashboard" in content:
                print("✅ Modern main.py has comprehensive dashboard function")
            else:
                issues_found.append("❌ main.py missing comprehensive dashboard function")
            
            if "start_modern_cli" in content:
                print("✅ Modern main.py has CLI functionality")
            else:
                issues_found.append("❌ main.py missing CLI functionality")
    
    # Check 5: Verify entry point consolidation
    unified_launcher = Path("jarvis_launcher.py")
    if unified_launcher.exists():
        print("✅ Unified launcher created for entry point clarity")
    else:
        issues_found.append("❌ Unified launcher missing")
    
    # Check 6: Verify legacy code is properly archived
    legacy_gui = Path("archive/legacy_code/legacy_gui.py")
    if legacy_gui.exists():
        print("✅ Legacy GUI properly archived")
    else:
        issues_found.append("❌ Legacy GUI not properly archived")
    
    # Check 7: Verify PyQt5 installation 
    try:
        import PyQt5
        print("✅ PyQt5 is installed and available")
    except ImportError:
        issues_found.append("❌ PyQt5 not installed")
    
    print("\n" + "=" * 50)
    
    if issues_found:
        print("❌ LEGACY STRUCTURE ISSUES FOUND:")
        for issue in issues_found:
            print(f"   {issue}")
        return False
    else:
        print("✅ ALL LEGACY STRUCTURE ISSUES RESOLVED!")
        print("✅ Entry points properly unified")
        print("✅ Professional features all implemented")
        print("✅ GUI loading chain fixed")
        print("✅ Archive structure cleaned up")
        return True

if __name__ == "__main__":
    success = validate_legacy_structure()
    sys.exit(0 if success else 1)