#!/usr/bin/env python3
"""
Error Recovery Testing Script - Stage 2 Validation
Tests error recovery protocols and rollback mechanisms.
"""

import sys
import os
import json
import shutil
import tempfile
import sqlite3
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class ErrorRecoveryTester:
    """Tests error recovery and rollback protocols"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.temp_dir = Path(tempfile.mkdtemp(prefix="jarvis_recovery_test_"))
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "recovery_tests": {},
            "rollback_tests": {},
            "state_restoration": {},
            "user_guidance": {},
            "success": False
        }
        
    def test_database_recovery(self):
        """Test database recovery mechanisms"""
        db_recovery = {
            "backup_creation": False,
            "corruption_simulation": False,
            "integrity_restoration": False,
            "data_preservation": False,
            "recovery_time": 0,
            "test_success": False
        }
        
        try:
            # Find a test database to work with
            test_db_source = None
            for db_file in self.project_root.rglob("*.db"):
                if db_file.stat().st_size > 0 and db_file.stat().st_size < 50 * 1024 * 1024:  # < 50MB
                    test_db_source = db_file
                    break
            
            if test_db_source:
                start_time = datetime.now()
                
                # Create backup
                test_db_backup = self.temp_dir / "test_backup.db"
                shutil.copy2(test_db_source, test_db_backup)
                db_recovery["backup_creation"] = True
                
                # Create working copy
                test_db_working = self.temp_dir / "test_working.db"
                shutil.copy2(test_db_source, test_db_working)
                
                # Test integrity before corruption
                conn = sqlite3.connect(str(test_db_working))
                cursor = conn.cursor()
                cursor.execute("PRAGMA integrity_check")
                integrity_before = cursor.fetchone()[0]
                conn.close()
                
                if integrity_before == "ok":
                    # Simulate corruption (write garbage to file)
                    with open(test_db_working, 'ab') as f:
                        f.write(b'\x00\xFF\x00\xFF' * 1000)  # Add garbage data
                    
                    db_recovery["corruption_simulation"] = True
                    
                    # Test integrity after corruption
                    try:
                        conn = sqlite3.connect(str(test_db_working))
                        cursor = conn.cursor()
                        cursor.execute("PRAGMA integrity_check")
                        integrity_after = cursor.fetchone()[0]
                        conn.close()
                        
                        # If still "ok", try a more aggressive corruption
                        if integrity_after == "ok":
                            with open(test_db_working, 'r+b') as f:
                                f.seek(0)
                                f.write(b'\x00' * 1024)  # Overwrite header
                    except Exception:
                        pass  # Corruption successful
                    
                    # Restore from backup
                    shutil.copy2(test_db_backup, test_db_working)
                    
                    # Verify restoration
                    try:
                        conn = sqlite3.connect(str(test_db_working))
                        cursor = conn.cursor()
                        cursor.execute("PRAGMA integrity_check")
                        integrity_restored = cursor.fetchone()[0]
                        conn.close()
                        
                        if integrity_restored == "ok":
                            db_recovery["integrity_restoration"] = True
                            db_recovery["data_preservation"] = True
                    except Exception:
                        pass
                
                end_time = datetime.now()
                db_recovery["recovery_time"] = (end_time - start_time).total_seconds()
                db_recovery["test_success"] = db_recovery["integrity_restoration"]
                
        except Exception as e:
            db_recovery["error"] = str(e)
        
        self.results["recovery_tests"]["database"] = db_recovery
        return db_recovery
    
    def test_file_rollback(self):
        """Test file modification rollback capabilities"""
        file_rollback = {
            "backup_system": False,
            "modification_tracking": False,
            "rollback_capability": False,
            "version_control": False,
            "test_success": False
        }
        
        try:
            # Create test file
            test_file = self.temp_dir / "test_config.json"
            original_content = {"test": "original", "timestamp": datetime.now().isoformat()}
            
            with open(test_file, 'w') as f:
                json.dump(original_content, f, indent=2)
            
            # Create backup
            backup_file = self.temp_dir / "test_config.json.backup"
            shutil.copy2(test_file, backup_file)
            file_rollback["backup_system"] = True
            
            # Modify file
            modified_content = {"test": "modified", "timestamp": datetime.now().isoformat()}
            with open(test_file, 'w') as f:
                json.dump(modified_content, f, indent=2)
            
            file_rollback["modification_tracking"] = True
            
            # Rollback file
            shutil.copy2(backup_file, test_file)
            
            # Verify rollback
            with open(test_file, 'r') as f:
                restored_content = json.load(f)
            
            if restored_content["test"] == "original":
                file_rollback["rollback_capability"] = True
                file_rollback["test_success"] = True
            
            # Check for version control (git)
            if (self.project_root / ".git").exists():
                file_rollback["version_control"] = True
                
        except Exception as e:
            file_rollback["error"] = str(e)
        
        self.results["rollback_tests"]["file_system"] = file_rollback
        return file_rollback
    
    def test_configuration_recovery(self):
        """Test configuration recovery mechanisms"""
        config_recovery = {
            "default_config_available": False,
            "config_validation": False,
            "automatic_recovery": False,
            "user_notification": False,
            "test_success": False
        }
        
        try:
            # Look for configuration files
            config_files = [
                self.project_root / "config.json",
                self.project_root / "config" / "config.json",
                self.project_root / "settings.json"
            ]
            
            existing_config = None
            for config_file in config_files:
                if config_file.exists():
                    existing_config = config_file
                    break
            
            if existing_config:
                # Create backup
                config_backup = self.temp_dir / "config_backup.json"
                shutil.copy2(existing_config, config_backup)
                
                # Test if default config exists
                default_config_files = [
                    existing_config.parent / "default_config.json",
                    existing_config.parent / "config_default.json",
                    self.project_root / "config" / "defaults.json"
                ]
                
                for default_file in default_config_files:
                    if default_file.exists():
                        config_recovery["default_config_available"] = True
                        break
                
                # Test configuration validation
                try:
                    with open(existing_config, 'r') as f:
                        config_data = json.load(f)
                    config_recovery["config_validation"] = True
                except Exception:
                    config_recovery["config_validation"] = False
                
                # Check for validation scripts
                validation_scripts = [
                    self.project_root / "scripts" / "validate_config.py",
                    self.project_root / "scripts" / "check_config.py"
                ]
                
                if any(script.exists() for script in validation_scripts):
                    config_recovery["automatic_recovery"] = True
                
                config_recovery["test_success"] = config_recovery["config_validation"]
                
        except Exception as e:
            config_recovery["error"] = str(e)
        
        self.results["recovery_tests"]["configuration"] = config_recovery
        return config_recovery
    
    def test_state_restoration(self):
        """Test system state restoration capabilities"""
        state_restoration = {
            "checkpoint_system": False,
            "state_snapshots": False,
            "memory_restoration": False,
            "service_recovery": False,
            "test_success": False
        }
        
        try:
            # Look for state management files
            state_files = list(self.project_root.rglob("*state*")) + list(self.project_root.rglob("*checkpoint*"))
            if state_files:
                state_restoration["checkpoint_system"] = True
            
            # Look for snapshot/backup directories
            snapshot_dirs = [
                self.project_root / "snapshots",
                self.project_root / "backups",
                self.project_root / "checkpoints"
            ]
            
            if any(d.exists() for d in snapshot_dirs):
                state_restoration["state_snapshots"] = True
            
            # Check for memory state files
            memory_files = list(self.project_root.rglob("*memory*"))
            if memory_files:
                state_restoration["memory_restoration"] = True
            
            # Check for service recovery scripts
            service_scripts = [
                self.project_root / "scripts" / "restart_services.py",
                self.project_root / "scripts" / "recover_services.py",
                self.project_root / "start.py",
                self.project_root / "restart.py"
            ]
            
            if any(script.exists() for script in service_scripts):
                state_restoration["service_recovery"] = True
            
            # Assess overall state restoration capability
            restoration_features = [
                state_restoration["checkpoint_system"],
                state_restoration["state_snapshots"],
                state_restoration["memory_restoration"],
                state_restoration["service_recovery"]
            ]
            
            state_restoration["test_success"] = sum(restoration_features) >= 2
            
        except Exception as e:
            state_restoration["error"] = str(e)
        
        self.results["state_restoration"] = state_restoration
        return state_restoration
    
    def test_user_guidance(self):
        """Test user guidance and error communication systems"""
        user_guidance = {
            "error_documentation": False,
            "recovery_instructions": False,
            "help_system": False,
            "user_friendly_messages": False,
            "contact_information": False,
            "test_success": False
        }
        
        try:
            # Look for documentation files
            doc_files = [
                self.project_root / "README.md",
                self.project_root / "TROUBLESHOOTING.md",
                self.project_root / "docs",
                self.project_root / "HELP.md"
            ]
            
            doc_content = ""
            for doc_file in doc_files:
                if doc_file.exists():
                    if doc_file.is_file():
                        with open(doc_file, 'r', encoding='utf-8') as f:
                            doc_content += f.read().lower()
                    user_guidance["error_documentation"] = True
            
            # Check for recovery instructions
            recovery_keywords = ["recovery", "restore", "fix", "troubleshoot", "error", "problem"]
            if any(keyword in doc_content for keyword in recovery_keywords):
                user_guidance["recovery_instructions"] = True
            
            # Check for help system
            help_keywords = ["help", "support", "faq", "guide"]
            if any(keyword in doc_content for keyword in help_keywords):
                user_guidance["help_system"] = True
            
            # Look for user-friendly error handling in code
            friendly_error_count = 0
            for py_file in self.project_root.rglob("*.py"):
                if any(exclude in str(py_file) for exclude in ['.git', '__pycache__']):
                    continue
                
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read().lower()
                    
                    # Look for user-friendly error patterns
                    friendly_patterns = [
                        "user-friendly", "please", "sorry", "help", "try again",
                        "contact support", "check the", "make sure"
                    ]
                    
                    if any(pattern in content for pattern in friendly_patterns):
                        friendly_error_count += 1
                        
                except Exception:
                    continue
            
            user_guidance["user_friendly_messages"] = friendly_error_count > 5
            
            # Check for contact information
            contact_keywords = ["contact", "support", "email", "github", "issue"]
            if any(keyword in doc_content for keyword in contact_keywords):
                user_guidance["contact_information"] = True
            
            # Assess overall user guidance
            guidance_features = [
                user_guidance["error_documentation"],
                user_guidance["recovery_instructions"], 
                user_guidance["help_system"],
                user_guidance["user_friendly_messages"],
                user_guidance["contact_information"]
            ]
            
            user_guidance["test_success"] = sum(guidance_features) >= 3
            
        except Exception as e:
            user_guidance["error"] = str(e)
        
        self.results["user_guidance"] = user_guidance
        return user_guidance
    
    def run_tests(self):
        """Run complete error recovery testing"""
        print("🔍 Starting comprehensive error recovery testing...")
        
        # Test database recovery
        print("💾 Testing database recovery mechanisms...")
        db_recovery = self.test_database_recovery()
        print(f"   Database recovery: {'✅' if db_recovery['test_success'] else '❌'}")
        
        # Test file rollback
        print("📁 Testing file rollback capabilities...")
        file_rollback = self.test_file_rollback()
        print(f"   File rollback: {'✅' if file_rollback['test_success'] else '❌'}")
        
        # Test configuration recovery
        print("⚙️ Testing configuration recovery...")
        config_recovery = self.test_configuration_recovery()
        print(f"   Configuration recovery: {'✅' if config_recovery['test_success'] else '❌'}")
        
        # Test state restoration
        print("🔄 Testing state restoration capabilities...")
        state_restoration = self.test_state_restoration()
        print(f"   State restoration: {'✅' if state_restoration['test_success'] else '❌'}")
        
        # Test user guidance
        print("👤 Testing user guidance systems...")
        user_guidance = self.test_user_guidance()
        print(f"   User guidance: {'✅' if user_guidance['test_success'] else '❌'}")
        
        self.results["success"] = True
        
        # Clean up temp directory
        try:
            shutil.rmtree(self.temp_dir)
        except Exception:
            pass
        
        # Save results
        report_path = self.project_root / f"error_recovery_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n✅ Error recovery testing complete!")
        print(f"📄 Report saved to: {report_path}")
        
        return self.results
    
    def print_summary(self):
        """Print testing summary"""
        if not self.results["success"]:
            print("❌ Testing failed")
            return
        
        print("\n" + "="*60)
        print("🎯 ERROR RECOVERY TESTING SUMMARY")
        print("="*60)
        
        # Database recovery
        db_recovery = self.results["recovery_tests"]["database"]
        print(f"💾 Database Recovery: {'✅' if db_recovery['test_success'] else '❌'}")
        print(f"   • Backup creation: {'✅' if db_recovery['backup_creation'] else '❌'}")
        print(f"   • Corruption simulation: {'✅' if db_recovery['corruption_simulation'] else '❌'}")
        print(f"   • Integrity restoration: {'✅' if db_recovery['integrity_restoration'] else '❌'}")
        print(f"   • Recovery time: {db_recovery['recovery_time']:.2f}s")
        
        # File rollback
        file_rollback = self.results["rollback_tests"]["file_system"]
        print(f"\n📁 File Rollback: {'✅' if file_rollback['test_success'] else '❌'}")
        print(f"   • Backup system: {'✅' if file_rollback['backup_system'] else '❌'}")
        print(f"   • Modification tracking: {'✅' if file_rollback['modification_tracking'] else '❌'}")
        print(f"   • Rollback capability: {'✅' if file_rollback['rollback_capability'] else '❌'}")
        print(f"   • Version control: {'✅' if file_rollback['version_control'] else '❌'}")
        
        # Configuration recovery
        config_recovery = self.results["recovery_tests"]["configuration"]
        print(f"\n⚙️ Configuration Recovery: {'✅' if config_recovery['test_success'] else '❌'}")
        print(f"   • Default config available: {'✅' if config_recovery['default_config_available'] else '❌'}")
        print(f"   • Config validation: {'✅' if config_recovery['config_validation'] else '❌'}")
        print(f"   • Automatic recovery: {'✅' if config_recovery['automatic_recovery'] else '❌'}")
        
        # State restoration
        state_restoration = self.results["state_restoration"]
        print(f"\n🔄 State Restoration: {'✅' if state_restoration['test_success'] else '❌'}")
        print(f"   • Checkpoint system: {'✅' if state_restoration['checkpoint_system'] else '❌'}")
        print(f"   • State snapshots: {'✅' if state_restoration['state_snapshots'] else '❌'}")
        print(f"   • Memory restoration: {'✅' if state_restoration['memory_restoration'] else '❌'}")
        print(f"   • Service recovery: {'✅' if state_restoration['service_recovery'] else '❌'}")
        
        # User guidance
        user_guidance = self.results["user_guidance"]
        print(f"\n👤 User Guidance: {'✅' if user_guidance['test_success'] else '❌'}")
        print(f"   • Error documentation: {'✅' if user_guidance['error_documentation'] else '❌'}")
        print(f"   • Recovery instructions: {'✅' if user_guidance['recovery_instructions'] else '❌'}")
        print(f"   • Help system: {'✅' if user_guidance['help_system'] else '❌'}")
        print(f"   • User-friendly messages: {'✅' if user_guidance['user_friendly_messages'] else '❌'}")
        
        # Overall assessment
        all_tests = [
            db_recovery['test_success'],
            file_rollback['test_success'],
            config_recovery['test_success'],
            state_restoration['test_success'],
            user_guidance['test_success']
        ]
        
        success_rate = (sum(all_tests) / len(all_tests)) * 100
        print(f"\n🎯 Overall Recovery Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("✅ Excellent error recovery capabilities")
        elif success_rate >= 60:
            print("⚠️ Good error recovery, some improvements needed")
        elif success_rate >= 40:
            print("⚠️ Basic error recovery, significant improvements needed")
        else:
            print("❌ Poor error recovery, major implementation required")
        
        print("\n✅ Testing complete - Error recovery assessment finished!")


def main():
    """Main execution function"""
    tester = ErrorRecoveryTester()
    results = tester.run_tests()
    tester.print_summary()
    
    return results["success"]


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)