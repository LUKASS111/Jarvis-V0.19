"""
Professional Program Evolution Orchestrator for Jarvis V0.19
Master orchestrator that coordinates all evolution activities with comprehensive logging and reporting
"""

import time
import threading
import asyncio
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import json

from .program_evolution_tracker import get_evolution_tracker, EvolutionMetric, FunctionalityUpdate
from .enhanced_logging import get_enhanced_logger, get_all_loggers_report
from .functional_data_manager import get_functional_data_validator, get_functional_data_updater

class ProfessionalEvolutionOrchestrator:
    """Master orchestrator for professional program evolution"""
    
    def __init__(self):
        self.logger = get_enhanced_logger('evolution_orchestrator')
        self.evolution_tracker = get_evolution_tracker()
        self.data_validator = get_functional_data_validator()
        self.data_updater = get_functional_data_updater()
        
        # Current evolution state
        self.current_session_id: Optional[str] = None
        self.evolution_objectives: List[str] = []
        self.completed_objectives: List[str] = []
        
        # Performance tracking
        self.start_time = time.time()
        self.evolution_phases = {
            'initialization': {'completed': False, 'start_time': None, 'duration': 0},
            'validation': {'completed': False, 'start_time': None, 'duration': 0},
            'optimization': {'completed': False, 'start_time': None, 'duration': 0},
            'enhancement': {'completed': False, 'start_time': None, 'duration': 0},
            'validation_final': {'completed': False, 'start_time': None, 'duration': 0}
        }
        
        self.logger.info("Professional Evolution Orchestrator initialized")
    
    def start_evolution_cycle(self, objectives: List[str]) -> str:
        """Start a complete evolution cycle"""
        with self.logger.operation_context("start_evolution_cycle", objectives=objectives) as op_logger:
            self.evolution_objectives = objectives
            self.completed_objectives = []
            
            # Start evolution session
            self.current_session_id = self.evolution_tracker.start_evolution_session(objectives)
            
            op_logger.info(
                "Evolution cycle started",
                session_id=self.current_session_id,
                total_objectives=len(objectives)
            )
            
            return self.current_session_id
    
    def execute_phase_initialization(self) -> Dict[str, Any]:
        """Execute initialization phase"""
        phase_name = 'initialization'
        self.evolution_phases[phase_name]['start_time'] = time.time()
        
        with self.logger.operation_context(f"phase_{phase_name}") as op_logger:
            results = {
                'phase': phase_name,
                'success': True,
                'details': {},
                'metrics': {}
            }
            
            try:
                op_logger.info("Starting initialization phase")
                
                # 1. System health check
                op_logger.info("Performing system health check")
                
                # Import system health monitor
                try:
                    import sys
                    import os
                    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
                    from jarvis.monitoring.system_health import SystemHealthMonitor
                    
                    health_monitor = SystemHealthMonitor()
                    health_report = health_monitor.get_health_report()
                    
                    results['details']['system_health'] = {
                        'overall_score': health_report.overall_score,
                        'overall_status': health_report.overall_status,
                        'component_count': len(health_report.component_statuses)
                    }
                    
                    # Log system health metric
                    metric = EvolutionMetric(
                        timestamp=datetime.now().isoformat(),
                        metric_type='performance',
                        component='system_health',
                        value=health_report.overall_score,
                        baseline=90.0,
                        improvement=health_report.overall_score - 90.0,
                        validation_status='validated',
                        data_source='system_health_monitor',
                        notes=f"System health status: {health_report.overall_status}"
                    )
                    self.evolution_tracker.log_evolution_metric(metric)
                    
                except Exception as e:
                    op_logger.warning("System health check failed", error=str(e))
                    results['details']['system_health'] = {'error': str(e)}
                
                # 2. Validate current data integrity
                op_logger.info("Validating data integrity")
                validation_results = self.data_validator.validate_all_components()
                
                integrity_scores = {
                    comp: result.data_integrity_score 
                    for comp, result in validation_results.items()
                }
                
                avg_integrity = sum(integrity_scores.values()) / len(integrity_scores) if integrity_scores else 0
                
                results['details']['data_integrity'] = {
                    'components_validated': len(validation_results),
                    'average_integrity_score': avg_integrity,
                    'individual_scores': integrity_scores
                }
                
                # Log data integrity metrics
                for comp, result in validation_results.items():
                    metric = EvolutionMetric(
                        timestamp=datetime.now().isoformat(),
                        metric_type='quality',
                        component=f'data_{comp}',
                        value=result.data_integrity_score,
                        baseline=95.0,
                        improvement=result.data_integrity_score - 95.0,
                        validation_status='validated',
                        data_source='functional_data_validator',
                        notes=f"Issues found: {len(result.issues_found)}"
                    )
                    self.evolution_tracker.log_evolution_metric(metric)
                
                # 3. Run test suite for baseline
                op_logger.info("Running baseline test suite")
                
                try:
                    import subprocess
                    import os
                    
                    # Change to project root for test execution
                    project_root = os.path.join(os.path.dirname(__file__), '..', '..')
                    
                    # Run test suite
                    test_result = subprocess.run(
                        ['python', 'run_tests.py'],
                        cwd=project_root,
                        capture_output=True,
                        text=True,
                        timeout=600  # 10 minute timeout
                    )
                    
                    # Parse test results
                    if test_result.returncode == 0:
                        # Extract test statistics from output
                        output_lines = test_result.stdout.split('\n')
                        test_stats = {'total_tests': 0, 'passed_tests': 0, 'failed_tests': 0}
                        
                        for line in output_lines:
                            if 'Individual Tests:' in line and 'passed' in line:
                                # Extract test numbers
                                parts = line.split()
                                for i, part in enumerate(parts):
                                    if part.endswith('passed'):
                                        test_stats['passed_tests'] = int(parts[i-1].split('/')[0])
                                        test_stats['total_tests'] = int(parts[i-1].split('/')[1])
                                        test_stats['failed_tests'] = test_stats['total_tests'] - test_stats['passed_tests']
                                        break
                        
                        test_success_rate = (test_stats['passed_tests'] / test_stats['total_tests'] * 100) if test_stats['total_tests'] > 0 else 0
                        
                        results['details']['baseline_tests'] = {
                            'success': True,
                            'total_tests': test_stats['total_tests'],
                            'passed_tests': test_stats['passed_tests'],
                            'failed_tests': test_stats['failed_tests'],
                            'success_rate': test_success_rate
                        }
                        
                        # Log test success metric
                        metric = EvolutionMetric(
                            timestamp=datetime.now().isoformat(),
                            metric_type='quality',
                            component='test_suite',
                            value=test_success_rate,
                            baseline=100.0,
                            improvement=test_success_rate - 100.0,
                            validation_status='validated',
                            data_source='test_runner',
                            notes=f"Tests: {test_stats['passed_tests']}/{test_stats['total_tests']}"
                        )
                        self.evolution_tracker.log_evolution_metric(metric)
                        
                    else:
                        results['details']['baseline_tests'] = {
                            'success': False,
                            'error': test_result.stderr or 'Test execution failed'
                        }
                        results['success'] = False
                
                except Exception as e:
                    op_logger.warning("Baseline test execution failed", error=str(e))
                    results['details']['baseline_tests'] = {'error': str(e)}
                
                # Complete phase
                phase_end_time = time.time()
                phase_duration = phase_end_time - self.evolution_phases[phase_name]['start_time']
                
                self.evolution_phases[phase_name]['duration'] = phase_duration
                self.evolution_phases[phase_name]['completed'] = results['success']
                
                results['metrics']['duration_seconds'] = phase_duration
                
                # Complete objective
                objective = "System initialization and baseline validation"
                if objective in self.evolution_objectives:
                    self.evolution_tracker.complete_task(objective, results)
                    self.completed_objectives.append(objective)
                
                op_logger.info(
                    "Initialization phase completed",
                    success=results['success'],
                    duration_seconds=phase_duration
                )
                
                return results
                
            except Exception as e:
                op_logger.error("Initialization phase failed", error=str(e))
                results['success'] = False
                results['error'] = str(e)
                return results
    
    def execute_phase_optimization(self) -> Dict[str, Any]:
        """Execute optimization phase"""
        phase_name = 'optimization'
        self.evolution_phases[phase_name]['start_time'] = time.time()
        
        with self.logger.operation_context(f"phase_{phase_name}") as op_logger:
            results = {
                'phase': phase_name,
                'success': True,
                'details': {},
                'metrics': {}
            }
            
            try:
                op_logger.info("Starting optimization phase")
                
                # 1. Database optimization
                op_logger.info("Optimizing databases")
                
                # Find and optimize all databases
                data_root = Path(os.path.join(os.path.dirname(__file__), '..', '..', 'data'))
                optimized_dbs = []
                
                for db_file in data_root.glob('*.db'):
                    try:
                        optimization_result = self.data_updater.optimize_database(str(db_file))
                        optimized_dbs.append({
                            'database': db_file.name,
                            'success': optimization_result.success,
                            'performance_impact': optimization_result.performance_impact
                        })
                        
                        # Log optimization metric
                        if optimization_result.success:
                            size_reduction = optimization_result.performance_impact.get('size_reduction_percentage', 0)
                            metric = EvolutionMetric(
                                timestamp=datetime.now().isoformat(),
                                metric_type='performance',
                                component=f'database_{db_file.name}',
                                value=100 - size_reduction,  # Efficiency score
                                baseline=100.0,
                                improvement=-size_reduction,  # Size reduction is improvement
                                validation_status='validated',
                                data_source='database_optimizer',
                                notes=f"Size reduced by {size_reduction:.1f}%"
                            )
                            self.evolution_tracker.log_evolution_metric(metric)
                        
                    except Exception as e:
                        op_logger.warning(f"Database optimization failed for {db_file.name}", error=str(e))
                        optimized_dbs.append({
                            'database': db_file.name,
                            'success': False,
                            'error': str(e)
                        })
                
                results['details']['database_optimization'] = {
                    'databases_processed': len(optimized_dbs),
                    'results': optimized_dbs
                }
                
                # 2. Memory optimization
                op_logger.info("Performing memory optimization")
                
                try:
                    import gc
                    import psutil
                    
                    # Get memory usage before
                    memory_before = psutil.Process().memory_info().rss / 1024 / 1024  # MB
                    
                    # Force garbage collection
                    collected = gc.collect()
                    
                    # Get memory usage after
                    memory_after = psutil.Process().memory_info().rss / 1024 / 1024  # MB
                    memory_freed = memory_before - memory_after
                    
                    results['details']['memory_optimization'] = {
                        'success': True,
                        'memory_before_mb': memory_before,
                        'memory_after_mb': memory_after,
                        'memory_freed_mb': memory_freed,
                        'objects_collected': collected
                    }
                    
                    # Log memory optimization metric
                    efficiency_improvement = (memory_freed / memory_before * 100) if memory_before > 0 else 0
                    metric = EvolutionMetric(
                        timestamp=datetime.now().isoformat(),
                        metric_type='performance',
                        component='memory_usage',
                        value=100 - (memory_after / memory_before * 100) if memory_before > 0 else 100,
                        baseline=100.0,
                        improvement=efficiency_improvement,
                        validation_status='validated',
                        data_source='memory_optimizer',
                        notes=f"Freed {memory_freed:.1f}MB, collected {collected} objects"
                    )
                    self.evolution_tracker.log_evolution_metric(metric)
                    
                except Exception as e:
                    op_logger.warning("Memory optimization failed", error=str(e))
                    results['details']['memory_optimization'] = {'error': str(e)}
                
                # Complete phase
                phase_end_time = time.time()
                phase_duration = phase_end_time - self.evolution_phases[phase_name]['start_time']
                
                self.evolution_phases[phase_name]['duration'] = phase_duration
                self.evolution_phases[phase_name]['completed'] = results['success']
                
                results['metrics']['duration_seconds'] = phase_duration
                
                # Complete objective
                objective = "System optimization and performance enhancement"
                if objective in self.evolution_objectives:
                    self.evolution_tracker.complete_task(objective, results)
                    self.completed_objectives.append(objective)
                
                op_logger.info(
                    "Optimization phase completed",
                    success=results['success'],
                    duration_seconds=phase_duration
                )
                
                return results
                
            except Exception as e:
                op_logger.error("Optimization phase failed", error=str(e))
                results['success'] = False
                results['error'] = str(e)
                return results
    
    def execute_full_evolution_cycle(self, objectives: List[str] = None) -> Dict[str, Any]:
        """Execute a complete evolution cycle"""
        if objectives is None:
            objectives = [
                "System initialization and baseline validation",
                "Enhanced logging system implementation",
                "Functional data validation and updates", 
                "System optimization and performance enhancement",
                "Professional evolution procedures establishment"
            ]
        
        # Start evolution cycle
        session_id = self.start_evolution_cycle(objectives)
        
        with self.logger.operation_context("full_evolution_cycle", session_id=session_id) as op_logger:
            cycle_results = {
                'session_id': session_id,
                'start_time': datetime.now().isoformat(),
                'objectives': objectives,
                'phase_results': {},
                'overall_success': True,
                'summary': {}
            }
            
            try:
                # Phase 1: Initialization
                op_logger.info("Executing initialization phase")
                init_results = self.execute_phase_initialization()
                cycle_results['phase_results']['initialization'] = init_results
                
                if not init_results['success']:
                    cycle_results['overall_success'] = False
                
                # Phase 2: Optimization
                op_logger.info("Executing optimization phase")
                opt_results = self.execute_phase_optimization()
                cycle_results['phase_results']['optimization'] = opt_results
                
                if not opt_results['success']:
                    cycle_results['overall_success'] = False
                
                # Final validation
                op_logger.info("Performing final validation")
                final_validation = self.data_validator.validate_all_components()
                
                final_scores = {
                    comp: result.data_integrity_score 
                    for comp, result in final_validation.items()
                }
                
                final_avg_score = sum(final_scores.values()) / len(final_scores) if final_scores else 0
                
                cycle_results['phase_results']['final_validation'] = {
                    'success': all(result.is_valid for result in final_validation.values()),
                    'average_integrity_score': final_avg_score,
                    'component_scores': final_scores
                }
                
                # Generate comprehensive summary
                total_duration = sum(
                    phase['duration'] for phase in self.evolution_phases.values()
                    if phase['completed']
                )
                
                completed_phases = sum(1 for phase in self.evolution_phases.values() if phase['completed'])
                total_phases = len(self.evolution_phases)
                
                cycle_results['summary'] = {
                    'total_duration_seconds': total_duration,
                    'completed_phases': completed_phases,
                    'total_phases': total_phases,
                    'phase_completion_rate': (completed_phases / total_phases * 100),
                    'objectives_completed': len(self.completed_objectives),
                    'total_objectives': len(objectives),
                    'objective_completion_rate': (len(self.completed_objectives) / len(objectives) * 100),
                    'final_integrity_score': final_avg_score
                }
                
                # Complete evolution session
                next_priorities = [
                    "RAG system implementation",
                    "Multi-modal AI integration", 
                    "Advanced agent orchestration",
                    "Enhanced user interfaces"
                ]
                
                session_summary = self.evolution_tracker.end_evolution_session(next_priorities)
                cycle_results['session_summary'] = session_summary
                
                # Generate final report
                logging_report = get_all_loggers_report()
                validation_summary = self.data_validator.get_validation_summary()
                evolution_report = self.evolution_tracker.get_evolution_report()
                
                cycle_results['comprehensive_report'] = {
                    'logging_activity': logging_report,
                    'data_validation': validation_summary,
                    'evolution_tracking': evolution_report
                }
                
                op_logger.info(
                    "Evolution cycle completed",
                    overall_success=cycle_results['overall_success'],
                    session_id=session_id,
                    total_duration=total_duration,
                    final_score=final_avg_score
                )
                
                return cycle_results
                
            except Exception as e:
                op_logger.error("Evolution cycle failed", error=str(e))
                cycle_results['overall_success'] = False
                cycle_results['error'] = str(e)
                
                # End session with error
                if self.current_session_id:
                    self.evolution_tracker.end_evolution_session(['Error recovery', 'System stabilization'])
                
                return cycle_results
    
    def get_evolution_status(self) -> Dict[str, Any]:
        """Get current evolution status"""
        return {
            'current_session_id': self.current_session_id,
            'objectives': self.evolution_objectives,
            'completed_objectives': self.completed_objectives,
            'progress_percentage': (len(self.completed_objectives) / len(self.evolution_objectives) * 100) if self.evolution_objectives else 0,
            'phases': self.evolution_phases,
            'running_time_seconds': time.time() - self.start_time,
            'active': self.current_session_id is not None
        }

# Global instance
_orchestrator = None

def get_evolution_orchestrator() -> ProfessionalEvolutionOrchestrator:
    """Get global evolution orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = ProfessionalEvolutionOrchestrator()
    return _orchestrator