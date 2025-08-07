"""
CRDT Conflict Resolution System
Phase 4 - Integration: Advanced conflict resolution for semantic conflicts

This module provides conflict resolution beyond the mathematical guarantees
of CRDTs, handling semantic conflicts and maintaining data integrity.
"""

import json
import time
import logging
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import hashlib

# from .crdt_base import CRDTOperationResult


from dataclasses import dataclass


@dataclass 
class CRDTOperationResult:
    """Result of a CRDT operation"""
    success: bool
    error: str = ""
    result: Any = None


logger = logging.getLogger(__name__)


class ConflictType(Enum):
    """Types of conflicts that can occur"""
    SEMANTIC = "semantic"
    BUSINESS_LOGIC = "business_logic"
    ACCESS_CONTROL = "access_control"
    DATA_INTEGRITY = "data_integrity"
    TEMPORAL = "temporal"
    DEPENDENCY = "dependency"


class ResolutionStrategy(Enum):
    """Conflict resolution strategies"""
    LAST_WRITE_WINS = "last_write_wins"
    MERGE_VALUES = "merge_values"
    MANUAL_INTERVENTION = "manual_intervention"
    AUTOMATIC_RULE = "automatic_rule"
    USER_PREFERENCE = "user_preference"
    HIGHEST_PRIORITY = "highest_priority"


@dataclass
class ConflictEvent:
    """Information about a detected conflict"""
    conflict_id: str
    conflict_type: ConflictType
    crdt_name: str
    involved_nodes: List[str]
    conflicting_operations: List[Dict[str, Any]]
    detection_time: datetime
    resolution_strategy: Optional[ResolutionStrategy] = None
    resolution_time: Optional[datetime] = None
    resolution_details: Optional[Dict[str, Any]] = None
    manual_review_required: bool = False
    priority: str = "normal"  # low, normal, high, critical
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        result = asdict(self)
        result['conflict_type'] = self.conflict_type.value
        result['detection_time'] = self.detection_time.isoformat()
        
        if self.resolution_strategy:
            result['resolution_strategy'] = self.resolution_strategy.value
        if self.resolution_time:
            result['resolution_time'] = self.resolution_time.isoformat()
            
        return result


@dataclass
class ResolutionRule:
    """Rule for automatic conflict resolution"""
    rule_id: str
    conflict_type: ConflictType
    conditions: Dict[str, Any]
    strategy: ResolutionStrategy
    priority: int
    enabled: bool = True
    description: str = ""
    
    def matches(self, conflict: ConflictEvent) -> bool:
        """Check if this rule matches the given conflict"""
        if not self.enabled or conflict.conflict_type != self.conflict_type:
            return False
        
        # Check all conditions
        for condition_key, condition_value in self.conditions.items():
            if not self._check_condition(conflict, condition_key, condition_value):
                return False
        
        return True
    
    def _check_condition(self, conflict: ConflictEvent, key: str, value: Any) -> bool:
        """Check a specific condition"""
        if key == "crdt_name_pattern":
            return value in conflict.crdt_name
        elif key == "max_nodes":
            return len(conflict.involved_nodes) <= value
        elif key == "priority":
            return conflict.priority == value
        elif key == "operation_type":
            return any(op.get("type") == value for op in conflict.conflicting_operations)
        else:
            return True  # Unknown condition passes by default


