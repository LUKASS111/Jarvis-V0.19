"""
Production Configuration Manager for Jarvis Deployment
Handles enterprise configuration generation and management
"""

import logging
import yaml
import json
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

class ProductionConfigManager:
    """
    Production Configuration Manager for Jarvis CRDT Cluster
    
    Manages enterprise-grade configuration generation, validation,
    and deployment for distributed AI system operations.
    """
    
    def __init__(self):
        """Initialize production configuration manager"""
        self.base_config_path = Path("config/environments")
        self.generated_configs = {}
        logger.info("Initialized ProductionConfigManager")
    
    async def generate_cluster_config(self, deployment_id: str, node_count: int, 
                                    base_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate cluster-specific configuration
        
        Args:
            deployment_id: Unique deployment identifier
            node_count: Number of cluster nodes
            base_config: Base configuration template
            
        Returns:
            Generated cluster configuration
        """
        try:
            logger.info(f"Generating cluster config for deployment: {deployment_id}")
            
            # Load base production configuration
            prod_config = await self._load_base_production_config()
            
            # Merge with provided base config
            cluster_config = self._deep_merge(prod_config, base_config)
            
            # Add cluster-specific settings
            cluster_config.update({
                'deployment': {
                    'id': deployment_id,
                    'timestamp': datetime.now().isoformat(),
                    'node_count': node_count
                },
                'cluster': {
                    'nodes': self._generate_node_configs(node_count),
                    'replication_factor': min(3, node_count),
                    'consensus_nodes': min(3, node_count)
                },
                'crdt': {
                    'cluster_enabled': True,
                    'sync_interval': 5,
                    'conflict_resolution': 'advanced',
                    'node_discovery': 'kubernetes',
                    'gossip_protocol': {
                        'enabled': True,
                        'interval': 10,
                        'fanout': 3
                    }
                },
                'monitoring': {
                    'cluster_metrics': True,
                    'node_health_checks': True,
                    'performance_tracking': True,
                    'alert_thresholds': {
                        'cpu_usage': 80,
                        'memory_usage': 85,
                        'disk_usage': 90,
                        'crdt_sync_latency': 1000  # ms
                    }
                }
            })
            
            # Store generated config
            self.generated_configs[deployment_id] = cluster_config
            
            logger.info(f"Cluster configuration generated for {node_count} nodes")
            
            return cluster_config
            
        except Exception as e:
            logger.error(f"Failed to generate cluster config: {e}")
            raise
    
    async def create_kubernetes_configs(self, cluster_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create Kubernetes ConfigMaps and Secrets from cluster configuration
        
        Args:
            cluster_config: Generated cluster configuration
            
        Returns:
            Kubernetes configuration resources
        """
        try:
            logger.info("Creating Kubernetes configuration resources")
            
            deployment_id = cluster_config['deployment']['id']
            
            # Generate ConfigMap data
            configmap_data = {
                'production.yaml': yaml.dump(cluster_config, default_flow_style=False),
                'cluster-config.json': json.dumps(cluster_config['cluster'], indent=2),
                'monitoring-config.json': json.dumps(cluster_config['monitoring'], indent=2)
            }
            
            # Generate Secret data (base64 encoded in real implementation)
            secret_data = {
                'api-key': self._generate_api_key(),
                'database-password': self._generate_password(),
                'encryption-key': self._generate_encryption_key(),
                'cluster-token': self._generate_cluster_token()
            }
            
            kubernetes_configs = {
                'configmap': {
                    'name': 'jarvis-config',
                    'namespace': 'jarvis-system',
                    'data': configmap_data
                },
                'secret': {
                    'name': 'jarvis-secrets',
                    'namespace': 'jarvis-system',
                    'data': secret_data
                }
            }
            
            # Store for deployment use
            self.generated_configs[f"{deployment_id}_k8s"] = kubernetes_configs
            
            logger.info("Kubernetes configuration resources created")
            
            return kubernetes_configs
            
        except Exception as e:
            logger.error(f"Failed to create Kubernetes configs: {e}")
            raise
    
    async def _load_base_production_config(self) -> Dict[str, Any]:
        """Load base production configuration"""
        try:
            config_file = self.base_config_path / "production.yaml"
            if config_file.exists():
                with open(config_file, 'r') as f:
                    return yaml.safe_load(f)
            else:
                logger.warning("Base production config not found, using defaults")
                return self._get_default_production_config()
        except Exception as e:
            logger.error(f"Failed to load base production config: {e}")
            return self._get_default_production_config()
    
    def _get_default_production_config(self) -> Dict[str, Any]:
        """Get default production configuration"""
        return {
            'system': {
                'debug': False,
                'log_level': 'INFO'
            },
            'plugins': {
                'enabled': True,
                'auto_load': True
            },
            'llm': {
                'default_provider': 'ollama',
                'timeout': 60,
                'max_retries': 5
            },
            'database': {
                'path': '/data/jarvis_archive.db',
                'backup_enabled': True,
                'backup_interval': 3600
            },
            'security': {
                'encryption_enabled': True,
                'api_key_required': True
            },
            'monitoring': {
                'enabled': True,
                'metrics_collection': True
            }
        }
    
    def _generate_node_configs(self, node_count: int) -> List[Dict[str, Any]]:
        """Generate configuration for individual cluster nodes"""
        nodes = []
        for i in range(node_count):
            node = {
                'node_id': f"jarvis-node-{i+1}",
                'node_name': f"jarvis-backend-{i+1}",
                'role': 'backend',
                'crdt_port': 8001,
                'api_port': 8000,
                'monitoring_port': 9090,
                'zone_preference': f"us-west1-{chr(97 + (i % 3))}",  # a, b, c
                'resources': {
                    'cpu_limit': '1000m',
                    'memory_limit': '2Gi',
                    'storage_size': '10Gi'
                }
            }
            nodes.append(node)
        return nodes
    
    def _generate_api_key(self) -> str:
        """Generate secure API key"""
        import secrets
        return secrets.token_urlsafe(32)
    
    def _generate_password(self) -> str:
        """Generate secure password"""
        import secrets
        import string
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(24))
    
    def _generate_encryption_key(self) -> str:
        """Generate encryption key"""
        import secrets
        return secrets.token_hex(32)
    
    def _generate_cluster_token(self) -> str:
        """Generate cluster authentication token"""
        import secrets
        return secrets.token_urlsafe(48)
    
    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries"""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result
    
    async def validate_configuration(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate configuration for deployment readiness
        
        Args:
            config: Configuration to validate
            
        Returns:
            Validation result with status and details
        """
        try:
            validation_result = {
                'valid': True,
                'errors': [],
                'warnings': [],
                'checks_performed': []
            }
            
            # Required sections check
            required_sections = ['system', 'cluster', 'crdt', 'monitoring']
            for section in required_sections:
                if section not in config:
                    validation_result['errors'].append(f"Missing required section: {section}")
                    validation_result['valid'] = False
                validation_result['checks_performed'].append(f"Required section: {section}")
            
            # Cluster configuration validation
            if 'cluster' in config:
                cluster_config = config['cluster']
                if 'nodes' not in cluster_config or len(cluster_config['nodes']) == 0:
                    validation_result['errors'].append("No cluster nodes configured")
                    validation_result['valid'] = False
                
                if cluster_config.get('replication_factor', 0) < 1:
                    validation_result['errors'].append("Invalid replication factor")
                    validation_result['valid'] = False
                
                validation_result['checks_performed'].append("Cluster configuration")
            
            # Security validation
            if 'security' in config:
                security_config = config['security']
                if not security_config.get('encryption_enabled', False):
                    validation_result['warnings'].append("Encryption is disabled")
                
                if not security_config.get('api_key_required', False):
                    validation_result['warnings'].append("API key authentication is disabled")
                
                validation_result['checks_performed'].append("Security configuration")
            
            # Performance validation
            if 'crdt' in config:
                crdt_config = config['crdt']
                sync_interval = crdt_config.get('sync_interval', 0)
                if sync_interval < 1 or sync_interval > 60:
                    validation_result['warnings'].append("CRDT sync interval outside recommended range (1-60s)")
                
                validation_result['checks_performed'].append("CRDT configuration")
            
            logger.info(f"Configuration validation completed: {'PASSED' if validation_result['valid'] else 'FAILED'}")
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return {
                'valid': False,
                'errors': [f"Validation error: {str(e)}"],
                'warnings': [],
                'checks_performed': []
            }
    
    async def get_configuration(self, deployment_id: str) -> Optional[Dict[str, Any]]:
        """
        Get generated configuration for deployment
        
        Args:
            deployment_id: Deployment identifier
            
        Returns:
            Configuration if found, None otherwise
        """
        return self.generated_configs.get(deployment_id)