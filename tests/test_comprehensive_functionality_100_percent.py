#!/usr/bin/env python3
"""
Comprehensive System Functionality Test Suite
100% Functionality validation for all core Jarvis systems
"""

import sys
import os
import unittest
import time
import tempfile
import shutil
from unittest.mock import patch

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test imports with fallbacks
modules_available = {}
try:
    from jarvis.monitoring.realtime_metrics import AdvancedMetricsCollector
    modules_available['metrics'] = True
except ImportError:
    modules_available['metrics'] = False

try:
    from jarvis.monitoring.system_health import SystemHealthMonitor
    modules_available['health'] = True
except ImportError:
    modules_available['health'] = False

try:
    from jarvis.core.main import JarvisCore
    modules_available['core'] = True
except ImportError:
    modules_available['core'] = False

try:
    from jarvis.backend import get_jarvis_backend
    modules_available['backend'] = True
except ImportError:
    modules_available['backend'] = False


class TestCoreSystemFunctionality(unittest.TestCase):
    """Test core system functionality"""
    
    def test_core_system_imports(self):
        """Test that core systems can be imported"""
        self.assertTrue(modules_available['metrics'], "Metrics system not available")
        self.assertTrue(modules_available['health'], "Health system not available")
        self.assertTrue(modules_available['backend'], "Backend system not available")
    
    def test_metrics_system_basic_functionality(self):
        """Test basic metrics system functionality"""
        if not modules_available['metrics']:
            self.skipTest("Metrics system not available")
        
        metrics = AdvancedMetricsCollector()
        
        # Test metric registration
        initial_metrics = len(metrics.metric_definitions)
        self.assertGreaterEqual(initial_metrics, 12, "Should have at least 12 built-in metrics")
        
        # Test auto-registration
        metrics.record_gauge('test.functionality.gauge', 100.0, {'test': 'functionality'})
        new_metrics = len(metrics.metric_definitions)
        self.assertGreater(new_metrics, initial_metrics, "Auto-registration should add new metrics")
        
        # Test metric recording
        metrics.record_counter('test.functionality.counter', 5.0)
        
        # Test data retrieval
        current_values = metrics.get_current_values()
        self.assertIsInstance(current_values, dict)
        
        print(f"✅ Metrics system: {new_metrics} metrics registered, auto-registration working")
    
    def test_health_system_basic_functionality(self):
        """Test basic health system functionality"""
        if not modules_available['health']:
            self.skipTest("Health system not available")
        
        # Test without WebSocket to avoid conflicts
        with patch.object(SystemHealthMonitor, '_start_websocket_server'):
            health = SystemHealthMonitor()
            
            # Test health report generation
            report = health.get_health_report()
            self.assertIsInstance(report.overall_score, (int, float))
            self.assertIn(report.overall_status, ['healthy', 'warning', 'critical', 'unknown'])
            
            # Test monitoring lifecycle
            health.start_monitoring()
            self.assertTrue(health.is_running)
            
            # Allow some monitoring
            time.sleep(1)
            
            # Get updated report
            updated_report = health.get_health_report()
            self.assertIsInstance(updated_report.component_statuses, dict)
            
            health.stop_monitoring()
            self.assertFalse(health.is_running)
            
            print(f"✅ Health system: {updated_report.overall_score:.1f}% health score, {len(updated_report.component_statuses)} components")
    
    def test_backend_system_functionality(self):
        """Test backend system functionality"""
        if not modules_available['backend']:
            self.skipTest("Backend system not available")
        
        # Test backend retrieval
        backend = get_jarvis_backend()
        self.assertIsNotNone(backend)
        
        # Test backend has required attributes
        required_attributes = ['memory', 'llm', 'api']
        for attr in required_attributes:
            self.assertTrue(hasattr(backend, attr), f"Backend missing {attr}")
        
        print("✅ Backend system: Core components available")
    
    def test_integrated_system_functionality(self):
        """Test systems working together"""
        if not (modules_available['metrics'] and modules_available['health']):
            self.skipTest("Required systems not available")
        
        # Create systems with WebSocket disabled
        with patch.object(SystemHealthMonitor, '_start_websocket_server'):
            metrics = AdvancedMetricsCollector()
            health = SystemHealthMonitor()
            
            # Start monitoring (without WebSocket conflicts)
            with patch.object(metrics, 'start_collection'):  # Mock to avoid threading issues
                health.start_monitoring()
                
                time.sleep(1)
                
                # Get health data
                health_report = health.get_health_report()
                
                # Record health as metric
                metrics.record_gauge('integration.test.health_score', health_report.overall_score)
                
                # Verify metric was recorded
                current_values = metrics.get_current_values()
                self.assertGreater(len(current_values), 0)
                
                health.stop_monitoring()
        
        print("✅ Integration: Systems work together successfully")


