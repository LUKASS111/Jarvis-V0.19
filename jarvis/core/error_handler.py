#!/usr/bin/env python3
"""
Comprehensive Error Handling Framework for AutoGPT System
Provides centralized error handling, validation, fallbacks, and user feedback
"""

import os
import sys
import json
import time
import traceback
import logging
import functools
from typing import Any, Callable, Dict, List
from datetime import datetime
from enum import Enum

class ErrorLevel(Enum):
    """Error severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class ErrorHandler:
    """Centralized error handling system"""
    
    def __init__(self, log_file: str = "logs/error_log.jsonl"):
        self.log_file = log_file
        self.error_count = 0
        self.warning_count = 0
        self.fallback_count = 0
        self.session_errors: List[Dict] = []
        
        # Create logs directory if it doesn't exist
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def log_error(self, error: Exception, context: str = "", level: ErrorLevel = ErrorLevel.ERROR, 
                  user_message: str = None) -> Dict[str, Any]:
        """Log error with context and user feedback"""
        
        error_data = {
            "timestamp": datetime.now().isoformat(),
            "level": level.value,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            "traceback": traceback.format_exc() if level in [ErrorLevel.ERROR, ErrorLevel.CRITICAL] else None,
            "user_message": user_message or self._generate_user_message(error, context),
            "session_id": getattr(self, 'session_id', 'unknown')
        }
        
        # Update counters
        if level == ErrorLevel.ERROR or level == ErrorLevel.CRITICAL:
            self.error_count += 1
        elif level == ErrorLevel.WARNING:
            self.warning_count += 1
            
        self.session_errors.append(error_data)
        
        # Write to log file (skip intentional test errors to keep production logs clean)
        is_test_error = (
            "Test error" in str(error) or 
            "Simulated error" in str(error) or
            "test_" in context.lower() or
            "_test" in context.lower() or
            "performance_test" in context.lower()
        )
        
        if not is_test_error:
            try:
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.write(json.dumps(error_data, ensure_ascii=False) + "\n")
            except Exception as log_error:
                print(f"[WARN] Failed to write error log: {log_error}")
        
        # Console output (skip test errors to keep console clean during testing)
        if not is_test_error:
            emoji = self._get_error_emoji(level)
            print(f"{emoji} {error_data['user_message']}")
        
        # Logger output (always log but with appropriate level)
        if not is_test_error:
            if level in [ErrorLevel.ERROR, ErrorLevel.CRITICAL]:
                self.logger.error(f"{context}: {error}")
            elif level == ErrorLevel.WARNING:
                self.logger.warning(f"{context}: {error}")
            else:
                self.logger.info(f"{context}: {error}")
            
        return error_data
    
    def _generate_user_message(self, error: Exception, context: str) -> str:
        """Generate user-friendly error message"""
        error_type = type(error).__name__
        
        if "ModuleNotFoundError" in error_type:
            module_name = str(error).split("'")[1] if "'" in str(error) else "unknown"
            return f"Brak wymaganego modułu: {module_name}. Sprawdź instalację zależności."
        elif "FileNotFoundError" in error_type:
            return f"Nie znaleziono pliku wymaganego przez system. Sprawdź ścieżki plików."
        elif "ConnectionError" in error_type or "requests" in str(error).lower():
            return f"Problem z połączeniem sieciowym. Sprawdź połączenie internetowe."
        elif "PermissionError" in error_type:
            return f"Brak uprawnień do wykonania operacji. Sprawdź uprawnienia plików."
        elif "JSONDecodeError" in error_type:
            return f"Problem z parsowaniem danych JSON. Sprawdź format plików konfiguracyjnych."
        elif "ImportError" in error_type:
            return f"Problem z importem modułu. Sprawdź zależności systemu."
        else:
            return f"Błąd w {context}: {str(error)[:100]}"
    
    def _get_error_emoji(self, level: ErrorLevel) -> str:
        """Get appropriate emoji for error level"""
        emoji_map = {
            ErrorLevel.INFO: "[INFO]",
            ErrorLevel.WARNING: "[WARN]",
            ErrorLevel.ERROR: "[FAIL]",
            ErrorLevel.CRITICAL: "[ALERT]"
        }
        return emoji_map.get(level, "❓")
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of errors in current session"""
        return {
            "total_errors": self.error_count,
            "total_warnings": self.warning_count,
            "total_fallbacks": self.fallback_count,
            "recent_errors": self.session_errors[-5:],  # Last 5 errors
            "most_common_errors": self._get_common_errors()
        }
    
    def _get_common_errors(self) -> List[Dict]:
        """Get most common error types"""
        error_types = {}
        for error in self.session_errors:
            error_type = error.get("error_type", "Unknown")
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        return [{"type": k, "count": v} for k, v in sorted(error_types.items(), 
                                                          key=lambda x: x[1], reverse=True)[:3]]

