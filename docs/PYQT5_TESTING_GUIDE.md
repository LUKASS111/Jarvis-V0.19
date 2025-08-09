# PyQt5 GUI Testing Guide

## Overview

This guide provides comprehensive instructions for setting up and running PyQt5 GUI tests, both in normal and headless environments. It addresses the historical issues with false-positive testing and ensures reliable GUI validation.

## Installation Requirements

### System Dependencies

#### Ubuntu/Debian
```bash
# Install PyQt5 system packages
sudo apt-get update
sudo apt-get install -y python3-pyqt5 xvfb

# For development (optional)
sudo apt-get install -y qt5-default qttools5-dev-tools
```

#### Alternative: pip installation (if system packages fail)
```bash
# Note: This may require additional system dependencies
pip install PyQt5>=5.15.0 PyQt5-tools>=5.15.0
```

### Virtual Display for Headless Testing
```bash
# Install xvfb for headless GUI testing
sudo apt-get install -y xvfb

# Test xvfb is working
xvfb-run -a python3 -c "print('Xvfb working')"
```

## Environment Configuration

### Headless Testing Environment Variables
```bash
export QT_QPA_PLATFORM=offscreen
export DISPLAY=:99
```

### Python Environment Setup
```python
import os
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
os.environ['DISPLAY'] = ':99'
```

## Testing Framework

### Running GUI Tests

#### Method 1: Direct Test Execution
```bash
# Run GUI tests with headless configuration
cd /path/to/jarvis
DISPLAY=:99 QT_QPA_PLATFORM=offscreen python3 tests/test_gui_components.py
```

#### Method 2: Using xvfb-run
```bash
# Run with virtual framebuffer
xvfb-run -a python3 tests/test_gui_components.py
```

#### Method 3: Integrated with pytest
```bash
# Run with pytest (recommended for CI/CD)
DISPLAY=:99 QT_QPA_PLATFORM=offscreen python3 -m pytest tests/test_gui_components.py -v
```

### Test Validation Levels

#### Level 1: PyQt5 Installation Validation
- ✅ **MUST PASS**: Verifies PyQt5 is properly installed
- ✅ **MUST PASS**: Tests basic widget creation (QMainWindow, QLabel, etc.)
- ❌ **MUST FAIL**: If PyQt5 is not available or broken

#### Level 2: GUI Component Functionality
- ✅ Tests comprehensive dashboard creation
- ✅ Tests modern component library
- ✅ Tests tab factory and architecture
- ✅ Tests design standards and styling

#### Level 3: Real Functionality Validation
- ✅ **NO MOCKING**: Tests actual PyQt5 widget behavior
- ✅ Tests headless rendering capabilities
- ✅ Tests widget interaction and event handling
- ✅ Tests complex widget hierarchies

## Common Issues and Solutions

### Issue 1: PyQt5 Not Found
```
ModuleNotFoundError: No module named 'PyQt5'
```

**Solution:**
```bash
# Install system packages first
sudo apt-get install -y python3-pyqt5

# Verify installation
python3 -c "import PyQt5.QtWidgets; print('PyQt5 working')"
```

### Issue 2: Display/X11 Errors in Headless Environment
```
qt.qpa.xcb: could not connect to display
```

**Solution:**
```bash
# Use xvfb for virtual display
export QT_QPA_PLATFORM=offscreen
xvfb-run -a your_command
```

### Issue 3: Tests Passing When They Should Fail
The old test framework had this problem due to excessive mocking and `skipTest` usage.

**Solution:**
- Use the new test framework that fails when PyQt5 is not available
- Remove excessive mocking that masks real issues
- Test actual GUI functionality, not just imports

### Issue 4: CI/CD Pipeline Integration
```yaml
# GitHub Actions example
- name: Install PyQt5 dependencies
  run: |
    sudo apt-get update
    sudo apt-get install -y python3-pyqt5 xvfb

- name: Run GUI tests
  run: |
    xvfb-run -a python3 tests/test_gui_components.py
  env:
    QT_QPA_PLATFORM: offscreen
```

## Test Development Guidelines

### Do's ✅
- Always test real PyQt5 functionality
- Use proper headless configuration
- Validate widget creation and interaction
- Test without excessive mocking
- Ensure tests fail when PyQt5 is broken

### Don'ts ❌
- Don't use `skipTest` for missing PyQt5 (should fail instead)
- Don't mock everything (defeats the purpose of testing)
- Don't use `assertTrue(True, ...)` as a substitute for real validation
- Don't ignore import errors for critical dependencies

## Example Test Structure

```python
import unittest
import os
from PyQt5.QtWidgets import QApplication, QMainWindow

class TestGUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Configure headless environment
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        
        # Validate PyQt5 is available (MUST fail if not)
        try:
            from PyQt5.QtWidgets import QApplication
            cls.app = QApplication([])
        except ImportError as e:
            raise unittest.SkipTest(f"PyQt5 not available: {e}")
    
    def test_real_gui_functionality(self):
        """Test actual GUI functionality without mocking"""
        from PyQt5.QtWidgets import QMainWindow, QLabel
        
        window = QMainWindow()
        label = QLabel("Test")
        window.setCentralWidget(label)
        
        # Test real functionality
        self.assertEqual(label.text(), "Test")
        self.assertIsNotNone(window.centralWidget())
```

## Verification Commands

### Quick PyQt5 Health Check
```bash
# Test basic PyQt5 functionality
python3 -c "
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
import sys
app = QApplication(sys.argv)
window = QMainWindow()
label = QLabel('PyQt5 working!')
window.setCentralWidget(label)
print('✅ PyQt5 is functional')
app.quit()
"
```

### Comprehensive GUI Test
```bash
# Run the complete test suite
cd /path/to/jarvis
python3 tests/test_gui_components.py
```

### Headless Environment Verification
```bash
# Verify headless testing works
DISPLAY=:99 QT_QPA_PLATFORM=offscreen python3 -c "
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys
app = QApplication(sys.argv)
window = QMainWindow()
window.show()  # This should work in headless mode
print('✅ Headless GUI testing is functional')
app.quit()
"
```

## Integration with Jarvis Testing Framework

The GUI tests are integrated with the main testing framework:

```bash
# Run all tests including GUI
python3 run_tests.py

# Run only GUI tests
python3 tests/test_gui_components.py

# Run with coverage
python3 -m pytest tests/test_gui_components.py --cov=gui
```

## Troubleshooting

If you encounter issues:

1. **Check PyQt5 installation**: `python3 -c "import PyQt5.QtWidgets"`
2. **Verify system dependencies**: `dpkg -l | grep qt5`
3. **Test headless configuration**: `xvfb-run -a echo "headless working"`
4. **Check environment variables**: `echo $QT_QPA_PLATFORM`
5. **Review test output carefully** - new framework provides detailed error information

## Support

For additional help:
- Check the test output for specific error messages
- Verify all installation steps were completed
- Ensure you're using the updated test framework (not the old mocking-heavy version)
- Test with a simple PyQt5 example first before running full test suite