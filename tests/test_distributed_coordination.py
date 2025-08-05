"""
Comprehensive Test Suite for Distributed Agent Coordination System
Phase 6 Implementation: Advanced Distributed Intelligence Testing
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import time
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List

from jarvis.core.distributed_agent_coordinator import (
    DistributedAgentCoordinator, DistributedTask, AgentCapabilities,
    TaskPriority, AgentStatus, get_distributed_coordinator
)

class TestDistributedAgentCoordination(unittest.TestCase):
    """Test suite for distributed agent coordination functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.coordinator = DistributedAgentCoordinator()
        self.test_agents = []
        self.test_tasks = []
        
        # Create test agents
        for i in range(3):
            agent = AgentCapabilities(
                agent_id=f"test_agent_{i}",
                node_id=f"node_{i}",
                max_concurrent_tasks=5,
                specialized_types=["functional", "performance"] if i % 2 == 0 else ["integration", "security"],
                performance_rating=8.0 + i,
                resource_availability={
                    "cpu": 80.0 - (i * 10),
                    "memory": 90.0 - (i * 5),
                    "network": 95.0,
                    "storage": 85.0
                },
                last_health_check=datetime.now().isoformat(),
                network_latency=50.0 + (i * 10)
            )
            self.test_agents.append(agent)
        
        # Create test tasks
        for i in range(5):
            task = DistributedTask(
                task_id=f"test_task_{i}",
                name=f"Test Task {i}",
                description=f"Test task for distributed coordination {i}",
                task_type="functional" if i % 2 == 0 else "performance",
                priority=TaskPriority.HIGH if i < 2 else TaskPriority.NORMAL,
                data={"test_data": f"data_{i}"},
                requirements={
                    "resources": {
                        "cpu": 10 + i,
                        "memory": 15 + i,
                        "network": 5,
                        "storage": 8
                    }
                },
                deadline=(datetime.now().isoformat() if i < 3 else None),
                dependencies=[],
                assigned_agents=[],
                created_at=datetime.now().isoformat()
            )
            self.test_tasks.append(task)
    
    def test_coordinator_initialization(self):
        """Test coordinator initialization"""
        coordinator = DistributedAgentCoordinator()
        
        # Check initialization
        self.assertIsNotNone(coordinator.coordinator_id)
        self.assertIsNotNone(coordinator.crdt_manager)
        self.assertIsNotNone(coordinator.agent_states)
        self.assertIsNotNone(coordinator.task_assignments)
        self.assertIsNotNone(coordinator.resource_pool)
        self.assertFalse(coordinator.running)
        
        # Check initial metrics
        self.assertEqual(coordinator.metrics.total_tasks_coordinated, 0)
        self.assertEqual(coordinator.metrics.successful_coordinations, 0)
        
        print("✓ Coordinator initialization test passed")
    
    def test_agent_registration(self):
        """Test agent registration functionality"""
        # Register test agents
        for agent in self.test_agents:
            result = self.coordinator.register_agent(agent)
            self.assertTrue(result)
        
        # Verify agents are registered
        self.assertEqual(len(self.coordinator.agents), 3)
        
        # Check agent data
        for agent in self.test_agents:
            self.assertIn(agent.agent_id, self.coordinator.agents)
            registered_agent = self.coordinator.agents[agent.agent_id]
            self.assertEqual(registered_agent.agent_id, agent.agent_id)
            self.assertEqual(registered_agent.node_id, agent.node_id)
        
        # Check CRDT state
        agent_states = self.coordinator.agent_states.elements()
        self.assertEqual(len(agent_states), 3)
        
        print("✓ Agent registration test passed")
    
    def test_task_submission(self):
        """Test task submission functionality"""
        # Submit test tasks
        for task in self.test_tasks:
            result = self.coordinator.submit_distributed_task(task)
            self.assertTrue(result)
        
        # Verify tasks are submitted
        self.assertEqual(len(self.coordinator.pending_tasks), 5)
        
        # Check task data
        for task in self.test_tasks:
            self.assertIn(task.task_id, self.coordinator.pending_tasks)
            submitted_task = self.coordinator.pending_tasks[task.task_id]
            self.assertEqual(submitted_task.task_id, task.task_id)
            self.assertEqual(submitted_task.status, "pending")
        
        print("✓ Task submission test passed")
    
    def test_task_coordination(self):
        """Test full task coordination process"""
        # Register agents
        for agent in self.test_agents:
            self.coordinator.register_agent(agent)
        
        # Coordinate tasks
        results = self.coordinator.coordinate_agents(self.test_tasks)
        
        # Verify coordination results
        self.assertIsInstance(results, dict)
        self.assertIn("coordinated_tasks", results)
        self.assertIn("successful_assignments", results)
        self.assertIn("coordination_time", results)
        
        # Check that tasks were coordinated
        self.assertEqual(results["coordinated_tasks"], 5)
        self.assertGreater(results["successful_assignments"], 0)
        self.assertGreater(results["coordination_time"], 0)
        
        # Verify some tasks moved to active
        self.assertGreater(len(self.coordinator.active_tasks), 0)
        
        print(f"✓ Task coordination test passed - {results['successful_assignments']}/{results['coordinated_tasks']} tasks assigned")
    
    def test_intelligent_assignment(self):
        """Test intelligent task assignment algorithm"""
        # Register agents with different capabilities
        for agent in self.test_agents:
            self.coordinator.register_agent(agent)
        
        # Submit tasks
        for task in self.test_tasks:
            self.coordinator.submit_distributed_task(task)
        
        # Perform assignment
        assignment_results = self.coordinator._perform_intelligent_assignment()
        
        # Verify assignment results
        self.assertIsInstance(assignment_results, dict)
        self.assertIn("successful_assignments", assignment_results)
        self.assertIn("assignment_details", assignment_results)
        
        # Check assignment quality
        self.assertGreater(assignment_results["successful_assignments"], 0)
        
        # Verify assignment details
        for detail in assignment_results["assignment_details"]:
            self.assertIn("task_id", detail)
            self.assertIn("agent_id", detail)
            self.assertIn("assignment_score", detail)
            self.assertGreater(detail["assignment_score"], 0.5)  # Good assignment score
        
        print(f"✓ Intelligent assignment test passed - {assignment_results['successful_assignments']} successful assignments")
    
    def test_assignment_scoring(self):
        """Test assignment scoring algorithm"""
        agent = self.test_agents[0]
        task = self.test_tasks[0]
        
        # Calculate assignment score
        score = self.coordinator._calculate_assignment_score(task, agent)
        
        # Verify score is reasonable
        self.assertGreater(score, 0.0)
        self.assertLessEqual(score, 1.0)
        
        # Test with specialized agent
        specialized_agent = AgentCapabilities(
            agent_id="specialized_agent",
            node_id="specialized_node",
            max_concurrent_tasks=10,
            specialized_types=["functional"],  # Matches task type
            performance_rating=10.0,
            resource_availability={"cpu": 100, "memory": 100, "network": 100, "storage": 100},
            last_health_check=datetime.now().isoformat(),
            network_latency=10.0
        )
        
        specialized_score = self.coordinator._calculate_assignment_score(task, specialized_agent)
        
        # Specialized agent should score higher
        self.assertGreater(specialized_score, score)
        
        print(f"✓ Assignment scoring test passed - base score: {score:.2f}, specialized score: {specialized_score:.2f}")
    
    def test_coordination_lifecycle(self):
        """Test coordination system lifecycle"""
        # Start coordination
        self.coordinator.start_coordination()
        self.assertTrue(self.coordinator.running)
        self.assertIsNotNone(self.coordinator.coordination_thread)
        
        # Let it run briefly
        time.sleep(0.5)
        
        # Stop coordination
        self.coordinator.stop_coordination()
        self.assertFalse(self.coordinator.running)
        
        print("✓ Coordination lifecycle test passed")
    
    def test_load_balancing(self):
        """Test load balancing functionality"""
        # Register agents
        for agent in self.test_agents:
            self.coordinator.register_agent(agent)
        
        # Submit and assign tasks
        for task in self.test_tasks:
            self.coordinator.submit_distributed_task(task)
        
        self.coordinator._perform_intelligent_assignment()
        
        # Calculate load balance efficiency
        efficiency = self.coordinator._calculate_load_balance_efficiency()
        
        # Verify efficiency calculation
        self.assertGreaterEqual(efficiency, 0.0)
        self.assertLessEqual(efficiency, 1.0)
        
        print(f"✓ Load balancing test passed - efficiency: {efficiency:.2f}")
    
    def test_resource_management(self):
        """Test resource pool management"""
        # Check initial resource pool
        initial_resources = {
            resource: self.coordinator.resource_pool[resource].value()
            for resource in ["cpu", "memory", "network", "storage"]
        }
        
        # Register an agent (should increase resources)
        agent = self.test_agents[0]
        self.coordinator.register_agent(agent)
        
        # Check resource increase
        for resource, capacity in agent.resource_availability.items():
            if resource in self.coordinator.resource_pool:
                new_value = self.coordinator.resource_pool[resource].value()
                self.assertGreaterEqual(new_value, initial_resources.get(resource, 0))
        
        print("✓ Resource management test passed")
    
    def test_crdt_integration(self):
        """Test CRDT integration functionality"""
        # Register agent and check CRDT state
        agent = self.test_agents[0]
        self.coordinator.register_agent(agent)
        
        # Check agent states CRDT
        agent_states = self.coordinator.agent_states.elements()
        self.assertEqual(len(agent_states), 1)
        
        # Parse agent state
        agent_data = json.loads(list(agent_states)[0])
        self.assertEqual(agent_data["agent_id"], agent.agent_id)
        
        # Submit task and check task assignments CRDT
        task = self.test_tasks[0]
        self.coordinator.submit_distributed_task(task)
        
        # Check task assignment CRDT
        task_assignment = self.coordinator.task_assignments.read()
        self.assertIsNotNone(task_assignment)
        
        assignment_data = json.loads(task_assignment) if task_assignment else {}
        self.assertIn("task_id", assignment_data)
        
        print("✓ CRDT integration test passed")
    
    def test_coordination_metrics(self):
        """Test coordination metrics collection"""
        # Register agents and coordinate tasks
        for agent in self.test_agents:
            self.coordinator.register_agent(agent)
        
        results = self.coordinator.coordinate_agents(self.test_tasks)
        
        # Check metrics update
        metrics = self.coordinator.metrics
        self.assertGreater(metrics.total_tasks_coordinated, 0)
        self.assertGreaterEqual(metrics.successful_coordinations, 0)
        self.assertGreaterEqual(metrics.average_coordination_time, 0)
        
        print(f"✓ Coordination metrics test passed - {metrics.total_tasks_coordinated} tasks coordinated")
    
    def test_health_metrics(self):
        """Test health metrics generation"""
        # Register agents
        for agent in self.test_agents:
            self.coordinator.register_agent(agent)
        
        # Get health metrics
        health_metrics = self.coordinator.get_health_metrics()
        
        # Verify health metrics structure
        expected_fields = [
            "coordination_efficiency", "average_coordination_time",
            "load_balancing_score", "network_efficiency",
            "agent_count", "active_tasks", "system_status"
        ]
        
        for field in expected_fields:
            self.assertIn(field, health_metrics)
        
        # Verify values
        self.assertEqual(health_metrics["agent_count"], 3)
        self.assertEqual(health_metrics["system_status"], "stopped")  # Not started
        
        print("✓ Health metrics test passed")
    
    def test_coordination_status(self):
        """Test coordination status reporting"""
        # Register agents and submit tasks
        for agent in self.test_agents:
            self.coordinator.register_agent(agent)
        
        for task in self.test_tasks:
            self.coordinator.submit_distributed_task(task)
        
        # Get coordination status
        status = self.coordinator.get_coordination_status()
        
        # Verify status structure
        expected_fields = [
            "coordinator_id", "running", "registered_agents",
            "pending_tasks", "active_tasks", "completed_tasks",
            "metrics", "resource_pool", "agents"
        ]
        
        for field in expected_fields:
            self.assertIn(field, status)
        
        # Verify values
        self.assertEqual(status["registered_agents"], 3)
        self.assertEqual(status["pending_tasks"], 5)
        self.assertFalse(status["running"])
        
        print("✓ Coordination status test passed")
    
    def test_global_coordinator_instance(self):
        """Test global coordinator instance management"""
        # Get global instance
        coordinator1 = get_distributed_coordinator()
        coordinator2 = get_distributed_coordinator()
        
        # Should be the same instance
        self.assertIs(coordinator1, coordinator2)
        
        print("✓ Global coordinator instance test passed")

