#!/usr/bin/env python3
"""
Headless GUI Testing Setup for Jarvis PyQt5 Components
Sets up the environment for running GUI tests in headless mode
"""

import os
import sys
import subprocess
from pathlib import Path

def setup_headless_environment():
    """Configure environment variables for headless PyQt5 testing"""
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    os.environ['DISPLAY'] = ':99'
    
    # Disable Qt debug output for cleaner test results
    os.environ['QT_LOGGING_RULES'] = '*.debug=false'
    
    print("✅ Headless environment configured")
    print(f"   - QT_QPA_PLATFORM: {os.environ.get('QT_QPA_PLATFORM')}")
    print(f"   - DISPLAY: {os.environ.get('DISPLAY')}")

def check_pyqt5_installation():
    """Verify PyQt5 is properly installed"""
    try:
        import PyQt5.QtWidgets
        import PyQt5.QtCore
        import PyQt5.QtGui
        print("✅ PyQt5 installation verified")
        return True
    except ImportError as e:
        print(f"❌ PyQt5 not installed: {e}")
        print("   Install with: sudo apt-get install python3-pyqt5")
        return False

def check_xvfb_availability():
    """Check if xvfb is available for virtual display"""
    try:
        result = subprocess.run(['which', 'xvfb-run'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ xvfb available for virtual display")
            return True
        else:
            print("⚠️  xvfb not found - install with: sudo apt-get install xvfb")
            return False
    except Exception:
        print("⚠️  Could not check xvfb availability")
        return False

def test_basic_pyqt5_functionality():
    """Test basic PyQt5 functionality in headless mode"""
    try:
        from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
        
        app = QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()
        
        # Create a simple window
        window = QMainWindow()
        window.setWindowTitle("Headless Test")
        label = QLabel("PyQt5 headless test")
        window.setCentralWidget(label)
        
        # Test basic functionality
        assert window.windowTitle() == "Headless Test"
        assert label.text() == "PyQt5 headless test"
        
        print("✅ Basic PyQt5 functionality test passed")
        
        if app != QApplication.instance():
            app.quit()
        
        return True
    except Exception as e:
        print(f"❌ Basic PyQt5 functionality test failed: {e}")
        return False

def run_gui_tests():
    """Run the full GUI test suite"""
    test_file = Path(__file__).parent.parent / "tests" / "test_gui_components.py"
    
    if not test_file.exists():
        print(f"❌ Test file not found: {test_file}")
        return False
    
    print("🧪 Running GUI test suite...")
    try:
        result = subprocess.run([
            sys.executable, str(test_file)
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        
        if result.returncode == 0:
            print("✅ GUI test suite passed")
            # Print the last few lines of output for summary
            lines = result.stdout.strip().split('\n')
            for line in lines[-10:]:
                if line.strip() and ('✅' in line or '🎉' in line):
                    print(f"   {line}")
            return True
        else:
            print("❌ GUI test suite failed")
            print("STDOUT:", result.stdout[-500:])  # Last 500 chars
            print("STDERR:", result.stderr[-500:])
            return False
    except Exception as e:
        print(f"❌ Error running GUI tests: {e}")
        return False

def main():
    """Main setup and testing function"""
    print("=" * 70)
    print("🎯 Jarvis PyQt5 Headless Testing Setup")
    print("=" * 70)
    
    # Step 1: Setup environment
    setup_headless_environment()
    
    # Step 2: Check prerequisites
    print("\n📋 Checking Prerequisites...")
    pyqt5_ok = check_pyqt5_installation()
    xvfb_ok = check_xvfb_availability()
    
    if not pyqt5_ok:
        print("\n❌ PyQt5 not available - cannot proceed with GUI tests")
        return False
    
    # Step 3: Test basic functionality
    print("\n🔧 Testing Basic Functionality...")
    basic_test_ok = test_basic_pyqt5_functionality()
    
    if not basic_test_ok:
        print("\n❌ Basic PyQt5 test failed - GUI tests may not work correctly")
        return False
    
    # Step 4: Run full test suite
    print("\n🧪 Running Full Test Suite...")
    tests_ok = run_gui_tests()
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 SETUP SUMMARY")
    print("=" * 70)
    print(f"PyQt5 Installation: {'✅ OK' if pyqt5_ok else '❌ FAILED'}")
    print(f"Xvfb Availability: {'✅ OK' if xvfb_ok else '⚠️  NOT FOUND'}")
    print(f"Basic Functionality: {'✅ OK' if basic_test_ok else '❌ FAILED'}")
    print(f"GUI Test Suite: {'✅ PASSED' if tests_ok else '❌ FAILED'}")
    
    overall_success = pyqt5_ok and basic_test_ok and tests_ok
    
    if overall_success:
        print("\n🎉 HEADLESS GUI TESTING SETUP COMPLETE!")
        print("   All tests passed - PyQt5 GUI system is fully functional")
    else:
        print("\n💥 SETUP INCOMPLETE!")
        print("   Some components failed - check the issues above")
    
    print("=" * 70)
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)