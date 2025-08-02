# Jarvis AI Assistant - Unified Entry Point

## Overview

The Jarvis AI Assistant now uses a unified entry point system that ensures consistent initialization and behavior regardless of how the application is started. This eliminates duplication and ensures that critical startup tasks (like archive cleanup and version management) always run.

## Features

- **Single entry point**: All startup methods now route through `main.py`
- **Unified initialization**: Archive cleanup, version management, and health scoring run regardless of mode
- **Mode detection**: Automatically detects whether to run CLI or GUI mode
- **Legacy compatibility**: Old startup methods still work but redirect to unified entry point
- **Command-line interface**: Full argument parsing with help and version information

## Usage

### Auto-Detection Mode (Recommended)
```bash
python main.py
```
Automatically detects the best mode based on environment:
- GUI mode if display is available and PyQt5 is installed
- CLI mode for headless/terminal environments

### Explicit Mode Selection
```bash
# Force CLI mode
python main.py --cli

# Force GUI mode  
python main.py --gui

# Show version information
python main.py --version

# Show help
python main.py --help
```

### Legacy Methods (Still Supported)
```bash
# Legacy GUI launchers (redirect to unified entry point)
python start_gui.py
python -m gui.modern_gui

# Batch file (Windows)
scripts\start_gui.bat
```

## Startup Process

Every application start now follows this unified sequence:

1. **Version Detection**: Automatically detects current program version
2. **Archive Cleanup**: Removes all data from older program versions  
3. **Health Assessment**: Calculates and displays system health score
4. **Mode Selection**: Determines CLI vs GUI mode
5. **Application Launch**: Starts the appropriate interface

### Example Startup Output
```
[LAUNCH] Jarvis 0.2 - CLI Mode
============================================================
[STARTUP] Initializing automatic version-based archive cleanup...
[PURGE] Current version: 0.2
[PURGE] Archive is clean - no old version data found
[ARCHIVE] Health Score: 100/100, Size: 0.0MB, Entries: 4
[BRAIN] Jarvis CLI uruchomiony. Zadaj pytanie...
```

## Benefits

- **Consistency**: Same initialization regardless of startup method
- **Reliability**: Critical startup tasks always execute
- **Maintainability**: Single point of configuration and initialization
- **User Experience**: Clear feedback on system health and version
- **Future-proof**: Easy to add new startup tasks or modes

## Architecture

```
main.py (Unified Entry Point)
├── Auto-detection or explicit mode selection
├── run_startup_initialization()
│   ├── Archive cleanup and version management
│   ├── Health score calculation
│   └── System status reporting
├── main_cli() → jarvis.core.main.main()
└── main_gui() → gui.modern_gui.SimplifiedJarvisGUI.run()
```

All legacy entry points (`start_gui.py`, `scripts/start_gui.bat`, `python -m gui.modern_gui`) now redirect to this unified system, ensuring consistent behavior while maintaining backward compatibility.

## Development Notes

- The `jarvis.core.main.main()` function now accepts a `skip_startup_init` parameter to avoid duplicate initialization
- GUI module redirects direct calls to the unified entry point
- All startup logic is centralized in the `run_startup_initialization()` function
- Mode detection uses environment variables and module availability to determine the best interface

This unified approach ensures that the Jarvis AI Assistant always starts with a clean, properly initialized state and provides consistent behavior across all usage scenarios.