"""
Standardized Error Handling System for Jarvis 1.0.0
Provides consistent error handling, logging, and reporting across all system components
"""

import logging
import traceback
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for classification"""
    SYSTEM = "system"
    PLUGIN = "plugin"
    LLM = "llm"
    DATABASE = "database"
    NETWORK = "network"
    CONFIGURATION = "configuration"
    SECURITY = "security"
    USER_INPUT = "user_input"
    CRDT = "crdt"
    FILE_PROCESSING = "file_processing"


@dataclass
class ErrorContext:
    """Context information for errors"""
    component: str = ""
    operation: str = ""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    additional_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ErrorReport:
    """Comprehensive error report"""
    error_id: str
    timestamp: float
    error_type: str
    message: str
    severity: ErrorSeverity
    category: ErrorCategory
    context: ErrorContext
    stack_trace: Optional[str] = None
    resolution_steps: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    resolved: bool = False
    resolution_time: Optional[float] = None


class JarvisException(Exception):
    """Base exception class for all Jarvis-specific errors"""
    
    def __init__(self, 
                 message: str, 
                 error_code: str = None,
                 severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                 category: ErrorCategory = ErrorCategory.SYSTEM,
                 context: ErrorContext = None,
                 cause: Exception = None):
        super().__init__(message)
        self.error_id = str(uuid.uuid4())
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.severity = severity
        self.category = category
        self.context = context or ErrorContext()
        self.cause = cause
        self.timestamp = time.time()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary"""
        return {
            "error_id": self.error_id,
            "timestamp": self.timestamp,
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "severity": self.severity.value,
            "category": self.category.value,
            "context": {
                "component": self.context.component,
                "operation": self.context.operation,
                "user_id": self.context.user_id,
                "session_id": self.context.session_id,
                "request_id": self.context.request_id,
                "additional_data": self.context.additional_data
            },
            "cause": str(self.cause) if self.cause else None
        }


class PluginException(JarvisException):
    """Exception for plugin-related errors"""
    
    def __init__(self, message: str, plugin_name: str = None, **kwargs):
        kwargs.setdefault('category', ErrorCategory.PLUGIN)
        kwargs.setdefault('context', ErrorContext()).component = plugin_name or "unknown_plugin"
        super().__init__(message, **kwargs)


class LLMException(JarvisException):
    """Exception for LLM-related errors"""
    
    def __init__(self, message: str, provider: str = None, model: str = None, **kwargs):
        kwargs.setdefault('category', ErrorCategory.LLM)
        context = kwargs.setdefault('context', ErrorContext())
        context.component = provider or "unknown_provider"
        context.additional_data.update({"model": model} if model else {})
        super().__init__(message, **kwargs)


class DatabaseException(JarvisException):
    """Exception for database-related errors"""
    
    def __init__(self, message: str, table: str = None, operation: str = None, **kwargs):
        kwargs.setdefault('category', ErrorCategory.DATABASE)
        context = kwargs.setdefault('context', ErrorContext())
        context.component = "database"
        context.operation = operation or "unknown_operation"
        context.additional_data.update({"table": table} if table else {})
        super().__init__(message, **kwargs)


class NetworkException(JarvisException):
    """Exception for network-related errors"""
    
    def __init__(self, message: str, endpoint: str = None, **kwargs):
        kwargs.setdefault('category', ErrorCategory.NETWORK)
        context = kwargs.setdefault('context', ErrorContext())
        context.component = "network"
        context.additional_data.update({"endpoint": endpoint} if endpoint else {})
        super().__init__(message, **kwargs)


class ConfigurationException(JarvisException):
    """Exception for configuration-related errors"""
    
    def __init__(self, message: str, config_key: str = None, **kwargs):
        kwargs.setdefault('category', ErrorCategory.CONFIGURATION)
        context = kwargs.setdefault('context', ErrorContext())
        context.component = "configuration"
        context.additional_data.update({"config_key": config_key} if config_key else {})
        super().__init__(message, **kwargs)


class SecurityException(JarvisException):
    """Exception for security-related errors"""
    
    def __init__(self, message: str, **kwargs):
        kwargs.setdefault('category', ErrorCategory.SECURITY)
        kwargs.setdefault('severity', ErrorSeverity.HIGH)
        super().__init__(message, **kwargs)


class FileProcessingException(JarvisException):
    """Exception for file processing errors"""
    
    def __init__(self, message: str, file_path: str = None, processor: str = None, **kwargs):
        kwargs.setdefault('category', ErrorCategory.FILE_PROCESSING)
        context = kwargs.setdefault('context', ErrorContext())
        context.component = processor or "file_processor"
        context.additional_data.update({
            "file_path": file_path
        } if file_path else {})
        super().__init__(message, **kwargs)


