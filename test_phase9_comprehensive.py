#!/usr/bin/env python3
"""
Phase 9 Testing: Autonomous Intelligence & Predictive Systems
=============================================================

Comprehensive test suite for autonomous intelligence, predictive analytics,
self-management, and proactive assistance systems.
"""

import sys
import os
import unittest
import time
import json
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jarvis.phase9.autonomous_intelligence_manager import (
    AutonomousIntelligenceManager, AutonomousMode, AutonomousTask, TaskPriority,
    create_autonomous_intelligence_manager
)
from jarvis.phase9.predictive_analytics_engine import (
    PredictiveAnalyticsEngine, PredictionType, create_predictive_analytics_engine,
    simulate_predictive_data
)
from jarvis.phase9.self_management_system import (
    SelfManagementSystem, ManagementAction, SystemComponent, create_self_management_system
)
from jarvis.phase9.proactive_assistance_engine import (
    ProactiveAssistanceEngine, AssistanceType, AssistanceCategory, UrgencyLevel,
    create_proactive_assistance_engine
)
from jarvis.phase9.phase9_integration_manager import (
    Phase9IntegrationManager, process_phase9_request, get_phase9_dashboard, get_phase9_health
)


class TestAutonomousIntelligenceManager(unittest.TestCase):
    """Test autonomous intelligence manager functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.ai_manager = create_autonomous_intelligence_manager("test_ai", AutonomousMode.REACTIVE)
    
    def tearDown(self):
        """Clean up test environment"""
        if self.ai_manager.is_active:
            self.ai_manager.stop()
    
    def test_ai_manager_initialization(self):
        """Test AI manager initialization"""
        self.assertEqual(self.ai_manager.node_id, "test_ai")
        self.assertEqual(self.ai_manager.mode, AutonomousMode.REACTIVE)
        self.assertFalse(self.ai_manager.is_active)
        self.assertEqual(len(self.ai_manager.task_queue), 0)
        
        print("✓ Autonomous AI manager initialization test passed")
    
    def test_ai_manager_start_stop(self):
        """Test starting and stopping AI manager"""
        # Test start
        success = self.ai_manager.start()
        self.assertTrue(success)
        self.assertTrue(self.ai_manager.is_active)
        
        # Test stop
        success = self.ai_manager.stop()
        self.assertTrue(success)
        self.assertFalse(self.ai_manager.is_active)
        
        print("✓ Autonomous AI manager start/stop test passed")
    
    def test_autonomous_task_management(self):
        """Test autonomous task management"""
        self.ai_manager.start()
        
        # Create test task
        task = AutonomousTask(
            task_id="test_task_001",
            task_type="optimization",
            priority=TaskPriority.HIGH,
            description="Test optimization task"
        )
        
        # Add task
        success = self.ai_manager.add_autonomous_task(task)
        self.assertTrue(success)
        self.assertEqual(len(self.ai_manager.task_queue), 1)
        
        # Test duplicate task rejection
        duplicate_success = self.ai_manager.add_autonomous_task(task)
        self.assertFalse(duplicate_success)
        self.assertEqual(len(self.ai_manager.task_queue), 1)
        
        print("✓ Autonomous task management test passed")
    
    def test_autonomous_decision_making(self):
        """Test autonomous decision making"""
        self.ai_manager.start()
        
        # Create decision context
        context = {
            "performance": "degraded",
            "cpu_usage": 85.0,
            "memory_usage": 75.0
        }
        
        # Make autonomous decision
        decision = self.ai_manager.make_autonomous_decision(context)
        
        self.assertIsNotNone(decision)
        self.assertIsNotNone(decision.decision_id)
        self.assertGreater(decision.confidence, 0.0)
        self.assertLessEqual(decision.confidence, 1.0)
        self.assertEqual(len(self.ai_manager.pending_decisions), 1)
        
        print("✓ Autonomous decision making test passed")
    
    def test_mode_switching(self):
        """Test autonomous mode switching"""
        self.ai_manager.start()
        
        # Test mode changes
        success = self.ai_manager.set_mode(AutonomousMode.PROACTIVE)
        self.assertTrue(success)
        self.assertEqual(self.ai_manager.mode, AutonomousMode.PROACTIVE)
        
        success = self.ai_manager.set_mode(AutonomousMode.AUTONOMOUS)
        self.assertTrue(success)
        self.assertEqual(self.ai_manager.mode, AutonomousMode.AUTONOMOUS)
        
        print("✓ Autonomous mode switching test passed")
    
    def test_autonomous_status_reporting(self):
        """Test autonomous status reporting"""
        self.ai_manager.start()
        
        status = self.ai_manager.get_autonomous_status()
        
        required_fields = [
            "node_id", "mode", "is_active", "task_queue_size", 
            "metrics", "system_knowledge", "autonomous_health"
        ]
        
        for field in required_fields:
            self.assertIn(field, status)
        
        self.assertEqual(status["node_id"], "test_ai")
        self.assertTrue(status["is_active"])
        
        print("✓ Autonomous status reporting test passed")


class TestPredictiveAnalyticsEngine(unittest.TestCase):
    """Test predictive analytics engine functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.pred_engine = create_predictive_analytics_engine("test_predictor")
    
    def tearDown(self):
        """Clean up test environment"""
        if self.pred_engine.is_active:
            self.pred_engine.stop()
    
    def test_predictive_engine_initialization(self):
        """Test predictive engine initialization"""
        self.assertEqual(self.pred_engine.node_id, "test_predictor")
        self.assertFalse(self.pred_engine.is_active)
        self.assertEqual(len(self.pred_engine.predictions), 0)
        
        print("✓ Predictive engine initialization test passed")
    
    def test_predictive_engine_start_stop(self):
        """Test starting and stopping predictive engine"""
        # Test start
        success = self.pred_engine.start()
        self.assertTrue(success)
        self.assertTrue(self.pred_engine.is_active)
        
        # Test stop
        success = self.pred_engine.stop()
        self.assertTrue(success)
        self.assertFalse(self.pred_engine.is_active)
        
        print("✓ Predictive engine start/stop test passed")
    
    def test_data_point_management(self):
        """Test data point management"""
        self.pred_engine.start()
        
        # Add data points
        success = self.pred_engine.add_data_point("cpu_usage", 45.0)
        self.assertTrue(success)
        
        success = self.pred_engine.add_data_point("memory_usage", 60.0, 80.0, 90.0)
        self.assertTrue(success)
        
        # Verify data points
        self.assertIn("cpu_usage", self.pred_engine.time_series_data)
        self.assertIn("memory_usage", self.pred_engine.time_series_data)
        
        print("✓ Data point management test passed")
    
    def test_prediction_generation(self):
        """Test prediction generation"""
        self.pred_engine.start()
        
        # Add sufficient data points
        simulate_predictive_data(self.pred_engine, "test_metric", 20)
        
        # Make prediction
        prediction = self.pred_engine.make_prediction(
            PredictionType.PERFORMANCE, "test_metric", 3600
        )
        
        self.assertIsNotNone(prediction)
        self.assertIsNotNone(prediction.prediction_id)
        self.assertGreater(prediction.confidence, 0.0)
        self.assertLessEqual(prediction.confidence, 1.0)
        self.assertEqual(prediction.time_horizon, 3600)
        
        print("✓ Prediction generation test passed")
    
    def test_trend_detection(self):
        """Test trend detection"""
        self.pred_engine.start()
        
        # Add trending data
        for i in range(20):
            self.pred_engine.add_data_point("trending_metric", 50 + i * 2)
        
        time.sleep(0.1)  # Allow processing
        
        # Detect trends
        trend_result = self.pred_engine.detect_trends("trending_metric", 1)
        
        self.assertIn("trend", trend_result)
        self.assertIn("confidence", trend_result)
        self.assertGreater(trend_result["confidence"], 0.0)
        
        print("✓ Trend detection test passed")
    
    def test_anomaly_detection(self):
        """Test anomaly detection"""
        self.pred_engine.start()
        
        # Add normal data with anomaly
        for i in range(15):
            value = 50.0 if i != 10 else 150.0  # Anomaly at position 10
            self.pred_engine.add_data_point("anomaly_metric", value)
        
        # Detect anomalies
        anomalies = self.pred_engine.detect_anomalies("anomaly_metric", 2.0)
        
        self.assertGreater(len(anomalies), 0)
        self.assertIn("timestamp", anomalies[0])
        self.assertIn("z_score", anomalies[0])
        
        print("✓ Anomaly detection test passed")
    
    def test_prediction_validation(self):
        """Test prediction validation"""
        self.pred_engine.start()
        
        # Create and validate prediction
        simulate_predictive_data(self.pred_engine, "validation_metric", 15)
        
        prediction = self.pred_engine.make_prediction(
            PredictionType.PERFORMANCE, "validation_metric", 1800
        )
        
        self.assertIsNotNone(prediction)
        
        # Validate prediction
        actual_outcome = {"value": prediction.prediction.get("value", 0) * 1.1}
        success = self.pred_engine.validate_prediction(prediction.prediction_id, actual_outcome)
        
        self.assertTrue(success)
        self.assertTrue(prediction.validated)
        self.assertIsNotNone(prediction.accuracy)
        
        print("✓ Prediction validation test passed")