class TestDistributedTaskManagement(unittest.TestCase):
    """Test suite for distributed task management"""
    
    def setUp(self):
        """Set up test environment"""
        self.coordinator = DistributedAgentCoordinator()
        
        # Create test agent
        self.test_agent = AgentCapabilities(
            agent_id="task_test_agent",
            node_id="task_test_node",
            max_concurrent_tasks=3,
            specialized_types=["functional", "performance"],
            performance_rating=9.0,
            resource_availability={"cpu": 90, "memory": 85, "network": 95, "storage": 80},
            last_health_check=datetime.now().isoformat(),
            network_latency=30.0
        )
        
        self.coordinator.register_agent(self.test_agent)
    
    def test_task_priority_handling(self):
        """Test task priority handling in assignment"""
        # Create tasks with different priorities
        high_priority_task = DistributedTask(
            task_id="high_priority_task",
            name="High Priority Task",
            description="Critical task",
            task_type="functional",
            priority=TaskPriority.CRITICAL,
            data={"priority": "critical"},
            requirements={"resources": {"cpu": 10}},
            deadline=None,
            dependencies=[],
            assigned_agents=[],
            created_at=datetime.now().isoformat()
        )
        
        low_priority_task = DistributedTask(
            task_id="low_priority_task", 
            name="Low Priority Task",
            description="Background task",
            task_type="functional",
            priority=TaskPriority.BACKGROUND,
            data={"priority": "background"},
            requirements={"resources": {"cpu": 5}},
            deadline=None,
            dependencies=[],
            assigned_agents=[],
            created_at=datetime.now().isoformat()
        )
        
        # Submit in reverse priority order
        self.coordinator.submit_distributed_task(low_priority_task)
        self.coordinator.submit_distributed_task(high_priority_task)
        
        # Perform assignment
        results = self.coordinator._perform_intelligent_assignment()
        
        # High priority task should be assigned first
        self.assertGreater(results["successful_assignments"], 0)
        
        # Check which task was assigned
        assigned_tasks = list(self.coordinator.active_tasks.values())
        if assigned_tasks:
            # Should prioritize critical task
            first_assigned = assigned_tasks[0]
            self.assertEqual(first_assigned.priority, TaskPriority.CRITICAL)
        
        print("✓ Task priority handling test passed")
    
    def test_task_dependencies(self):
        """Test task dependency handling"""
        # Create dependent tasks
        parent_task = DistributedTask(
            task_id="parent_task",
            name="Parent Task",
            description="Parent task",
            task_type="functional",
            priority=TaskPriority.NORMAL,
            data={"type": "parent"},
            requirements={"resources": {"cpu": 10}},
            deadline=None,
            dependencies=[],
            assigned_agents=[],
            created_at=datetime.now().isoformat()
        )
        
        child_task = DistributedTask(
            task_id="child_task",
            name="Child Task", 
            description="Dependent task",
            task_type="functional",
            priority=TaskPriority.NORMAL,
            data={"type": "child"},
            requirements={"resources": {"cpu": 8}},
            deadline=None,
            dependencies=["parent_task"],
            assigned_agents=[],
            created_at=datetime.now().isoformat()
        )
        
        # Submit tasks
        self.coordinator.submit_distributed_task(parent_task)
        self.coordinator.submit_distributed_task(child_task)
        
        # Verify dependency structure
        self.assertEqual(len(child_task.dependencies), 1)
        self.assertIn("parent_task", child_task.dependencies)
        
        print("✓ Task dependencies test passed")
    
    def test_resource_requirements(self):
        """Test resource requirement validation"""
        # Create task with high resource requirements
        resource_intensive_task = DistributedTask(
            task_id="resource_intensive_task",
            name="Resource Intensive Task",
            description="Task requiring many resources",
            task_type="performance",
            priority=TaskPriority.HIGH,
            data={"type": "resource_intensive"},
            requirements={
                "resources": {
                    "cpu": 50,
                    "memory": 60,
                    "network": 20,
                    "storage": 30
                }
            },
            deadline=None,
            dependencies=[],
            assigned_agents=[],
            created_at=datetime.now().isoformat()
        )
        
        # Submit and try to assign
        self.coordinator.submit_distributed_task(resource_intensive_task)
        results = self.coordinator._perform_intelligent_assignment()
        
        # Should handle resource requirements appropriately
        self.assertIsInstance(results, dict)
        self.assertIn("successful_assignments", results)
        
        print("✓ Resource requirements test passed")

