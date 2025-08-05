#!/usr/bin/env python3
"""
Production Deployment Tests for Jarvis V0.19
Integration with existing test framework without pytest dependency
"""

import asyncio
import sys
import os
import tempfile
import yaml
import json
from pathlib import Path

# Add project path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from jarvis.deployment import (
    ProductionDeploymentManager,
    InfrastructureProvisioner,
    KubernetesOrchestrator,
    ProductionConfigManager,
    ProductionMonitoring
)

class DeploymentTestSuite:
    """Test suite for production deployment framework"""
    
    def __init__(self):
        """Initialize test suite"""
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_results = []
    
    def assert_equal(self, actual, expected, message=""):
        """Assert that two values are equal"""
        if actual != expected:
            raise AssertionError(f"{message}: Expected {expected}, got {actual}")
    
    def assert_true(self, condition, message=""):
        """Assert that condition is True"""
        if not condition:
            raise AssertionError(f"{message}: Expected True, got {condition}")
    
    def assert_in(self, item, container, message=""):
        """Assert that item is in container"""
        if item not in container:
            raise AssertionError(f"{message}: {item} not found in {container}")
    
    async def run_test(self, test_name, test_func):
        """Run a single test"""
        try:
            print(f"Running {test_name}...")
            await test_func()
            print(f"✅ {test_name} PASSED")
            self.tests_passed += 1
            self.test_results.append({'name': test_name, 'status': 'PASSED'})
        except Exception as e:
            print(f"❌ {test_name} FAILED: {e}")
            self.tests_failed += 1
            self.test_results.append({'name': test_name, 'status': 'FAILED', 'error': str(e)})
    
    async def test_infrastructure_provisioner(self):
        """Test infrastructure provisioner functionality"""
        provisioner = InfrastructureProvisioner()
        
        # Test compute provisioning
        result = await provisioner.provision_compute(3, 'medium', ['us-west1-a'])
        self.assert_equal(result['status'], 'provisioned')
        self.assert_equal(result['node_count'], 3)
        self.assert_equal(len(result['resources']['nodes']), 3)
        
        # Test storage provisioning
        result = await provisioner.provision_storage('100Gi', 'fast-ssd')
        self.assert_equal(result['status'], 'provisioned')
        self.assert_equal(result['total_size'], '100Gi')
        
        # Test network provisioning
        result = await provisioner.provision_network('10.0.0.0/16', True)
        self.assert_equal(result['status'], 'provisioned')
        self.assert_equal(result['vpc_cidr'], '10.0.0.0/16')
        
        # Test cleanup
        result = await provisioner.cleanup_resources('test-deployment')
        self.assert_equal(result['status'], 'completed')
    
    async def test_kubernetes_orchestrator(self):
        """Test Kubernetes orchestrator functionality"""
        orchestrator = KubernetesOrchestrator()
        
        # Test manifest application (simulation mode)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump({
                'apiVersion': 'v1',
                'kind': 'ConfigMap',
                'metadata': {'name': 'test-config'}
            }, f)
            manifest_path = f.name
        
        try:
            result = await orchestrator.apply_manifest(manifest_path)
            self.assert_in(result['status'], ['applied', 'simulated'])
            
            # Test rollout waiting
            result = await orchestrator.wait_for_rollout('test-deployment', 'test-namespace')
            self.assert_in(result['status'], ['completed', 'simulated'])
            
            # Test health checks
            result = await orchestrator.check_pod_health('test-namespace')
            self.assert_in('healthy', result)
            
            result = await orchestrator.check_service_health('test-service', 'test-namespace')
            self.assert_in('healthy', result)
            
        finally:
            os.unlink(manifest_path)
    
    async def test_production_config_manager(self):
        """Test production configuration manager"""
        config_manager = ProductionConfigManager()
        
        # Test cluster config generation
        base_config = {'system': {'debug': False}, 'custom': 'test'}
        cluster_config = await config_manager.generate_cluster_config(
            'test-deployment', 3, base_config
        )
        
        # Verify required sections
        self.assert_in('deployment', cluster_config)
        self.assert_in('cluster', cluster_config)
        self.assert_in('crdt', cluster_config)
        self.assert_in('monitoring', cluster_config)
        
        # Verify deployment info
        self.assert_equal(cluster_config['deployment']['id'], 'test-deployment')
        self.assert_equal(cluster_config['deployment']['node_count'], 3)
        
        # Verify cluster config
        self.assert_equal(len(cluster_config['cluster']['nodes']), 3)
        
        # Verify base config merge
        self.assert_equal(cluster_config['custom'], 'test')
        
        # Test Kubernetes config creation
        k8s_configs = await config_manager.create_kubernetes_configs(cluster_config)
        self.assert_in('configmap', k8s_configs)
        self.assert_in('secret', k8s_configs)
        
        # Test configuration validation
        result = await config_manager.validate_configuration(cluster_config)
        self.assert_true(result['valid'])
    
    async def test_production_monitoring(self):
        """Test production monitoring functionality"""
        monitoring = ProductionMonitoring()
        
        # Test Prometheus deployment
        result = await monitoring.deploy_prometheus()
        self.assert_equal(result['status'], 'deployed')
        self.assert_equal(result['component'], 'prometheus')
        
        # Test Grafana deployment
        result = await monitoring.deploy_grafana()
        self.assert_equal(result['status'], 'deployed')
        self.assert_equal(result['component'], 'grafana')
        
        # Test alerting setup
        result = await monitoring.setup_alerting()
        self.assert_equal(result['status'], 'configured')
        self.assert_true(result['alert_rules_count'] > 0)
        
        # Test metrics collection
        result = await monitoring.collect_metrics()
        self.assert_equal(result['status'], 'collected')
        self.assert_in('metrics', result)
        
        # Test health check
        result = await monitoring.check_system_health()
        self.assert_in('overall_healthy', result)
        self.assert_in('health_score', result)
    
    async def test_deployment_manager_integration(self):
        """Test complete deployment manager integration"""
        # Create temporary config
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump({'system': {'debug': False}}, f)
            temp_config = f.name
        
        try:
            manager = ProductionDeploymentManager(temp_config)
            
            # Test deployment
            cluster_config = {
                'infrastructure': {
                    'node_count': 3,
                    'instance_type': 'medium',
                    'availability_zones': ['us-west1-a']
                }
            }
            
            result = await manager.deploy_cluster(cluster_config)
            self.assert_equal(result['status'], 'success')
            self.assert_in('deployment_id', result)
            
            # Test status retrieval
            status = await manager.get_deployment_status()
            self.assert_equal(status['state']['status'], 'deployed')
            
        finally:
            os.unlink(temp_config)
    
    async def run_all_tests(self):
        """Run all deployment tests"""
        print("🚀 Starting Production Deployment Framework Tests")
        print("=" * 60)
        
        test_methods = [
            ('Infrastructure Provisioner', self.test_infrastructure_provisioner),
            ('Kubernetes Orchestrator', self.test_kubernetes_orchestrator),
            ('Production Config Manager', self.test_production_config_manager),
            ('Production Monitoring', self.test_production_monitoring),
            ('Deployment Manager Integration', self.test_deployment_manager_integration)
        ]
        
        for test_name, test_func in test_methods:
            await self.run_test(test_name, test_func)
        
        print("=" * 60)
        print(f"📊 Test Results: {self.tests_passed} passed, {self.tests_failed} failed")
        
        if self.tests_failed > 0:
            print("❌ Some tests failed!")
            return False
        else:
            print("✅ All deployment tests passed!")
            return True

async def main():
    """Main test entry point"""
    test_suite = DeploymentTestSuite()
    success = await test_suite.run_all_tests()
    return 0 if success else 1

if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code)