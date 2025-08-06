# Troubleshooting Guide

## Common Issues and Solutions

### Database Issues

#### "file is not a database" Error
This is the most common issue when starting Jarvis.

**Symptoms:**
```
sqlite3.DatabaseError: file is not a database
```

**Solution:**
```bash
# Fix corrupted databases
python scripts/repair_databases.py

# Verify system health
python scripts/test_database.py

# If issues persist, reset databases
rm data/*.db
python main.py  # Will recreate databases
```

#### Database Corruption
**Symptoms:**
- Slow database operations
- Intermittent SQLite errors
- Missing data

**Solution:**
```bash
# Check database integrity
python scripts/test_database.py --integrity

# Repair specific database
python scripts/repair_databases.py --database jarvis_archive.db

# Full system repair
python scripts/repair_databases.py --full
```

### GUI Issues

#### PyQt5 Not Found
**Symptoms:**
```
ModuleNotFoundError: No module named 'PyQt5'
```

**Solution:**
```bash
# Windows
pip install PyQt5

# macOS with Homebrew
brew install pyqt5

# Ubuntu/Debian
sudo apt-get install python3-pyqt5

# If still issues, try:
pip install --upgrade PyQt5
```

#### GUI Not Loading (Shows 4 tabs instead of 9)
**Symptoms:**
- Basic interface with only 4 tabs
- Missing professional dashboard features

**Solution:**
```bash
# Check if comprehensive dashboard is available
python -c "from gui.enhanced.comprehensive_dashboard import main; print('Dashboard available')"

# Force GUI mode
python main.py --force-gui

# Check for missing dependencies
pip install -r requirements.txt
```

#### GUI Crashes on Startup
**Symptoms:**
- GUI window opens then immediately closes
- Qt-related error messages

**Solution:**
```bash
# Check system environment
export QT_DEBUG_PLUGINS=1
python main.py

# Try CLI mode first
python main.py --cli

# Check for conflicts
pip list | grep -i qt
```

### LLM Integration Issues

#### Ollama Connection Failed
**Symptoms:**
```
LLMProviderException: Ollama interface not available
```

**Solution:**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/version

# Start Ollama service
ollama serve

# Test specific model
ollama run llama3:8b "Hello"

# Configure alternative provider
export LLM_PROVIDER=openai
export OPENAI_API_KEY=your_key
```

#### Model Not Found
**Symptoms:**
```
Model 'llama3:8b' not found
```

**Solution:**
```bash
# List available models
ollama list

# Pull required model
ollama pull llama3:8b

# Use alternative model
python main.py --model codellama:13b
```

### Performance Issues

#### Slow System Response
**Symptoms:**
- Long delays in operations
- High CPU/memory usage
- Unresponsive interface

**Diagnosis:**
```bash
# Check system health
python system_dashboard.py

# Monitor performance
python scripts/performance_monitor.py

# Check CRDT sync status
python -c "from jarvis.core import get_crdt_manager; print(get_crdt_manager().get_sync_status())"
```

**Solutions:**
```bash
# Clear cache and temporary files
python scripts/cleanup_cache.py

# Optimize database
python scripts/optimize_databases.py

# Restart with fresh state
python main.py --fresh-start
```

#### Memory Leaks
**Symptoms:**
- Gradually increasing memory usage
- System becomes slower over time

**Solution:**
```bash
# Monitor memory usage
python scripts/memory_monitor.py

# Restart backend service
python main.py --restart-backend

# Clear memory caches
python scripts/clear_memory_cache.py
```

### Network/CRDT Issues

#### CRDT Synchronization Failures
**Symptoms:**
```
CRDTException: Sync failed with peer nodes
```

**Solution:**
```bash
# Check network connectivity
python -c "from jarvis.core.crdt.crdt_network import test_connectivity; test_connectivity()"

# Reset network state
python scripts/reset_crdt_network.py

# Check firewall settings
# Ensure ports 8000-8010 are open for CRDT sync
```

#### Conflict Resolution Issues
**Symptoms:**
- Data inconsistencies between nodes
- Unresolved conflicts in logs

**Solution:**
```bash
# Force conflict resolution
python scripts/resolve_crdt_conflicts.py

# Reset to last known good state
python scripts/restore_crdt_backup.py

# Check mathematical guarantees
python tests/test_crdt_comprehensive.py
```

### Installation Issues

#### Permission Errors
**Symptoms:**
```
PermissionError: [Errno 13] Permission denied
```

**Solution:**
```bash
# Fix file permissions
chmod +x scripts/*.py
sudo chown -R $USER:$USER .

# Use virtual environment
python -m venv jarvis_env
source jarvis_env/bin/activate  # Linux/macOS
# or
jarvis_env\Scripts\activate     # Windows
pip install -r requirements.txt
```

#### Missing Dependencies
**Symptoms:**
- Import errors for specific modules
- Feature not working as expected

**Solution:**
```bash
# Install all dependencies
pip install -r requirements.txt

# Install optional dependencies
pip install torch transformers chromadb

# Check for conflicts
pip check

# Update all packages
pip install --upgrade -r requirements.txt
```

### Configuration Issues

#### Environment Variables Not Loading
**Symptoms:**
- Default values used instead of configured values
- Configuration not taking effect

**Solution:**
```bash
# Check environment file
cat .env

# Export variables manually
export JARVIS_MODE=production
export DEBUG=false

# Load configuration explicitly
python -c "from jarvis.core.config import get_config_manager; config = get_config_manager(); print(config.get_all())"
```

#### Invalid Configuration
**Symptoms:**
```
ConfigurationError: Invalid configuration value
```

**Solution:**
```bash
# Validate configuration
python scripts/validate_config.py

# Reset to defaults
cp config/environments/development.yaml.example config/environments/development.yaml

# Check YAML syntax
python -c "import yaml; yaml.safe_load(open('config/environments/development.yaml'))"
```

## Testing and Validation

### System Health Check
```bash
# Complete system validation
python scripts/system_health_check.py

# Run core tests
python run_tests.py --quick

# Test specific components
python tests/test_crdt_implementation.py
python tests/test_archive_system.py
```

### Performance Benchmarking
```bash
# Run performance tests
python tests/test_crdt_phase5.py

# Benchmark operations
python scripts/benchmark_operations.py

# Memory usage analysis
python scripts/analyze_memory_usage.py
```

## Getting Help

### Log Analysis
```bash
# Check recent logs
tail -f logs/jarvis.log

# Analyze error patterns
python scripts/analyze_logs.py --errors

# Generate diagnostic report
python scripts/generate_diagnostic_report.py
```

### Debug Mode
```bash
# Enable verbose logging
export JARVIS_DEBUG=true
export LOG_LEVEL=DEBUG
python main.py --cli

# Save debug session
python main.py --debug --save-session debug_session.log
```

### Community Support
- **GitHub Issues**: Report bugs and feature requests
- **Documentation**: Check `docs/` directory for detailed guides
- **Test Suite**: Run tests to validate your environment

## Emergency Recovery

### Complete System Reset
**Use only as last resort:**
```bash
# Backup current state
cp -r data/ data_backup/

# Reset all databases
rm data/*.db

# Clear all caches
rm -rf __pycache__/ */__pycache__/

# Reinstall dependencies
pip uninstall -r requirements.txt -y
pip install -r requirements.txt

# Start fresh
python main.py
```

### Data Recovery
```bash
# Restore from backup
python scripts/restore_from_backup.py --latest

# Recover corrupted archive
python scripts/recover_archive.py --repair

# Export data before reset
python scripts/export_all_data.py --format json
```