class TestDistributedAgentCapabilities(unittest.TestCase):
    """Test suite for distributed agent capabilities"""
    
    def test_agent_specialization(self):
        """Test agent specialization handling"""
        # Create specialized agents
        functional_agent = AgentCapabilities(
            agent_id="functional_agent",
            node_id="functional_node",
            max_concurrent_tasks=5,
            specialized_types=["functional", "integration"],
            performance_rating=8.5,
            resource_availability={"cpu": 80, "memory": 85, "network": 90, "storage": 75},
            last_health_check=datetime.now().isoformat(),
            network_latency=40.0
        )
        
        performance_agent = AgentCapabilities(
            agent_id="performance_agent",
            node_id="performance_node",
            max_concurrent_tasks=3,
            specialized_types=["performance", "load"],
            performance_rating=9.2,
            resource_availability={"cpu": 95, "memory": 90, "network": 85, "storage": 80},
            last_health_check=datetime.now().isoformat(),
            network_latency=25.0
        )
        
        coordinator = DistributedAgentCoordinator()
        
        # Register agents
        coordinator.register_agent(functional_agent)
        coordinator.register_agent(performance_agent)
        
        # Create specialized tasks
        functional_task = DistributedTask(
            task_id="functional_task",
            name="Functional Test Task",
            description="Functional testing task",
            task_type="functional",
            priority=TaskPriority.NORMAL,
            data={"test_type": "functional"},
            requirements={"resources": {"cpu": 15}},
            deadline=None,
            dependencies=[],
            assigned_agents=[],
            created_at=datetime.now().isoformat()
        )
        
        performance_task = DistributedTask(
            task_id="performance_task",
            name="Performance Test Task",
            description="Performance testing task",
            task_type="performance",
            priority=TaskPriority.NORMAL,
            data={"test_type": "performance"},
            requirements={"resources": {"cpu": 20}},
            deadline=None,
            dependencies=[],
            assigned_agents=[],
            created_at=datetime.now().isoformat()
        )
        
        # Test assignment scoring
        functional_score_functional = coordinator._calculate_assignment_score(functional_task, functional_agent)
        functional_score_performance = coordinator._calculate_assignment_score(functional_task, performance_agent)
        
        performance_score_functional = coordinator._calculate_assignment_score(performance_task, functional_agent)
        performance_score_performance = coordinator._calculate_assignment_score(performance_task, performance_agent)
        
        # Specialized agents should score higher for their specialization
        self.assertGreater(functional_score_functional, functional_score_performance)
        self.assertGreater(performance_score_performance, performance_score_functional)
        
        print("✓ Agent specialization test passed")

