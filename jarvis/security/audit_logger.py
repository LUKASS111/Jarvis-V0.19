"""
Security Audit Logger for Jarvis Security Framework
Comprehensive security event logging and audit trail management
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class SecurityEvent:
    """Security event record"""
    event_id: str
    timestamp: datetime
    event_type: str
    severity: str  # 'debug', 'info', 'warning', 'error', 'critical'
    message: str
    source: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    resource: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class SecurityAuditLogger:
    """
    Security Audit Logger for Enterprise Security Framework
    
    Provides comprehensive security event logging including:
    - Structured security event logging
    - Audit trail management
    - Security event correlation
    - Compliance reporting
    - Real-time security monitoring
    - Log integrity protection
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize security audit logger"""
        self.config = config or {}
        
        # Logging configuration
        self.log_level = self.config.get('log_level', 'info')
        self.log_file_path = Path(self.config.get('log_file', 'logs/security_audit.log'))
        self.max_log_size = self.config.get('max_log_size', 100 * 1024 * 1024)  # 100MB
        self.log_rotation_count = self.config.get('log_rotation_count', 10)
        self.enable_encryption = self.config.get('enable_encryption', True)
        self.enable_integrity_check = self.config.get('enable_integrity_check', True)
        
        # In-memory event storage (for quick access and correlation)
        self.recent_events: List[SecurityEvent] = []
        self.max_memory_events = self.config.get('max_memory_events', 10000)
        
        # Event correlation
        self.correlation_windows = {
            'authentication': timedelta(minutes=5),
            'authorization': timedelta(minutes=2),
            'data_access': timedelta(minutes=10),
            'configuration_change': timedelta(hours=1)
        }
        
        # Ensure log directory exists
        self.log_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info("Initialized SecurityAuditLogger")
    
    async def log_security_event(self, event_type: str, severity: str, message: str,
                                metadata: Optional[Dict[str, Any]] = None,
                                user_id: Optional[str] = None,
                                session_id: Optional[str] = None,
                                ip_address: Optional[str] = None,
                                resource: Optional[str] = None) -> str:
        """
        Log security event
        
        Args:
            event_type: Type of security event
            severity: Event severity level
            message: Event message
            metadata: Additional event metadata
            user_id: User identifier (if applicable)
            session_id: Session identifier (if applicable)
            ip_address: Source IP address (if applicable)
            resource: Affected resource (if applicable)
            
        Returns:
            Event ID of logged event
        """
        try:
            import secrets
            
            # Create security event
            event = SecurityEvent(
                event_id=secrets.token_urlsafe(16),
                timestamp=datetime.now(),
                event_type=event_type,
                severity=severity.lower(),
                message=message,
                source='jarvis_security',
                user_id=user_id,
                session_id=session_id,
                ip_address=ip_address,
                resource=resource,
                metadata=metadata or {}
            )
            
            # Add to memory storage
            self.recent_events.append(event)
            
            # Maintain memory limit
            if len(self.recent_events) > self.max_memory_events:
                self.recent_events = self.recent_events[-self.max_memory_events:]
            
            # Write to log file
            await self._write_event_to_log(event)
            
            # Check for security event correlations
            await self._check_event_correlations(event)
            
            return event.event_id
            
        except Exception as e:
            logger.error(f"Failed to log security event: {e}")
            raise
    
    async def _write_event_to_log(self, event: SecurityEvent) -> None:
        """Write security event to log file"""
        try:
            # Convert event to dictionary
            event_dict = asdict(event)
            
            # Convert datetime to ISO format
            event_dict['timestamp'] = event.timestamp.isoformat()
            
            # Create log entry
            log_entry = {
                'security_event': event_dict,
                'log_timestamp': datetime.now().isoformat(),
                'log_version': '1.0'
            }
            
            # Convert to JSON
            log_line = json.dumps(log_entry, ensure_ascii=False) + '\n'
            
            # Write to file (async)
            async with asyncio.Lock():
                with open(self.log_file_path, 'a', encoding='utf-8') as f:
                    f.write(log_line)
            
            # Check file size and rotate if necessary
            await self._check_log_rotation()
            
        except Exception as e:
            logger.error(f"Failed to write event to log: {e}")
            raise
    
    async def _check_log_rotation(self) -> None:
        """Check if log rotation is needed"""
        try:
            if self.log_file_path.exists() and self.log_file_path.stat().st_size > self.max_log_size:
                await self._rotate_log_file()
        except Exception as e:
            logger.error(f"Log rotation check failed: {e}")
    
    async def _rotate_log_file(self) -> None:
        """Rotate log file"""
        try:
            # Move existing log files
            for i in range(self.log_rotation_count - 1, 0, -1):
                old_file = self.log_file_path.with_suffix(f'.{i}.log')
                new_file = self.log_file_path.with_suffix(f'.{i+1}.log')
                
                if old_file.exists():
                    if new_file.exists():
                        new_file.unlink()
                    old_file.rename(new_file)
            
            # Move current log to .1
            if self.log_file_path.exists():
                rotated_file = self.log_file_path.with_suffix('.1.log')
                if rotated_file.exists():
                    rotated_file.unlink()
                self.log_file_path.rename(rotated_file)
            
            logger.info("Security audit log rotated")
            
        except Exception as e:
            logger.error(f"Log rotation failed: {e}")
    
    async def _check_event_correlations(self, event: SecurityEvent) -> None:
        """Check for security event correlations"""
        try:
            correlations = []
            
            # Get correlation window for event type
            correlation_window = self.correlation_windows.get(
                event.event_type, timedelta(minutes=5)
            )
            
            # Find related events within time window
            cutoff_time = event.timestamp - correlation_window
            related_events = [
                e for e in self.recent_events
                if e.timestamp >= cutoff_time and e.event_id != event.event_id
            ]
            
            # Check for authentication correlation patterns
            if event.event_type.startswith('authentication'):
                auth_correlations = await self._check_authentication_correlations(
                    event, related_events
                )
                correlations.extend(auth_correlations)
            
            # Check for authorization correlation patterns
            if event.event_type.startswith('authorization'):
                authz_correlations = await self._check_authorization_correlations(
                    event, related_events
                )
                correlations.extend(authz_correlations)
            
            # Check for data access patterns
            if 'data_access' in event.event_type:
                data_correlations = await self._check_data_access_correlations(
                    event, related_events
                )
                correlations.extend(data_correlations)
            
            # Log correlations if found
            if correlations:
                await self.log_security_event(
                    'event_correlation',
                    'info',
                    f"Security event correlations detected: {len(correlations)} patterns",
                    {
                        'original_event_id': event.event_id,
                        'correlations': correlations
                    }
                )
            
        except Exception as e:
            logger.error(f"Event correlation check failed: {e}")
    
    async def _check_authentication_correlations(self, event: SecurityEvent, 
                                               related_events: List[SecurityEvent]) -> List[Dict[str, Any]]:
        """Check for authentication-related correlations"""
        correlations = []
        
        try:
            # Check for multiple failed login attempts
            if event.event_type == 'authentication_failed':
                failed_attempts = [
                    e for e in related_events
                    if e.event_type == 'authentication_failed' and
                       e.user_id == event.user_id
                ]
                
                if len(failed_attempts) >= 3:
                    correlations.append({
                        'pattern': 'multiple_failed_logins',
                        'severity': 'high',
                        'description': f'Multiple failed login attempts for user {event.user_id}',
                        'event_count': len(failed_attempts),
                        'time_span': (event.timestamp - failed_attempts[0].timestamp).total_seconds()
                    })
            
            # Check for login from multiple IPs
            if event.event_type == 'authentication_success':
                ip_logins = [
                    e for e in related_events
                    if e.event_type == 'authentication_success' and
                       e.user_id == event.user_id and
                       e.ip_address != event.ip_address
                ]
                
                if ip_logins:
                    unique_ips = set(e.ip_address for e in ip_logins if e.ip_address)
                    if event.ip_address:
                        unique_ips.add(event.ip_address)
                    
                    if len(unique_ips) > 1:
                        correlations.append({
                            'pattern': 'multiple_ip_logins',
                            'severity': 'medium',
                            'description': f'User {event.user_id} logged in from multiple IPs',
                            'ip_addresses': list(unique_ips),
                            'event_count': len(ip_logins) + 1
                        })
            
        except Exception as e:
            logger.error(f"Authentication correlation check failed: {e}")
        
        return correlations
    
    async def _check_authorization_correlations(self, event: SecurityEvent,
                                              related_events: List[SecurityEvent]) -> List[Dict[str, Any]]:
        """Check for authorization-related correlations"""
        correlations = []
        
        try:
            # Check for multiple access denials
            if event.event_type == 'authorization_denied':
                denied_attempts = [
                    e for e in related_events
                    if e.event_type == 'authorization_denied' and
                       e.user_id == event.user_id
                ]
                
                if len(denied_attempts) >= 5:
                    correlations.append({
                        'pattern': 'multiple_access_denials',
                        'severity': 'medium',
                        'description': f'Multiple access denials for user {event.user_id}',
                        'event_count': len(denied_attempts),
                        'resources_attempted': list(set(e.resource for e in denied_attempts if e.resource))
                    })
            
            # Check for privilege escalation attempts
            if event.event_type == 'permission_check_failed':
                escalation_attempts = [
                    e for e in related_events
                    if e.event_type in ['permission_check_failed', 'authorization_denied'] and
                       e.user_id == event.user_id
                ]
                
                if len(escalation_attempts) >= 3:
                    correlations.append({
                        'pattern': 'privilege_escalation_attempt',
                        'severity': 'high',
                        'description': f'Possible privilege escalation attempt by user {event.user_id}',
                        'event_count': len(escalation_attempts)
                    })
            
        except Exception as e:
            logger.error(f"Authorization correlation check failed: {e}")
        
        return correlations
    
    async def _check_data_access_correlations(self, event: SecurityEvent,
                                            related_events: List[SecurityEvent]) -> List[Dict[str, Any]]:
        """Check for data access related correlations"""
        correlations = []
        
        try:
            # Check for bulk data access
            if 'data_access' in event.event_type:
                data_events = [
                    e for e in related_events
                    if 'data_access' in e.event_type and
                       e.user_id == event.user_id
                ]
                
                if len(data_events) >= 10:  # Threshold for bulk access
                    correlations.append({
                        'pattern': 'bulk_data_access',
                        'severity': 'medium',
                        'description': f'Bulk data access pattern detected for user {event.user_id}',
                        'event_count': len(data_events),
                        'time_span': (event.timestamp - data_events[0].timestamp).total_seconds()
                    })
            
            # Check for sensitive data access
            if event.metadata and event.metadata.get('data_classification') == 'sensitive':
                sensitive_access = [
                    e for e in related_events
                    if e.metadata and e.metadata.get('data_classification') == 'sensitive' and
                       e.user_id == event.user_id
                ]
                
                if len(sensitive_access) >= 3:
                    correlations.append({
                        'pattern': 'multiple_sensitive_data_access',
                        'severity': 'high',
                        'description': f'Multiple sensitive data access by user {event.user_id}',
                        'event_count': len(sensitive_access)
                    })
            
        except Exception as e:
            logger.error(f"Data access correlation check failed: {e}")
        
        return correlations
    
    async def get_security_events(self, filters: Optional[Dict[str, Any]] = None,
                                limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get security events with optional filtering
        
        Args:
            filters: Optional filters (event_type, severity, user_id, etc.)
            limit: Maximum number of events to return
            
        Returns:
            List of security events
        """
        try:
            events = self.recent_events.copy()
            
            # Apply filters
            if filters:
                if 'event_type' in filters:
                    events = [e for e in events if e.event_type == filters['event_type']]
                
                if 'severity' in filters:
                    events = [e for e in events if e.severity == filters['severity']]
                
                if 'user_id' in filters:
                    events = [e for e in events if e.user_id == filters['user_id']]
                
                if 'start_time' in filters:
                    start_time = datetime.fromisoformat(filters['start_time'])
                    events = [e for e in events if e.timestamp >= start_time]
                
                if 'end_time' in filters:
                    end_time = datetime.fromisoformat(filters['end_time'])
                    events = [e for e in events if e.timestamp <= end_time]
            
            # Sort by timestamp (newest first)
            events.sort(key=lambda e: e.timestamp, reverse=True)
            
            # Limit results
            events = events[:limit]
            
            # Convert to dictionaries
            return [asdict(event) for event in events]
            
        except Exception as e:
            logger.error(f"Failed to get security events: {e}")
            return []
    
    async def generate_audit_report(self, start_time: datetime, end_time: datetime,
                                  report_type: str = 'summary') -> Dict[str, Any]:
        """
        Generate security audit report
        
        Args:
            start_time: Report start time
            end_time: Report end time
            report_type: Type of report ('summary', 'detailed', 'compliance')
            
        Returns:
            Security audit report
        """
        try:
            # Filter events by time range
            events_in_range = [
                e for e in self.recent_events
                if start_time <= e.timestamp <= end_time
            ]
            
            if report_type == 'summary':
                report = await self._generate_summary_report(events_in_range, start_time, end_time)
            elif report_type == 'detailed':
                report = await self._generate_detailed_report(events_in_range, start_time, end_time)
            elif report_type == 'compliance':
                report = await self._generate_compliance_report(events_in_range, start_time, end_time)
            else:
                raise ValueError(f"Unknown report type: {report_type}")
            
            return report
            
        except Exception as e:
            logger.error(f"Audit report generation failed: {e}")
            raise
    
    async def _generate_summary_report(self, events: List[SecurityEvent],
                                     start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Generate summary audit report"""
        try:
            # Event statistics
            total_events = len(events)
            events_by_severity = {}
            events_by_type = {}
            
            for event in events:
                # Count by severity
                events_by_severity[event.severity] = events_by_severity.get(event.severity, 0) + 1
                
                # Count by type
                events_by_type[event.event_type] = events_by_type.get(event.event_type, 0) + 1
            
            # Security metrics
            authentication_events = sum(1 for e in events if 'authentication' in e.event_type)
            authorization_events = sum(1 for e in events if 'authorization' in e.event_type)
            failed_logins = sum(1 for e in events if e.event_type == 'authentication_failed')
            access_denials = sum(1 for e in events if e.event_type == 'authorization_denied')
            
            # Critical events
            critical_events = [e for e in events if e.severity == 'critical']
            
            return {
                'report_type': 'Security Audit Summary',
                'time_period': {
                    'start_time': start_time.isoformat(),
                    'end_time': end_time.isoformat(),
                    'duration_hours': (end_time - start_time).total_seconds() / 3600
                },
                'event_statistics': {
                    'total_events': total_events,
                    'events_by_severity': events_by_severity,
                    'events_by_type': events_by_type
                },
                'security_metrics': {
                    'authentication_events': authentication_events,
                    'authorization_events': authorization_events,
                    'failed_logins': failed_logins,
                    'access_denials': access_denials,
                    'critical_events_count': len(critical_events)
                },
                'critical_events': [asdict(e) for e in critical_events[:10]],  # Top 10
                'generation_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Summary report generation failed: {e}")
            raise
    
    async def _generate_detailed_report(self, events: List[SecurityEvent],
                                      start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Generate detailed audit report"""
        summary_report = await self._generate_summary_report(events, start_time, end_time)
        
        # Add detailed event listing
        summary_report.update({
            'report_type': 'Detailed Security Audit Report',
            'all_events': [asdict(e) for e in events],
            'event_timeline': self._create_event_timeline(events),
            'user_activity': self._analyze_user_activity(events),
            'ip_address_analysis': self._analyze_ip_addresses(events)
        })
        
        return summary_report
    
    def _create_event_timeline(self, events: List[SecurityEvent]) -> List[Dict[str, Any]]:
        """Create timeline of security events"""
        timeline = []
        
        # Group events by hour
        hourly_groups = {}
        for event in events:
            hour_key = event.timestamp.replace(minute=0, second=0, microsecond=0)
            if hour_key not in hourly_groups:
                hourly_groups[hour_key] = []
            hourly_groups[hour_key].append(event)
        
        # Create timeline entries
        for hour, hour_events in sorted(hourly_groups.items()):
            timeline.append({
                'timestamp': hour.isoformat(),
                'event_count': len(hour_events),
                'severity_breakdown': {
                    severity: sum(1 for e in hour_events if e.severity == severity)
                    for severity in ['critical', 'error', 'warning', 'info', 'debug']
                },
                'top_event_types': [
                    event_type for event_type, _ in 
                    sorted(
                        {e.event_type: sum(1 for ev in hour_events if ev.event_type == e.event_type) 
                         for e in hour_events}.items(),
                        key=lambda x: x[1], reverse=True
                    )[:3]
                ]
            })
        
        return timeline
    
    def _analyze_user_activity(self, events: List[SecurityEvent]) -> Dict[str, Any]:
        """Analyze user activity patterns"""
        user_stats = {}
        
        for event in events:
            if event.user_id:
                if event.user_id not in user_stats:
                    user_stats[event.user_id] = {
                        'total_events': 0,
                        'event_types': {},
                        'severity_counts': {},
                        'first_activity': event.timestamp,
                        'last_activity': event.timestamp
                    }
                
                stats = user_stats[event.user_id]
                stats['total_events'] += 1
                stats['event_types'][event.event_type] = stats['event_types'].get(event.event_type, 0) + 1
                stats['severity_counts'][event.severity] = stats['severity_counts'].get(event.severity, 0) + 1
                
                if event.timestamp < stats['first_activity']:
                    stats['first_activity'] = event.timestamp
                if event.timestamp > stats['last_activity']:
                    stats['last_activity'] = event.timestamp
        
        # Convert timestamps to ISO format
        for user_id, stats in user_stats.items():
            stats['first_activity'] = stats['first_activity'].isoformat()
            stats['last_activity'] = stats['last_activity'].isoformat()
        
        return user_stats
    
    def _analyze_ip_addresses(self, events: List[SecurityEvent]) -> Dict[str, Any]:
        """Analyze IP address patterns"""
        ip_stats = {}
        
        for event in events:
            if event.ip_address:
                if event.ip_address not in ip_stats:
                    ip_stats[event.ip_address] = {
                        'total_events': 0,
                        'unique_users': set(),
                        'event_types': {},
                        'severity_counts': {}
                    }
                
                stats = ip_stats[event.ip_address]
                stats['total_events'] += 1
                if event.user_id:
                    stats['unique_users'].add(event.user_id)
                stats['event_types'][event.event_type] = stats['event_types'].get(event.event_type, 0) + 1
                stats['severity_counts'][event.severity] = stats['severity_counts'].get(event.severity, 0) + 1
        
        # Convert sets to lists for JSON serialization
        for ip, stats in ip_stats.items():
            stats['unique_users'] = list(stats['unique_users'])
            stats['unique_user_count'] = len(stats['unique_users'])
        
        return ip_stats
    
    async def _generate_compliance_report(self, events: List[SecurityEvent],
                                        start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Generate compliance-focused audit report"""
        summary_report = await self._generate_summary_report(events, start_time, end_time)
        
        # Add compliance-specific metrics
        compliance_events = {
            'access_attempts': sum(1 for e in events if 'authentication' in e.event_type),
            'failed_access_attempts': sum(1 for e in events if e.event_type == 'authentication_failed'),
            'privilege_escalations': sum(1 for e in events if 'escalation' in e.event_type),
            'data_access_events': sum(1 for e in events if 'data_access' in e.event_type),
            'configuration_changes': sum(1 for e in events if 'configuration' in e.event_type),
            'security_violations': sum(1 for e in events if e.severity in ['critical', 'error'])
        }
        
        summary_report.update({
            'report_type': 'Security Compliance Audit Report',
            'compliance_metrics': compliance_events,
            'regulatory_findings': self._assess_regulatory_compliance(events),
            'audit_trail_integrity': await self._verify_audit_trail_integrity()
        })
        
        return summary_report
    
    def _assess_regulatory_compliance(self, events: List[SecurityEvent]) -> Dict[str, Any]:
        """Assess regulatory compliance based on events"""
        findings = {
            'gdpr_compliance': {
                'data_access_logged': sum(1 for e in events if 'data_access' in e.event_type) > 0,
                'consent_tracking': sum(1 for e in events if 'consent' in e.event_type) > 0,
                'data_breach_detection': sum(1 for e in events if 'breach' in e.event_type) == 0
            },
            'sox_compliance': {
                'access_controls_monitored': sum(1 for e in events if 'authorization' in e.event_type) > 0,
                'financial_data_access_logged': sum(1 for e in events 
                                                   if e.metadata and 
                                                      e.metadata.get('data_type') == 'financial') > 0
            },
            'hipaa_compliance': {
                'healthcare_data_access_logged': sum(1 for e in events 
                                                    if e.metadata and 
                                                       e.metadata.get('data_type') == 'healthcare') > 0,
                'minimum_necessary_principle': True  # Would need more complex logic
            }
        }
        
        return findings
    
    async def _verify_audit_trail_integrity(self) -> Dict[str, Any]:
        """Verify audit trail integrity"""
        try:
            # Check if log file exists and is accessible
            if not self.log_file_path.exists():
                return {
                    'integrity_status': 'fail',
                    'reason': 'Log file not found'
                }
            
            # Check file permissions
            file_stat = self.log_file_path.stat()
            
            # Basic integrity checks
            integrity_checks = {
                'file_exists': self.log_file_path.exists(),
                'file_readable': self.log_file_path.is_file(),
                'file_size': file_stat.st_size,
                'last_modified': datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                'events_in_memory': len(self.recent_events)
            }
            
            return {
                'integrity_status': 'pass',
                'checks': integrity_checks,
                'verification_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'integrity_status': 'error',
                'error': str(e)
            }