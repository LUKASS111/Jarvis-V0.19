"""
GUI Performance Configuration
Optimized settings for responsive user experience
"""

# Performance settings
PERFORMANCE_CONFIG = {
    # GUI responsiveness settings
    "target_fps": 60,
    "max_frame_time_ms": 16.67,
    "lazy_loading_threshold": 100,  # Load tabs with >100 elements lazily
    
    # Memory management
    "cache_size_limit": 50,  # Maximum cached widgets
    "gc_interval": 1000,     # Garbage collection interval (ms)
    
    # UI update settings
    "update_interval_ms": 16,  # UI update interval for 60fps
    "batch_update_size": 10,   # Batch UI updates
    
    # Loading optimization
    "startup_delay_ms": 0,     # Delay non-critical startup operations
    "async_loading": True,     # Use async loading where possible
    
    # Visual optimization
    "animation_duration": 200,  # Animation duration (ms)
    "use_opengl": False,       # Use OpenGL acceleration (if available)
    "double_buffering": True,  # Enable double buffering
}

# Performance monitoring
MONITORING_CONFIG = {
    "enable_performance_monitoring": True,
    "log_slow_operations": True,
    "slow_operation_threshold": 16,  # ms
    "memory_monitoring": True,
    "fps_monitoring": True
}

# GUI optimization flags
OPTIMIZATION_FLAGS = {
    "lazy_tab_loading": True,
    "widget_caching": True,
    "image_caching": True,
    "font_caching": True,
    "style_caching": True
}

def get_performance_config():
    """Get current performance configuration"""
    return PERFORMANCE_CONFIG

def get_monitoring_config():
    """Get monitoring configuration"""
    return MONITORING_CONFIG

def get_optimization_flags():
    """Get optimization flags"""
    return OPTIMIZATION_FLAGS

def update_performance_setting(key, value):
    """Update performance setting"""
    if key in PERFORMANCE_CONFIG:
        PERFORMANCE_CONFIG[key] = value
        return True
    return False
