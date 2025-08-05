# AGENT_TASKS.md - Comprehensive Data Archiving and Verification System

## System Overview

Jarvis-V0.19 implements a comprehensive data archiving and verification system designed to ensure maximum data integrity, truthfulness, and system reliability through automated agent workflows.

## Core System Components

### 1. Data Archiving System (`jarvis/core/data_archiver.py`)

**Purpose**: Archive all data flowing through the program with comprehensive metadata.

**Key Features**:
- SQLite-based storage for all input/output/intermediate/system data
- Thread-safe operations with locking mechanisms  
- Automatic content hashing for deduplication
- Metadata tracking (source, operation, timestamps)
- Verification queue management
- Agent activity logging

**Database Schema**:
```sql
-- Main archive entries
archive_entries (
    id, timestamp, data_type, content, source, operation,
    content_hash, metadata, verification_status, 
    verification_score, verification_model, 
    verification_timestamp, verification_details
)

-- Verification queue
verification_queue (
    id, archive_entry_id, priority, attempts, max_attempts
)

-- Agent activities
agent_activities (
    id, agent_id, activity_type, description, data, timestamp
)
```

### 2. Data Verification System (`jarvis/core/data_verifier.py`)

**Purpose**: Implement dual-model verification with confidence scoring.

**Verification Types**:
- **Fact Checking**: Verify factual accuracy using secondary LLM
- **Logical Consistency**: Check for internal contradictions and logical flow
- **Format Validation**: Validate JSON, XML, and other structured formats
- **Code Validation**: Check code safety, syntax, and best practices
- **General Content**: Overall quality and appropriateness assessment

**Verification Process**:
1. Background worker continuously processes verification queue
2. Entries verified using different model than primary (bias prevention)
3. Results scored 0.0-1.0 confidence with reasoning
4. Failed verifications marked for manual review
5. Verified data marked safe for use in further operations

### 3. Agent Workflow System (`jarvis/core/agent_workflow.py`)

**Purpose**: Autonomous testing cycles with auto-correction capabilities.

**Test Scenarios**:
- Functional tests (basic archiving, verification)
- Integration tests (memory system compatibility)
- Performance tests (high-volume processing)
- Resilience tests (error handling validation)

**Workflow Process**:
1. Agent registers with system capabilities
2. System runs 100+ automated test cycles
3. Each cycle selects appropriate test scenario
4. Results verified against validation criteria
5. Auto-correction applied for failures
6. Compliance tracking until target threshold met
7. Comprehensive reports generated

### 4. Backup & Recovery System (`jarvis/core/backup_recovery.py`)

**Purpose**: Comprehensive backup, recovery, and data integrity management.

**Backup Types**:
- **Scheduled**: Daily (2 AM) and weekly (Sunday 3 AM) automated backups
- **Pre-Change**: Created before significant system modifications
- **Manual**: User-initiated backups with custom descriptions
- **Emergency**: Automatic backups during critical system events

**Features**:
- Compressed tar.gz archives with integrity checksums
- Metadata tracking and verification
- Automated cleanup with retention policies
- Point-in-time recovery capabilities
- Backup verification before restore operations

## Agent Workflow Commands

### Setting Up Agents

```python
from jarvis.core.agent_workflow import get_workflow_manager, start_agent_workflow

# Register an agent
manager = get_workflow_manager()
manager.register_agent(
    "test_agent_001", 
    capabilities=["testing", "verification", "correction"],
    config={"timeout": 30, "max_retries": 3}
)

# Start 100-cycle workflow with 90% compliance target
cycle_id = start_agent_workflow("test_agent_001", 100, 0.90)
```

### Monitoring Workflows

```python
# Check workflow status
status = manager.get_cycle_status(cycle_id)
print(f"Status: {status['status']}")
print(f"Compliance: {status.get('compliance_achieved', False)}")

# Get agent performance summary
summary = manager.get_agent_summary("test_agent_001")
print(f"Total cycles: {summary['total_cycles']}")
print(f"Recent average score: {summary['average_recent_score']:.2f}")
```