class CRDTConflictResolver:
    """
    Advanced conflict resolution system for CRDTs
    
    Handles semantic conflicts that go beyond the mathematical
    guarantees provided by CRDT algorithms.
    """
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        
        # Conflict tracking
        self.active_conflicts: Dict[str, ConflictEvent] = {}
        self.resolved_conflicts: List[ConflictEvent] = []
        self.resolution_rules: List[ResolutionRule] = []
        
        # Statistics
        self.conflict_stats = {
            "total_detected": 0,
            "total_resolved": 0,
            "auto_resolved": 0,
            "manual_resolved": 0,
            "pending_manual": 0
        }
        
        # Configuration
        self.max_history_size = 1000
        self.auto_resolution_enabled = True
        self.manual_review_threshold = timedelta(hours=24)
        
        # Setup default resolution rules
        self._setup_default_rules()
        
        logger.info(f"CRDT Conflict Resolver initialized for node {node_id}")
    
    def _setup_default_rules(self):
        """Setup default conflict resolution rules"""
        
        # Rule 1: Last write wins for configuration updates
        self.resolution_rules.append(ResolutionRule(
            rule_id="config_lww",
            conflict_type=ConflictType.SEMANTIC,
            conditions={"crdt_name_pattern": "config", "max_nodes": 5},
            strategy=ResolutionStrategy.LAST_WRITE_WINS,
            priority=100,
            description="Use last-write-wins for configuration conflicts"
        ))
        
        # Rule 2: Merge values for counter increments
        self.resolution_rules.append(ResolutionRule(
            rule_id="counter_merge",
            conflict_type=ConflictType.SEMANTIC,
            conditions={"operation_type": "increment"},
            strategy=ResolutionStrategy.MERGE_VALUES,
            priority=90,
            description="Merge counter increment operations"
        ))
        
        # Rule 3: Manual review for high-priority operations
        self.resolution_rules.append(ResolutionRule(
            rule_id="high_priority_manual",
            conflict_type=ConflictType.BUSINESS_LOGIC,
            conditions={"priority": "high"},
            strategy=ResolutionStrategy.MANUAL_INTERVENTION,
            priority=200,
            description="Require manual review for high-priority conflicts"
        ))
        
        # Rule 4: Automatic rule for access control conflicts
        self.resolution_rules.append(ResolutionRule(
            rule_id="access_control_auto",
            conflict_type=ConflictType.ACCESS_CONTROL,
            conditions={},
            strategy=ResolutionStrategy.HIGHEST_PRIORITY,
            priority=150,
            description="Use highest priority for access control conflicts"
        ))
    
    def detect_semantic_conflict(self, crdt_name: str, operation1: Dict[str, Any], 
                                operation2: Dict[str, Any]) -> Optional[ConflictEvent]:
        """
        Detect semantic conflicts between two operations
        
        This goes beyond CRDT mathematical guarantees to check for
        business logic and semantic conflicts.
        """
        
        # Check for various types of semantic conflicts
        conflicts = []
        
        # 1. Check for business logic conflicts
        business_conflict = self._check_business_logic_conflict(
            crdt_name, operation1, operation2
        )
        if business_conflict:
            conflicts.append(business_conflict)
        
        # 2. Check for temporal conflicts
        temporal_conflict = self._check_temporal_conflict(
            operation1, operation2
        )
        if temporal_conflict:
            conflicts.append(temporal_conflict)
        
        # 3. Check for data integrity conflicts
        integrity_conflict = self._check_data_integrity_conflict(
            operation1, operation2
        )
        if integrity_conflict:
            conflicts.append(integrity_conflict)
        
        # 4. Check for dependency conflicts
        dependency_conflict = self._check_dependency_conflict(
            operation1, operation2
        )
        if dependency_conflict:
            conflicts.append(dependency_conflict)
        
        if conflicts:
            # Create conflict event for the most severe conflict
            primary_conflict = max(conflicts, key=lambda c: self._get_conflict_severity(c))
            
            conflict_event = ConflictEvent(
                conflict_id=self._generate_conflict_id(),
                conflict_type=primary_conflict,
                crdt_name=crdt_name,
                involved_nodes=[
                    operation1.get("node_id", "unknown"),
                    operation2.get("node_id", "unknown")
                ],
                conflicting_operations=[operation1, operation2],
                detection_time=datetime.utcnow(),
                priority=self._determine_conflict_priority(primary_conflict, operation1, operation2)
            )
            
            self.active_conflicts[conflict_event.conflict_id] = conflict_event
            self.conflict_stats["total_detected"] += 1
            
            logger.warning(f"Semantic conflict detected: {conflict_event.conflict_id}")
            return conflict_event
        
        return None
    
    def _check_business_logic_conflict(self, crdt_name: str, op1: Dict[str, Any], 
                                     op2: Dict[str, Any]) -> Optional[ConflictType]:
        """Check for business logic conflicts"""
        
        # Example: Archive operations that conflict with purge operations
        if (op1.get("operation") == "archive_data" and 
            op2.get("operation") == "purge_data" and
            op1.get("entry_id") == op2.get("entry_id")):
            return ConflictType.BUSINESS_LOGIC
        
        # Example: Conflicting permission changes
        if (op1.get("operation") == "grant_permission" and 
            op2.get("operation") == "revoke_permission" and
            op1.get("resource") == op2.get("resource")):
            return ConflictType.BUSINESS_LOGIC
        
        return None
    
    def _check_temporal_conflict(self, op1: Dict[str, Any], 
                               op2: Dict[str, Any]) -> Optional[ConflictType]:
        """Check for temporal ordering conflicts"""
        
        # Check if operations have explicit ordering requirements
        if (op1.get("must_be_before") and 
            op2.get("operation_id") in op1.get("must_be_before", [])):
            return ConflictType.TEMPORAL
        
        if (op2.get("must_be_before") and 
            op1.get("operation_id") in op2.get("must_be_before", [])):
            return ConflictType.TEMPORAL
        
        return None
    
    def _check_data_integrity_conflict(self, op1: Dict[str, Any], 
                                     op2: Dict[str, Any]) -> Optional[ConflictType]:
        """Check for data integrity conflicts"""
        
        # Example: Conflicting data types
        if (op1.get("data_type") and op2.get("data_type") and
            op1.get("field_name") == op2.get("field_name") and
            op1.get("data_type") != op2.get("data_type")):
            return ConflictType.DATA_INTEGRITY
        
        # Example: Constraint violations
        if (op1.get("constraint_violation") or op2.get("constraint_violation")):
            return ConflictType.DATA_INTEGRITY
        
        return None
    
    def _check_dependency_conflict(self, op1: Dict[str, Any], 
                                 op2: Dict[str, Any]) -> Optional[ConflictType]:
        """Check for dependency conflicts"""
        
        # Check if operations depend on conflicting resources
        op1_deps = set(op1.get("dependencies", []))
        op2_deps = set(op2.get("dependencies", []))
        
        # Check for conflicting dependencies
        if op1_deps.intersection(op2.get("conflicts_with", set())):
            return ConflictType.DEPENDENCY
        
        if op2_deps.intersection(op1.get("conflicts_with", set())):
            return ConflictType.DEPENDENCY
        
        return None
    
    def resolve_conflict(self, conflict_id: str) -> CRDTOperationResult:
        """Resolve a specific conflict"""
        
        conflict = self.active_conflicts.get(conflict_id)
        if not conflict:
            return CRDTOperationResult(
                success=False,
                error=f"Conflict {conflict_id} not found"
            )
        
        try:
            # Find applicable resolution rule
            resolution_rule = self._find_resolution_rule(conflict)
            
            if resolution_rule and self.auto_resolution_enabled:
                # Apply automatic resolution
                result = self._apply_resolution_strategy(conflict, resolution_rule)
                
                if result.success:
                    conflict.resolution_strategy = resolution_rule.strategy
                    conflict.resolution_time = datetime.utcnow()
                    conflict.resolution_details = result.result
                    
                    # Move to resolved conflicts
                    self.resolved_conflicts.append(conflict)
                    del self.active_conflicts[conflict_id]
                    
                    self.conflict_stats["total_resolved"] += 1
                    self.conflict_stats["auto_resolved"] += 1
                    
                    logger.info(f"Auto-resolved conflict {conflict_id} using {resolution_rule.rule_id}")
                
                return result
            
            else:
                # Mark for manual intervention
                conflict.manual_review_required = True
                self.conflict_stats["pending_manual"] += 1
                
                logger.warning(f"Conflict {conflict_id} requires manual intervention")
                
                return CRDTOperationResult(
                    success=False,
                    error="Manual intervention required",
                    result={"requires_manual_review": True}
                )
                
        except Exception as e:
            logger.error(f"Error resolving conflict {conflict_id}: {e}")
            return CRDTOperationResult(
                success=False,
                error=f"Resolution error: {e}"
            )
    
    def _find_resolution_rule(self, conflict: ConflictEvent) -> Optional[ResolutionRule]:
        """Find the best resolution rule for a conflict"""
        
        matching_rules = [
            rule for rule in self.resolution_rules
            if rule.matches(conflict)
        ]
        
        if not matching_rules:
            return None
        
        # Return rule with highest priority
        return max(matching_rules, key=lambda r: r.priority)
    
    def _apply_resolution_strategy(self, conflict: ConflictEvent, 
                                 rule: ResolutionRule) -> CRDTOperationResult:
        """Apply a specific resolution strategy"""
        
        strategy = rule.strategy
        operations = conflict.conflicting_operations
        
        if strategy == ResolutionStrategy.LAST_WRITE_WINS:
            return self._resolve_last_write_wins(operations)
        
        elif strategy == ResolutionStrategy.MERGE_VALUES:
            return self._resolve_merge_values(operations)
        
        elif strategy == ResolutionStrategy.HIGHEST_PRIORITY:
            return self._resolve_highest_priority(operations)
        
        elif strategy == ResolutionStrategy.AUTOMATIC_RULE:
            return self._resolve_automatic_rule(conflict, rule)
        
        else:
            return CRDTOperationResult(
                success=False,
                error=f"Unsupported resolution strategy: {strategy}"
            )
    
    def _resolve_last_write_wins(self, operations: List[Dict[str, Any]]) -> CRDTOperationResult:
        """Resolve using last-write-wins strategy"""
        
        # Find operation with latest timestamp
        latest_op = max(operations, key=lambda op: op.get("timestamp", 0))
        
        return CRDTOperationResult(
            success=True,
            result={
                "strategy": "last_write_wins",
                "winning_operation": latest_op,
                "discarded_operations": [op for op in operations if op != latest_op]
            }
        )
    
    def _resolve_merge_values(self, operations: List[Dict[str, Any]]) -> CRDTOperationResult:
        """Resolve by merging values"""
        
        # For numeric values, sum them
        if all(isinstance(op.get("value"), (int, float)) for op in operations):
            merged_value = sum(op.get("value", 0) for op in operations)
            
            return CRDTOperationResult(
                success=True,
                result={
                    "strategy": "merge_values",
                    "merged_value": merged_value,
                    "original_operations": operations
                }
            )
        
        # For sets, union them
        elif all(isinstance(op.get("value"), (list, set)) for op in operations):
            merged_set = set()
            for op in operations:
                merged_set.update(op.get("value", []))
            
            return CRDTOperationResult(
                success=True,
                result={
                    "strategy": "merge_values",
                    "merged_value": list(merged_set),
                    "original_operations": operations
                }
            )
        
        else:
            return CRDTOperationResult(
                success=False,
                error="Cannot merge incompatible value types"
            )
    
    def _resolve_highest_priority(self, operations: List[Dict[str, Any]]) -> CRDTOperationResult:
        """Resolve using highest priority operation"""
        
        # Priority order: critical > high > normal > low
        priority_order = {"critical": 4, "high": 3, "normal": 2, "low": 1}
        
        highest_priority_op = max(
            operations,
            key=lambda op: priority_order.get(op.get("priority", "normal"), 2)
        )
        
        return CRDTOperationResult(
            success=True,
            result={
                "strategy": "highest_priority",
                "winning_operation": highest_priority_op,
                "discarded_operations": [op for op in operations if op != highest_priority_op]
            }
        )
    
    def _resolve_automatic_rule(self, conflict: ConflictEvent, 
                              rule: ResolutionRule) -> CRDTOperationResult:
        """Apply custom automatic rule logic"""
        
        # This would contain custom business logic for specific rules
        # For now, default to last-write-wins
        return self._resolve_last_write_wins(conflict.conflicting_operations)
    
    def manual_resolve_conflict(self, conflict_id: str, resolution: Dict[str, Any]) -> CRDTOperationResult:
        """Manually resolve a conflict"""
        
        conflict = self.active_conflicts.get(conflict_id)
        if not conflict:
            return CRDTOperationResult(
                success=False,
                error=f"Conflict {conflict_id} not found"
            )
        
        try:
            # Apply manual resolution
            conflict.resolution_strategy = ResolutionStrategy.MANUAL_INTERVENTION
            conflict.resolution_time = datetime.utcnow()
            conflict.resolution_details = resolution
            
            # Move to resolved conflicts
            self.resolved_conflicts.append(conflict)
            del self.active_conflicts[conflict_id]
            
            self.conflict_stats["total_resolved"] += 1
            self.conflict_stats["manual_resolved"] += 1
            self.conflict_stats["pending_manual"] -= 1
            
            logger.info(f"Manually resolved conflict {conflict_id}")
            
            return CRDTOperationResult(
                success=True,
                result={"manual_resolution": resolution}
            )
            
        except Exception as e:
            logger.error(f"Error in manual resolution of {conflict_id}: {e}")
            return CRDTOperationResult(
                success=False,
                error=f"Manual resolution error: {e}"
            )
    
    def add_resolution_rule(self, rule: ResolutionRule):
        """Add a custom resolution rule"""
        self.resolution_rules.append(rule)
        logger.info(f"Added resolution rule: {rule.rule_id}")
    
    def remove_resolution_rule(self, rule_id: str) -> bool:
        """Remove a resolution rule"""
        original_count = len(self.resolution_rules)
        self.resolution_rules = [r for r in self.resolution_rules if r.rule_id != rule_id]
        
        if len(self.resolution_rules) < original_count:
            logger.info(f"Removed resolution rule: {rule_id}")
            return True
        
        return False
    
    def get_conflict_statistics(self) -> Dict[str, Any]:
        """Get conflict resolution statistics"""
        return {
            "statistics": self.conflict_stats.copy(),
            "active_conflicts": len(self.active_conflicts),
            "resolution_rules": len(self.resolution_rules),
            "auto_resolution_enabled": self.auto_resolution_enabled,
            "conflicts_by_type": self._get_conflicts_by_type(),
            "average_resolution_time": self._calculate_average_resolution_time()
        }
    
    def get_pending_manual_conflicts(self) -> List[Dict[str, Any]]:
        """Get conflicts requiring manual intervention"""
        manual_conflicts = [
            conflict for conflict in self.active_conflicts.values()
            if conflict.manual_review_required
        ]
        
        return [conflict.to_dict() for conflict in manual_conflicts]
    
    def _generate_conflict_id(self) -> str:
        """Generate unique conflict ID"""
        timestamp = str(int(time.time() * 1000))
        node_hash = hashlib.md5(self.node_id.encode()).hexdigest()[:8]
        return f"conflict_{timestamp}_{node_hash}"
    
    def _get_conflict_severity(self, conflict_type: ConflictType) -> int:
        """Get numeric severity for conflict type"""
        severity_map = {
            ConflictType.DATA_INTEGRITY: 5,
            ConflictType.BUSINESS_LOGIC: 4,
            ConflictType.ACCESS_CONTROL: 3,
            ConflictType.DEPENDENCY: 2,
            ConflictType.TEMPORAL: 2,
            ConflictType.SEMANTIC: 1
        }
        return severity_map.get(conflict_type, 1)
    
    def _determine_conflict_priority(self, conflict_type: ConflictType, 
                                   op1: Dict[str, Any], op2: Dict[str, Any]) -> str:
        """Determine priority for a conflict"""
        
        # High priority for data integrity and access control
        if conflict_type in [ConflictType.DATA_INTEGRITY, ConflictType.ACCESS_CONTROL]:
            return "high"
        
        # Check operation priorities
        op_priorities = [op.get("priority", "normal") for op in [op1, op2]]
        if "critical" in op_priorities:
            return "critical"
        elif "high" in op_priorities:
            return "high"
        
        return "normal"
    
    def _get_conflicts_by_type(self) -> Dict[str, int]:
        """Get count of conflicts by type"""
        type_counts = {}
        
        for conflict in self.active_conflicts.values():
            conflict_type = conflict.conflict_type.value
            type_counts[conflict_type] = type_counts.get(conflict_type, 0) + 1
        
        for conflict in self.resolved_conflicts:
            conflict_type = conflict.conflict_type.value
            resolved_key = f"{conflict_type}_resolved"
            type_counts[resolved_key] = type_counts.get(resolved_key, 0) + 1
        
        return type_counts
    
    def _calculate_average_resolution_time(self) -> float:
        """Calculate average time to resolve conflicts"""
        resolution_times = []
        
        for conflict in self.resolved_conflicts:
            if conflict.resolution_time and conflict.detection_time:
                delta = conflict.resolution_time - conflict.detection_time
                resolution_times.append(delta.total_seconds())
        
        if resolution_times:
            return sum(resolution_times) / len(resolution_times)
        
        return 0.0
    
    def cleanup_current_conflicts(self, max_age_days: int = 30):
        """Clean up old resolved conflicts"""
        cutoff_time = datetime.utcnow() - timedelta(days=max_age_days)
        
        original_count = len(self.resolved_conflicts)
        
        self.resolved_conflicts = [
            conflict for conflict in self.resolved_conflicts
            if conflict.resolution_time and conflict.resolution_time > cutoff_time
        ]
        
        cleaned_count = original_count - len(self.resolved_conflicts)
        if cleaned_count > 0:
            logger.info(f"Cleaned up {cleaned_count} old resolved conflicts")


