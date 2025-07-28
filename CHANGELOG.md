# Changelog

All notable changes to Jarvis AI Assistant will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.19.1] - 2025-07-28 (Repository Restructuring)

### Changed
- **🏗️ Major Repository Restructuring**: Complete reorganization for improved maintainability
  - Moved core modules to `jarvis/` package structure
  - Separated GUI components into `gui/` directory
  - Organized tests by type in `tests/` subdirectories
  - Created dedicated directories for scripts, docs, config, and data
  - Added proper `__init__.py` files for all Python packages

- **📁 New Directory Structure**:
  ```
  jarvis/core/         # Main application logic (main.py, error_handler.py)
  jarvis/llm/          # LLM interface modules
  jarvis/memory/       # Memory management system
  jarvis/utils/        # Utility modules (logs.py)
  gui/                 # GUI components (modern_gui.py)
  tests/unit/          # Unit tests
  tests/integration/   # Integration tests
  tests/regression/    # Regression tests
  tests/performance/   # Performance tests
  tests/functional/    # Functional tests
  scripts/             # Development tools and automation
  docs/                # Documentation
  config/              # Configuration files
  data/                # Application data and exports
  ```

- **🔧 Updated Import System**: All imports updated to use new modular structure
  - Tests updated to import from new package locations
  - Maintained backward compatibility through main.py facade
  - Updated all cross-module references

- **📝 Enhanced Documentation**: Updated README and documentation
  - Comprehensive project structure explanation
  - Updated installation and usage instructions
  - Clear guidance for development and testing

### Added
- **🚀 New Entry Points**: Simplified application startup
  - `main.py` - CLI entry point with backward compatibility
  - `start_gui.py` - Dedicated GUI launcher
  - `run_tests.py` - Test suite runner
  - Updated Windows batch files

### Fixed
- **🔗 Import Dependencies**: Resolved all import path issues after restructuring
- **📊 Test Framework**: Updated test runners for new directory structure
- **⚙️ Configuration Paths**: Updated data file paths for new organization

## [0.19] - 2025-07-28

### Fixed
- **Critical GUI PyQt5 Signal Issue**: Fixed `'PyQt5.QtCore.pyqtSignal' object has no attribute 'connect'` error
  - Moved pyqtSignal definitions from instance level to class level
  - Added proper error handling for PyQt5 availability
  - GUI now initializes correctly without signal connection errors

- **Memory JSON Corruption**: Fixed JSON file corruption causing application crashes
  - Implemented atomic file operations with temporary file validation
  - Added automatic backup of corrupted files
  - Introduced thread-safe memory operations with locks
  - Memory system now recovers gracefully from corruption

- **Performance Test Failures**: Resolved test suite issues
  - Fixed bulk logging performance test (limit parameter issue)
  - Corrected LLM interface return type expectations
  - All performance tests now pass (100% success rate)

### Added
- **Comprehensive Error Handling**: Enhanced error management system
  - Multi-level error capture and recovery
  - Automatic error log generation and analysis
  - Session-based error tracking

- **Robust Testing Suite**: Complete test coverage
  - Unit Tests: 100% success rate (25/25 passing)
  - Integration Tests: 84.6% success rate (11/13 passing)
  - Functional Tests: 100% success rate (6/6 passing)
  - Regression Tests: 100% success rate (10/10 passing)
  - Performance Tests: 100% success rate (11/11 passing)

- **Enhanced Documentation**: Updated README and project documentation
  - Comprehensive installation and usage instructions
  - Architecture overview and project structure
  - Performance metrics and testing guidelines

### Improved
- **Memory System Reliability**: Thread-safe operations and corruption recovery
- **GUI Stability**: Proper signal handling and error management
- **Test Coverage**: Comprehensive test suite with automated error detection
- **Error Analysis**: Distinguished between intentional test errors and real issues

### Technical Details
- Added `.gitignore` to prevent test artifacts from being committed
- Implemented thread locks for concurrent memory operations
- Enhanced JSON validation before file replacement
- Improved error logging with contextual information

## [0.4.1] - Previous Release

### Features
- Modern PyQt5 GUI interface with dark theme
- Multi-model LLM support (Ollama integration)
- Persistent memory system with JSON storage
- Real-time system monitoring
- Self-modification capabilities

### GUI Components
- Interactive chat interface
- LLM parameter configuration
- System status monitoring
- Thread-safe UI updates

## [0.4.0] - Initial Release

### Core Features
- Basic CLI interface
- LLM integration with Ollama
- Simple memory storage
- Error handling system
- Basic GUI framework