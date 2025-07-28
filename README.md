# Jarvis v0.19 - AI Assistant with Modular Architecture

🤖 Advanced AI assistant with modern modular architecture, comprehensive testing, and professional GUI interface.

## 🚀 Quick Start

### CLI Mode
```bash
python main.py
```

### GUI Mode (requires PyQt5)
```bash
python start_gui.py
```

### Running Tests
```bash
python run_tests.py
```

### Windows Users
```batch
# Start GUI
scripts\start_gui.bat
```

## 📁 Project Structure

```
jarvis-v0.19/
├── jarvis/                 # Core application modules
│   ├── core/              # Main application logic
│   │   ├── main.py        # Primary entry point
│   │   └── error_handler.py # Error handling system
│   ├── llm/               # LLM interface modules
│   │   └── llm_interface.py # Ollama integration
│   ├── memory/            # Memory management
│   │   └── memory.py      # Persistent fact storage
│   ├── utils/             # Utility modules
│   │   └── logs.py        # Logging system
│   └── plugins/           # Plugin system (extensible)
├── gui/                   # GUI components
│   └── modern_gui.py      # PyQt5 interface
├── tests/                 # Comprehensive test suite
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   ├── regression/        # Regression tests
│   ├── performance/       # Performance tests
│   └── functional/        # Functional tests
├── scripts/               # Development tools
│   ├── run_tests.py       # Test automation
│   └── start_gui.bat      # Windows GUI launcher
├── config/                # Configuration files
├── data/                  # Application data
│   ├── memory_exports/    # Memory backups
│   └── test_reports/      # Test result reports
├── docs/                  # Documentation
└── logs/                  # Application logs
```

## 🔧 Features

### Core Functionality
- 🤖 **Multi-Model LLM Support** - Compatible with Ollama (llama3, codellama)
- 🧠 **Persistent Memory System** - Thread-safe JSON-based fact storage
- 📝 **Comprehensive Logging** - Error tracking, event logging, session management
- 🛡️ **Robust Error Handling** - Multi-level error capture and recovery
- 🏗️ **Modular Architecture** - Clean separation of concerns

### GUI Interface
- 🎨 **Modern Dark Theme** - Professional interface with responsive design
- ⚙️ **LLM Configuration** - Temperature, Top-P, tokens, timeout controls
- 💬 **Interactive Chat** - Real-time conversation with AI models
- 📊 **System Monitoring** - CPU, memory, and performance metrics
- 🔍 **Thread-Safe Updates** - Proper signal handling for concurrent operations

### Testing & Quality Assurance
- ✅ **Comprehensive Test Suite** - 80+ tests across all categories
- 📈 **Automated Test Reports** - JSON-based test result tracking
- 🔄 **Continuous Error Monitoring** - Real-time error tracking and analysis
- 🎯 **High Test Success Rates** - Robust and reliable codebase
- 📊 **Coverage Analysis** - Detailed code coverage reporting

## 📋 Installation

### Prerequisites
```bash
# Install Python dependencies
pip install PyQt5 psutil requests

# Verify Ollama is running (for LLM functionality)
ollama list
```

### Available Models
- `llama3:8b` - Lightweight general-purpose model
- `codellama:13b` - Code-focused model  
- `codellama:34b` - Advanced code model
- `llama3:70b` - High-capacity model

## 🧪 Testing

### Running All Tests
```bash
python run_tests.py
```

### Running Specific Test Categories
```bash
# Unit tests only
python tests/unit/test_unit_comprehensive.py

# Integration tests only  
python tests/integration/test_integration_comprehensive.py

# Performance tests only
python tests/performance/test_performance_comprehensive.py
```

### Test Coverage
Tests cover all core functionality:
- ✅ **Error Handler** - Exception handling and logging
- ✅ **LLM Interface** - Ollama communication and model management
- ✅ **Memory System** - Data persistence and retrieval
- ✅ **GUI Components** - Interface functionality and thread safety
- ✅ **Integration** - Cross-module compatibility
- ✅ **Performance** - Response times and resource usage

## 🔧 Development

### Run All Tests
```bash
# Unit tests
python test/test_unit_comprehensive.py

# Integration tests  
QT_QPA_PLATFORM=offscreen python test/test_integration_comprehensive.py

# Performance tests
python test/test_performance_comprehensive.py

# Full test suite
python test/run_all_tests.py
```

### Test Coverage
Current test success rates:
- **Unit Tests**: 100% (25/25 passing)
- **Integration Tests**: 84.6% (11/13 passing) 
- **Functional Tests**: 100% (6/6 passing)
- **Regression Tests**: 100% (10/10 passing)
- **Performance Tests**: 100% (11/11 passing)

## 🔧 Usage Examples

### Memory Operations
```python
from memory import remember_fact, recall_fact, forget_fact

# Store information
remember_fact("Python version to 3.12")

# Retrieve information  
recall_fact("Python version")  # Returns: "3.12"

# Remove information
forget_fact("Python version")
```

### LLM Interaction
```python
from llm_interface import ask_local_llm
from main import simple_llm_process

# Direct LLM call
response = ask_local_llm("Explain quantum computing")

# Processed LLM call with metadata
result = simple_llm_process("Write a Python function")
print(result["response"])
```

### Error Handling
```python
from error_handler import error_handler, ErrorLevel

@error_handler
def risky_function():
    # Your code here
    pass
```

## 🐛 Recent Fixes (v0.19)

### Critical Issues Resolved
- ✅ **GUI PyQt5 Signal Issue** - Fixed signal connection errors preventing GUI startup
- ✅ **Memory JSON Corruption** - Added robust error handling and atomic file operations
- ✅ **Thread Safety** - Implemented memory locks and proper signal handling
- ✅ **Performance Test Failures** - Fixed bulk logging and LLM interface test issues

### Error Log Analysis
The `error_log.jsonl` contains primarily intentional test errors for validation:
- Test errors are expected behavior for error handling validation
- Real errors are automatically backed up and handled gracefully
- System maintains operational stability during error conditions

## 📈 Performance Metrics

- **Memory Operations**: Thread-safe with atomic writes
- **LLM Calls**: Configurable timeouts (15-120s)
- **Bulk Logging**: >1000 events/sec capability
- **GUI Responsiveness**: Non-blocking UI updates
- **Error Recovery**: Automatic corruption detection and backup

## 🔮 Roadmap

- [ ] **Agent Task Management** - Autonomous task delegation system
- [ ] **Advanced Analytics** - Enhanced performance monitoring
- [ ] **Plugin Architecture** - Extensible module system  
- [ ] **Multi-Language Support** - International localization
- [ ] **Cloud Integration** - Remote model support

## 📞 Support

For issues, feature requests, or contributions, please check the error logs:
```bash
python main.py
# Type 'błędy' to view recent errors
```

---

**Version**: 0.19  
**License**: MIT  
**Python**: 3.6+ Required  
**GUI**: PyQt5 (optional)