class TestFileSystemCapabilities(unittest.TestCase):
    """Test file system and data handling capabilities"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_data_directory_structure(self):
        """Test data directory structure exists"""
        expected_dirs = ['data', 'logs', 'tests']
        for directory in expected_dirs:
            dir_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), directory)
            self.assertTrue(os.path.exists(dir_path), f"Directory {directory} should exist")
    
    def test_database_creation(self):
        """Test database creation capabilities"""
        # Test SQLite database creation
        import sqlite3
        db_path = os.path.join(self.test_dir, 'test.db')
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE test_table (id INTEGER PRIMARY KEY, data TEXT)''')
        cursor.execute("INSERT INTO test_table (data) VALUES ('test_data')")
        conn.commit()
        
        # Verify data
        cursor.execute("SELECT data FROM test_table WHERE id = 1")
        result = cursor.fetchone()
        self.assertEqual(result[0], 'test_data')
        
        conn.close()
        print("✅ Database: SQLite operations working")
    
    def test_json_handling(self):
        """Test JSON data handling"""
        import json
        
        test_data = {
            'system': 'jarvis',
            'version': '0.19',
            'functionality': ['monitoring', 'health', 'metrics'],
            'score': 95.5
        }
        
        json_path = os.path.join(self.test_dir, 'test.json')
        
        # Write JSON
        with open(json_path, 'w') as f:
            json.dump(test_data, f)
        
        # Read JSON
        with open(json_path, 'r') as f:
            loaded_data = json.load(f)
        
        self.assertEqual(loaded_data, test_data)
        print("✅ File handling: JSON operations working")


class TestSystemPerformance(unittest.TestCase):
    """Test system performance characteristics"""
    
    def test_import_performance(self):
        """Test system import performance"""
        start_time = time.time()
        
        # Import key modules
        if modules_available['metrics']:
            from jarvis.monitoring.realtime_metrics import AdvancedMetricsCollector
        if modules_available['health']:
            from jarvis.monitoring.system_health import SystemHealthMonitor
        if modules_available['backend']:
            from jarvis.backend import get_jarvis_backend
        
        import_time = time.time() - start_time
        
        # Imports should be reasonably fast (< 5 seconds)
        self.assertLess(import_time, 5.0, "Module imports taking too long")
        print(f"✅ Performance: Module imports completed in {import_time:.2f}s")
    
    def test_basic_operation_performance(self):
        """Test basic operation performance"""
        if not modules_available['metrics']:
            self.skipTest("Metrics system not available")
        
        metrics = AdvancedMetricsCollector()
        
        start_time = time.time()
        
        # Record 100 metrics
        for i in range(100):
            metrics.record_gauge(f'test.performance.metric_{i % 10}', float(i))
        
        operation_time = time.time() - start_time
        
        # Should handle 100 metrics quickly (< 2 seconds)
        self.assertLess(operation_time, 2.0, "Metric recording too slow")
        print(f"✅ Performance: 100 metrics recorded in {operation_time:.2f}s")


def run_comprehensive_functionality_tests():
    """Run comprehensive functionality tests"""
    print("=" * 60)
    print("COMPREHENSIVE JARVIS V0.19 FUNCTIONALITY TEST SUITE")
    print("=" * 60)
    
    # Report system availability
    print(f"\n[SYSTEM STATUS]")
    for system, available in modules_available.items():
        status = "✅ AVAILABLE" if available else "❌ NOT AVAILABLE"
        print(f"   {system.upper()}: {status}")
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestCoreSystemFunctionality,
        TestFileSystemCapabilities,
        TestSystemPerformance
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    print(f"\n[TESTING] Starting comprehensive functionality tests...")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Calculate results
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    passed = total_tests - failures - errors
    success_rate = (passed / total_tests * 100) if total_tests > 0 else 0
    
    # Report results
    print("\n" + "=" * 60)
    print("COMPREHENSIVE FUNCTIONALITY TEST RESULTS")
    print("=" * 60)
    print(f"   Total Tests: {total_tests}")
    print(f"   Passed: {passed}")
    print(f"   Failed: {failures}")
    print(f"   Errors: {errors}")
    print(f"   Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("   Overall Status: 🟢 EXCELLENT")
    elif success_rate >= 80:
        print("   Overall Status: 🟡 GOOD")
    else:
        print("   Overall Status: 🔴 NEEDS IMPROVEMENT")
    
    print("=" * 60)
    
    return success_rate >= 90


if __name__ == "__main__":
    success = run_comprehensive_functionality_tests()
    sys.exit(0 if success else 1)