### Manual Data Operations

```python
from jarvis.core.data_archiver import archive_input, archive_output, get_archive_stats
from jarvis.core.data_verifier import verify_data_immediately

# Archive input data
archive_id = archive_input(
    content="User input: What is Python?",
    source="main_interface",
    operation="user_query",
    metadata={"user_id": "user_001", "session": "sess_123"}
)

# Immediate verification
result = verify_data_immediately(
    content="Python is a programming language",
    data_type="factual",
    source="llm_response", 
    operation="fact_statement"
)
print(f"Verified: {result.is_verified}, Confidence: {result.confidence_score}")

# Check archive statistics
stats = get_archive_stats()
print(f"Total entries: {stats['total_entries']}")
print(f"Verification stats: {stats['verification_stats']}")
```

### Backup Operations

```python
from jarvis.core.backup_recovery import create_backup, create_pre_change_backup, restore_from_backup

# Create manual backup
backup_info = create_backup("Before major refactoring")
print(f"Backup created: {backup_info.backup_id}")

# Pre-change backup
pre_backup = create_pre_change_backup("Updating verification algorithms")

# List available backups
from jarvis.core.backup_recovery import list_available_backups
backups = list_available_backups()
for backup in backups[:5]:  # Show 5 most recent
    print(f"{backup.backup_id}: {backup.description} ({backup.timestamp})")

# Restore from backup
success = restore_from_backup("backup_20250128_120000_manual")
print(f"Restore successful: {success}")
```

## System Integration

### Memory System Integration

The archiving system integrates with the existing memory system:

```python
# Modified memory operations now archive all changes
from jarvis.memory.memory import remember_fact, recall_fact

# This will automatically archive the operation
remember_fact("Important system parameter: max_tokens=2048")

# Retrieval also logged
result = recall_fact("system parameter")
```

### LLM Interface Integration

LLM interactions are automatically archived:

```python
from jarvis.llm.llm_interface import ask_local_llm

# All LLM calls now archived with verification
response = ask_local_llm("Explain quantum computing")
# Automatically creates archive entries for input and output
# Queues verification of response accuracy
```

## Agent Testing Procedures

### Running Complete Agent Workflow

```bash
# Command-line interface for agent testing
python -c "
from jarvis.core.agent_workflow import start_agent_workflow
import time

# Start comprehensive testing
cycle_id = start_agent_workflow('production_agent', 100, 0.95)
print(f'Started workflow: {cycle_id}')

# Monitor progress (runs in background)
# Check data/agent_reports/ for detailed results
"
```

### Custom Test Scenarios

Add custom test scenarios to `config/test_scenarios.json`:

```json
{
  "id": "custom_scenario_001",
  "name": "Custom API Integration Test",
  "description": "Test custom API integration with verification",
  "input_data": {
    "api_endpoint": "/test/endpoint",
    "expected_format": "json"
  },
  "expected_outcomes": [
    "api_response_received",
    "format_validated",
    "data_archived"
  ],
  "validation_criteria": {
    "response_time_ms": 5000,
    "success_rate": 0.95,
    "verification_required": true
  },
  "priority": 2,
  "category": "integration"
}
```

## Quality Assurance Workflow

### Daily Operations

1. **Morning Review**:
   ```python
   from jarvis.core.data_archiver import get_archive_stats
   from jarvis.core.backup_recovery import get_backup_stats
   
   # Check overnight activity
   archive_stats = get_archive_stats()
   backup_stats = get_backup_stats()
   
   print(f"New entries: {archive_stats['total_entries']}")
   print(f"Verification rate: {archive_stats['verification_stats']}")
   print(f"Latest backup: {backup_stats['newest_backup']}")
   ```

