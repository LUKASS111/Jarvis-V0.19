"""Evolution package for Jarvis 1.0.0 - Professional Program Thought Tracking & Intelligent Monitoring Framework"""

# Updated implementation
from .program_evolution_tracker import (
    ProgramEvolutionTracker,
    EvolutionMetric,
    FunctionalityUpdate,
    EvolutionSession,
    get_evolution_tracker
)

# New thought tracking system
from .program_thought_tracker import (
    ProgramThoughtTracker,
    ThoughtProcess,
    DecisionPattern,
    IntelligentSuggestion,
    ThoughtSession,
    get_thought_tracker
)

from .enhanced_logging import (
    EnhancedLogger,
    get_enhanced_logger,
    get_all_loggers_report
)

from .functional_data_manager import (
    FunctionalDataValidator,
    FunctionalDataUpdater,
    DataValidationResult,
    DataUpdateResult,
    get_functional_data_validator,
    get_functional_data_updater
)

# Updated implementation
from .professional_orchestrator import (
    ProfessionalEvolutionOrchestrator,
    get_evolution_orchestrator
)

# New intelligent monitoring orchestrator
from .intelligent_monitoring_orchestrator import (
    IntelligentMonitoringOrchestrator,
    get_intelligent_monitoring_orchestrator
)

__all__ = [
    # Updated implementation
    'ProgramEvolutionTracker',
    'EvolutionMetric', 
    'FunctionalityUpdate',
    'EvolutionSession',
    'get_evolution_tracker',
    
    # New thought tracking system
    'ProgramThoughtTracker',
    'ThoughtProcess',
    'DecisionPattern', 
    'IntelligentSuggestion',
    'ThoughtSession',
    'get_thought_tracker',
    
    # Enhanced logging
    'EnhancedLogger',
    'get_enhanced_logger',
    'get_all_loggers_report',
    
    # Data management
    'FunctionalDataValidator',
    'FunctionalDataUpdater',
    'DataValidationResult',
    'DataUpdateResult',
    'get_functional_data_validator',
    'get_functional_data_updater',
    
    # Updated implementation
    'ProfessionalEvolutionOrchestrator',
    'get_evolution_orchestrator',
    
    # New intelligent monitoring
    'IntelligentMonitoringOrchestrator',
    'get_intelligent_monitoring_orchestrator'
]