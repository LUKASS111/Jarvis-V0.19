#!/usr/bin/env python3
"""
Unified GUI Launcher for Jarvis V0.19
Professional launcher that detects and launches the best available GUI interface.
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def launch_enhanced_gui():
    """Launch the comprehensive enhanced GUI"""
    try:
        from gui.enhanced.comprehensive_dashboard import launch_comprehensive_dashboard
        print("🚀 Launching Jarvis V0.19 Comprehensive Professional Dashboard...")
        return launch_comprehensive_dashboard()
    except ImportError as e:
        print(f"❌ Enhanced GUI not available: {e}")
        return False

def launch_production_gui():
    """Launch the production GUI as fallback"""
    try:
        from jarvis.interfaces.production_gui import launch_production_gui
        print("🚀 Launching Jarvis V0.19 Production GUI...")
        return launch_production_gui()
    except ImportError as e:
        print(f"❌ Production GUI not available: {e}")
        return False

def launch_basic_gui():
    """Launch the basic GUI as final fallback"""
    try:
        from main import main_gui
        print("🚀 Launching Jarvis V0.19 Basic GUI...")
        return main_gui()
    except ImportError as e:
        print(f"❌ Basic GUI not available: {e}")
        return False

def main():
    """Main launcher function"""
    print("🎯 JARVIS V0.19 PROFESSIONAL GUI LAUNCHER")
    print("=" * 50)
    
    # Try to launch GUIs in order of preference
    gui_options = [
        ("Enhanced Professional Dashboard", launch_enhanced_gui),
        ("Production GUI", launch_production_gui),
        ("Basic GUI", launch_basic_gui)
    ]
    
    for gui_name, gui_func in gui_options:
        print(f"🔄 Attempting to launch {gui_name}...")
        try:
            result = gui_func()
            if result is not False:
                print(f"✅ {gui_name} launched successfully")
                return result
        except Exception as e:
            print(f"❌ {gui_name} failed: {e}")
            continue
    
    # If all GUIs fail, offer CLI
    print("\n⚠️ No GUI interfaces available")
    print("🔧 Falling back to Enhanced CLI...")
    
    try:
        from jarvis.interfaces.enhanced_cli import main as cli_main
        cli_main()
    except ImportError:
        print("❌ Enhanced CLI not available either")
        print("💡 Try running: python -m jarvis.interfaces.production_cli")
        return 1

if __name__ == "__main__":
    sys.exit(main())