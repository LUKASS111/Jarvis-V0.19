#!/usr/bin/env python3
"""
Jarvis Production Deployment CLI
Enterprise deployment management command-line interface
"""

import asyncio
import argparse
import json
import yaml
import logging
from pathlib import Path
from typing import Dict, Any

# Setup path for imports
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from jarvis.deployment import ProductionDeploymentManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class DeploymentCLI:
    """Production Deployment Command Line Interface"""
    
    def __init__(self):
        """Initialize deployment CLI"""
        self.deployment_manager = None
        
    async def deploy_cluster(self, config_file: str, output_format: str = 'yaml') -> None:
        """
        Deploy production CRDT cluster
        
        Args:
            config_file: Path to cluster configuration file
            output_format: Output format (yaml, json)
        """
        try:
            logger.info(f"Starting cluster deployment with config: {config_file}")
            
            # Load cluster configuration
            config_path = Path(config_file)
            if not config_path.exists():
                raise FileNotFoundError(f"Configuration file not found: {config_file}")
            
            with open(config_path, 'r') as f:
                if config_path.suffix.lower() in ['.yaml', '.yml']:
                    cluster_config = yaml.safe_load(f)
                else:
                    cluster_config = json.load(f)
            
            # Initialize deployment manager
            prod_config_path = cluster_config.get('production_config', 'config/environments/production.yaml')
            self.deployment_manager = ProductionDeploymentManager(prod_config_path)
            
            # Deploy cluster
            result = await self.deployment_manager.deploy_cluster(cluster_config)
            
            # Output result
            self._output_result(result, output_format)
            
            if result['status'] == 'success':
                logger.info(f"✅ Cluster deployment successful: {result['deployment_id']}")
                logger.info(f"🌐 Cluster endpoint: {result['cluster_endpoint']}")
                logger.info(f"📊 Monitoring endpoint: {result['monitoring_endpoint']}")
                logger.info(f"⏱️  Deployment time: {result['deployment_time']:.1f}s")
            else:
                logger.error(f"❌ Cluster deployment failed: {result.get('error', 'Unknown error')}")
                return 1
                
        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            return 1
        
        return 0
    
    async def get_status(self, deployment_id: str = None, output_format: str = 'yaml') -> None:
        """
        Get deployment status
        
        Args:
            deployment_id: Specific deployment ID (optional)
            output_format: Output format (yaml, json)
        """
        try:
            if not self.deployment_manager:
                logger.error("No active deployment manager. Run deploy first.")
                return 1
            
            logger.info("Getting deployment status...")
            
            status = await self.deployment_manager.get_deployment_status()
            
            # Output status
            self._output_result(status, output_format)
            
            # Pretty print key information
            state = status.get('state', {})
            logger.info(f"📊 Deployment Status: {state.get('status', 'unknown')}")
            if 'start_time' in state:
                logger.info(f"🕐 Start time: {state['start_time']}")
            if 'end_time' in state:
                logger.info(f"🕐 End time: {state['end_time']}")
                
        except Exception as e:
            logger.error(f"Failed to get status: {e}")
            return 1
        
        return 0
    
    async def monitor_health(self, continuous: bool = False, interval: int = 30) -> None:
        """
        Monitor cluster health
        
        Args:
            continuous: Monitor continuously
            interval: Check interval in seconds
        """
        try:
            if not self.deployment_manager:
                logger.error("No active deployment manager. Run deploy first.")
                return 1
            
            logger.info("Starting health monitoring...")
            
            while True:
                health_status = await self.deployment_manager.monitoring.check_system_health()
                
                # Display health summary
                overall_health = "🟢 HEALTHY" if health_status['overall_healthy'] else "🔴 UNHEALTHY"
                logger.info(f"Health Status: {overall_health} (Score: {health_status['health_score']:.2f})")
                logger.info(f"Checks: {health_status['checks_passed']}/{health_status['total_checks']} passed")
                
                # Display detailed health information
                for check_name, check_result in health_status['details'].items():
                    status_icon = "✅" if check_result['healthy'] else "❌"
                    logger.info(f"  {status_icon} {check_name}: {check_result.get('details', 'OK')}")
                
                if not continuous:
                    break
                
                logger.info(f"⏱️  Next check in {interval} seconds...")
                await asyncio.sleep(interval)
                
        except KeyboardInterrupt:
            logger.info("Health monitoring stopped by user")
        except Exception as e:
            logger.error(f"Health monitoring failed: {e}")
            return 1
        
        return 0
    
    async def cleanup_deployment(self, deployment_id: str) -> None:
        """
        Clean up deployment resources
        
        Args:
            deployment_id: Deployment ID to clean up
        """
        try:
            if not self.deployment_manager:
                logger.error("No active deployment manager.")
                return 1
            
            logger.info(f"Cleaning up deployment: {deployment_id}")
            
            # Cleanup resources
            await self.deployment_manager._cleanup_failed_deployment()
            
            logger.info("✅ Deployment cleanup completed")
                
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return 1
        
        return 0
    
    async def generate_config_template(self, output_file: str) -> None:
        """
        Generate deployment configuration template
        
        Args:
            output_file: Output file path
        """
        try:
            logger.info(f"Generating configuration template: {output_file}")
            
            template = {
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
                    'replicas': 3,
                    'auto_scaling': {
                        'enabled': True,
                        'min_replicas': 3,
                        'max_replicas': 10,
                        'target_cpu_utilization': 70
                    }
                },
                'production_config': 'config/environments/production.yaml',
                'monitoring': {
                    'prometheus_enabled': True,
                    'grafana_enabled': True,
                    'alerting_enabled': True
                },
                'security': {
                    'enable_tls': True,
                    'enable_rbac': True,
                    'network_policies': True
                }
            }
            
            output_path = Path(output_file)
            with open(output_path, 'w') as f:
                if output_path.suffix.lower() in ['.yaml', '.yml']:
                    yaml.dump(template, f, default_flow_style=False, indent=2)
                else:
                    json.dump(template, f, indent=2)
            
            logger.info(f"✅ Configuration template created: {output_file}")
            logger.info("📝 Edit the template and run: python deployment_cli.py deploy <config_file>")
                
        except Exception as e:
            logger.error(f"Failed to generate template: {e}")
            return 1
        
        return 0
    
    def _output_result(self, result: Dict[str, Any], format: str) -> None:
        """Output result in specified format"""
        if format.lower() == 'json':
            print(json.dumps(result, indent=2, default=str))
        else:  # yaml
            print(yaml.dump(result, default_flow_style=False, indent=2))

