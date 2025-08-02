"""
Core functionality modules for Jarvis AI Assistant.
"""

# Import core components
from .data_archiver import (
    get_archiver, archive_input, archive_output, 
    archive_intermediate, archive_system, get_archive_stats,
    create_archive_backup, DataArchiver, ArchiveEntry
)

from .data_verifier import (
    get_verifier, verify_data_immediately, is_data_safe_to_use,
    DataVerifier, VerificationResult
)

from .agent_workflow import (
    get_workflow_manager, start_agent_workflow, get_workflow_status,
    AgentWorkflowManager, TestScenario, CycleResult, AgentReport
)

from .backup_recovery import (
    get_backup_manager, create_backup, create_pre_change_backup,
    restore_from_backup, list_available_backups, get_backup_stats,
    BackupRecoveryManager, BackupInfo, RecoveryPoint
)

# Main components for easy access
__all__ = [
    # Data Archiving
    'get_archiver', 'archive_input', 'archive_output', 
    'archive_intermediate', 'archive_system', 'get_archive_stats',
    'create_archive_backup', 'DataArchiver', 'ArchiveEntry',
    
    # Data Verification  
    'get_verifier', 'verify_data_immediately', 'is_data_safe_to_use',
    'DataVerifier', 'VerificationResult',
    
    # Agent Workflows
    'get_workflow_manager', 'start_agent_workflow', 'get_workflow_status',
    'AgentWorkflowManager', 'TestScenario', 'CycleResult', 'AgentReport',
    
    # Backup & Recovery
    'get_backup_manager', 'create_backup', 'create_pre_change_backup',
    'restore_from_backup', 'list_available_backups', 'get_backup_stats',
    'BackupRecoveryManager', 'BackupInfo', 'RecoveryPoint'
]