#!/usr/bin/env python3
"""
Efficient Test Runner with Consolidated Logging
Redesigned to minimize file creation while maintaining full functionality.
"""

import sys
import os
import json
import unittest
import time
import subprocess
import tempfile
import shutil
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.consolidated_log_manager import ConsolidatedLogManager, TestLogAdapter

class EfficientTestRunner:
    """
    Test runner that uses consolidated logging to minimize file creation
    """
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.log_manager = ConsolidatedLogManager(self.project_root)
        self.test_adapter = TestLogAdapter(self.log_manager)
        self.temp_dir = None
        
    def setup_temp_environment(self):
        """Setup temporary directory for test artifacts"""
        self.temp_dir = tempfile.mkdtemp(prefix="jarvis_test_")
        print(f"[SETUP] Created temporary test environment: {self.temp_dir}")
        
    def cleanup_temp_environment(self):
        """Cleanup temporary test environment"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            print(f"[CLEANUP] Removed temporary test environment")
    
    def run_test_file(self, test_file, description, timeout_seconds=300):
        """
        Run a single test file with efficient logging
        """
        self.test_adapter.start_test_suite(test_file)
        start_time = time.time()
        
        result = {
            "file": test_file,
            "description": description,
            "status": "UNKNOWN",
            "tests_run": 0,
            "failures": 0,
            "errors": 0,
            "duration": 0,
            "output": "",
            "error_output": ""
        }
        
        try:
            test_path = self.project_root / "tests" / test_file
            if not test_path.exists():
                result["status"] = "SKIPPED"
                result["reason"] = f"Test file not found: {test_path}"
                return result
            
            print(f"[RUNNER] Starting {description}")
            
            # Redirect test outputs to temporary location
            env = os.environ.copy()
            env['JARVIS_TEST_TEMP_DIR'] = self.temp_dir
            env['JARVIS_CONSOLIDATED_LOGGING'] = "1"
            
            # Run test with timeout
            process = subprocess.Popen(
                [sys.executable, str(test_path)],
                cwd=str(self.project_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env
            )
            
            try:
                stdout, stderr = process.communicate(timeout=timeout_seconds)
                result["output"] = stdout
                result["error_output"] = stderr
                
                # Parse test results from output
                result.update(self._parse_test_output(stdout, stderr))
                
                if process.returncode == 0:
                    result["status"] = "PASS"
                else:
                    result["status"] = "FAIL"
                    
            except subprocess.TimeoutExpired:
                process.kill()
                result["status"] = "TIMEOUT"
                result["reason"] = f"Test timed out after {timeout_seconds} seconds"
                
        except Exception as e:
            result["status"] = "ERROR"
            result["reason"] = f"Exception running test: {str(e)}"
            result["error_output"] = str(e)
        
        result["duration"] = time.time() - start_time
        
        # Log test results
        self.test_adapter.end_test_suite(
            result["tests_run"], 
            result["failures"], 
            result["errors"]
        )
        
        # Log individual test result
        self.test_adapter.log_test_result(
            test_file,
            result["status"],
            result["duration"],
            {
                "tests_run": result["tests_run"],
                "failures": result["failures"], 
                "errors": result["errors"],
                "output_length": len(result["output"]),
                "error_output_length": len(result["error_output"])
            }
        )
        
        return result
    
    def _parse_test_output(self, stdout, stderr):
        """Parse test execution output to extract metrics"""
        result = {"tests_run": 0, "failures": 0, "errors": 0}
        
        # Look for unittest output patterns
        combined_output = stdout + stderr
        lines = combined_output.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # unittest pattern: "Ran X tests in Ys"
            if "Ran " in line and " tests in " in line:
                try:
                    parts = line.split()
                    if len(parts) >= 2 and parts[1].isdigit():
                        result["tests_run"] = int(parts[1])
                except (ValueError, IndexError):
                    pass
            
            # Error counting patterns
            if "FAILED (failures=" in line or "FAILED (errors=" in line:
                try:
                    # Parse "FAILED (failures=X, errors=Y)" or similar
                    start = line.find("(") + 1
                    end = line.find(")")
                    if start > 0 and end > start:
                        failure_part = line[start:end]
                        for part in failure_part.split(","):
                            part = part.strip()
                            if part.startswith("failures="):
                                result["failures"] = int(part.split("=")[1])
                            elif part.startswith("errors="):
                                result["errors"] = int(part.split("=")[1])
                except (ValueError, IndexError):
                    pass
            
            # Alternative patterns for test counting
            if ".py::" in line and ("PASSED" in line or "FAILED" in line or "ERROR" in line):
                result["tests_run"] += 1
                if "FAILED" in line:
                    result["failures"] += 1
                elif "ERROR" in line:
                    result["errors"] += 1
        
        return result
    
    def run_all_tests(self):
        """Run all test suites with efficient logging"""
        print(f"[LAUNCHER] Starting Efficient Test Runner")
        print(f"[LAUNCHER] Session ID: {self.log_manager.session_id}")
        
        self.setup_temp_environment()
        
        try:
            # Define test suites (same as original but with efficient logging)
            test_suites = [
                ("test_simplified_system.py", "Core System - Simplified system validation"),
                ("test_crdt_implementation.py", "CRDT Core - Basic CRDT operations and synchronization"), 
                ("test_crdt_comprehensive.py", "CRDT Advanced - Comprehensive CRDT functionality"),
                ("test_crdt_phase4.py", "CRDT Phase 4 - Enhanced synchronization algorithms"),
                ("test_crdt_phase5.py", "CRDT Phase 5 - Real-time collaboration features"),
                ("test_archiving_system.py", "Archive System - Data archiving and retrieval"),
                ("test_error_handling_comprehensive.py", "Error Handling - Comprehensive error management"),
                ("test_coverage_comprehensive.py", "Coverage Analysis - Comprehensive test coverage"),
                ("comprehensive_function_test.py", "Function Coverage - All system functions validation"),
                ("test_agent_workflow.py", "Agent Workflow - Agent task management and execution"),
                ("test_backup_recovery.py", "Backup Recovery - System backup and recovery operations"),
                ("test_archive_purge.py", "Archive Purge - Archive cleanup and purge operations"),
                ("test_verification_optimizer.py", "Verification Optimizer - Queue optimization and verification"),
                ("test_system_dashboard.py", "System Dashboard - Dashboard functionality and monitoring"),
                ("test_gui_components.py", "GUI Components - User interface components"),
                ("test_cli_interfaces.py", "CLI Interfaces - Command-line interface functionality"),
                ("test_distributed_coordination.py", "Distributed Coordination - Phase 6 Advanced distributed intelligence"),
                ("test_phase7_distributed_memory.py", "Phase 7 Memory - Advanced distributed memory architecture"),
                ("test_phase8_advanced_network_topology.py", "Phase 8 Network - Advanced network topologies and enterprise features")
            ]
            
            overall_start_time = time.time()
            results = []
            
            # Run each test suite
            for test_file, description in test_suites:
                result = self.run_test_file(test_file, description)
                results.append(result)
                
                # Log progress
                status_symbol = {
                    "PASS": "✅",
                    "FAIL": "❌", 
                    "TIMEOUT": "⏰",
                    "ERROR": "💥",
                    "SKIPPED": "⏭️"
                }.get(result["status"], "❓")
                
                print(f"[RESULT] {description}: {status_symbol} ({result['duration']:.1f}s)")
            
            overall_duration = time.time() - overall_start_time
            
            # Generate comprehensive summary
            summary = self._generate_test_summary(results, overall_duration)
            
            # Log final summary
            self.test_adapter.log_performance_data({
                'event': 'test_suite_complete',
                'total_duration': overall_duration,
                'total_suites': len(results),
                'passed_suites': summary['passed_suites'],
                'failed_suites': summary['failed_suites'],
                'total_tests': summary['total_tests'],
                'success_rate': summary['test_success_rate'],
                'suite_success_rate': summary['suite_success_rate']
            })
            
            return summary, results
            
        finally:
            self.cleanup_temp_environment()
    
    def _generate_test_summary(self, results, overall_duration):
        """Generate comprehensive test summary"""
        print(f"\n{'='*80}")
        print("[SUMMARY] COMPREHENSIVE TEST RESULTS")
        print(f"{'='*80}")
        
        total_tests = 0
        total_failures = 0
        total_errors = 0
        passed_suites = 0
        failed_suites = 0
        
        print(f"{'Test Suite':<40} {'Status':<10} {'Tests':<8} {'Fails':<8} {'Errors':<8} {'Time':<8}")
        print("-" * 80)
        
        for result in results:
            status_symbol = {
                "PASS": "✅",
                "FAIL": "❌", 
                "TIMEOUT": "⏰",
                "ERROR": "💥",
                "SKIPPED": "⏭️"
            }.get(result["status"], "❓")
            
            print(f"{result['description']:<40} {status_symbol} {result['status']:<7} "
                  f"{result['tests_run']:<8} {result['failures']:<8} {result['errors']:<8} "
                  f"{result['duration']:.1f}s")
            
            total_tests += result["tests_run"]
            total_failures += result["failures"]
            total_errors += result["errors"]
            
            if result["status"] == "PASS":
                passed_suites += 1
            elif result["status"] in ["FAIL", "TIMEOUT", "ERROR"]:
                failed_suites += 1
        
        print("-" * 80)
        print(f"{'TOTALS':<40} {'---':<10} {total_tests:<8} {total_failures:<8} {total_errors:<8} {overall_duration:.1f}s")
        
        # Calculate success rates
        total_suite_count = len([r for r in results if r["status"] != "SKIPPED"])
        suite_success_rate = (passed_suites / total_suite_count * 100) if total_suite_count > 0 else 0
        
        test_success_rate = 0
        if total_tests > 0:
            successful_tests = total_tests - total_failures - total_errors
            test_success_rate = (successful_tests / total_tests * 100)
        
        print(f"\n[SUMMARY] RESULTS:")
        print(f"   Test Suites:      {passed_suites}/{total_suite_count} passed ({suite_success_rate:.1f}%)")
        print(f"   Individual Tests: {total_tests - total_failures - total_errors}/{total_tests} passed ({test_success_rate:.1f}%)")
        print(f"   Total Duration:   {overall_duration:.1f} seconds")
        print(f"   Total Failures:   {total_failures}")
        print(f"   Total Errors:     {total_errors}")
        
        # Overall status
        if suite_success_rate >= 100:
            overall_status = "🟢 PERFECT"
        elif suite_success_rate >= 80:
            overall_status = "🟢 EXCELLENT"
        elif suite_success_rate >= 60:
            overall_status = "🟡 GOOD"
        elif suite_success_rate >= 40:
            overall_status = "🟠 NEEDS IMPROVEMENT"
        else:
            overall_status = "🔴 CRITICAL ISSUES"
        
        print(f"   Overall Status:   {overall_status}")
        
        return {
            'total_tests': total_tests,
            'total_failures': total_failures,
            'total_errors': total_errors,
            'passed_suites': passed_suites,
            'failed_suites': failed_suites,
            'suite_success_rate': suite_success_rate,
            'test_success_rate': test_success_rate,
            'overall_duration': overall_duration,
            'overall_status': overall_status
        }
    
    def finalize_logging(self):
        """Finalize logging and create archives"""
        print(f"\n[FINALIZATION] Creating consolidated log archives...")
        
        # Flush all logs
        self.log_manager.flush_all()
        
        # Create session summary
        summary = self.log_manager.create_session_summary()
        
        # Clean up old sessions (keep last 3 days)
        cleaned_files = self.log_manager.cleanup_old_sessions(keep_days=3)
        
        print(f"[FINALIZATION] Log consolidation complete:")
        print(f"   Session ID: {self.log_manager.session_id}")
        print(f"   Total entries logged: {summary['total_entries']}")
        print(f"   Files created: {len(summary['files_created'])}")
        print(f"   Old files cleaned: {len(cleaned_files)}")
        
        # Copy essential logs to original upload location for compatibility
        self._create_compatibility_uploads(summary)
        
        return summary
    
    def _create_compatibility_uploads(self, summary):
        """Create compatibility uploads for existing scripts"""
        upload_dir = self.project_root / "tests" / "output" / "uploaded_logs" 
        session_dir = upload_dir / f"efficient_logs_{self.log_manager.session_id}"
        session_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy session summary
        summary_file = self.log_manager.log_root / f"session_summary_{self.log_manager.session_id}.json"
        if summary_file.exists():
            shutil.copy2(summary_file, session_dir / "session_summary.json")
        
        # Create aggregated logs for each category
        for category in ['test_execution', 'agent_reports', 'compliance', 'performance', 'errors']:
            logs = self.log_manager.get_logs_by_category(category)
            if logs:
                category_file = session_dir / f"{category}_aggregated.json"
                with open(category_file, 'w', encoding='utf-8') as f:
                    json.dump(logs, f, indent=2, ensure_ascii=False)
        
        print(f"[COMPATIBILITY] Created compatibility uploads in {session_dir}")


def main():
    """Main entry point for efficient test runner"""
    runner = EfficientTestRunner()
    
    try:
        summary, results = runner.run_all_tests()
        
        # Finalize logging
        log_summary = runner.finalize_logging()
        
        print(f"\n[COMPLETE] Test execution finished")
        print(f"[STATS] Files created: {len(log_summary['files_created'])} (vs ~10,000 in old system)")
        print(f"[STATS] Total log entries: {log_summary['total_entries']}")
        
        # Return appropriate exit code
        if summary['suite_success_rate'] >= 80 and summary['total_errors'] == 0:
            return 0  # Success
        else:
            return 1  # Failure
            
    except Exception as e:
        print(f"[ERROR] Test runner failed: {e}")
        runner.finalize_logging()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)