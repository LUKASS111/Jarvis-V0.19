#!/usr/bin/env python3
"""
Advanced AI Workflow Manager - Stage 7
Professional AI workflow automation and orchestration
"""

import os
import sys
import json
import time
import uuid
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from jarvis.core.error_handler import ErrorHandler, ErrorLevel, safe_execute

class WorkflowStatus(Enum):
    """Workflow execution status"""
    DRAFT = "draft"
    ACTIVE = "active"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskType(Enum):
    """AI task types"""
    TEXT_GENERATION = "text_generation"
    IMAGE_ANALYSIS = "image_analysis"
    AUDIO_PROCESSING = "audio_processing"
    DATA_PROCESSING = "data_processing"
    MODEL_TRAINING = "model_training"
    QUALITY_ASSURANCE = "quality_assurance"
    CUSTOM = "custom"

@dataclass
class WorkflowTask:
    """Individual workflow task definition"""
    id: str
    name: str
    task_type: TaskType
    parameters: Dict[str, Any]
    dependencies: List[str]
    timeout_seconds: int = 300
    retry_count: int = 3
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

@dataclass
class Workflow:
    """AI workflow definition"""
    id: str
    name: str
    description: str
    tasks: List[WorkflowTask]
    status: WorkflowStatus
    created_at: str
    updated_at: str
    created_by: str
    tags: List[str]
    schedule: Optional[str] = None
    
    def to_dict(self):
        """Convert workflow to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'tasks': [asdict(task) for task in self.tasks],
            'status': self.status.value,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'created_by': self.created_by,
            'tags': self.tags,
            'schedule': self.schedule
        }

class AIWorkflowManager:
    """Professional AI workflow management system"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or Path("config/ai_workflows")
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.workflows: Dict[str, Workflow] = {}
        self.workflow_history: Dict[str, List[Dict]] = {}
        self.active_executions: Dict[str, Dict] = {}
        
        # Performance metrics
        self.metrics = {
            'total_workflows': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'average_execution_time': 0.0,
            'last_execution': None
        }
        
        # Load existing workflows
        self._load_workflows()
        
        print("[AI Workflow] Manager initialized successfully")
    
    def _load_workflows(self):
        """Load workflows from configuration"""
        workflow_file = self.config_dir / "workflows.json"
        
        if workflow_file.exists():
            try:
                with open(workflow_file, 'r') as f:
                    data = json.load(f)
                
                for workflow_data in data.get('workflows', []):
                    workflow = self._dict_to_workflow(workflow_data)
                    self.workflows[workflow.id] = workflow
                
                self.metrics.update(data.get('metrics', {}))
                
                print(f"[AI Workflow] Loaded {len(self.workflows)} workflows")
                
            except Exception as e:
                print(f"[AI Workflow] Error loading workflows: {e}")
                # Create sample workflows
                self._create_sample_workflows()
        else:
            # Create sample workflows for demonstration
            self._create_sample_workflows()
    
    def _dict_to_workflow(self, data: Dict) -> Workflow:
        """Convert dictionary to workflow object"""
        tasks = []
        for task_data in data['tasks']:
            task = WorkflowTask(
                id=task_data['id'],
                name=task_data['name'],
                task_type=TaskType(task_data['task_type']),
                parameters=task_data['parameters'],
                dependencies=task_data['dependencies'],
                timeout_seconds=task_data.get('timeout_seconds', 300),
                retry_count=task_data.get('retry_count', 3),
                created_at=task_data.get('created_at')
            )
            tasks.append(task)
        
        return Workflow(
            id=data['id'],
            name=data['name'],
            description=data['description'],
            tasks=tasks,
            status=WorkflowStatus(data['status']),
            created_at=data['created_at'],
            updated_at=data['updated_at'],
            created_by=data['created_by'],
            tags=data['tags'],
            schedule=data.get('schedule')
        )
    
    def _create_sample_workflows(self):
        """Create sample workflows for demonstration"""
        sample_workflows = [
            {
                'name': 'Data Processing Pipeline',
                'description': 'Automated data preprocessing and analysis workflow',
                'tasks': [
                    {
                        'name': 'Data Validation',
                        'task_type': TaskType.DATA_PROCESSING,
                        'parameters': {'validation_rules': ['required_fields', 'data_types']},
                        'dependencies': []
                    },
                    {
                        'name': 'Data Cleaning',
                        'task_type': TaskType.DATA_PROCESSING,
                        'parameters': {'remove_duplicates': True, 'fill_missing': 'mean'},
                        'dependencies': ['Data Validation']
                    },
                    {
                        'name': 'Feature Engineering',
                        'task_type': TaskType.DATA_PROCESSING,
                        'parameters': {'normalize': True, 'create_features': ['date_parts']},
                        'dependencies': ['Data Cleaning']
                    }
                ],
                'tags': ['data', 'preprocessing', 'automation']
            },
            {
                'name': 'Content Generation Workflow',
                'description': 'Automated content generation and review process',
                'tasks': [
                    {
                        'name': 'Topic Research',
                        'task_type': TaskType.TEXT_GENERATION,
                        'parameters': {'research_depth': 'comprehensive', 'sources': 5},
                        'dependencies': []
                    },
                    {
                        'name': 'Content Generation',
                        'task_type': TaskType.TEXT_GENERATION,
                        'parameters': {'style': 'professional', 'length': 'medium'},
                        'dependencies': ['Topic Research']
                    },
                    {
                        'name': 'Quality Review',
                        'task_type': TaskType.QUALITY_ASSURANCE,
                        'parameters': {'check_grammar': True, 'check_facts': True},
                        'dependencies': ['Content Generation']
                    }
                ],
                'tags': ['content', 'generation', 'review']
            },
            {
                'name': 'Model Training Pipeline',
                'description': 'Automated model training and evaluation workflow',
                'tasks': [
                    {
                        'name': 'Data Preparation',
                        'task_type': TaskType.DATA_PROCESSING,
                        'parameters': {'split_ratio': [0.8, 0.1, 0.1], 'stratify': True},
                        'dependencies': []
                    },
                    {
                        'name': 'Model Training',
                        'task_type': TaskType.MODEL_TRAINING,
                        'parameters': {'epochs': 100, 'batch_size': 32, 'learning_rate': 0.001},
                        'dependencies': ['Data Preparation']
                    },
                    {
                        'name': 'Model Evaluation',
                        'task_type': TaskType.QUALITY_ASSURANCE,
                        'parameters': {'metrics': ['accuracy', 'precision', 'recall']},
                        'dependencies': ['Model Training']
                    }
                ],
                'tags': ['training', 'ml', 'evaluation']
            }
        ]
        
        for workflow_data in sample_workflows:
            workflow = self.create_workflow(
                name=workflow_data['name'],
                description=workflow_data['description'],
                tasks=workflow_data['tasks'],
                tags=workflow_data['tags']
            )
            workflow.status = WorkflowStatus.ACTIVE
        
        self._save_workflows()
    
    def create_workflow(self, name: str, description: str, tasks: List[Dict], 
                       tags: Optional[List[str]] = None) -> Workflow:
        """Create a new workflow"""
        workflow_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        # Convert task dictionaries to WorkflowTask objects
        workflow_tasks = []
        for i, task_data in enumerate(tasks):
            task_id = f"{workflow_id}_task_{i}"
            task = WorkflowTask(
                id=task_id,
                name=task_data['name'],
                task_type=task_data['task_type'],
                parameters=task_data['parameters'],
                dependencies=task_data['dependencies'],
                timeout_seconds=task_data.get('timeout_seconds', 300),
                retry_count=task_data.get('retry_count', 3)
            )
            workflow_tasks.append(task)
        
        workflow = Workflow(
            id=workflow_id,
            name=name,
            description=description,
            tasks=workflow_tasks,
            status=WorkflowStatus.DRAFT,
            created_at=timestamp,
            updated_at=timestamp,
            created_by="system",
            tags=tags or []
        )
        
        self.workflows[workflow_id] = workflow
        self.metrics['total_workflows'] += 1
        
        print(f"[AI Workflow] Created workflow: {name} ({workflow_id})")
        return workflow
    
    def execute_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Execute a workflow"""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow = self.workflows[workflow_id]
        
        if workflow.status == WorkflowStatus.RUNNING:
            return {'status': 'error', 'message': 'Workflow is already running'}
        
        print(f"[AI Workflow] Starting execution of: {workflow.name}")
        
        execution_id = str(uuid.uuid4())
        start_time = time.time()
        
        execution_log = {
            'execution_id': execution_id,
            'workflow_id': workflow_id,
            'workflow_name': workflow.name,
            'start_time': datetime.now().isoformat(),
            'status': 'running',
            'tasks_completed': 0,
            'total_tasks': len(workflow.tasks),
            'errors': []
        }
        
        self.active_executions[execution_id] = execution_log
        workflow.status = WorkflowStatus.RUNNING
        
        try:
            # Execute tasks in dependency order
            completed_tasks = set()
            
            for task in workflow.tasks:
                # Check dependencies
                if all(dep in completed_tasks for dep in task.dependencies):
                    # Execute task
                    task_result = self._execute_task(task)
                    
                    if task_result['status'] == 'success':
                        completed_tasks.add(task.name)
                        execution_log['tasks_completed'] += 1
                        print(f"[AI Workflow] Completed task: {task.name}")
                    else:
                        execution_log['errors'].append({
                            'task': task.name,
                            'error': task_result.get('error', 'Unknown error')
                        })
                        print(f"[AI Workflow] Task failed: {task.name}")
                        break
            
            # Update execution status
            if execution_log['tasks_completed'] == execution_log['total_tasks']:
                execution_log['status'] = 'completed'
                workflow.status = WorkflowStatus.COMPLETED
                self.metrics['successful_executions'] += 1
                print(f"[AI Workflow] Workflow completed successfully: {workflow.name}")
            else:
                execution_log['status'] = 'failed'
                workflow.status = WorkflowStatus.FAILED
                self.metrics['failed_executions'] += 1
                print(f"[AI Workflow] Workflow failed: {workflow.name}")
            
        except Exception as e:
            execution_log['status'] = 'failed'
            execution_log['errors'].append({'general': str(e)})
            workflow.status = WorkflowStatus.FAILED
            self.metrics['failed_executions'] += 1
            print(f"[AI Workflow] Workflow execution error: {e}")
        
        finally:
            # Finalize execution
            end_time = time.time()
            execution_time = end_time - start_time
            
            execution_log['end_time'] = datetime.now().isoformat()
            execution_log['execution_time'] = execution_time
            
            # Update metrics
            self.metrics['average_execution_time'] = (
                (self.metrics['average_execution_time'] * 
                 (self.metrics['successful_executions'] + self.metrics['failed_executions'] - 1) + 
                 execution_time) / 
                (self.metrics['successful_executions'] + self.metrics['failed_executions'])
            )
            self.metrics['last_execution'] = datetime.now().isoformat()
            
            # Store execution history
            if workflow_id not in self.workflow_history:
                self.workflow_history[workflow_id] = []
            self.workflow_history[workflow_id].append(execution_log)
            
            # Clean up active executions
            if execution_id in self.active_executions:
                del self.active_executions[execution_id]
            
            workflow.updated_at = datetime.now().isoformat()
            self._save_workflows()
        
        return execution_log
    
    def _execute_task(self, task: WorkflowTask) -> Dict[str, Any]:
        """Execute an individual task"""
        print(f"[AI Workflow] Executing task: {task.name} ({task.task_type.value})")
        
        try:
            # Simulate task execution based on type
            if task.task_type == TaskType.TEXT_GENERATION:
                return self._execute_text_generation_task(task)
            elif task.task_type == TaskType.IMAGE_ANALYSIS:
                return self._execute_image_analysis_task(task)
            elif task.task_type == TaskType.DATA_PROCESSING:
                return self._execute_data_processing_task(task)
            elif task.task_type == TaskType.MODEL_TRAINING:
                return self._execute_model_training_task(task)
            elif task.task_type == TaskType.QUALITY_ASSURANCE:
                return self._execute_quality_assurance_task(task)
            else:
                return self._execute_custom_task(task)
                
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _execute_text_generation_task(self, task: WorkflowTask) -> Dict[str, Any]:
        """Execute text generation task"""
        # Simulate text generation
        time.sleep(1)  # Simulate processing time
        return {
            'status': 'success',
            'result': f"Generated text for task: {task.name}",
            'parameters_used': task.parameters
        }
    
    def _execute_image_analysis_task(self, task: WorkflowTask) -> Dict[str, Any]:
        """Execute image analysis task"""
        # Simulate image analysis
        time.sleep(2)  # Simulate processing time
        return {
            'status': 'success',
            'result': f"Analyzed images for task: {task.name}",
            'parameters_used': task.parameters
        }
    
    def _execute_data_processing_task(self, task: WorkflowTask) -> Dict[str, Any]:
        """Execute data processing task"""
        # Simulate data processing
        time.sleep(1.5)  # Simulate processing time
        return {
            'status': 'success',
            'result': f"Processed data for task: {task.name}",
            'parameters_used': task.parameters
        }
    
    def _execute_model_training_task(self, task: WorkflowTask) -> Dict[str, Any]:
        """Execute model training task"""
        # Simulate model training
        time.sleep(3)  # Simulate processing time
        return {
            'status': 'success',
            'result': f"Trained model for task: {task.name}",
            'parameters_used': task.parameters
        }
    
    def _execute_quality_assurance_task(self, task: WorkflowTask) -> Dict[str, Any]:
        """Execute quality assurance task"""
        # Simulate QA process
        time.sleep(1)  # Simulate processing time
        return {
            'status': 'success',
            'result': f"Quality check completed for task: {task.name}",
            'parameters_used': task.parameters
        }
    
    def _execute_custom_task(self, task: WorkflowTask) -> Dict[str, Any]:
        """Execute custom task"""
        # Simulate custom task execution
        time.sleep(1)  # Simulate processing time
        return {
            'status': 'success',
            'result': f"Custom task completed: {task.name}",
            'parameters_used': task.parameters
        }
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get workflow status and execution history"""
        if workflow_id not in self.workflows:
            return {'error': 'Workflow not found'}
        
        workflow = self.workflows[workflow_id]
        history = self.workflow_history.get(workflow_id, [])
        
        return {
            'workflow': workflow.to_dict(),
            'execution_history': history,
            'metrics': {
                'total_executions': len(history),
                'successful_executions': sum(1 for h in history if h['status'] == 'completed'),
                'failed_executions': sum(1 for h in history if h['status'] == 'failed'),
                'average_execution_time': sum(h.get('execution_time', 0) for h in history) / len(history) if history else 0
            }
        }
    
    def list_workflows(self, status_filter: Optional[WorkflowStatus] = None) -> List[Dict]:
        """List all workflows, optionally filtered by status"""
        workflows = []
        
        for workflow in self.workflows.values():
            if status_filter is None or workflow.status == status_filter:
                workflows.append(workflow.to_dict())
        
        return workflows
    
    def delete_workflow(self, workflow_id: str) -> bool:
        """Delete a workflow"""
        if workflow_id in self.workflows:
            del self.workflows[workflow_id]
            if workflow_id in self.workflow_history:
                del self.workflow_history[workflow_id]
            self._save_workflows()
            print(f"[AI Workflow] Deleted workflow: {workflow_id}")
            return True
        return False
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system-wide workflow metrics"""
        active_workflows = len([w for w in self.workflows.values() if w.status == WorkflowStatus.ACTIVE])
        running_workflows = len(self.active_executions)
        
        return {
            **self.metrics,
            'active_workflows': active_workflows,
            'running_workflows': running_workflows,
            'total_workflow_history': sum(len(history) for history in self.workflow_history.values())
        }
    
    def _save_workflows(self):
        """Save workflows to configuration file"""
        workflow_file = self.config_dir / "workflows.json"
        
        data = {
            'workflows': [workflow.to_dict() for workflow in self.workflows.values()],
            'metrics': self.metrics,
            'last_saved': datetime.now().isoformat()
        }
        
        try:
            with open(workflow_file, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"[AI Workflow] Saved {len(self.workflows)} workflows")
        except Exception as e:
            print(f"[AI Workflow] Error saving workflows: {e}")

# Global workflow manager instance
workflow_manager = None

def get_workflow_manager() -> AIWorkflowManager:
    """Get or create global workflow manager instance"""
    global workflow_manager
    if workflow_manager is None:
        workflow_manager = AIWorkflowManager()
    return workflow_manager

def main():
    """Main function for testing"""
    manager = get_workflow_manager()
    
    # Demo execution
    workflows = manager.list_workflows(WorkflowStatus.ACTIVE)
    if workflows:
        print(f"\nExecuting workflow: {workflows[0]['name']}")
        result = manager.execute_workflow(workflows[0]['id'])
        print(f"Execution result: {result['status']}")
        print(f"Tasks completed: {result['tasks_completed']}/{result['total_tasks']}")
    
    # Show metrics
    metrics = manager.get_system_metrics()
    print(f"\nSystem Metrics:")
    print(f"Total workflows: {metrics['total_workflows']}")
    print(f"Active workflows: {metrics['active_workflows']}")
    print(f"Successful executions: {metrics['successful_executions']}")

if __name__ == "__main__":
    main()