2. **Verification Review**:
   ```python
   from jarvis.core.data_verifier import get_verifier
   
   verifier = get_verifier()
   # Review rejected or low-confidence verifications
   # Manual review process for edge cases
   ```

3. **Agent Performance Review**:
   ```python
   from jarvis.core.agent_workflow import get_workflow_manager
   
   manager = get_workflow_manager()
   # Review agent reports in data/agent_reports/
   # Analyze compliance trends and error patterns
   ```

### Weekly Operations

1. **Backup Verification**:
   ```python
   from jarvis.core.backup_recovery import get_backup_manager
   
   manager = get_backup_manager()
   backups = manager.list_backups(backup_type="weekly")
   
   # Verify integrity of weekly backups
   for backup in backups:
       integrity = manager.verify_backup_integrity(backup.backup_id)
       print(f"{backup.backup_id}: {'OK' if integrity else 'FAILED'}")
   ```

2. **System Health Check**:
   ```python
   # Run comprehensive system verification
   cycle_id = start_agent_workflow("health_check_agent", 50, 0.98)
   # Review results for system health trends
   ```

### Monthly Operations

1. **Backup Cleanup**:
   ```python
   from jarvis.core.backup_recovery import get_backup_manager
   
   manager = get_backup_manager()
   manager.cleanup_old_backups(
       days_to_keep=30,
       keep_weekly=True,
       keep_monthly=True
   )
   ```

2. **Archive Optimization**:
   ```python
   # Archive maintenance and optimization
   # Review verification model performance
   # Update test scenarios based on new requirements
   ```

## Error Handling and Recovery

### System Failures

1. **Archive Database Corruption**:
   ```python
   # Automatic backup creation before any database operations
   # Corruption detection with automatic recovery
   from jarvis.core.backup_recovery import restore_from_backup
   
   # Find latest valid backup
   backups = list_available_backups()
   latest_backup = backups[0]
   
   # Restore database
   restore_success = restore_from_backup(latest_backup.backup_id)
   ```

2. **Verification System Failures**:
   ```python
   # Fallback verification mechanisms
   # Manual review queue for failed verifications
   # Emergency mode with reduced verification requirements
   ```

3. **Agent Workflow Failures**:
   ```python
   # Auto-restart mechanisms
   # Degraded mode operation
   # Alert systems for critical failures
   ```

## Performance Monitoring

### Key Metrics

1. **Archive Performance**:
   - Entries per second
   - Storage efficiency
   - Query response times

2. **Verification Performance**:
   - Verification queue length
   - Average confidence scores
   - Model response times

3. **Agent Performance**:
   - Compliance rates
   - Error frequencies
   - Correction effectiveness

### Monitoring Commands

```python
# Real-time statistics
from jarvis.core.data_archiver import get_archive_stats
from jarvis.core.data_verifier import get_verifier
from jarvis.core.agent_workflow import get_workflow_manager

def system_health_report():
    archive_stats = get_archive_stats()
    workflow_manager = get_workflow_manager()
    
    print("=== SYSTEM HEALTH REPORT ===")
    print(f"Archive Entries: {archive_stats['total_entries']}")
    print(f"Pending Verification: {archive_stats['pending_verification']}")
    print(f"Average Verification Score: {archive_stats['average_verification_score']}")
    print(f"Active Workflows: {len(workflow_manager.active_cycles)}")
    
    return {
        'archive_health': 'OK' if archive_stats['pending_verification'] < 100 else 'WARN',
        'verification_health': 'OK' if archive_stats['average_verification_score'] > 0.7 else 'WARN',
        'workflow_health': 'OK'
    }
```

## Security and Compliance

### Data Protection

1. **Access Control**: All archive operations logged with source tracking
2. **Integrity Verification**: Cryptographic hashes for all stored data
3. **Audit Trail**: Complete history of all system operations
4. **Backup Security**: Encrypted backups with integrity verification