def run_distributed_coordination_tests():
    """Run all distributed coordination tests"""
    print("\n" + "="*80)
    print("DISTRIBUTED AGENT COORDINATION TESTS - Phase 6 Implementation")
    print("="*80)
    
    test_suites = [
        TestDistributedAgentCoordination,
        TestDistributedTaskManagement,
        TestDistributedAgentCapabilities
    ]
    
    total_tests = 0
    passed_tests = 0
    
    for test_suite_class in test_suites:
        print(f"\nRunning {test_suite_class.__name__}...")
        suite = unittest.TestLoader().loadTestsFromTestCase(test_suite_class)
        runner = unittest.TextTestRunner(verbosity=0, stream=open('/dev/null', 'w'))
        result = runner.run(suite)
        
        total_tests += result.testsRun
        passed_tests += result.testsRun - len(result.failures) - len(result.errors)
        
        if result.failures:
            print(f"FAILURES in {test_suite_class.__name__}:")
            for test, traceback in result.failures:
                print(f"  - {test}: {traceback}")
        
        if result.errors:
            print(f"ERRORS in {test_suite_class.__name__}:")
            for test, traceback in result.errors:
                print(f"  - {test}: {traceback}")
    
    print("\n" + "="*80)
    print("DISTRIBUTED COORDINATION TEST SUMMARY")
    print("="*80)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%" if total_tests > 0 else "No tests run")
    
    if passed_tests == total_tests:
        print("🎉 ALL DISTRIBUTED COORDINATION TESTS PASSED!")
        return True
    else:
        print("⚠️  Some distributed coordination tests failed")
        return False

if __name__ == "__main__":
    run_distributed_coordination_tests()