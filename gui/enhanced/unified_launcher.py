#!/usr/bin/env python3
"""
Modern GUI Launcher for Jarvis V1.0
Professional 9-tab comprehensive dashboard launcher only.
All legacy fallbacks removed.
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def launch_comprehensive_dashboard():
    """Launch the modern 9-tab comprehensive dashboard"""
    try:
        from gui.enhanced.comprehensive_dashboard import launch_comprehensive_dashboard
        print("🚀 Launching Jarvis V1.0 Comprehensive Professional Dashboard...")
        print("📊 Features: Overview, Archive, CRDT, Vector DB, Agents, Monitoring, Security, API, Deployment")
        return launch_comprehensive_dashboard()
    except ImportError as e:
        print(f"❌ Comprehensive dashboard not available: {e}")
        print("💡 Install PyQt5: pip install PyQt5")
        return False
    except Exception as e:
        print(f"❌ Dashboard startup failed: {e}")
        return False

def main():
    """Main launcher function - Comprehensive dashboard only"""
    print("🎯 JARVIS V1.0 MODERN PROFESSIONAL LAUNCHER")
    print("=" * 50)
    
    # Launch comprehensive dashboard only - no legacy fallbacks
    print("🔄 Launching Comprehensive Professional Dashboard...")
    
    try:
        result = launch_comprehensive_dashboard()
        if result is not False:
            print("✅ Comprehensive dashboard launched successfully")
            return 0
        else:
            print("❌ Dashboard failed to launch")
            return 1
    except Exception as e:
        print(f"❌ Dashboard launch failed: {e}")
        print("💡 Try: python main.py --cli")
        return 1

if __name__ == "__main__":
    sys.exit(main())