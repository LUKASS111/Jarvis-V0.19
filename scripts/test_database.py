#!/usr/bin/env python3
"""
Jarvis Database Diagnostic Tool
Tests database functionality and provides repair guidance.
"""

import os
import sys
import sqlite3
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_database_functionality():
    """Test database initialization and basic functionality"""
    
    print("🔍 Jarvis Database Diagnostic")
    print("=" * 50)
    
    try:
        # Test Data Archiver
        print("1. Testing Data Archiver...")
        from jarvis.core.data_archiver import get_archiver
        archiver = get_archiver()
        
        # Test basic archiving functionality
        test_id = archiver.archive_data(
            data_type="test",
            content="Database diagnostic test",
            source="diagnostic_tool",
            operation="test_operation"
        )
        print(f"   ✅ Archive test successful (ID: {test_id})")
        
    except Exception as e:
        print(f"   ❌ Archive test failed: {e}")
        return False
    
    try:
        # Test Memory Manager  
        print("2. Testing Memory Manager...")
        from jarvis.memory.memory_manager import MemoryManager
        memory = MemoryManager()
        
        # Test basic memory functionality
        memory.store(
            content="Test memory entry",
            category="diagnostic",
            importance=5,
            tags=["test"]
        )
        print(f"   ✅ Memory test successful")
        
    except Exception as e:
        print(f"   ❌ Memory test failed: {e}")
        return False
    
    try:
        # Test Backend Initialization
        print("3. Testing Backend Services...")
        from jarvis.backend import get_jarvis_backend
        backend = get_jarvis_backend()
        status = backend.get_system_status()
        health = status.get('system_metrics', {}).get('health_score', 0)
        print(f"   ✅ Backend test successful (Health: {health})")
        
    except Exception as e:
        print(f"   ❌ Backend test failed: {e}")
        return False
    
    print("\n🎉 All database tests passed successfully!")
    return True

def main():
    """Main diagnostic function"""
    
    success = test_database_functionality()
    
    if success:
        print("\n" + "=" * 50)
        print("✅ Jarvis is ready to use!")
        print("\nAvailable commands:")
        print("  python main.py           # Launch 9-tab professional dashboard")
        print("  python main.py --cli     # Launch CLI interface")
        print("  python main.py --backend # Start backend service")
        print("\nIf you experience database errors:")
        print("  python scripts/repair_databases.py  # Repair corrupted databases")
        
    else:
        print("\n" + "=" * 50)
        print("❌ Database issues detected!")
        print("\nRecommended actions:")
        print("1. Run: python scripts/repair_databases.py")
        print("2. If issues persist, delete data/*.db files")
        print("3. Restart Jarvis to recreate fresh databases")
        
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())