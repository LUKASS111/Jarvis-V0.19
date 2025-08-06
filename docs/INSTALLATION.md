# Installation & Setup Guide

## System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, Linux
- **Memory**: 4GB+ RAM recommended
- **Storage**: 2GB free space
- **Optional**: GPU for enhanced AI processing

## Dependencies Installation

### Core Dependencies
```bash
pip install PyQt5 psutil requests sqlite3
```

### AI/ML Dependencies (Optional)
```bash
pip install transformers torch chromadb
```

### Development Dependencies (Optional)
```bash
pip install pytest pytest-cov black flake8
```

## Installation Steps

1. **Clone Repository**
   ```bash
   git clone https://github.com/LUKASS111/Jarvis-V0.19.git
   cd Jarvis-V0.19
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize System**
   ```bash
   python scripts/test_database.py  # Verify system health
   ```

4. **First Launch**
   ```bash
   python main.py  # Start GUI mode
   ```

## Configuration

### Environment Setup
Create a `.env` file in the root directory:
```env
JARVIS_MODE=production
DEBUG=false
LLM_PROVIDER=ollama
OLLAMA_HOST=localhost:11434
```

### Database Configuration
The system uses SQLite databases stored in `data/`:
- `jarvis_archive.db` - Main data archive
- `jarvis_memory.db` - Memory system
- `health.db` - System health metrics

## Troubleshooting Installation

### Common Issues

1. **PyQt5 Installation Issues**
   ```bash
   # On Ubuntu/Debian
   sudo apt-get install python3-pyqt5
   
   # On macOS with Homebrew
   brew install pyqt5
   ```

2. **Database Corruption**
   ```bash
   python scripts/repair_databases.py
   ```

3. **Permission Issues**
   ```bash
   chmod +x scripts/*.py
   ```

## Verification

After installation, verify everything works:
```bash
python run_tests.py           # Run test suite
python main.py --cli         # Test CLI mode
python main.py              # Test GUI mode
```

## Next Steps

- See `ARCHITECTURE.md` for system overview
- See `API_REFERENCE.md` for development
- See `DEVELOPMENT.md` for contributing