# Global error handler instance
error_handler = ErrorHandler()

def safe_execute(fallback_value: Any = None, context: str = "", 
                user_message: str = None, level: ErrorLevel = ErrorLevel.ERROR):
    """Decorator for safe function execution with error handling"""
    def decorator(func: Callable) -> Callable:
        """
        Decorator function that wraps the target function with error handling.
        
        Args:
            func: The function to wrap with error handling
            
        Returns:
            Wrapper function with error handling
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            """
            Wrapper function that executes the target function safely.
            
            Args:
                *args: Arguments to pass to the target function
                **kwargs: Keyword arguments to pass to the target function
                
            Returns:
                Result of the target function or fallback value on error
            """
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_handler.log_error(e, context or func.__name__, level, user_message)
                error_handler.fallback_count += 1
                return fallback_value
        return wrapper
    return decorator











# Emergency recovery functions
def emergency_fallback(operation: str = "unknown") -> Dict[str, Any]:
    """Emergency fallback for critical system failures"""
    return {
        "status": "emergency_fallback",
        "operation": operation,
        "message": "System używa awaryjnego trybu działania",
        "timestamp": datetime.now().isoformat(),
        "recommendations": [
            "Sprawdź logi błędów",
            "Zrestartuj system",
            "Sprawdź zależności"
        ]
    }

def create_error_report() -> str:
    """Create comprehensive error report"""
    summary = error_handler.get_session_summary()
    
    report = f"""
# AutoGPT System - Raport Błędów
Wygenerowano: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Podsumowanie
- Błędy: {summary['total_errors']}
- Ostrzeżenia: {summary['total_warnings']}  
- Użycia fallback: {summary['total_fallbacks']}

## Najczęstsze błędy
"""
    
    for error in summary['most_common_errors']:
        report += f"- {error['type']}: {error['count']} wystąpień\n"
    
    report += "\n## Ostatnie błędy\n"
    for error in summary['recent_errors']:
        report += f"- [{error['level'].upper()}] {error['timestamp']}: {error['user_message']}\n"
    
    return report

def validate_file_path(file_path):
    """Validate file path format"""
    try:
        return isinstance(file_path, str) and len(file_path) > 0
    except Exception:
        return False

def validate_json_data(data):
    """Validate JSON data format"""
    try:
        import json
        if isinstance(data, str):
            json.loads(data)
        elif isinstance(data, dict):
            json.dumps(data)
        else:
            return False
        return True
    except Exception:
        return False

def validate_model_name(model_name):
    """Validate model name format"""
    try:
        return isinstance(model_name, str) and ":" in model_name and len(model_name) > 3
    except Exception:
        return False

# Global error handler instance
_global_error_handler = ErrorHandler()

def log_error(error: Exception, context: str = "", level: ErrorLevel = ErrorLevel.ERROR):
    """Global function to log errors using the global error handler"""
    return _global_error_handler.log_error(error, context, level)

if __name__ == "__main__":
    # Test error handling (only when run directly, not during imports)
    if "--test-error-handler" in sys.argv:
        @safe_execute(fallback_value="Fallback result", context="Test function")
        def test_function():
            """
            Test function for error handler demonstration.
            
            Raises:
                ValueError: Always raises this error to test error handling
                
            Returns:
                Never returns normally, always raises exception
            """
            raise ValueError("Test error")
        
        print("Testing error handler...")
        result = test_function()
        print(f"Result: {result}")
        
        print("\nError summary:")
        print(create_error_report())