# Example usage
if __name__ == "__main__":
    import sys
    
    logging.basicConfig(level=logging.INFO)
    
    # Create conflict resolver
    resolver = CRDTConflictResolver("test_node")
    
    # Example operations that conflict
    operation1 = {
        "operation_id": "op_001",
        "node_id": "node_1",
        "operation": "archive_data",
        "entry_id": "entry_123",
        "timestamp": time.time(),
        "priority": "normal"
    }
    
    operation2 = {
        "operation_id": "op_002",
        "node_id": "node_2",
        "operation": "purge_data",
        "entry_id": "entry_123",
        "timestamp": time.time() + 1,
        "priority": "high"
    }
    
    # Detect conflict
    conflict = resolver.detect_semantic_conflict("archive_entries", operation1, operation2)
    
    if conflict:
        print(f"Detected conflict: {conflict.conflict_id}")
        print(f"Type: {conflict.conflict_type}")
        print(f"Priority: {conflict.priority}")
        
        # Try to resolve
        result = resolver.resolve_conflict(conflict.conflict_id)
        print(f"Resolution result: {result.success}")
        
        if result.success:
            print(f"Resolution details: {result.result}")
        else:
            print(f"Resolution error: {result.error}")
    
    # Print statistics
    stats = resolver.get_conflict_statistics()
    print(f"Conflict statistics: {json.dumps(stats, indent=2)}")