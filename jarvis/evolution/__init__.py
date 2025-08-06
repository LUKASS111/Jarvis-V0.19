"""Evolution package for Jarvis V0.19 - Professional Program Evolution Framework"""

from .program_evolution_tracker import (
    ProgramEvolutionTracker,
    EvolutionMetric,
    FunctionalityUpdate,
    EvolutionSession,
    get_evolution_tracker
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

from .professional_orchestrator import (
    ProfessionalEvolutionOrchestrator,
    get_evolution_orchestrator
)

__all__ = [
    # Core tracking
    'ProgramEvolutionTracker',
    'EvolutionMetric', 
    'FunctionalityUpdate',
    'EvolutionSession',
    'get_evolution_tracker',
    
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
    
    # Orchestration
    'ProfessionalEvolutionOrchestrator',
    'get_evolution_orchestrator'
]