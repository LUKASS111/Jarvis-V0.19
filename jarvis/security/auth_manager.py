"""
Authentication Manager for Jarvis Security Framework
Advanced authentication, authorization, and session management
"""

import asyncio
import logging
import hashlib
import secrets
import jwt
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class User:
    """User account representation"""
    user_id: str
    username: str
    email: str
    password_hash: str
    roles: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)
    mfa_enabled: bool = False
    mfa_secret: Optional[str] = None
    failed_attempts: int = 0
    locked_until: Optional[datetime] = None
    last_login: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True

@dataclass
class Session:
    """User session representation"""
    session_id: str
    user_id: str
    created_at: datetime
    expires_at: datetime
    ip_address: str
    user_agent: str
    is_active: bool = True
    last_activity: datetime = field(default_factory=datetime.now)

@dataclass
class AuthenticationAttempt:
    """Authentication attempt record"""
    attempt_id: str
    timestamp: datetime
    username: str
    ip_address: str
    success: bool
    failure_reason: Optional[str] = None
    user_agent: Optional[str] = None

class AuthenticationManager:
    """
    Advanced Authentication Manager for Jarvis Security Framework
    
    Provides comprehensive authentication and authorization including:
    - Multi-factor authentication (MFA)
    - Role-based access control (RBAC)
    - Session management
    - Account lockout protection
    - Authentication anomaly detection
    - JWT token management
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize authentication manager"""
        self.config = config or {}
        
        # Authentication configuration
        self.jwt_secret = self.config.get('jwt_secret', secrets.token_urlsafe(32))
        self.jwt_expiration = self.config.get('jwt_expiration', 3600)  # 1 hour
        self.session_timeout = self.config.get('session_timeout', 1800)  # 30 minutes
        self.max_failed_attempts = self.config.get('max_failed_attempts', 3)
        self.lockout_duration = self.config.get('lockout_duration', 900)  # 15 minutes
        self.require_mfa = self.config.get('require_mfa', False)
        self.password_complexity = self.config.get('password_complexity', True)
        
        # In-memory storage (in production, use database)
        self.users: Dict[str, User] = {}
        self.sessions: Dict[str, Session] = {}
        self.auth_attempts: List[AuthenticationAttempt] = []
        
        # Load default admin user
        self._create_default_admin()
        
        logger.info("Initialized AuthenticationManager")
    
    def _create_default_admin(self) -> None:
        """Create default admin user"""
        admin_password = self.config.get('admin_password', 'admin123!')
        admin_user = User(
            user_id='admin-001',
            username='admin',
            email='admin@jarvis.local',
            password_hash=self._hash_password(admin_password),
            roles=['admin', 'user'],
            permissions=['*'],  # All permissions
            mfa_enabled=self.require_mfa
        )
        
        if self.require_mfa:
            admin_user.mfa_secret = secrets.token_urlsafe(16)
        
        self.users[admin_user.username] = admin_user
        logger.info("Created default admin user")
    
    def _hash_password(self, password: str) -> str:
        """Hash password using secure algorithm"""
        # Use PBKDF2 with SHA-256
        salt = secrets.token_bytes(32)
        pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return salt.hex() + ':' + pwdhash.hex()
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        try:
            salt_hex, hash_hex = password_hash.split(':')
            salt = bytes.fromhex(salt_hex)
            stored_hash = bytes.fromhex(hash_hex)
            
            pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
            return pwdhash == stored_hash
        except Exception:
            return False
    
    def _validate_password_complexity(self, password: str) -> List[str]:
        """Validate password complexity requirements"""
        issues = []
        
        if not self.password_complexity:
            return issues
        
        if len(password) < 8:
            issues.append("Password must be at least 8 characters long")
        
        if not any(c.isupper() for c in password):
            issues.append("Password must contain at least one uppercase letter")
        
        if not any(c.islower() for c in password):
            issues.append("Password must contain at least one lowercase letter")
        
        if not any(c.isdigit() for c in password):
            issues.append("Password must contain at least one digit")
        
        if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            issues.append("Password must contain at least one special character")
        
        return issues
    
    async def authenticate_user(self, username: str, password: str, 
                              mfa_token: Optional[str] = None,
                              ip_address: str = '127.0.0.1',
                              user_agent: str = 'Unknown') -> Dict[str, Any]:
        """
        Authenticate user with username and password
        
        Args:
            username: Username
            password: Password
            mfa_token: MFA token (if MFA is enabled)
            ip_address: Client IP address
            user_agent: Client user agent
            
        Returns:
            Authentication result with session details
        """
        try:
            attempt_id = secrets.token_urlsafe(16)
            
            # Create authentication attempt record
            auth_attempt = AuthenticationAttempt(
                attempt_id=attempt_id,
                timestamp=datetime.now(),
                username=username,
                ip_address=ip_address,
                success=False,
                user_agent=user_agent
            )
            
            # Check if user exists
            if username not in self.users:
                auth_attempt.failure_reason = 'user_not_found'
                self.auth_attempts.append(auth_attempt)
                
                return {
                    'success': False,
                    'error': 'Invalid credentials',
                    'attempt_id': attempt_id
                }
            
            user = self.users[username]
            
            # Check if account is locked
            if user.locked_until and user.locked_until > datetime.now():
                auth_attempt.failure_reason = 'account_locked'
                self.auth_attempts.append(auth_attempt)
                
                return {
                    'success': False,
                    'error': 'Account is temporarily locked',
                    'locked_until': user.locked_until.isoformat(),
                    'attempt_id': attempt_id
                }
            
            # Check if account is active
            if not user.is_active:
                auth_attempt.failure_reason = 'account_disabled'
                self.auth_attempts.append(auth_attempt)
                
                return {
                    'success': False,
                    'error': 'Account is disabled',
                    'attempt_id': attempt_id
                }
            
            # Verify password
            if not self._verify_password(password, user.password_hash):
                user.failed_attempts += 1
                
                # Lock account if too many failed attempts
                if user.failed_attempts >= self.max_failed_attempts:
                    user.locked_until = datetime.now() + timedelta(seconds=self.lockout_duration)
                    auth_attempt.failure_reason = 'invalid_password_locked'
                else:
                    auth_attempt.failure_reason = 'invalid_password'
                
                self.auth_attempts.append(auth_attempt)
                
                return {
                    'success': False,
                    'error': 'Invalid credentials',
                    'failed_attempts': user.failed_attempts,
                    'max_attempts': self.max_failed_attempts,
                    'attempt_id': attempt_id
                }
            
            # Verify MFA if enabled
            if user.mfa_enabled:
                if not mfa_token:
                    auth_attempt.failure_reason = 'mfa_required'
                    self.auth_attempts.append(auth_attempt)
                    
                    return {
                        'success': False,
                        'error': 'MFA token required',
                        'mfa_required': True,
                        'attempt_id': attempt_id
                    }
                
                if not self._verify_mfa_token(user.mfa_secret, mfa_token):
                    auth_attempt.failure_reason = 'invalid_mfa'
                    self.auth_attempts.append(auth_attempt)
                    
                    return {
                        'success': False,
                        'error': 'Invalid MFA token',
                        'attempt_id': attempt_id
                    }
            
            # Authentication successful
            auth_attempt.success = True
            self.auth_attempts.append(auth_attempt)
            
            # Reset failed attempts
            user.failed_attempts = 0
            user.locked_until = None
            user.last_login = datetime.now()
            
            # Create session
            session = await self._create_session(user, ip_address, user_agent)
            
            # Generate JWT token
            jwt_token = self._generate_jwt_token(user, session)
            
            logger.info(f"User authenticated successfully: {username}")
            
            return {
                'success': True,
                'user_id': user.user_id,
                'username': user.username,
                'roles': user.roles,
                'permissions': user.permissions,
                'session_id': session.session_id,
                'jwt_token': jwt_token,
                'expires_at': session.expires_at.isoformat(),
                'attempt_id': attempt_id
            }
            
        except Exception as e:
            logger.error(f"Authentication failed for {username}: {e}")
            return {
                'success': False,
                'error': 'Authentication system error',
                'attempt_id': attempt_id if 'attempt_id' in locals() else None
            }
    
    def _verify_mfa_token(self, mfa_secret: str, token: str) -> bool:
        """Verify MFA token (simplified TOTP implementation)"""
        # In real implementation, use proper TOTP library like pyotp
        # For now, simulate MFA verification
        if not mfa_secret or not token:
            return False
        
        # Simple time-based verification (demo purposes)
        current_time = int(datetime.now().timestamp() // 30)  # 30-second window
        expected_token = str(abs(hash(f"{mfa_secret}{current_time}")) % 1000000).zfill(6)
        
        return token == expected_token
    
    async def _create_session(self, user: User, ip_address: str, user_agent: str) -> Session:
        """Create user session"""
        session = Session(
            session_id=secrets.token_urlsafe(32),
            user_id=user.user_id,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(seconds=self.session_timeout),
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.sessions[session.session_id] = session
        
        return session
    
    def _generate_jwt_token(self, user: User, session: Session) -> str:
        """Generate JWT token for user"""
        payload = {
            'user_id': user.user_id,
            'username': user.username,
            'roles': user.roles,
            'permissions': user.permissions,
            'session_id': session.session_id,
            'iat': datetime.now().timestamp(),
            'exp': (datetime.now() + timedelta(seconds=self.jwt_expiration)).timestamp()
        }
        
        return jwt.encode(payload, self.jwt_secret, algorithm='HS256')
    
    async def validate_jwt_token(self, token: str) -> Dict[str, Any]:
        """
        Validate JWT token
        
        Args:
            token: JWT token to validate
            
        Returns:
            Token validation result
        """
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            
            # Check if session is still valid
            session_id = payload.get('session_id')
            if session_id not in self.sessions:
                return {
                    'valid': False,
                    'error': 'Session not found'
                }
            
            session = self.sessions[session_id]
            if not session.is_active or session.expires_at < datetime.now():
                return {
                    'valid': False,
                    'error': 'Session expired'
                }
            
            # Update session activity
            session.last_activity = datetime.now()
            
            return {
                'valid': True,
                'payload': payload,
                'session': {
                    'session_id': session.session_id,
                    'expires_at': session.expires_at.isoformat(),
                    'last_activity': session.last_activity.isoformat()
                }
            }
            
        except jwt.ExpiredSignatureError:
            return {
                'valid': False,
                'error': 'Token expired'
            }
        except jwt.InvalidTokenError:
            return {
                'valid': False,
                'error': 'Invalid token'
            }
        except Exception as e:
            logger.error(f"JWT validation error: {e}")
            return {
                'valid': False,
                'error': 'Token validation failed'
            }
    
    async def check_permissions(self, user_id: str, required_permission: str) -> bool:
        """
        Check if user has required permission
        
        Args:
            user_id: User identifier
            required_permission: Required permission
            
        Returns:
            Permission check result
        """
        try:
            # Find user by ID
            user = None
            for u in self.users.values():
                if u.user_id == user_id:
                    user = u
                    break
            
            if not user:
                return False
            
            # Check if user has wildcard permission
            if '*' in user.permissions:
                return True
            
            # Check exact permission match
            if required_permission in user.permissions:
                return True
            
            # Check role-based permissions
            role_permissions = {
                'admin': ['*'],
                'user': ['read', 'write'],
                'readonly': ['read']
            }
            
            for role in user.roles:
                if role in role_permissions:
                    if '*' in role_permissions[role] or required_permission in role_permissions[role]:
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Permission check failed: {e}")
            return False
    
    async def detect_auth_anomalies(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Detect authentication anomalies
        
        Args:
            context: Authentication context
            
        Returns:
            List of detected anomalies
        """
        anomalies = []
        
        try:
            username = context.get('username')
            ip_address = context.get('ip_address')
            user_agent = context.get('user_agent')
            
            if not username:
                return anomalies
            
            # Get recent authentication attempts for user
            recent_attempts = [
                attempt for attempt in self.auth_attempts[-100:]  # Last 100 attempts
                if attempt.username == username and 
                   attempt.timestamp > datetime.now() - timedelta(hours=24)
            ]
            
            # Check for unusual login times
            current_hour = datetime.now().hour
            if current_hour < 6 or current_hour > 22:  # Outside business hours
                anomalies.append({
                    'type': 'unusual_login_time',
                    'severity': 'low',
                    'description': f'Login attempt outside business hours: {current_hour}:00',
                    'details': {'hour': current_hour}
                })
            
            # Check for multiple failed attempts
            failed_attempts = [a for a in recent_attempts if not a.success]
            if len(failed_attempts) >= 3:
                anomalies.append({
                    'type': 'multiple_failed_attempts',
                    'severity': 'medium',
                    'description': f'Multiple failed login attempts: {len(failed_attempts)}',
                    'details': {'failed_count': len(failed_attempts)}
                })
            
            # Check for login from new IP address
            user_ips = list(set(a.ip_address for a in recent_attempts if a.success))
            if ip_address and ip_address not in user_ips and len(user_ips) > 0:
                anomalies.append({
                    'type': 'new_ip_address',
                    'severity': 'medium',
                    'description': f'Login from new IP address: {ip_address}',
                    'details': {'new_ip': ip_address, 'known_ips': user_ips}
                })
            
            # Check for rapid login attempts
            if len(recent_attempts) >= 5:
                # Check if attempts are within short time window
                attempt_times = [a.timestamp for a in recent_attempts[-5:]]
                time_span = (max(attempt_times) - min(attempt_times)).total_seconds()
                
                if time_span < 60:  # 5 attempts in less than 1 minute
                    anomalies.append({
                        'type': 'rapid_login_attempts',
                        'severity': 'high',
                        'description': f'Rapid login attempts: 5 attempts in {time_span:.0f} seconds',
                        'details': {'attempts': 5, 'time_span': time_span}
                    })
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Auth anomaly detection failed: {e}")
            return []
    
    async def get_auth_status(self) -> Dict[str, Any]:
        """
        Get authentication system status
        
        Returns:
            Authentication system status
        """
        try:
            active_sessions = sum(1 for s in self.sessions.values() 
                                if s.is_active and s.expires_at > datetime.now())
            
            failed_attempts_24h = sum(1 for a in self.auth_attempts 
                                    if not a.success and 
                                       a.timestamp > datetime.now() - timedelta(hours=24))
            
            locked_accounts = sum(1 for u in self.users.values() 
                                if u.locked_until and u.locked_until > datetime.now())
            
            return {
                'total_users': len(self.users),
                'active_sessions': active_sessions,
                'total_sessions': len(self.sessions),
                'failed_attempts_24h': failed_attempts_24h,
                'locked_accounts': locked_accounts,
                'mfa_enabled_users': sum(1 for u in self.users.values() if u.mfa_enabled),
                'authentication_config': {
                    'jwt_expiration': self.jwt_expiration,
                    'session_timeout': self.session_timeout,
                    'max_failed_attempts': self.max_failed_attempts,
                    'lockout_duration': self.lockout_duration,
                    'require_mfa': self.require_mfa,
                    'password_complexity': self.password_complexity
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get auth status: {e}")
            return {'error': str(e)}
    
    async def validate_auth_compliance(self) -> Dict[str, Any]:
        """
        Validate authentication compliance
        
        Returns:
            Authentication compliance status
        """
        try:
            compliance_score = 100
            compliance_issues = []
            
            # Check MFA implementation
            mfa_enabled_percentage = (sum(1 for u in self.users.values() if u.mfa_enabled) / 
                                    len(self.users) * 100) if self.users else 0
            
            if mfa_enabled_percentage < 100 and self.require_mfa:
                compliance_score -= 20
                compliance_issues.append("Not all users have MFA enabled")
            
            # Check password complexity
            if not self.password_complexity:
                compliance_score -= 15
                compliance_issues.append("Password complexity requirements not enforced")
            
            # Check session timeout
            if self.session_timeout > 3600:  # More than 1 hour
                compliance_score -= 10
                compliance_issues.append("Session timeout too long for security best practices")
            
            # Check account lockout
            if self.max_failed_attempts > 5:
                compliance_score -= 10
                compliance_issues.append("Maximum failed attempts too high")
            
            # Check for active sessions without recent activity
            stale_sessions = sum(1 for s in self.sessions.values()
                               if s.is_active and 
                                  s.last_activity < datetime.now() - timedelta(minutes=30))
            
            if stale_sessions > 0:
                compliance_score -= 5
                compliance_issues.append(f"{stale_sessions} stale sessions detected")
            
            return {
                'score': max(0, compliance_score),
                'compliance_level': 'good' if compliance_score >= 80 else 'needs_improvement',
                'issues': compliance_issues,
                'metrics': {
                    'mfa_enabled_percentage': mfa_enabled_percentage,
                    'password_complexity_enabled': self.password_complexity,
                    'session_timeout': self.session_timeout,
                    'max_failed_attempts': self.max_failed_attempts,
                    'stale_sessions': stale_sessions
                }
            }
            
        except Exception as e:
            logger.error(f"Auth compliance validation failed: {e}")
            return {
                'score': 0,
                'error': str(e)
            }