"""
Enhanced Security Manager for Jarvis 1.0.0
Comprehensive security management and coordination
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass

from .compliance_validator import ComplianceValidator
from .auth_manager import AuthenticationManager
from .audit_logger import SecurityAuditLogger
from .encryption_manager import EncryptionManager

logger = logging.getLogger(__name__)

@dataclass
class SecurityPolicy:
    """Security policy configuration"""
    name: str
    description: str
    level: str  # 'basic', 'standard', 'strict', 'enterprise'
    rules: Dict[str, Any]
    enforcement: bool = True
    exceptions: List[str] = None

@dataclass
class SecurityIncident:
    """Security incident record"""
    incident_id: str
    timestamp: datetime
    severity: str  # 'low', 'medium', 'high', 'critical'
    category: str
    description: str
    source_ip: Optional[str] = None
    user_id: Optional[str] = None
    affected_resources: List[str] = None
    status: str = 'open'  # 'open', 'investigating', 'resolved', 'closed'

class SecurityManager:
    """
    Enhanced Security Manager for Jarvis Enterprise System
    
    Provides comprehensive security management including:
    - Policy enforcement and compliance validation
    - Authentication and authorization management
    - Security incident detection and response
    - Audit logging and compliance reporting
    - Encryption and data protection
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize security manager with configuration"""
        self.config = config or {}
        self.security_level = self.config.get('security_level', 'standard')
        
        # Initialize security components
        self.compliance_validator = ComplianceValidator(self.config.get('compliance', {}))
        self.auth_manager = AuthenticationManager(self.config.get('authentication', {}))
        self.audit_logger = SecurityAuditLogger(self.config.get('audit_logging', {}))
        self.encryption_manager = EncryptionManager(self.config.get('encryption', {}))
        
        # Security state
        self.active_policies: Dict[str, SecurityPolicy] = {}
        self.security_incidents: List[SecurityIncident] = []
        self.threat_level = 'normal'  # 'low', 'normal', 'elevated', 'high', 'critical'
        
        # Load default security policies
        self._load_default_policies()
        
        logger.info(f"Initialized SecurityManager with security level: {self.security_level}")
    
    def _load_default_policies(self) -> None:
        """Load default security policies based on security level"""
        policies = {
            'authentication_policy': SecurityPolicy(
                name='Authentication Policy',
                description='User authentication and session management',
                level=self.security_level,
                rules={
                    'require_mfa': self.security_level in ['strict', 'enterprise'],
                    'session_timeout': 3600 if self.security_level == 'basic' else 1800,
                    'max_failed_attempts': 5 if self.security_level == 'basic' else 3,
                    'password_complexity': self.security_level != 'basic',
                    'jwt_expiration': 3600
                }
            ),
            'api_security_policy': SecurityPolicy(
                name='API Security Policy',
                description='API access control and rate limiting',
                level=self.security_level,
                rules={
                    'require_api_key': True,
                    'rate_limit_enabled': True,
                    'rate_limit_requests': 1000 if self.security_level == 'basic' else 500,
                    'rate_limit_window': 3600,
                    'request_logging': True,
                    'cors_strict': self.security_level in ['strict', 'enterprise']
                }
            ),
            'data_protection_policy': SecurityPolicy(
                name='Data Protection Policy',
                description='Data encryption and privacy protection',
                level=self.security_level,
                rules={
                    'encryption_at_rest': self.security_level != 'basic',
                    'encryption_in_transit': True,
                    'data_masking': self.security_level in ['strict', 'enterprise'],
                    'backup_encryption': self.security_level != 'basic',
                    'audit_data_access': True
                }
            ),
            'network_security_policy': SecurityPolicy(
                name='Network Security Policy',
                description='Network access and communication security',
                level=self.security_level,
                rules={
                    'ip_whitelisting': self.security_level in ['strict', 'enterprise'],
                    'ssl_required': True,
                    'intrusion_detection': self.security_level != 'basic',
                    'firewall_enabled': True,
                    'vpc_isolation': self.security_level in ['strict', 'enterprise']
                }
            )
        }
        
        for policy_id, policy in policies.items():
            self.active_policies[policy_id] = policy
            logger.info(f"Loaded security policy: {policy.name}")
    
    async def validate_security_compliance(self) -> Dict[str, Any]:
        """
        Validate system security compliance
        
        Returns:
            Comprehensive compliance validation result
        """
        try:
            logger.info("Starting comprehensive security compliance validation")
            
            # Run compliance validation
            compliance_result = await self.compliance_validator.validate_full_compliance()
            
            # Check authentication compliance
            auth_compliance = await self.auth_manager.validate_auth_compliance()
            
            # Validate encryption compliance
            encryption_compliance = await self.encryption_manager.validate_encryption_compliance()
            
            # Check policy enforcement
            policy_compliance = await self._validate_policy_compliance()
            
            # Aggregate results
            overall_score = (
                compliance_result.get('score', 0) * 0.3 +
                auth_compliance.get('score', 0) * 0.3 +
                encryption_compliance.get('score', 0) * 0.2 +
                policy_compliance.get('score', 0) * 0.2
            )
            
            compliance_status = {
                'overall_score': overall_score,
                'compliance_level': self._get_compliance_level(overall_score),
                'timestamp': datetime.now().isoformat(),
                'details': {
                    'regulatory_compliance': compliance_result,
                    'authentication_compliance': auth_compliance,
                    'encryption_compliance': encryption_compliance,
                    'policy_compliance': policy_compliance
                },
                'recommendations': self._generate_compliance_recommendations(overall_score)
            }
            
            # Log compliance validation
            await self.audit_logger.log_security_event(
                'compliance_validation',
                'info',
                f"Security compliance validation completed with score: {overall_score:.2f}",
                {'compliance_status': compliance_status}
            )
            
            logger.info(f"Security compliance validation completed: {overall_score:.2f}/100")
            
            return compliance_status
            
        except Exception as e:
            logger.error(f"Security compliance validation failed: {e}")
            await self.audit_logger.log_security_event(
                'compliance_validation_error',
                'error',
                f"Compliance validation failed: {str(e)}"
            )
            raise
    
    async def _validate_policy_compliance(self) -> Dict[str, Any]:
        """Validate compliance with active security policies"""
        policy_results = {}
        total_score = 0
        
        for policy_id, policy in self.active_policies.items():
            try:
                # Validate policy rules
                policy_score = await self._validate_individual_policy(policy)
                policy_results[policy_id] = {
                    'policy_name': policy.name,
                    'score': policy_score,
                    'level': policy.level,
                    'enforcement': policy.enforcement
                }
                total_score += policy_score
                
            except Exception as e:
                logger.error(f"Policy validation failed for {policy_id}: {e}")
                policy_results[policy_id] = {
                    'policy_name': policy.name,
                    'score': 0,
                    'error': str(e)
                }
        
        avg_score = total_score / len(self.active_policies) if self.active_policies else 0
        
        return {
            'score': avg_score,
            'policy_count': len(self.active_policies),
            'policy_results': policy_results
        }
    
    async def _validate_individual_policy(self, policy: SecurityPolicy) -> float:
        """Validate compliance with individual security policy"""
        score = 100.0
        rules_passed = 0
        total_rules = len(policy.rules)
        
        for rule_name, rule_value in policy.rules.items():
            try:
                if await self._check_policy_rule(rule_name, rule_value):
                    rules_passed += 1
                else:
                    score -= (100 / total_rules)
            except Exception as e:
                logger.warning(f"Rule check failed for {rule_name}: {e}")
                score -= (100 / total_rules)
        
        return max(0, score)
    
    async def _check_policy_rule(self, rule_name: str, rule_value: Any) -> bool:
        """Check compliance with specific policy rule"""
        # Simulate policy rule checking
        # In real implementation, this would check actual system configuration
        await asyncio.sleep(0.01)  # Simulate check time
        
        # Basic rule validation logic
        if rule_name in ['require_mfa', 'encryption_at_rest', 'ssl_required']:
            return bool(rule_value)  # These rules are met if enabled
        elif rule_name in ['rate_limit_enabled', 'request_logging']:
            return bool(rule_value)
        elif rule_name == 'session_timeout':
            return isinstance(rule_value, int) and rule_value <= 3600
        elif rule_name == 'max_failed_attempts':
            return isinstance(rule_value, int) and rule_value <= 5
        else:
            return True  # Default to compliant for unknown rules
    
    def _get_compliance_level(self, score: float) -> str:
        """Get compliance level based on score"""
        if score >= 95:
            return 'excellent'
        elif score >= 85:
            return 'good'
        elif score >= 70:
            return 'acceptable'
        elif score >= 50:
            return 'needs_improvement'
        else:
            return 'critical'
    
    def _generate_compliance_recommendations(self, score: float) -> List[str]:
        """Generate compliance improvement recommendations"""
        recommendations = []
        
        if score < 95:
            recommendations.append("Review and update security policies to align with best practices")
        
        if score < 85:
            recommendations.extend([
                "Implement multi-factor authentication for enhanced security",
                "Enable encryption at rest for sensitive data",
                "Review API security configurations and rate limiting"
            ])
        
        if score < 70:
            recommendations.extend([
                "Conduct comprehensive security audit",
                "Implement network security controls and IP whitelisting",
                "Enhance audit logging and monitoring capabilities"
            ])
        
        if score < 50:
            recommendations.extend([
                "URGENT: Address critical security vulnerabilities",
                "Implement immediate security incident response procedures",
                "Consider engaging security consulting services"
            ])
        
        return recommendations
    
    async def detect_security_threats(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect potential security threats
        
        Args:
            context: Security context including request details, user info, etc.
            
        Returns:
            Threat detection results
        """
        try:
            threats_detected = []
            threat_score = 0
            
            # Check for authentication anomalies
            auth_threats = await self.auth_manager.detect_auth_anomalies(context)
            if auth_threats:
                threats_detected.extend(auth_threats)
                threat_score += len(auth_threats) * 10
            
            # Check for API abuse
            api_threats = await self._detect_api_threats(context)
            if api_threats:
                threats_detected.extend(api_threats)
                threat_score += len(api_threats) * 5
            
            # Check for data access anomalies
            data_threats = await self._detect_data_access_threats(context)
            if data_threats:
                threats_detected.extend(data_threats)
                threat_score += len(data_threats) * 15
            
            # Determine threat level
            if threat_score >= 50:
                current_threat_level = 'critical'
            elif threat_score >= 30:
                current_threat_level = 'high'
            elif threat_score >= 15:
                current_threat_level = 'elevated'
            elif threat_score > 0:
                current_threat_level = 'normal'
            else:
                current_threat_level = 'low'
            
            # Update threat level if elevated
            if current_threat_level not in ['low', 'normal']:
                self.threat_level = current_threat_level
            
            threat_result = {
                'threat_level': current_threat_level,
                'threat_score': threat_score,
                'threats_detected': threats_detected,
                'timestamp': datetime.now().isoformat(),
                'context': context
            }
            
            # Log threat detection
            if threats_detected:
                await self.audit_logger.log_security_event(
                    'threat_detection',
                    'warning',
                    f"Security threats detected: {len(threats_detected)} threats",
                    threat_result
                )
            
            return threat_result
            
        except Exception as e:
            logger.error(f"Threat detection failed: {e}")
            await self.audit_logger.log_security_event(
                'threat_detection_error',
                'error',
                f"Threat detection failed: {str(e)}"
            )
            raise
    
    async def _detect_api_threats(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect API-related security threats"""
        threats = []
        
        # Check for unusual request patterns
        request_count = context.get('recent_requests', 0)
        if request_count > 1000:  # Threshold for rate limiting
            threats.append({
                'type': 'rate_limit_violation',
                'severity': 'medium',
                'description': f'Excessive API requests: {request_count}',
                'source_ip': context.get('source_ip')
            })
        
        # Check for suspicious endpoints
        endpoint = context.get('endpoint', '')
        if any(suspicious in endpoint.lower() for suspicious in ['admin', 'debug', 'test']):
            threats.append({
                'type': 'suspicious_endpoint_access',
                'severity': 'high',
                'description': f'Access to sensitive endpoint: {endpoint}',
                'source_ip': context.get('source_ip')
            })
        
        return threats
    
    async def _detect_data_access_threats(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect data access related security threats"""
        threats = []
        
        # Check for unusual data access patterns
        data_volume = context.get('data_accessed_mb', 0)
        if data_volume > 100:  # Threshold for large data access
            threats.append({
                'type': 'large_data_access',
                'severity': 'medium',
                'description': f'Large volume data access: {data_volume}MB',
                'user_id': context.get('user_id')
            })
        
        # Check for access to sensitive data
        accessed_tables = context.get('accessed_tables', [])
        sensitive_tables = ['users', 'credentials', 'audit_logs']
        for table in accessed_tables:
            if table in sensitive_tables:
                threats.append({
                    'type': 'sensitive_data_access',
                    'severity': 'high',
                    'description': f'Access to sensitive table: {table}',
                    'user_id': context.get('user_id')
                })
        
        return threats
    
    async def create_security_incident(self, incident_data: Dict[str, Any]) -> SecurityIncident:
        """
        Create and track security incident
        
        Args:
            incident_data: Incident details
            
        Returns:
            Created security incident
        """
        try:
            incident = SecurityIncident(
                incident_id=f"SEC-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{len(self.security_incidents)}",
                timestamp=datetime.now(),
                severity=incident_data.get('severity', 'medium'),
                category=incident_data.get('category', 'unknown'),
                description=incident_data.get('description', 'Security incident'),
                source_ip=incident_data.get('source_ip'),
                user_id=incident_data.get('user_id'),
                affected_resources=incident_data.get('affected_resources', [])
            )
            
            self.security_incidents.append(incident)
            
            # Log security incident
            await self.audit_logger.log_security_event(
                'security_incident_created',
                incident.severity,
                f"Security incident created: {incident.description}",
                {
                    'incident_id': incident.incident_id,
                    'category': incident.category,
                    'severity': incident.severity
                }
            )
            
            logger.warning(f"Security incident created: {incident.incident_id} - {incident.description}")
            
            return incident
            
        except Exception as e:
            logger.error(f"Failed to create security incident: {e}")
            raise
    
    async def get_security_status(self) -> Dict[str, Any]:
        """
        Get comprehensive security status
        
        Returns:
            Complete security system status
        """
        try:
            # Get compliance status
            compliance_status = await self.validate_security_compliance()
            
            # Get authentication status
            auth_status = await self.auth_manager.get_auth_status()
            
            # Get recent security incidents
            recent_incidents = [
                {
                    'incident_id': inc.incident_id,
                    'timestamp': inc.timestamp.isoformat(),
                    'severity': inc.severity,
                    'category': inc.category,
                    'status': inc.status
                }
                for inc in self.security_incidents[-10:]  # Last 10 incidents
            ]
            
            # Calculate security metrics
            critical_incidents = sum(1 for inc in self.security_incidents 
                                   if inc.severity == 'critical' and inc.status == 'open')
            
            security_status = {
                'overall_security_level': self.security_level,
                'threat_level': self.threat_level,
                'compliance_score': compliance_status.get('overall_score', 0),
                'compliance_level': compliance_status.get('compliance_level', 'unknown'),
                'active_policies': len(self.active_policies),
                'total_incidents': len(self.security_incidents),
                'open_critical_incidents': critical_incidents,
                'authentication_status': auth_status,
                'recent_incidents': recent_incidents,
                'last_compliance_check': compliance_status.get('timestamp'),
                'security_components': {
                    'compliance_validator': 'active',
                    'auth_manager': 'active',
                    'audit_logger': 'active',
                    'encryption_manager': 'active'
                }
            }
            
            return security_status
            
        except Exception as e:
            logger.error(f"Failed to get security status: {e}")
            return {
                'error': str(e),
                'overall_security_level': self.security_level,
                'threat_level': 'unknown'
            }
    
    async def update_security_policy(self, policy_id: str, policy_updates: Dict[str, Any]) -> bool:
        """
        Update security policy
        
        Args:
            policy_id: Policy identifier
            policy_updates: Policy updates to apply
            
        Returns:
            Success status
        """
        try:
            if policy_id not in self.active_policies:
                raise ValueError(f"Policy not found: {policy_id}")
            
            policy = self.active_policies[policy_id]
            
            # Update policy rules
            if 'rules' in policy_updates:
                policy.rules.update(policy_updates['rules'])
            
            # Update other policy attributes
            for attr in ['level', 'enforcement', 'description']:
                if attr in policy_updates:
                    setattr(policy, attr, policy_updates[attr])
            
            # Log policy update
            await self.audit_logger.log_security_event(
                'security_policy_updated',
                'info',
                f"Security policy updated: {policy.name}",
                {
                    'policy_id': policy_id,
                    'updates': policy_updates
                }
            )
            
            logger.info(f"Security policy updated: {policy_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update security policy {policy_id}: {e}")
            await self.audit_logger.log_security_event(
                'security_policy_update_error',
                'error',
                f"Failed to update security policy: {str(e)}"
            )
            return False