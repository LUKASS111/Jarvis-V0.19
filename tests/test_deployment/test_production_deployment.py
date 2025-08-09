"""
Test Suite for Production Deployment Framework
Comprehensive testing for enterprise deployment capabilities
"""

import pytest
import asyncio
import tempfile
import yaml
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

# Import deployment modules
try:
    from jarvis.deployment import (
        ProductionDeploymentManager,
        InfrastructureProvisioner,
        KubernetesOrchestrator,
        ProductionConfigManager,
        ProductionMonitoring
    )
except ImportError:
    # Use proper pytest PYTHONPATH configuration instead of sys.path manipulation
    pytest.skip("Deployment modules not available - check PYTHONPATH configuration")

class TestProductionDeploymentManager:
    """Test Production Deployment Manager functionality"""
    
    @pytest.fixture
    def deployment_manager(self):
        """Create deployment manager for testing"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump({
                'system': {'debug': False, 'log_level': 'INFO'},
                'cluster': {'enabled': True}
            }, f)
            temp_config = f.name
        
        manager = ProductionDeploymentManager(temp_config)
        yield manager
        
        # Cleanup
        os.unlink(temp_config)
    
    @pytest.fixture
    def cluster_config(self):
        """Sample cluster configuration for testing"""
        return {
            'infrastructure': {
                'node_count': 3,
                'instance_type': 'medium',
                'availability_zones': ['us-west1-a', 'us-west1-b', 'us-west1-c'],
                'storage_size': '100Gi',
                'storage_class': 'fast-ssd',
                'vpc_cidr': '10.0.0.0/16'
            },
            'deployment': {
                'environment': 'production',
                'replicas': 3
            }
        }
    
    @pytest.mark.asyncio
    async def test_deploy_cluster_success(self, deployment_manager, cluster_config):
        """Test successful cluster deployment"""
        result = await deployment_manager.deploy_cluster(cluster_config)
        
        assert result['status'] == 'success'
        assert 'deployment_id' in result
        assert 'cluster_endpoint' in result
        assert 'monitoring_endpoint' in result
        assert result['deployment_time'] > 0
    
    @pytest.mark.asyncio
    async def test_deployment_state_tracking(self, deployment_manager, cluster_config):
        """Test deployment state is properly tracked"""
        # Check initial state
        initial_status = await deployment_manager.get_deployment_status()
        assert initial_status['state']['status'] == 'initialized'
        
        # Deploy cluster
        await deployment_manager.deploy_cluster(cluster_config)
        
        # Check final state
        final_status = await deployment_manager.get_deployment_status()
        assert final_status['state']['status'] == 'deployed'
        assert final_status['state']['start_time'] is not None
        assert final_status['state']['end_time'] is not None
    
    @pytest.mark.asyncio
    async def test_infrastructure_provisioning(self, deployment_manager, cluster_config):
        """Test infrastructure provisioning phase"""
        # Mock the provisioning methods to test the flow
        with patch.object(deployment_manager.infrastructure_provisioner, 'provision_compute') as mock_compute, \
             patch.object(deployment_manager.infrastructure_provisioner, 'provision_storage') as mock_storage, \
             patch.object(deployment_manager.infrastructure_provisioner, 'provision_network') as mock_network:
            
            mock_compute.return_value = {'status': 'provisioned', 'nodes': 3}
            mock_storage.return_value = {'status': 'provisioned', 'size': '100Gi'}
            mock_network.return_value = {'status': 'provisioned', 'vpc': 'test-vpc'}
            
            await deployment_manager._provision_infrastructure(cluster_config)
            
            # Verify all provisioning methods were called
            mock_compute.assert_called_once()
            mock_storage.assert_called_once()
            mock_network.assert_called_once()
            
            # Check infrastructure state
            assert 'infrastructure' in deployment_manager.deployment_state
            assert 'compute' in deployment_manager.deployment_state['infrastructure']

class TestInfrastructureProvisioner:
    """Test Infrastructure Provisioner functionality"""
    
    @pytest.fixture
    def provisioner(self):
        """Create infrastructure provisioner for testing"""
        return InfrastructureProvisioner()
    
    @pytest.mark.asyncio
    async def test_provision_compute(self, provisioner):
        """Test compute resource provisioning"""
        result = await provisioner.provision_compute(
            node_count=3,
            instance_type='medium',
            zones=['us-west1-a', 'us-west1-b', 'us-west1-c']
        )
        
        assert result['status'] == 'provisioned'
        assert result['node_count'] == 3
        assert len(result['resources']['nodes']) == 3
        
        # Check node configuration
        for i, node in enumerate(result['resources']['nodes']):
            assert node['node_id'] == f'jarvis-node-{i+1}'
            assert node['instance_type'] == 'medium'
            assert node['status'] == 'running'
    
    @pytest.mark.asyncio
    async def test_provision_storage(self, provisioner):
        """Test storage resource provisioning"""
        result = await provisioner.provision_storage(
            storage_size='100Gi',
            storage_class='fast-ssd'
        )
        
        assert result['status'] == 'provisioned'
        assert result['total_size'] == '100Gi'
        assert len(result['resources']['volumes']) == 3  # Default for CRDT replication
        
        # Check volume configuration
        for volume in result['resources']['volumes']:
            assert volume['size'] == '100Gi'
            assert volume['storage_class'] == 'fast-ssd'
            assert volume['encryption'] == 'enabled'
    
    @pytest.mark.asyncio
    async def test_provision_network(self, provisioner):
        """Test network resource provisioning"""
        result = await provisioner.provision_network(
            vpc_cidr='10.0.0.0/16',
            enable_load_balancer=True
        )
        
        assert result['status'] == 'provisioned'
        assert result['vpc_cidr'] == '10.0.0.0/16'
        
        # Check VPC configuration
        assert result['resources']['vpc']['cidr_block'] == '10.0.0.0/16'
        
        # Check subnets
        assert len(result['resources']['subnets']) == 3
        
        # Check security groups
        assert len(result['resources']['security_groups']) == 2
        
        # Check load balancer
        assert result['resources']['load_balancer'] is not None
        assert result['resources']['load_balancer']['type'] == 'application'
    
    @pytest.mark.asyncio
    async def test_resource_cleanup(self, provisioner):
        """Test resource cleanup functionality"""
        # Provision some resources first
        await provisioner.provision_compute(3, 'medium', ['us-west1-a'])
        await provisioner.provision_storage('50Gi', 'standard')
        
        # Verify resources exist
        assert len(provisioner.provisioned_resources) > 0
        
        # Clean up resources
        result = await provisioner.cleanup_resources('test-deployment')
        
        assert result['status'] == 'completed'
        assert result['deployment_id'] == 'test-deployment'
        assert len(provisioner.provisioned_resources) == 0

class TestKubernetesOrchestrator:
    """Test Kubernetes Orchestrator functionality"""
    
    @pytest.fixture
    def orchestrator(self):
        """Create Kubernetes orchestrator for testing"""
        return KubernetesOrchestrator()
    
    def test_kubectl_availability_check(self, orchestrator):
        """Test kubectl availability check"""
        # This will be False in test environment without kubectl
        assert isinstance(orchestrator.kubectl_available, bool)
    
    @pytest.mark.asyncio
    async def test_apply_manifest_simulation_mode(self, orchestrator):
        """Test manifest application in simulation mode"""
        # Create temporary manifest file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump({
                'apiVersion': 'v1',
                'kind': 'ConfigMap',
                'metadata': {'name': 'test-config'}
            }, f)
            manifest_path = f.name
        
        try:
            result = await orchestrator.apply_manifest(manifest_path)
            
            # In simulation mode, should return simulated status
            assert result['status'] in ['applied', 'simulated']
            assert result['manifest'] == manifest_path
        finally:
            os.unlink(manifest_path)
    
    @pytest.mark.asyncio
    async def test_wait_for_rollout(self, orchestrator):
        """Test deployment rollout waiting"""
        result = await orchestrator.wait_for_rollout(
            'test-deployment',
            'test-namespace',
            timeout=10
        )
        
        assert result['status'] in ['completed', 'simulated']
        assert result['deployment'] == 'test-deployment'
        assert result['namespace'] == 'test-namespace'
    
    @pytest.mark.asyncio
    async def test_pod_health_check(self, orchestrator):
        """Test pod health checking"""
        result = await orchestrator.check_pod_health('test-namespace')
        
        assert 'healthy' in result
        assert result['namespace'] == 'test-namespace'
        assert 'running_pods' in result
        assert 'total_pods' in result
    
    @pytest.mark.asyncio
    async def test_service_health_check(self, orchestrator):
        """Test service health checking"""
        result = await orchestrator.check_service_health('test-service', 'test-namespace')
        
        assert 'healthy' in result
        assert result['service'] == 'test-service'
        assert result['namespace'] == 'test-namespace'

class TestProductionConfigManager:
    """Test Production Configuration Manager functionality"""
    
    @pytest.fixture
    def config_manager(self):
        """Create configuration manager for testing"""
        return ProductionConfigManager()
    
    @pytest.mark.asyncio
    async def test_generate_cluster_config(self, config_manager):
        """Test cluster configuration generation"""
        base_config = {
            'system': {'debug': False},
            'custom_setting': 'test_value'
        }
        
        cluster_config = await config_manager.generate_cluster_config(
            deployment_id='test-deployment',
            node_count=3,
            base_config=base_config
        )
        
        # Check required sections
        assert 'deployment' in cluster_config
        assert 'cluster' in cluster_config
        assert 'crdt' in cluster_config
        assert 'monitoring' in cluster_config
        
        # Check deployment info
        assert cluster_config['deployment']['id'] == 'test-deployment'
        assert cluster_config['deployment']['node_count'] == 3
        
        # Check cluster config
        assert len(cluster_config['cluster']['nodes']) == 3
        assert cluster_config['cluster']['replication_factor'] == 3
        
        # Check base config merge
        assert cluster_config['custom_setting'] == 'test_value'
    
    @pytest.mark.asyncio
    async def test_kubernetes_config_creation(self, config_manager):
        """Test Kubernetes configuration creation"""
        cluster_config = {
            'deployment': {'id': 'test-deployment'},
            'cluster': {'nodes': []},
            'monitoring': {'enabled': True}
        }
        
        k8s_configs = await config_manager.create_kubernetes_configs(cluster_config)
        
        # Check ConfigMap
        assert 'configmap' in k8s_configs
        assert k8s_configs['configmap']['name'] == 'jarvis-config'
        assert k8s_configs['configmap']['namespace'] == 'jarvis-system'
        assert 'production.yaml' in k8s_configs['configmap']['data']
        
        # Check Secret
        assert 'secret' in k8s_configs
        assert k8s_configs['secret']['name'] == 'jarvis-secrets'
        assert 'api-key' in k8s_configs['secret']['data']
        assert 'encryption-key' in k8s_configs['secret']['data']
    
    @pytest.mark.asyncio
    async def test_configuration_validation(self, config_manager):
        """Test configuration validation"""
        # Valid configuration
        valid_config = {
            'system': {'debug': False},
            'cluster': {
                'nodes': [{'node_id': 'test-node'}],
                'replication_factor': 1
            },
            'crdt': {'sync_interval': 5},
            'monitoring': {'enabled': True},
            'security': {
                'encryption_enabled': True,
                'api_key_required': True
            }
        }
        
        result = await config_manager.validate_configuration(valid_config)
        
        assert result['valid'] is True
        assert len(result['errors']) == 0
        assert len(result['checks_performed']) > 0
        
        # Invalid configuration
        invalid_config = {
            'system': {'debug': False}
            # Missing required sections
        }
        
        result = await config_manager.validate_configuration(invalid_config)
        
        assert result['valid'] is False
        assert len(result['errors']) > 0

class TestProductionMonitoring:
    """Test Production Monitoring functionality"""
    
    @pytest.fixture
    def monitoring(self):
        """Create production monitoring for testing"""
        return ProductionMonitoring()
    
    @pytest.mark.asyncio
    async def test_deploy_prometheus(self, monitoring):
        """Test Prometheus deployment"""
        result = await monitoring.deploy_prometheus()
        
        assert result['status'] == 'deployed'
        assert result['component'] == 'prometheus'
        assert 'config' in result
        assert 'endpoint' in result
        
        # Check Prometheus configuration
        config = result['config']
        assert config['deployment_name'] == 'prometheus-server'
        assert len(config['scrape_configs']) > 0
    
    @pytest.mark.asyncio
    async def test_deploy_grafana(self, monitoring):
        """Test Grafana deployment"""
        result = await monitoring.deploy_grafana()
        
        assert result['status'] == 'deployed'
        assert result['component'] == 'grafana'
        assert 'config' in result
        
        # Check Grafana configuration
        config = result['config']
        assert len(config['dashboards']) == 3
        assert len(config['datasources']) == 1
    
    @pytest.mark.asyncio
    async def test_setup_alerting(self, monitoring):
        """Test alerting setup"""
        result = await monitoring.setup_alerting()
        
        assert result['status'] == 'configured'
        assert result['alert_rules_count'] > 0
        assert 'notification_channels' in result
        
        # Check notification channels
        channels = result['notification_channels']
        assert 'slack' in channels
        assert 'email' in channels
        assert 'pagerduty' in channels
    
    @pytest.mark.asyncio
    async def test_collect_metrics(self, monitoring):
        """Test metrics collection"""
        result = await monitoring.collect_metrics()
        
        assert result['status'] == 'collected'
        assert 'metrics' in result
        
        # Check metric categories
        metrics = result['metrics']
        assert 'cluster' in metrics
        assert 'crdt' in metrics
        assert 'api' in metrics
        assert 'system' in metrics
        assert 'database' in metrics
    
    @pytest.mark.asyncio
    async def test_system_health_check(self, monitoring):
        """Test comprehensive system health check"""
        result = await monitoring.check_system_health()
        
        assert 'overall_healthy' in result
        assert 'health_score' in result
        assert 'checks_passed' in result
        assert 'total_checks' in result
        assert 'details' in result
        
        # Check individual health checks
        details = result['details']
        assert 'cluster_nodes' in details
        assert 'crdt_synchronization' in details
        assert 'api_endpoints' in details
        assert 'database_health' in details
        assert 'monitoring_systems' in details

# Integration tests
class TestDeploymentIntegration:
    """Integration tests for complete deployment workflow"""
    
    @pytest.mark.asyncio
    async def test_full_deployment_workflow(self):
        """Test complete deployment workflow integration"""
        # Create deployment manager
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump({'system': {'debug': False}}, f)
            temp_config = f.name
        
        try:
            manager = ProductionDeploymentManager(temp_config)
            
            # Cluster configuration
            cluster_config = {
                'infrastructure': {
                    'node_count': 3,
                    'instance_type': 'medium',
                    'availability_zones': ['us-west1-a']
                }
            }
            
            # Deploy cluster
            result = await manager.deploy_cluster(cluster_config)
            
            # Should succeed in simulation mode
            assert result['status'] == 'success'
            
            # Get deployment status
            status = await manager.get_deployment_status()
            assert status['state']['status'] == 'deployed'
            
        finally:
            os.unlink(temp_config)

if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v'])