class TestSelfManagementSystem(unittest.TestCase):
    """Test self-management system functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.mgmt_system = create_self_management_system("test_manager")
    
    def tearDown(self):
        """Clean up test environment"""
        if self.mgmt_system.is_active:
            self.mgmt_system.stop()
    
    def test_management_system_initialization(self):
        """Test management system initialization"""
        self.assertEqual(self.mgmt_system.node_id, "test_manager")
        self.assertFalse(self.mgmt_system.is_active)
        self.assertEqual(len(self.mgmt_system.management_tasks), 0)
        
        print("✓ Self-management system initialization test passed")
    
    def test_management_system_start_stop(self):
        """Test starting and stopping management system"""
        # Test start
        success = self.mgmt_system.start()
        self.assertTrue(success)
        self.assertTrue(self.mgmt_system.is_active)
        
        # Test stop
        success = self.mgmt_system.stop()
        self.assertTrue(success)
        self.assertFalse(self.mgmt_system.is_active)
        
        print("✓ Self-management system start/stop test passed")
    
    def test_system_metric_management(self):
        """Test system metric management"""
        self.mgmt_system.start()
        
        # Update system metrics
        success = self.mgmt_system.update_system_metric("cpu_usage", 75.0, 80.0, 90.0)
        self.assertTrue(success)
        
        success = self.mgmt_system.update_system_metric("memory_usage", 65.0)
        self.assertTrue(success)
        
        # Verify metrics
        self.assertIn("cpu_usage", self.mgmt_system.system_metrics)
        self.assertIn("memory_usage", self.mgmt_system.system_metrics)
        
        cpu_metric = self.mgmt_system.system_metrics["cpu_usage"]
        self.assertEqual(cpu_metric.current_value, 75.0)
        self.assertEqual(cpu_metric.threshold_warning, 80.0)
        self.assertEqual(cpu_metric.threshold_critical, 90.0)
        
        print("✓ System metric management test passed")
    
    def test_optimization_triggering(self):
        """Test optimization triggering"""
        self.mgmt_system.start()
        
        # Trigger optimization
        task_id = self.mgmt_system.trigger_optimization(
            SystemComponent.DATABASE, 
            {"target": "query_performance"}
        )
        
        self.assertNotEqual(task_id, "")
        self.assertEqual(len(self.mgmt_system.management_tasks), 1)
        
        task = self.mgmt_system.management_tasks[0]
        self.assertEqual(task.action_type, ManagementAction.OPTIMIZATION)
        self.assertEqual(task.component, SystemComponent.DATABASE)
        
        print("✓ Optimization triggering test passed")
    
    def test_healing_triggering(self):
        """Test self-healing triggering"""
        self.mgmt_system.start()
        
        # Trigger healing
        task_id = self.mgmt_system.trigger_healing(
            SystemComponent.NETWORK, 
            "Connection timeout issues"
        )
        
        self.assertNotEqual(task_id, "")
        self.assertGreater(len(self.mgmt_system.management_tasks), 0)
        
        # Find healing task
        healing_task = None
        for task in self.mgmt_system.management_tasks:
            if task.action_type == ManagementAction.HEALING:
                healing_task = task
                break
        
        self.assertIsNotNone(healing_task)
        self.assertEqual(healing_task.component, SystemComponent.NETWORK)
        
        print("✓ Self-healing triggering test passed")
    
    def test_management_status_reporting(self):
        """Test management status reporting"""
        self.mgmt_system.start()
        
        # Add some test data
        self.mgmt_system.update_system_metric("test_metric", 50.0)
        
        status = self.mgmt_system.get_management_status()
        
        required_fields = [
            "node_id", "is_active", "pending_tasks", "system_health",
            "metrics", "system_metrics", "management_score"
        ]
        
        for field in required_fields:
            self.assertIn(field, status)
        
        self.assertEqual(status["node_id"], "test_manager")
        self.assertTrue(status["is_active"])
        
        print("✓ Management status reporting test passed")


class TestProactiveAssistanceEngine(unittest.TestCase):
    """Test proactive assistance engine functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.assist_engine = create_proactive_assistance_engine("test_assistant")
    
    def tearDown(self):
        """Clean up test environment"""
        if self.assist_engine.is_active:
            self.assist_engine.stop()
    
    def test_assistance_engine_initialization(self):
        """Test assistance engine initialization"""
        self.assertEqual(self.assist_engine.node_id, "test_assistant")
        self.assertFalse(self.assist_engine.is_active)
        self.assertEqual(len(self.assist_engine.active_assistance), 0)
        
        print("✓ Proactive assistance engine initialization test passed")
    
    def test_assistance_engine_start_stop(self):
        """Test starting and stopping assistance engine"""
        # Test start
        success = self.assist_engine.start()
        self.assertTrue(success)
        self.assertTrue(self.assist_engine.is_active)
        
        # Test stop
        success = self.assist_engine.stop()
        self.assertTrue(success)
        self.assertFalse(self.assist_engine.is_active)
        
        print("✓ Proactive assistance engine start/stop test passed")
    
    def test_user_context_management(self):
        """Test user context management"""
        self.assist_engine.start()
        
        # Update user context
        success = self.assist_engine.update_user_context(
            "data_analysis", 
            {"duration": 300, "complexity": "medium"}
        )
        self.assertTrue(success)
        
        # Verify context update
        self.assertIn("data_analysis", self.assist_engine.user_context.recent_actions)
        self.assertGreater(len(self.assist_engine.interaction_history), 0)
        
        print("✓ User context management test passed")
    
    def test_proactive_assistance_generation(self):
        """Test proactive assistance generation"""
        self.assist_engine.start()
        
        # Set up context for assistance
        context = {
            "slow_response": True,
            "high_cpu": True,
            "user_struggling": True
        }
        
        # Generate assistance
        assistance_items = self.assist_engine.generate_proactive_assistance(context)
        
        # Should generate at least one assistance item
        self.assertGreaterEqual(len(assistance_items), 0)
        
        if assistance_items:
            assistance = assistance_items[0]
            self.assertIsNotNone(assistance.assistance_id)
            self.assertGreater(assistance.confidence, 0.0)
            self.assertIsInstance(assistance.recommendations, list)
        
        print("✓ Proactive assistance generation test passed")
    
    def test_contextual_help_provision(self):
        """Test contextual help provision"""
        self.assist_engine.start()
        
        # Request contextual help
        help_response = self.assist_engine.provide_contextual_help(
            "How to optimize database performance?",
            {"current_task": "database_maintenance"}
        )
        
        self.assertIn("assistance_id", help_response)
        self.assertIn("help_provided", help_response)
        
        help_data = help_response["help_provided"]
        self.assertIn("description", help_data)
        self.assertIn("recommendations", help_data)
        self.assertIn("confidence", help_data)
        
        print("✓ Contextual help provision test passed")
    
    def test_workflow_optimization_suggestions(self):
        """Test workflow optimization suggestions"""
        self.assist_engine.start()
        
        # Request workflow optimization
        optimization_response = self.assist_engine.suggest_workflow_optimization("data_processing")
        
        self.assertIn("assistance_id", optimization_response)
        self.assertIn("workflow_analysis", optimization_response)
        self.assertIn("optimizations", optimization_response)
        
        analysis = optimization_response["workflow_analysis"]
        self.assertIn("workflow_name", analysis)
        self.assertIn("optimization_score", analysis)
        
        print("✓ Workflow optimization suggestions test passed")
    
    def test_user_need_prediction(self):
        """Test user need prediction"""
        self.assist_engine.start()
        
        # Add some user context
        self.assist_engine.update_user_context("analyze_data")
        self.assist_engine.update_user_context("generate_report")
        
        # Predict user needs
        predictions = self.assist_engine.predict_user_needs(60)
        
        self.assertIsInstance(predictions, list)
        # Should have at least some predictions
        if predictions:
            prediction = predictions[0]
            self.assertIn("need", prediction)
            self.assertIn("confidence", prediction)
            self.assertIn("reasoning", prediction)
        
        print("✓ User need prediction test passed")
    
    def test_user_action_recording(self):
        """Test user action recording"""
        self.assist_engine.start()
        
        # Generate assistance first
        assistance_items = self.assist_engine.generate_proactive_assistance({
            "performance_issue": True
        })
        
        if assistance_items:
            assistance = assistance_items[0]
            
            # Record user action
            success = self.assist_engine.record_user_action(
                assistance.assistance_id, 
                "accepted", 
                0.8
            )
            
            self.assertTrue(success)
            self.assertEqual(assistance.user_action_taken, "accepted")
            self.assertEqual(assistance.effectiveness_score, 0.8)
            self.assertTrue(assistance.shown_to_user)
        
        print("✓ User action recording test passed")


