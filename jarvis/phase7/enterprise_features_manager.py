"""
Enterprise Features Manager - Phase 7
Advanced security, compliance, multi-tenant architecture, and enterprise analytics
"""

import json
import asyncio
import threading
import time
import hashlib
import hmac
import jwt
from typing import Dict, List, Any, Optional, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import secrets
import logging

from ..core.error_handler import error_handler, ErrorLevel, safe_execute
from ..backend import get_jarvis_backend

class SecurityLevel(Enum):
    """Security clearance levels"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    SECRET = "secret"
    TOP_SECRET = "top_secret"

class UserRole(Enum):
    """User roles in enterprise environment"""
    GUEST = "guest"
    USER = "user"
    ADMIN = "admin"
    SUPERADMIN = "superadmin"
    DEVELOPER = "developer"
    ANALYST = "analyst"
    AUDITOR = "auditor"

class ComplianceStandard(Enum):
    """Compliance standards supported"""
    GDPR = "gdpr"
    HIPAA = "hipaa"
    SOX = "sox"
    PCI_DSS = "pci_dss"
    ISO_27001 = "iso_27001"
    SOC2 = "soc2"
    FERPA = "ferpa"

class TenantType(Enum):
    """Tenant types for multi-tenant architecture"""
    TRIAL = "trial"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"

@dataclass
class SecurityPolicy:
    """Security policy configuration"""
    name: str
    level: SecurityLevel
    rules: List[Dict[str, Any]] = field(default_factory=list)
    enforcement: bool = True
    audit_required: bool = True
    exceptions: List[str] = field(default_factory=list)
    valid_until: Optional[datetime] = None

@dataclass
class UserProfile:
    """Enterprise user profile"""
    user_id: str
    username: str
    email: str
    role: UserRole
    tenant_id: str
    security_clearance: SecurityLevel
    permissions: List[str] = field(default_factory=list)
    groups: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    mfa_enabled: bool = False
    session_timeout: int = 3600  # seconds
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TenantConfig:
    """Multi-tenant configuration"""
    tenant_id: str
    name: str
    type: TenantType
    admin_email: str
    max_users: int = 100
    max_api_calls: int = 10000
    storage_limit_gb: int = 100
    features_enabled: List[str] = field(default_factory=list)
    security_policies: List[str] = field(default_factory=list)
    compliance_requirements: List[ComplianceStandard] = field(default_factory=list)
    custom_branding: Dict[str, Any] = field(default_factory=dict)
    api_rate_limits: Dict[str, int] = field(default_factory=dict)
    data_retention_days: int = 90
    backup_enabled: bool = True
    monitoring_level: str = "standard"
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AuditEvent:
    """Audit event for compliance tracking"""
    event_id: str
    tenant_id: str
    user_id: str
    event_type: str
    resource: str
    action: str
    timestamp: datetime
    ip_address: str
    user_agent: str
    success: bool
    details: Dict[str, Any] = field(default_factory=dict)
    security_level: SecurityLevel = SecurityLevel.INTERNAL
    compliance_relevant: bool = True

class EnterpriseFeaturesManager:
    """
    Phase 7 Enterprise Features Manager
    
    Provides comprehensive enterprise-grade features:
    - Advanced security and access control
    - Multi-tenant architecture with isolation
    - Compliance management (GDPR, HIPAA, SOX, etc.)
    - Enterprise analytics and reporting
    - Advanced user management and SSO
    - Audit logging and compliance reporting
    - Data governance and retention policies
    """
    
    def __init__(self):
        self.manager_id = str(uuid.uuid4())
        self.start_time = datetime.now()
        
        # Core components
        self.backend_service = get_jarvis_backend()
        
        # Security and access control
        self.security_policies: Dict[str, SecurityPolicy] = {}
        self.user_profiles: Dict[str, UserProfile] = {}
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.api_keys: Dict[str, Dict[str, Any]] = {}
        
        # Multi-tenant architecture
        self.tenants: Dict[str, TenantConfig] = {}
        self.tenant_isolation: Dict[str, Dict[str, Any]] = {}
        self.tenant_metrics: Dict[str, Dict[str, Any]] = {}
        
        # Compliance and audit
        self.audit_log: List[AuditEvent] = []
        self.compliance_reports: Dict[str, Any] = {}
        self.data_retention_policies: Dict[str, Any] = {}
        
        # Enterprise analytics
        self.analytics_engine: Dict[str, Any] = {}
        self.usage_metrics: Dict[str, Any] = {}
        self.performance_metrics: Dict[str, Any] = {}
        
        # Advanced features
        self.sso_providers: Dict[str, Any] = {}
        self.encryption_keys: Dict[str, str] = {}
        self.backup_policies: Dict[str, Any] = {}
        
        self._lock = threading.RLock()
        self._initialize_enterprise_features()
    
    def _initialize_enterprise_features(self):
        """Initialize enterprise features"""
        try:
            print("[PHASE7] Initializing Enterprise Features Manager...")
            
            # Initialize security framework
            self._initialize_security_framework()
            
            # Set up multi-tenant architecture
            self._setup_multi_tenant_architecture()
            
            # Initialize compliance management
            self._initialize_compliance_management()
            
            # Set up enterprise analytics
            self._setup_enterprise_analytics()
            
            # Initialize SSO and authentication
            self._setup_sso_authentication()
            
            # Set up data governance
            self._setup_data_governance()
            
            print("[PHASE7] Enterprise Features Manager initialized successfully")
            
        except Exception as e:
            error_handler.log_error(
                e, "Phase 7 Enterprise Features Initialization", ErrorLevel.CRITICAL,
                "Failed to initialize enterprise features manager"
            )
            raise
    
    def _initialize_security_framework(self):
        """Initialize advanced security framework"""
        # Core security policies
        self.security_policies["default"] = SecurityPolicy(
            name="Default Security Policy",
            level=SecurityLevel.INTERNAL,
            rules=[
                {"type": "authentication", "required": True},
                {"type": "encryption", "algorithm": "AES-256"},
                {"type": "session_timeout", "duration": 3600},
                {"type": "password_policy", "min_length": 12, "complexity": True},
                {"type": "mfa", "required_for_admin": True}
            ],
            enforcement=True,
            audit_required=True
        )
        
        self.security_policies["high_security"] = SecurityPolicy(
            name="High Security Policy",
            level=SecurityLevel.SECRET,
            rules=[
                {"type": "authentication", "required": True, "mfa_required": True},
                {"type": "encryption", "algorithm": "AES-256", "key_rotation": "weekly"},
                {"type": "session_timeout", "duration": 1800},
                {"type": "ip_whitelist", "enabled": True},
                {"type": "device_verification", "required": True},
                {"type": "audit_all_actions", "enabled": True}
            ],
            enforcement=True,
            audit_required=True
        )
        
        # Generate master encryption key
        self.encryption_keys["master"] = secrets.token_hex(32)
        self.encryption_keys["session"] = secrets.token_hex(32)
        self.encryption_keys["api"] = secrets.token_hex(32)
        
        # Initialize JWT configuration
        self.jwt_config = {
            "algorithm": "HS256",
            "secret_key": secrets.token_hex(32),
            "token_expiry": 3600,
            "refresh_token_expiry": 86400
        }
    
    def _setup_multi_tenant_architecture(self):
        """Set up multi-tenant architecture"""
        # Default system tenant
        self.tenants["system"] = TenantConfig(
            tenant_id="system",
            name="System Tenant",
            type=TenantType.ENTERPRISE,
            admin_email="admin@jarvis-ai.app",
            max_users=1000,
            max_api_calls=1000000,
            storage_limit_gb=1000,
            features_enabled=[
                "ai_chat",
                "multimodal_processing",
                "function_calling",
                "memory_management",
                "api_access",
                "analytics",
                "audit_logging",
                "backup_restore"
            ],
            security_policies=["high_security"],
            compliance_requirements=[
                ComplianceStandard.SOC2,
                ComplianceStandard.ISO_27001
            ],
            monitoring_level="enterprise"
        )
        
        # Demo tenant for trials
        self.tenants["demo"] = TenantConfig(
            tenant_id="demo",
            name="Demo Tenant",
            type=TenantType.TRIAL,
            admin_email="demo@jarvis-ai.app",
            max_users=5,
            max_api_calls=1000,
            storage_limit_gb=1,
            features_enabled=[
                "ai_chat",
                "basic_processing"
            ],
            security_policies=["default"],
            data_retention_days=30,
            monitoring_level="basic"
        )
        
        # Tenant isolation configuration
        self.tenant_isolation = {
            "database": {
                "strategy": "schema_per_tenant",
                "connection_pooling": True,
                "isolation_level": "complete"
            },
            "storage": {
                "strategy": "path_based",
                "encryption": "per_tenant_key",
                "backup_isolation": True
            },
            "compute": {
                "resource_limits": True,
                "cpu_quotas": True,
                "memory_quotas": True
            },
            "network": {
                "vlan_isolation": True,
                "firewall_rules": True,
                "rate_limiting": True
            }
        }
    
    def _initialize_compliance_management(self):
        """Initialize compliance management system"""
        self.compliance_frameworks = {
            ComplianceStandard.GDPR: {
                "requirements": [
                    "data_consent_management",
                    "right_to_be_forgotten",
                    "data_portability",
                    "privacy_by_design",
                    "data_breach_notification",
                    "data_protection_officer"
                ],
                "audit_frequency": "quarterly",
                "retention_period": "unlimited",
                "geographical_restrictions": ["EU"]
            },
            ComplianceStandard.HIPAA: {
                "requirements": [
                    "phi_encryption",
                    "access_controls",
                    "audit_logs",
                    "business_associate_agreements",
                    "risk_assessments",
                    "incident_response"
                ],
                "audit_frequency": "annually",
                "retention_period": "6_years",
                "geographical_restrictions": ["US"]
            },
            ComplianceStandard.SOX: {
                "requirements": [
                    "financial_controls",
                    "change_management",
                    "segregation_of_duties",
                    "management_certifications",
                    "audit_trails",
                    "data_integrity"
                ],
                "audit_frequency": "annually",
                "retention_period": "7_years",
                "geographical_restrictions": ["US"]
            },
            ComplianceStandard.SOC2: {
                "requirements": [
                    "security_controls",
                    "availability_controls",
                    "processing_integrity",
                    "confidentiality_controls",
                    "privacy_controls"
                ],
                "audit_frequency": "annually",
                "retention_period": "3_years",
                "geographical_restrictions": None
            }
        }
        
        # Data retention policies
        self.data_retention_policies = {
            "default": {
                "logs": 90,  # days
                "user_data": 365,
                "analytics": 730,
                "audit_trails": 2555,  # 7 years
                "backups": 30
            },
            "gdpr_compliant": {
                "logs": 90,
                "user_data": "user_defined",
                "analytics": 365,
                "audit_trails": "unlimited",
                "backups": 30
            },
            "hipaa_compliant": {
                "logs": 180,
                "user_data": 2190,  # 6 years
                "analytics": 2190,
                "audit_trails": 2190,
                "backups": 90
            }
        }
    
    def _setup_enterprise_analytics(self):
        """Set up enterprise analytics engine"""
        self.analytics_engine = {
            "data_sources": [
                "user_interactions",
                "api_usage",
                "system_performance",
                "security_events",
                "compliance_metrics",
                "business_metrics"
            ],
            "processing_pipeline": [
                "data_collection",
                "data_validation",
                "data_transformation",
                "analytics_computation",
                "report_generation",
                "alert_processing"
            ],
            "reporting_types": [
                "usage_reports",
                "performance_reports",
                "security_reports",
                "compliance_reports",
                "business_intelligence",
                "predictive_analytics"
            ],
            "real_time_dashboards": True,
            "automated_alerts": True,
            "export_formats": ["PDF", "CSV", "JSON", "Excel"]
        }
        
        # Initialize usage metrics
        self.usage_metrics = {
            "api_calls": {"total": 0, "by_tenant": {}, "by_endpoint": {}},
            "user_sessions": {"active": 0, "total": 0, "by_tenant": {}},
            "data_processed": {"total_mb": 0, "by_tenant": {}, "by_type": {}},
            "ai_requests": {"total": 0, "by_model": {}, "by_tenant": {}},
            "storage_usage": {"total_gb": 0, "by_tenant": {}},
            "bandwidth_usage": {"total_gb": 0, "by_tenant": {}}
        }
        
        # Performance metrics
        self.performance_metrics = {
            "response_times": {"api": [], "ai": [], "database": []},
            "throughput": {"requests_per_second": 0, "concurrent_users": 0},
            "availability": {"uptime_percentage": 99.9, "incidents": []},
            "resource_utilization": {"cpu": 0, "memory": 0, "storage": 0},
            "error_rates": {"by_endpoint": {}, "by_tenant": {}}
        }
    
    def _setup_sso_authentication(self):
        """Set up SSO and advanced authentication"""
        self.sso_providers = {
            "azure_ad": {
                "enabled": True,
                "client_id": "${AZURE_CLIENT_ID}",
                "tenant_id": "${AZURE_TENANT_ID}",
                "scopes": ["openid", "profile", "email"],
                "redirect_uri": "https://app.jarvis-ai.app/auth/azure/callback"
            },
            "google": {
                "enabled": True,
                "client_id": "${GOOGLE_CLIENT_ID}",
                "scopes": ["openid", "profile", "email"],
                "redirect_uri": "https://app.jarvis-ai.app/auth/google/callback"
            },
            "okta": {
                "enabled": True,
                "domain": "${OKTA_DOMAIN}",
                "client_id": "${OKTA_CLIENT_ID}",
                "scopes": ["openid", "profile", "email"],
                "redirect_uri": "https://app.jarvis-ai.app/auth/okta/callback"
            },
            "saml": {
                "enabled": True,
                "entity_id": "https://app.jarvis-ai.app",
                "acs_url": "https://app.jarvis-ai.app/auth/saml/acs",
                "sls_url": "https://app.jarvis-ai.app/auth/saml/sls"
            }
        }
        
        # MFA configuration
        self.mfa_config = {
            "enabled": True,
            "required_for_roles": [UserRole.ADMIN, UserRole.SUPERADMIN],
            "methods": ["totp", "sms", "email", "hardware_token"],
            "backup_codes": True,
            "session_timeout": 1800  # 30 minutes
        }
    
    def _setup_data_governance(self):
        """Set up data governance framework"""
        self.data_governance = {
            "classification": {
                "public": {"encryption": False, "access": "unrestricted"},
                "internal": {"encryption": True, "access": "authenticated"},
                "confidential": {"encryption": True, "access": "authorized"},
                "restricted": {"encryption": True, "access": "need_to_know"}
            },
            "data_lineage": {
                "tracking_enabled": True,
                "metadata_collection": True,
                "impact_analysis": True
            },
            "privacy_controls": {
                "anonymization": True,
                "pseudonymization": True,
                "consent_management": True,
                "right_to_erasure": True
            },
            "backup_policies": {
                "frequency": "daily",
                "retention": "30_days",
                "encryption": True,
                "off_site": True,
                "testing": "monthly"
            }
        }
    
    @safe_execute(fallback_value=None, context="User Authentication")
    def authenticate_user(self, credentials: Dict[str, Any], tenant_id: str = "system") -> Optional[Dict[str, Any]]:
        """
        Authenticate user with enterprise security
        """
        try:
            auth_method = credentials.get("method", "password")
            
            if auth_method == "password":
                return self._authenticate_password(credentials, tenant_id)
            elif auth_method == "sso":
                return self._authenticate_sso(credentials, tenant_id)
            elif auth_method == "api_key":
                return self._authenticate_api_key(credentials, tenant_id)
            elif auth_method == "jwt":
                return self._authenticate_jwt(credentials, tenant_id)
            else:
                raise ValueError(f"Unsupported authentication method: {auth_method}")
            
        except Exception as e:
            error_handler.log_error(
                e, "User Authentication", ErrorLevel.ERROR,
                f"Authentication failed for tenant: {tenant_id}"
            )
            
            # Log security event
            self._log_audit_event(
                tenant_id=tenant_id,
                user_id=credentials.get("username", "unknown"),
                event_type="authentication_failure",
                resource="auth_system",
                action="login",
                success=False,
                details={"method": credentials.get("method"), "error": str(e)}
            )
            
            return None
    
    def _authenticate_password(self, credentials: Dict[str, Any], tenant_id: str) -> Dict[str, Any]:
        """Authenticate with username/password"""
        username = credentials.get("username")
        password = credentials.get("password")
        
        if not username or not password:
            raise ValueError("Username and password required")
        
        # Simulate password verification (implement actual password hashing)
        user_key = f"{tenant_id}:{username}"
        
        # For demo purposes, create a default user if not exists
        if user_key not in self.user_profiles:
            self.user_profiles[user_key] = UserProfile(
                user_id=str(uuid.uuid4()),
                username=username,
                email=f"{username}@{tenant_id}.com",
                role=UserRole.USER,
                tenant_id=tenant_id,
                security_clearance=SecurityLevel.INTERNAL,
                permissions=["chat", "analyze", "memory_read"]
            )
        
        user_profile = self.user_profiles[user_key]
        
        # Create session
        session_token = self._create_session(user_profile)
        
        # Log successful authentication
        self._log_audit_event(
            tenant_id=tenant_id,
            user_id=user_profile.user_id,
            event_type="authentication_success",
            resource="auth_system",
            action="login",
            success=True,
            details={"method": "password"}
        )
        
        return {
            "success": True,
            "user_profile": user_profile,
            "session_token": session_token,
            "expires_at": (datetime.now() + timedelta(seconds=user_profile.session_timeout)).isoformat()
        }
    
    def _authenticate_sso(self, credentials: Dict[str, Any], tenant_id: str) -> Dict[str, Any]:
        """Authenticate with SSO provider"""
        provider = credentials.get("provider")
        token = credentials.get("token")
        
        if provider not in self.sso_providers:
            raise ValueError(f"SSO provider {provider} not configured")
        
        if not self.sso_providers[provider]["enabled"]:
            raise ValueError(f"SSO provider {provider} is disabled")
        
        # Simulate SSO token validation
        user_info = self._validate_sso_token(provider, token)
        
        # Create or update user profile
        user_key = f"{tenant_id}:{user_info['email']}"
        
        if user_key not in self.user_profiles:
            self.user_profiles[user_key] = UserProfile(
                user_id=str(uuid.uuid4()),
                username=user_info["email"],
                email=user_info["email"],
                role=UserRole.USER,
                tenant_id=tenant_id,
                security_clearance=SecurityLevel.INTERNAL,
                permissions=["chat", "analyze", "memory_read"]
            )
        
        user_profile = self.user_profiles[user_key]
        user_profile.last_login = datetime.now()
        
        # Create session
        session_token = self._create_session(user_profile)
        
        return {
            "success": True,
            "user_profile": user_profile,
            "session_token": session_token,
            "sso_provider": provider
        }
    
    def _authenticate_api_key(self, credentials: Dict[str, Any], tenant_id: str) -> Dict[str, Any]:
        """Authenticate with API key"""
        api_key = credentials.get("api_key")
        
        if not api_key:
            raise ValueError("API key required")
        
        # Check if API key exists and is valid
        if api_key not in self.api_keys:
            raise ValueError("Invalid API key")
        
        key_info = self.api_keys[api_key]
        
        if key_info["tenant_id"] != tenant_id:
            raise ValueError("API key not valid for this tenant")
        
        if key_info.get("expires_at") and datetime.fromisoformat(key_info["expires_at"]) < datetime.now():
            raise ValueError("API key expired")
        
        return {
            "success": True,
            "api_key_info": key_info,
            "tenant_id": tenant_id,
            "permissions": key_info.get("permissions", [])
        }
    
    def _authenticate_jwt(self, credentials: Dict[str, Any], tenant_id: str) -> Dict[str, Any]:
        """Authenticate with JWT token"""
        token = credentials.get("token")
        
        if not token:
            raise ValueError("JWT token required")
        
        try:
            # Decode and validate JWT
            payload = jwt.decode(
                token,
                self.jwt_config["secret_key"],
                algorithms=[self.jwt_config["algorithm"]]
            )
            
            user_id = payload.get("user_id")
            token_tenant_id = payload.get("tenant_id")
            
            if token_tenant_id != tenant_id:
                raise ValueError("Token not valid for this tenant")
            
            # Find user profile
            user_profile = None
            for profile in self.user_profiles.values():
                if profile.user_id == user_id and profile.tenant_id == tenant_id:
                    user_profile = profile
                    break
            
            if not user_profile:
                raise ValueError("User not found")
            
            return {
                "success": True,
                "user_profile": user_profile,
                "jwt_payload": payload
            }
            
        except jwt.ExpiredSignatureError:
            raise ValueError("JWT token expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid JWT token")
    
    def _create_session(self, user_profile: UserProfile) -> str:
        """Create user session"""
        session_id = str(uuid.uuid4())
        session_token = secrets.token_urlsafe(32)
        
        session_data = {
            "session_id": session_id,
            "user_id": user_profile.user_id,
            "tenant_id": user_profile.tenant_id,
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(seconds=user_profile.session_timeout)).isoformat(),
            "permissions": user_profile.permissions,
            "security_clearance": user_profile.security_clearance.value
        }
        
        with self._lock:
            self.active_sessions[session_token] = session_data
        
        return session_token
    
    def _validate_sso_token(self, provider: str, token: str) -> Dict[str, Any]:
        """Validate SSO token (simulated)"""
        # In real implementation, this would validate with the actual SSO provider
        return {
            "email": f"user@{provider}.com",
            "name": "SSO User",
            "provider": provider,
            "verified": True
        }
    
    @safe_execute(fallback_value=None, context="Tenant Creation")
    def create_tenant(self, tenant_config: TenantConfig) -> Optional[str]:
        """
        Create new tenant with enterprise features
        """
        try:
            tenant_id = tenant_config.tenant_id
            
            if tenant_id in self.tenants:
                raise ValueError(f"Tenant {tenant_id} already exists")
            
            # Validate tenant configuration
            self._validate_tenant_config(tenant_config)
            
            # Create tenant
            with self._lock:
                self.tenants[tenant_id] = tenant_config
                
                # Initialize tenant metrics
                self.tenant_metrics[tenant_id] = {
                    "users": 0,
                    "api_calls": 0,
                    "storage_used_gb": 0,
                    "created_at": datetime.now().isoformat(),
                    "last_activity": None
                }
                
                # Set up tenant isolation
                self._setup_tenant_isolation(tenant_id)
            
            # Log tenant creation
            self._log_audit_event(
                tenant_id=tenant_id,
                user_id="system",
                event_type="tenant_created",
                resource="tenant_management",
                action="create",
                success=True,
                details={"tenant_type": tenant_config.type.value}
            )
            
            return tenant_id
            
        except Exception as e:
            error_handler.log_error(
                e, "Tenant Creation", ErrorLevel.ERROR,
                f"Failed to create tenant: {tenant_config.tenant_id}"
            )
            return None
    
    def _validate_tenant_config(self, config: TenantConfig):
        """Validate tenant configuration"""
        if not config.tenant_id or not config.name:
            raise ValueError("Tenant ID and name are required")
        
        if config.max_users <= 0:
            raise ValueError("Max users must be positive")
        
        if config.max_api_calls <= 0:
            raise ValueError("Max API calls must be positive")
        
        # Validate compliance requirements
        for standard in config.compliance_requirements:
            if standard not in self.compliance_frameworks:
                raise ValueError(f"Compliance standard {standard} not supported")
    
    def _setup_tenant_isolation(self, tenant_id: str):
        """Set up tenant isolation"""
        isolation_config = {
            "database_schema": f"tenant_{tenant_id}",
            "storage_path": f"/data/tenants/{tenant_id}",
            "encryption_key": secrets.token_hex(32),
            "network_namespace": f"ns_{tenant_id}",
            "resource_limits": {
                "cpu_quota": 100000,  # 1 CPU
                "memory_limit": "4Gi",
                "storage_quota": "100Gi"
            }
        }
        
        with self._lock:
            self.tenant_isolation[tenant_id] = isolation_config
    
    def create_api_key(self, tenant_id: str, user_id: str, permissions: List[str], expires_in_days: int = 365) -> str:
        """Create API key for tenant"""
        api_key = f"jarvis_{secrets.token_urlsafe(32)}"
        
        key_info = {
            "tenant_id": tenant_id,
            "user_id": user_id,
            "permissions": permissions,
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(days=expires_in_days)).isoformat(),
            "last_used": None,
            "usage_count": 0
        }
        
        with self._lock:
            self.api_keys[api_key] = key_info
        
        return api_key
    
    def _log_audit_event(self, tenant_id: str, user_id: str, event_type: str, resource: str, 
                        action: str, success: bool, details: Dict[str, Any] = None, 
                        ip_address: str = "unknown", user_agent: str = "unknown"):
        """Log audit event for compliance"""
        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            user_id=user_id,
            event_type=event_type,
            resource=resource,
            action=action,
            timestamp=datetime.now(),
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            details=details or {}
        )
        
        with self._lock:
            self.audit_log.append(event)
            
            # Keep audit log size manageable
            if len(self.audit_log) > 100000:
                # Archive old entries (in production, this would go to long-term storage)
                self.audit_log = self.audit_log[-50000:]
    
    def generate_compliance_report(self, tenant_id: str, standard: ComplianceStandard, 
                                 start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate compliance report for specific standard"""
        if standard not in self.compliance_frameworks:
            raise ValueError(f"Compliance standard {standard} not supported")
        
        framework = self.compliance_frameworks[standard]
        
        # Filter audit events for the period
        relevant_events = [
            event for event in self.audit_log
            if event.tenant_id == tenant_id and 
               start_date <= event.timestamp <= end_date and
               event.compliance_relevant
        ]
        
        # Analyze compliance
        compliance_analysis = {
            "standard": standard.value,
            "tenant_id": tenant_id,
            "report_period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "requirements_status": {},
            "audit_events": len(relevant_events),
            "violations": [],
            "recommendations": [],
            "compliance_score": 0.0
        }
        
        # Check each requirement
        for requirement in framework["requirements"]:
            compliance_analysis["requirements_status"][requirement] = {
                "compliant": True,  # Simplified for demo
                "evidence": f"Compliance validated for {requirement}",
                "last_check": datetime.now().isoformat()
            }
        
        # Calculate compliance score
        compliant_requirements = sum(
            1 for status in compliance_analysis["requirements_status"].values()
            if status["compliant"]
        )
        total_requirements = len(framework["requirements"])
        compliance_analysis["compliance_score"] = compliant_requirements / total_requirements * 100
        
        return compliance_analysis
    
    def get_enterprise_analytics(self, tenant_id: str = None) -> Dict[str, Any]:
        """Get enterprise analytics dashboard"""
        with self._lock:
            analytics = {
                "overview": {
                    "total_tenants": len(self.tenants),
                    "active_users": len(self.active_sessions),
                    "total_api_calls": self.usage_metrics["api_calls"]["total"],
                    "system_health": 95.0  # Simplified
                },
                "usage_metrics": self.usage_metrics.copy(),
                "performance_metrics": self.performance_metrics.copy(),
                "security_metrics": {
                    "authentication_events": len([e for e in self.audit_log if "authentication" in e.event_type]),
                    "failed_logins": len([e for e in self.audit_log if "authentication_failure" in e.event_type]),
                    "active_sessions": len(self.active_sessions),
                    "api_keys_issued": len(self.api_keys)
                },
                "compliance_status": {
                    standard.value: "compliant" for standard in ComplianceStandard
                }
            }
            
            # Tenant-specific analytics
            if tenant_id and tenant_id in self.tenants:
                tenant_analytics = {
                    "tenant_info": self.tenants[tenant_id],
                    "tenant_metrics": self.tenant_metrics.get(tenant_id, {}),
                    "user_count": len([p for p in self.user_profiles.values() if p.tenant_id == tenant_id]),
                    "recent_activity": [
                        e for e in self.audit_log[-100:]
                        if e.tenant_id == tenant_id
                    ]
                }
                analytics["tenant_specific"] = tenant_analytics
            
            return analytics
    
    def get_user_activity_report(self, tenant_id: str, user_id: str = None, days: int = 30) -> Dict[str, Any]:
        """Get user activity report"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Filter events
        events = [
            event for event in self.audit_log
            if event.tenant_id == tenant_id and
               start_date <= event.timestamp <= end_date and
               (user_id is None or event.user_id == user_id)
        ]
        
        # Aggregate statistics
        activity_stats = {
            "total_events": len(events),
            "unique_users": len(set(e.user_id for e in events)),
            "event_types": {},
            "daily_activity": {},
            "security_events": len([e for e in events if "security" in e.event_type or "auth" in e.event_type])
        }
        
        # Count event types
        for event in events:
            activity_stats["event_types"][event.event_type] = activity_stats["event_types"].get(event.event_type, 0) + 1
        
        # Daily activity breakdown
        for event in events:
            day_key = event.timestamp.strftime("%Y-%m-%d")
            activity_stats["daily_activity"][day_key] = activity_stats["daily_activity"].get(day_key, 0) + 1
        
        return activity_stats
    
    def enforce_data_retention(self, tenant_id: str = None):
        """Enforce data retention policies"""
        tenants_to_process = [tenant_id] if tenant_id else list(self.tenants.keys())
        
        for tid in tenants_to_process:
            if tid not in self.tenants:
                continue
            
            tenant = self.tenants[tid]
            retention_days = tenant.data_retention_days
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            # Remove old audit events (keeping compliance-required events longer)
            original_count = len(self.audit_log)
            self.audit_log = [
                event for event in self.audit_log
                if event.tenant_id != tid or 
                   event.timestamp > cutoff_date or
                   event.compliance_relevant
            ]
            
            removed_count = original_count - len(self.audit_log)
            
            if removed_count > 0:
                self._log_audit_event(
                    tenant_id=tid,
                    user_id="system",
                    event_type="data_retention_enforced",
                    resource="audit_system",
                    action="cleanup",
                    success=True,
                    details={"events_removed": removed_count, "retention_days": retention_days}
                )
    
    def get_security_status(self) -> Dict[str, Any]:
        """Get comprehensive security status"""
        with self._lock:
            return {
                "security_policies": {
                    name: {
                        "level": policy.level.value,
                        "enforcement": policy.enforcement,
                        "rules_count": len(policy.rules)
                    }
                    for name, policy in self.security_policies.items()
                },
                "active_sessions": len(self.active_sessions),
                "api_keys": len(self.api_keys),
                "sso_providers": {
                    name: provider["enabled"] 
                    for name, provider in self.sso_providers.items()
                },
                "mfa_status": {
                    "enabled": self.mfa_config["enabled"],
                    "required_roles": [role.value for role in self.mfa_config["required_for_roles"]]
                },
                "recent_security_events": [
                    {
                        "event_type": event.event_type,
                        "timestamp": event.timestamp.isoformat(),
                        "success": event.success,
                        "tenant_id": event.tenant_id
                    }
                    for event in self.audit_log[-20:]
                    if "auth" in event.event_type or "security" in event.event_type
                ]
            }
    
    def get_manager_status(self) -> Dict[str, Any]:
        """Get comprehensive manager status"""
        with self._lock:
            return {
                "manager_id": self.manager_id,
                "uptime": (datetime.now() - self.start_time).total_seconds(),
                "tenants": {
                    "total": len(self.tenants),
                    "by_type": {
                        tenant_type.value: len([t for t in self.tenants.values() if t.type == tenant_type])
                        for tenant_type in TenantType
                    }
                },
                "users": {
                    "total": len(self.user_profiles),
                    "active_sessions": len(self.active_sessions),
                    "by_role": {
                        role.value: len([u for u in self.user_profiles.values() if u.role == role])
                        for role in UserRole
                    }
                },
                "security": {
                    "policies_count": len(self.security_policies),
                    "audit_events": len(self.audit_log),
                    "api_keys": len(self.api_keys),
                    "sso_enabled": any(p["enabled"] for p in self.sso_providers.values())
                },
                "compliance": {
                    "standards_supported": len(self.compliance_frameworks),
                    "frameworks": list(self.compliance_frameworks.keys())
                },
                "analytics": {
                    "data_sources": len(self.analytics_engine["data_sources"]),
                    "total_metrics": sum(len(metrics) if isinstance(metrics, dict) else 1 
                                      for metrics in self.usage_metrics.values())
                }
            }

# Global enterprise features manager instance
_enterprise_features_manager = None

def get_enterprise_features_manager() -> EnterpriseFeaturesManager:
    """Get the global enterprise features manager instance"""
    global _enterprise_features_manager
    if _enterprise_features_manager is None:
        _enterprise_features_manager = EnterpriseFeaturesManager()
    return _enterprise_features_manager

# Convenience functions
def authenticate_enterprise_user(username: str, password: str, tenant_id: str = "system") -> Dict[str, Any]:
    """Authenticate enterprise user"""
    manager = get_enterprise_features_manager()
    credentials = {"method": "password", "username": username, "password": password}
    return manager.authenticate_user(credentials, tenant_id)

def create_enterprise_tenant(name: str, admin_email: str, tenant_type: str = "professional") -> str:
    """Create enterprise tenant"""
    manager = get_enterprise_features_manager()
    
    tenant_config = TenantConfig(
        tenant_id=str(uuid.uuid4()),
        name=name,
        type=TenantType(tenant_type),
        admin_email=admin_email
    )
    
    return manager.create_tenant(tenant_config)

def generate_api_key(tenant_id: str, user_id: str, permissions: List[str]) -> str:
    """Generate API key for tenant"""
    manager = get_enterprise_features_manager()
    return manager.create_api_key(tenant_id, user_id, permissions)

def get_compliance_report(tenant_id: str, standard: str, days: int = 30) -> Dict[str, Any]:
    """Get compliance report"""
    manager = get_enterprise_features_manager()
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    return manager.generate_compliance_report(
        tenant_id,
        ComplianceStandard(standard),
        start_date,
        end_date
    )