async def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Jarvis Production Deployment CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate configuration template
  python deployment_cli.py template cluster-config.yaml
  
  # Deploy cluster
  python deployment_cli.py deploy cluster-config.yaml
  
  # Get deployment status
  python deployment_cli.py status
  
  # Monitor health continuously
  python deployment_cli.py health --continuous --interval 60
  
  # Cleanup deployment
  python deployment_cli.py cleanup deployment-id-123
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Deploy command
    deploy_parser = subparsers.add_parser('deploy', help='Deploy production cluster')
    deploy_parser.add_argument('config_file', help='Cluster configuration file')
    deploy_parser.add_argument('--format', choices=['yaml', 'json'], default='yaml',
                              help='Output format')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Get deployment status')
    status_parser.add_argument('--deployment-id', help='Specific deployment ID')
    status_parser.add_argument('--format', choices=['yaml', 'json'], default='yaml',
                              help='Output format')
    
    # Health command
    health_parser = subparsers.add_parser('health', help='Monitor cluster health')
    health_parser.add_argument('--continuous', action='store_true',
                              help='Monitor continuously')
    health_parser.add_argument('--interval', type=int, default=30,
                              help='Check interval in seconds')
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Cleanup deployment')
    cleanup_parser.add_argument('deployment_id', help='Deployment ID to cleanup')
    
    # Template command
    template_parser = subparsers.add_parser('template', help='Generate config template')
    template_parser.add_argument('output_file', help='Output template file')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    cli = DeploymentCLI()
    
    try:
        if args.command == 'deploy':
            return await cli.deploy_cluster(args.config_file, args.format)
        elif args.command == 'status':
            return await cli.get_status(args.deployment_id, args.format)
        elif args.command == 'health':
            return await cli.monitor_health(args.continuous, args.interval)
        elif args.command == 'cleanup':
            return await cli.cleanup_deployment(args.deployment_id)
        elif args.command == 'template':
            return await cli.generate_config_template(args.output_file)
        else:
            parser.print_help()
            return 1
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        return 130
    except Exception as e:
        logger.error(f"Command failed: {e}")
        return 1

if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code)