### Compliance Features

1. **Data Retention**: Configurable retention policies
2. **Data Purging**: Secure deletion of expired data
3. **Access Logging**: Complete audit trail of data access
4. **Verification Requirements**: Mandatory verification for critical data

## Troubleshooting Guide

### Common Issues

1. **High Verification Queue**:
   ```python
   # Check verification worker status
   # Increase verification model timeout
   # Add additional verification workers
   ```

2. **Low Compliance Rates**:
   ```python
   # Review test scenarios for relevance
   # Adjust validation criteria
   # Improve auto-correction algorithms
   ```

3. **Backup Failures**:
   ```python
   # Check disk space
   # Verify file permissions
   # Review backup configuration
   ```

### Diagnostic Commands

```python
def run_system_diagnostics():
    """Run comprehensive system diagnostics"""
    print("Running system diagnostics...")
    
    # Test archive operations
    test_id = archive_system("Diagnostic test", "diagnostics", "system_check")
    print(f"Archive test: {'PASS' if test_id else 'FAIL'}")
    
    # Test verification
    result = verify_data_immediately("Test data", "test", "diagnostics", "verification_check")
    print(f"Verification test: {'PASS' if result.is_verified else 'FAIL'}")
    
    # Test backup
    try:
        backup = create_backup("Diagnostic backup")
        print(f"Backup test: PASS ({backup.backup_id})")
    except Exception as e:
        print(f"Backup test: FAIL ({e})")
    
    return "Diagnostics complete"
```

## System Configuration

### Environment Variables

```bash
# Archive configuration
export JARVIS_ARCHIVE_DB_PATH="data/jarvis_archive.db"
export JARVIS_BACKUP_ROOT="data/backups"
export JARVIS_VERIFICATION_TIMEOUT=30

# Agent configuration  
export JARVIS_AGENT_CYCLES=100
export JARVIS_COMPLIANCE_TARGET=0.90
export JARVIS_AUTO_CORRECTION=true

# Backup configuration
export JARVIS_BACKUP_RETENTION_DAYS=30
export JARVIS_BACKUP_COMPRESSION=true
export JARVIS_SCHEDULED_BACKUPS=true
```

### Configuration Files

1. **config/archive_config.json**:
   ```json
   {
     "verification_models": ["llama3:8b", "codellama:13b"],
     "verification_timeout": 30,
     "max_verification_attempts": 3,
     "confidence_threshold": 0.7
   }
   ```

2. **config/backup_config.json**:
   ```json
   {
     "retention_policy": {
       "daily_backups_days": 7,
       "weekly_backups_weeks": 4,
       "monthly_backups_months": 12
     },
     "compression": true,
     "integrity_check": true
   }
   ```

## API Reference

### Core Functions

```python
# Data Archiving
archive_input(content, source, operation, metadata=None) -> int
archive_output(content, source, operation, metadata=None) -> int
archive_intermediate(content, source, operation, metadata=None) -> int
archive_system(content, source, operation, metadata=None) -> int

# Data Verification
verify_data_immediately(content, data_type, source, operation) -> VerificationResult
is_data_safe_to_use(archive_entry_id, min_confidence=0.7) -> bool

# Agent Workflows
start_agent_workflow(agent_id, cycle_count=100, target_compliance=0.90) -> str
get_workflow_status(cycle_id) -> Dict[str, Any]

# Backup Operations
create_backup(description="Manual backup") -> BackupInfo
create_pre_change_backup(change_description) -> BackupInfo
restore_from_backup(backup_id) -> bool
list_available_backups() -> List[BackupInfo]

# Statistics and Monitoring
get_archive_stats() -> Dict[str, Any]
get_backup_stats() -> Dict[str, Any]
system_health_report() -> Dict[str, str]
```

This comprehensive system ensures maximum data integrity, automated quality assurance, and robust recovery capabilities while maintaining high performance and ease of use.