class CRDTException(JarvisException):
    """Exception for CRDT-related errors"""
    
    def __init__(self, message: str, crdt_type: str = None, operation: str = None, **kwargs):
        kwargs.setdefault('category', ErrorCategory.CRDT)
        context = kwargs.setdefault('context', ErrorContext())
        context.component = crdt_type or "crdt"
        context.operation = operation or "unknown_operation"
        super().__init__(message, **kwargs)


class ErrorHandler:
    """Main error handler for the Jarvis system"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.error_reports: Dict[str, ErrorReport] = {}
        self.error_listeners: List[callable] = []
        self.auto_resolution_rules: Dict[str, callable] = {}
        
    def handle_exception(self, exc: Exception, context: ErrorContext = None) -> ErrorReport:
        """Handle an exception and create error report
        
        Args:
            exc: Exception to handle
            context: Additional context information
            
        Returns:
            ErrorReport: Generated error report
        """
        if isinstance(exc, JarvisException):
            # Update context if provided
            if context:
                exc.context.component = context.component or exc.context.component
                exc.context.operation = context.operation or exc.context.operation
                exc.context.additional_data.update(context.additional_data)
            
            error_report = ErrorReport(
                error_id=exc.error_id,
                timestamp=exc.timestamp,
                error_type=exc.__class__.__name__,
                message=exc.message,
                severity=exc.severity,
                category=exc.category,
                context=exc.context,
                stack_trace=traceback.format_exc(),
                resolution_steps=self._get_resolution_steps(exc)
            )
        else:
            # Handle non-Jarvis exceptions
            error_id = str(uuid.uuid4())
            error_context = context or ErrorContext()
            
            error_report = ErrorReport(
                error_id=error_id,
                timestamp=time.time(),
                error_type=exc.__class__.__name__,
                message=str(exc),
                severity=ErrorSeverity.MEDIUM,
                category=ErrorCategory.SYSTEM,
                context=error_context,
                stack_trace=traceback.format_exc(),
                resolution_steps=self._get_generic_resolution_steps(exc)
            )
        
        # Store error report
        self.error_reports[error_report.error_id] = error_report
        
        # Log the error
        self._log_error(error_report)
        
        # Notify listeners
        self._notify_listeners(error_report)
        
        # Attempt auto-resolution
        self._attempt_auto_resolution(error_report)
        
        return error_report
    
    def log_error(self, message: str, 
                  severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                  category: ErrorCategory = ErrorCategory.SYSTEM,
                  context: ErrorContext = None) -> ErrorReport:
        """Log an error without an exception
        
        Args:
            message: Error message
            severity: Error severity
            category: Error category
            context: Error context
            
        Returns:
            ErrorReport: Generated error report
        """
        error_id = str(uuid.uuid4())
        error_context = context or ErrorContext()
        
        error_report = ErrorReport(
            error_id=error_id,
            timestamp=time.time(),
            error_type="LoggedError",
            message=message,
            severity=severity,
            category=category,
            context=error_context,
            resolution_steps=[]
        )
        
        self.error_reports[error_id] = error_report
        self._log_error(error_report)
        self._notify_listeners(error_report)
        
        return error_report
    
    def get_error_report(self, error_id: str) -> Optional[ErrorReport]:
        """Get error report by ID"""
        return self.error_reports.get(error_id)
    
    def get_error_reports(self, 
                         category: ErrorCategory = None,
                         severity: ErrorSeverity = None,
                         resolved: bool = None,
                         limit: int = None) -> List[ErrorReport]:
        """Get error reports with optional filtering
        
        Args:
            category: Filter by error category
            severity: Filter by error severity
            resolved: Filter by resolution status
            limit: Maximum number of reports to return
            
        Returns:
            List of error reports
        """
        reports = list(self.error_reports.values())
        
        # Apply filters
        if category:
            reports = [r for r in reports if r.category == category]
        if severity:
            reports = [r for r in reports if r.severity == severity]
        if resolved is not None:
            reports = [r for r in reports if r.resolved == resolved]
        
        # Sort by timestamp (newest first)
        reports.sort(key=lambda r: r.timestamp, reverse=True)
        
        # Apply limit
        if limit:
            reports = reports[:limit]
        
        return reports
    
    def resolve_error(self, error_id: str, resolution_note: str = None) -> bool:
        """Mark an error as resolved
        
        Args:
            error_id: ID of the error to resolve
            resolution_note: Optional note about the resolution
            
        Returns:
            bool: True if error was resolved
        """
        if error_id in self.error_reports:
            error_report = self.error_reports[error_id]
            error_report.resolved = True
            error_report.resolution_time = time.time()
            
            if resolution_note:
                error_report.metadata["resolution_note"] = resolution_note
            
            self.logger.info(f"Error {error_id} marked as resolved")
            return True
        
        return False
    
    def add_error_listener(self, listener: callable) -> None:
        """Add error event listener
        
        Args:
            listener: Function to call when errors occur
        """
        self.error_listeners.append(listener)
    
    def remove_error_listener(self, listener: callable) -> None:
        """Remove error event listener"""
        if listener in self.error_listeners:
            self.error_listeners.remove(listener)
    
    def add_auto_resolution_rule(self, error_pattern: str, resolution_func: callable) -> None:
        """Add automatic error resolution rule
        
        Args:
            error_pattern: Pattern to match error types or messages
            resolution_func: Function to attempt resolution
        """
        self.auto_resolution_rules[error_pattern] = resolution_func
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics"""
        total_errors = len(self.error_reports)
        resolved_errors = len([r for r in self.error_reports.values() if r.resolved])
        
        # Count by category
        category_counts = {}
        for report in self.error_reports.values():
            category = report.category.value
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Count by severity
        severity_counts = {}
        for report in self.error_reports.values():
            severity = report.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Recent errors (last 24 hours)
        recent_threshold = time.time() - 86400  # 24 hours
        recent_errors = len([r for r in self.error_reports.values() if r.timestamp > recent_threshold])
        
        return {
            "total_errors": total_errors,
            "resolved_errors": resolved_errors,
            "unresolved_errors": total_errors - resolved_errors,
            "resolution_rate": resolved_errors / total_errors if total_errors > 0 else 0,
            "recent_errors_24h": recent_errors,
            "errors_by_category": category_counts,
            "errors_by_severity": severity_counts
        }
    
    def _log_error(self, error_report: ErrorReport) -> None:
        """Log error report"""
        log_level = {
            ErrorSeverity.LOW: logging.INFO,
            ErrorSeverity.MEDIUM: logging.WARNING,
            ErrorSeverity.HIGH: logging.ERROR,
            ErrorSeverity.CRITICAL: logging.CRITICAL
        }.get(error_report.severity, logging.ERROR)
        
        self.logger.log(
            log_level,
            f"[{error_report.category.value.upper()}] {error_report.message} "
            f"(ID: {error_report.error_id}, Component: {error_report.context.component})"
        )
        
        if error_report.stack_trace and error_report.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            self.logger.debug(f"Stack trace for {error_report.error_id}:\n{error_report.stack_trace}")
    
    def _notify_listeners(self, error_report: ErrorReport) -> None:
        """Notify error listeners"""
        for listener in self.error_listeners:
            try:
                listener(error_report)
            except Exception as e:
                self.logger.error(f"Error in error listener: {e}")
    
    def _attempt_auto_resolution(self, error_report: ErrorReport) -> None:
        """Attempt automatic error resolution"""
        for pattern, resolution_func in self.auto_resolution_rules.items():
            if (pattern in error_report.error_type or 
                pattern in error_report.message or
                pattern == error_report.category.value):
                try:
                    if resolution_func(error_report):
                        self.resolve_error(error_report.error_id, "Auto-resolved")
                        break
                except Exception as e:
                    self.logger.warning(f"Auto-resolution failed for {error_report.error_id}: {e}")
    
    def _get_resolution_steps(self, exc: JarvisException) -> List[str]:
        """Get resolution steps for Jarvis exceptions"""
        if isinstance(exc, PluginException):
            return [
                "Check plugin configuration",
                "Verify plugin dependencies",
                "Review plugin logs",
                "Restart plugin if necessary"
            ]
        elif isinstance(exc, LLMException):
            return [
                "Check LLM provider connectivity",
                "Verify model availability",
                "Review API credentials",
                "Try fallback provider if available"
            ]
        elif isinstance(exc, DatabaseException):
            return [
                "Check database connectivity",
                "Verify database permissions",
                "Check disk space",
                "Review database logs"
            ]
        elif isinstance(exc, NetworkException):
            return [
                "Check network connectivity",
                "Verify endpoint availability",
                "Review network configuration",
                "Check firewall settings"
            ]
        elif isinstance(exc, ConfigurationException):
            return [
                "Review configuration file",
                "Check configuration syntax",
                "Verify configuration values",
                "Reset to default if necessary"
            ]
        else:
            return self._get_generic_resolution_steps(exc)
    
    def _get_generic_resolution_steps(self, exc: Exception) -> List[str]:
        """Get generic resolution steps"""
        return [
            "Review error details and stack trace",
            "Check system logs for related issues",
            "Verify system resources and dependencies",
            "Restart affected component if necessary",
            "Contact support if issue persists"
        ]


# Global error handler instance
_error_handler: Optional[ErrorHandler] = None


def get_error_handler() -> ErrorHandler:
    """Get the global error handler instance"""
    global _error_handler
    if _error_handler is None:
        _error_handler = ErrorHandler()
    return _error_handler


def handle_error(exc: Exception, context: ErrorContext = None) -> ErrorReport:
    """Handle an error (convenience function)"""
    return get_error_handler().handle_exception(exc, context)


def log_error(message: str, 
              severity: ErrorSeverity = ErrorSeverity.MEDIUM,
              category: ErrorCategory = ErrorCategory.SYSTEM,
              context: ErrorContext = None) -> ErrorReport:
    """Log an error (convenience function)"""
    return get_error_handler().log_error(message, severity, category, context)