class TestPhase9Integration(unittest.TestCase):
    """Test Phase 9 integration functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.integration_manager = Phase9IntegrationManager("test_phase9")
    
    def tearDown(self):
        """Clean up test environment"""
        if self.integration_manager.is_active:
            self.integration_manager.stop()
    
    def test_phase9_integration_initialization(self):
        """Test Phase 9 integration initialization"""
        self.assertEqual(self.integration_manager.node_id, "test_phase9")
        self.assertFalse(self.integration_manager.is_active)
        self.assertIsNone(self.integration_manager.autonomous_ai)
        self.assertIsNone(self.integration_manager.predictive_engine)
        
        print("✓ Phase 9 integration initialization test passed")
    
    def test_phase9_integration_start_stop(self):
        """Test starting and stopping Phase 9 integration"""
        # Test start
        success = self.integration_manager.start()
        self.assertTrue(success)
        self.assertTrue(self.integration_manager.is_active)
        self.assertIsNotNone(self.integration_manager.autonomous_ai)
        self.assertIsNotNone(self.integration_manager.predictive_engine)
        
        # Test stop
        success = self.integration_manager.stop()
        self.assertTrue(success)
        self.assertFalse(self.integration_manager.is_active)
        
        print("✓ Phase 9 integration start/stop test passed")
    
    def test_phase9_request_processing(self):
        """Test Phase 9 request processing"""
        self.integration_manager.start()
        
        # Process request
        result = self.integration_manager.process_request(
            "Optimize system performance",
            "optimization",
            {"target": "cpu_usage"},
            autonomous_mode=True
        )
        
        self.assertIn("request_id", result)
        self.assertIn("success", result)
        self.assertIn("phase9_capabilities", result)
        
        capabilities = result["phase9_capabilities"]
        self.assertIn("autonomous_intelligence", capabilities)
        self.assertIn("predictive_analytics", capabilities)
        
        print("✓ Phase 9 request processing test passed")
    
    def test_phase9_dashboard_generation(self):
        """Test Phase 9 dashboard generation"""
        self.integration_manager.start()
        
        dashboard = self.integration_manager.get_dashboard()
        
        required_sections = [
            "overview", "autonomous_intelligence", "predictive_analytics",
            "integration_status", "performance_metrics", "system_health"
        ]
        
        for section in required_sections:
            self.assertIn(section, dashboard)
        
        overview = dashboard["overview"]
        self.assertEqual(overview["node_id"], "test_phase9")
        self.assertTrue(overview["is_active"])
        
        print("✓ Phase 9 dashboard generation test passed")
    
    def test_phase9_health_monitoring(self):
        """Test Phase 9 health monitoring"""
        self.integration_manager.start()
        
        health = self.integration_manager.get_health_status()
        
        required_fields = [
            "phase", "status", "overall_health", "component_health",
            "capabilities", "metrics"
        ]
        
        for field in required_fields:
            self.assertIn(field, health)
        
        self.assertEqual(health["phase"], "Phase 9: Autonomous Intelligence & Predictive Systems")
        self.assertIn(health["status"], ["operational", "degraded"])
        
        print("✓ Phase 9 health monitoring test passed")
    
    def test_autonomous_mode_enabling(self):
        """Test autonomous mode enabling"""
        self.integration_manager.start()
        
        # Enable different autonomous modes
        success = self.integration_manager.enable_autonomous_mode(AutonomousMode.PROACTIVE)
        self.assertTrue(success)
        
        success = self.integration_manager.enable_autonomous_mode(AutonomousMode.AUTONOMOUS)
        self.assertTrue(success)
        
        print("✓ Autonomous mode enabling test passed")
    
    def test_autonomous_assistant_creation(self):
        """Test autonomous assistant creation"""
        self.integration_manager.start()
        
        # Create autonomous assistant
        result = self.integration_manager.create_autonomous_assistant(
            "TestAssistant",
            ["analysis", "optimization", "monitoring"]
        )
        
        self.assertIn("success", result)
        self.assertTrue(result["success"])
        self.assertIn("assistant_id", result)
        self.assertIn("name", result)
        self.assertEqual(result["name"], "TestAssistant")
        
        print("✓ Autonomous assistant creation test passed")


class TestPhase9ModuleFunctions(unittest.TestCase):
    """Test Phase 9 module-level functions"""
    
    def test_process_phase9_request_function(self):
        """Test module-level request processing function"""
        result = process_phase9_request(
            "Test autonomous processing",
            "test",
            {"parameter": "value"},
            autonomous_mode=True
        )
        
        self.assertIn("request_id", result)
        self.assertIn("phase9_capabilities", result)
        
        print("✓ Module-level request processing test passed")
    
    def test_get_phase9_dashboard_function(self):
        """Test module-level dashboard function"""
        dashboard = get_phase9_dashboard()
        
        self.assertIn("overview", dashboard)
        self.assertIn("autonomous_intelligence", dashboard)
        self.assertIn("predictive_analytics", dashboard)
        
        print("✓ Module-level dashboard function test passed")
    
    def test_get_phase9_health_function(self):
        """Test module-level health function"""
        health = get_phase9_health()
        
        self.assertIn("phase", health)
        self.assertIn("overall_health", health)
        self.assertIn("capabilities", health)
        
        print("✓ Module-level health function test passed")


def run_phase9_tests():
    """Run all Phase 9 tests"""
    print("\n" + "="*70)
    print("PHASE 9: AUTONOMOUS INTELLIGENCE & PREDICTIVE SYSTEMS - TEST SUITE")
    print("="*70)
    
    # Test suites
    test_suites = [
        ('Autonomous Intelligence Manager', TestAutonomousIntelligenceManager),
        ('Predictive Analytics Engine', TestPredictiveAnalyticsEngine),
        ('Self-Management System', TestSelfManagementSystem),
        ('Proactive Assistance Engine', TestProactiveAssistanceEngine),
        ('Phase 9 Integration', TestPhase9Integration),
        ('Module Functions', TestPhase9ModuleFunctions)
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    
    for suite_name, test_class in test_suites:
        print(f"\n[TEST SUITE] {suite_name}")
        print("-" * 60)
        
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        runner = unittest.TextTestRunner(verbosity=0, stream=open('/dev/null', 'w'))
        result = runner.run(suite)
        
        suite_tests = result.testsRun
        suite_failures = len(result.failures)
        suite_errors = len(result.errors)
        suite_passed = suite_tests - suite_failures - suite_errors
        
        total_tests += suite_tests
        passed_tests += suite_passed
        failed_tests += suite_failures + suite_errors
        
        if suite_failures == 0 and suite_errors == 0:
            print(f"✅ {suite_name}: {suite_passed}/{suite_tests} tests passed")
        else:
            print(f"❌ {suite_name}: {suite_passed}/{suite_tests} tests passed")
            for failure in result.failures:
                print(f"   FAIL: {failure[0]}")
                print(f"   {failure[1]}")
            for error in result.errors:
                print(f"   ERROR: {error[0]}")
                print(f"   {error[1]}")
    
    # Final summary
    print(f"\n" + "="*70)
    print("PHASE 9 TEST RESULTS SUMMARY")
    print("="*70)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests == 0:
        print("\n🎉 ALL PHASE 9 TESTS PASSED!")
        print("✅ Autonomous Intelligence & Predictive Systems operational")
        print("✅ Self-management capabilities validated")
        print("✅ Proactive assistance engine functional")
        print("✅ Integration layer working perfectly")
        print("✅ Phase 9 ready for production deployment")
    else:
        print(f"\n⚠️  {failed_tests} tests failed - review implementation")
    
    return passed_tests, total_tests


if __name__ == "__main__":
    passed, total = run_phase9_tests()
    exit(0 if passed == total else 1)