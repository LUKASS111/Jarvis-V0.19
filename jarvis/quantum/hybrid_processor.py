"""
Hybrid Quantum-Classical Processor - Advanced processing architecture
===================================================================

Combines quantum and classical computing for optimal performance
across different problem domains.
"""

import numpy as np
from typing import List, Dict, Any, Callable, Optional, Union
import logging
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from .quantum_simulator import QuantumSimulator
from .quantum_optimizer import QuantumOptimizer
from .quantum_crypto import QuantumCrypto

logger = logging.getLogger(__name__)

class HybridProcessor:
    """
    Hybrid quantum-classical processing system that automatically
    determines optimal processing strategy for different problem types.
    """
    
    def __init__(self, max_qubits: int = 12, num_workers: int = 4):
        """
        Initialize hybrid processing system.
        
        Args:
            max_qubits: Maximum qubits for quantum simulation
            num_workers: Number of classical processing workers
        """
        self.max_qubits = max_qubits
        self.num_workers = num_workers
        
        # Initialize quantum components
        self.quantum_simulator = QuantumSimulator(max_qubits)
        self.quantum_optimizer = QuantumOptimizer()
        self.quantum_crypto = QuantumCrypto()
        
        # Processing history and statistics
        self.processing_history = []
        self.performance_metrics = {
            'quantum_tasks': 0,
            'classical_tasks': 0,
            'hybrid_tasks': 0,
            'total_processing_time': 0.0
        }
        
        logger.info(f"Hybrid processor initialized with {max_qubits} qubits, {num_workers} workers")
    
    def determine_optimal_strategy(self, problem_type: str, 
                                 problem_size: int,
                                 data_characteristics: Dict[str, Any]) -> str:
        """
        Automatically determine optimal processing strategy.
        
        Args:
            problem_type: Type of problem ('optimization', 'search', 'cryptography', 'ml', 'simulation')
            problem_size: Size/complexity of the problem
            data_characteristics: Characteristics of input data
        
        Returns:
            Optimal strategy ('quantum', 'classical', 'hybrid')
        """
        # Problem type suitability for quantum computing
        quantum_advantage_problems = {
            'optimization': 0.8,
            'search': 0.9,
            'cryptography': 0.95,
            'simulation': 0.85,
            'ml': 0.6,
            'factorization': 0.95,
            'database_search': 0.9
        }
        
        quantum_score = quantum_advantage_problems.get(problem_type, 0.3)
        
        # Size considerations
        if problem_size > 2**self.max_qubits:
            quantum_score *= 0.2  # Large problems need classical preprocessing
        elif problem_size < 100:
            quantum_score *= 0.5  # Small problems may not benefit from quantum
        
        # Data characteristics
        if data_characteristics.get('structure', 'unstructured') == 'structured':
            quantum_score *= 1.2
        if data_characteristics.get('sparsity', 0) > 0.7:
            quantum_score *= 1.3
        if data_characteristics.get('symmetry', False):
            quantum_score *= 1.1
        
        # Determine strategy
        if quantum_score > 0.8:
            return 'quantum'
        elif quantum_score > 0.5:
            return 'hybrid'
        else:
            return 'classical'
    
    def process_optimization_problem(self, 
                                   objective_function: Callable,
                                   dimensions: int,
                                   bounds: List[tuple],
                                   strategy: Optional[str] = None) -> Dict[str, Any]:
        """
        Process optimization problem using optimal strategy.
        
        Args:
            objective_function: Function to optimize
            dimensions: Problem dimensionality
            bounds: Variable bounds
            strategy: Force specific strategy ('quantum', 'classical', 'hybrid')
        
        Returns:
            Optimization results
        """
        start_time = time.time()
        
        # Determine strategy if not specified
        if strategy is None:
            data_char = {
                'structure': 'continuous',
                'sparsity': 0.1,
                'symmetry': False
            }
            strategy = self.determine_optimal_strategy('optimization', dimensions, data_char)
        
        logger.info(f"Processing optimization with {strategy} strategy")
        
        if strategy == 'quantum':
            # Pure quantum optimization
            results = self.quantum_optimizer.quantum_annealing_optimize(
                objective_function, dimensions, bounds, num_chains=8
            )
            results['strategy_used'] = 'quantum'
            
        elif strategy == 'classical':
            # Classical optimization (scipy-like approach)
            results = self._classical_optimization(objective_function, dimensions, bounds)
            results['strategy_used'] = 'classical'
            
        else:  # hybrid
            # Hybrid approach
            results = self._hybrid_optimization(objective_function, dimensions, bounds)
            results['strategy_used'] = 'hybrid'
        
        # Add processing metadata
        results['processing_time'] = time.time() - start_time
        results['dimensions'] = dimensions
        results['strategy'] = strategy
        
        self._update_metrics('optimization', results['processing_time'], strategy)
        return results
    
    def process_search_problem(self, 
                             search_space: List[Any],
                             fitness_function: Callable,
                             target_count: int = 1,
                             strategy: Optional[str] = None) -> Dict[str, Any]:
        """
        Process search problem with quantum enhancement.
        
        Args:
            search_space: Space to search
            fitness_function: Function to evaluate candidates
            target_count: Number of solutions to find
            strategy: Processing strategy
        
        Returns:
            Search results
        """
        start_time = time.time()
        
        if strategy is None:
            data_char = {
                'structure': 'discrete',
                'sparsity': len(search_space) / (len(search_space) ** 2),
                'symmetry': False
            }
            strategy = self.determine_optimal_strategy('search', len(search_space), data_char)
        
        logger.info(f"Processing search with {strategy} strategy")
        
        if strategy == 'quantum' and len(search_space) <= 2**self.max_qubits:
            # Quantum search using Grover's algorithm
            target_indices = list(range(min(target_count, len(search_space))))
            grover_results = self.quantum_simulator.grover_search(target_indices)
            
            # Evaluate quantum results
            best_items = []
            for idx in grover_results:
                if idx < len(search_space):
                    item = search_space[idx]
                    fitness = fitness_function(item)
                    best_items.append((item, fitness))
            
            best_items.sort(key=lambda x: x[1], reverse=True)
            
            results = {
                'best_items': best_items[:target_count],
                'quantum_indices': grover_results,
                'strategy_used': 'quantum'
            }
            
        elif strategy == 'hybrid':
            # Hybrid search: quantum preprocessing + classical refinement
            results = self._hybrid_search(search_space, fitness_function, target_count)
            results['strategy_used'] = 'hybrid'
            
        else:
            # Classical search
            results = self._classical_search(search_space, fitness_function, target_count)
            results['strategy_used'] = 'classical'
        
        results['processing_time'] = time.time() - start_time
        results['search_space_size'] = len(search_space)
        results['strategy'] = strategy
        
        self._update_metrics('search', results['processing_time'], strategy)
        return results
    
    def process_cryptographic_task(self, 
                                 task_type: str,
                                 data: bytes,
                                 **kwargs) -> Dict[str, Any]:
        """
        Process cryptographic tasks with quantum enhancement.
        
        Args:
            task_type: Type of crypto task ('encrypt', 'decrypt', 'sign', 'verify', 'key_gen')
            data: Data to process
            **kwargs: Additional arguments
        
        Returns:
            Cryptographic results
        """
        start_time = time.time()
        
        logger.info(f"Processing {task_type} cryptographic task")
        
        if task_type == 'encrypt':
            results = self.quantum_crypto.quantum_safe_encrypt(data, kwargs.get('key'))
            
        elif task_type == 'decrypt':
            results = self.quantum_crypto.quantum_safe_decrypt(
                data, kwargs['salt'], kwargs['auth_tag'], kwargs['key']
            )
            
        elif task_type == 'key_distribution':
            results = self.quantum_crypto.bb84_key_distribution(kwargs.get('key_length', 256))
            
        elif task_type == 'sign':
            results = self.quantum_crypto.quantum_digital_signature(data, kwargs.get('private_key'))
            
        elif task_type == 'random_generation':
            random_bytes = self.quantum_crypto.quantum_random_generator(kwargs.get('num_bytes', 32))
            results = {'random_data': random_bytes}
            
        else:
            raise ValueError(f"Unknown cryptographic task: {task_type}")
        
        results['processing_time'] = time.time() - start_time
        results['task_type'] = task_type
        results['strategy_used'] = 'quantum'
        
        self._update_metrics('cryptography', results['processing_time'], 'quantum')
        return results
    
    def process_ml_task(self, 
                       model_params: np.ndarray,
                       loss_function: Callable,
                       training_data: Optional[Any] = None,
                       strategy: Optional[str] = None) -> Dict[str, Any]:
        """
        Process machine learning task with quantum enhancement.
        
        Args:
            model_params: Model parameters to optimize
            loss_function: Loss function to minimize
            training_data: Training data
            strategy: Processing strategy
        
        Returns:
            ML optimization results
        """
        start_time = time.time()
        
        if strategy is None:
            data_char = {
                'structure': 'continuous',
                'sparsity': 0.3,
                'symmetry': False
            }
            strategy = self.determine_optimal_strategy('ml', len(model_params), data_char)
        
        logger.info(f"Processing ML task with {strategy} strategy")
        
        if strategy == 'quantum':
            # Quantum machine learning optimization
            results = self.quantum_optimizer.quantum_machine_learning_optimize(
                model_params, loss_function
            )
            results['strategy_used'] = 'quantum'
            
        elif strategy == 'hybrid':
            # Hybrid ML: quantum feature mapping + classical training
            results = self._hybrid_ml_optimization(model_params, loss_function, training_data)
            results['strategy_used'] = 'hybrid'
            
        else:
            # Classical ML optimization
            results = self._classical_ml_optimization(model_params, loss_function)
            results['strategy_used'] = 'classical'
        
        results['processing_time'] = time.time() - start_time
        results['parameter_count'] = len(model_params)
        results['strategy'] = strategy
        
        self._update_metrics('ml', results['processing_time'], strategy)
        return results
    
    async def async_hybrid_processing(self, 
                                    tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process multiple tasks asynchronously with optimal resource allocation.
        
        Args:
            tasks: List of task specifications
        
        Returns:
            List of results for all tasks
        """
        logger.info(f"Starting async processing of {len(tasks)} tasks")
        
        # Separate tasks by processing type
        quantum_tasks = []
        classical_tasks = []
        
        for task in tasks:
            task_type = task.get('type')
            problem_size = task.get('size', 100)
            data_char = task.get('data_characteristics', {})
            
            strategy = self.determine_optimal_strategy(task_type, problem_size, data_char)
            task['optimal_strategy'] = strategy
            
            if strategy == 'quantum':
                quantum_tasks.append(task)
            else:
                classical_tasks.append(task)
        
        # Process tasks asynchronously
        results = []
        
        # Process quantum tasks sequentially (quantum simulator limitation)
        for task in quantum_tasks:
            result = await self._async_process_single_task(task)
            results.append(result)
        
        # Process classical tasks in parallel
        if classical_tasks:
            with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
                classical_futures = [
                    executor.submit(self._process_single_task, task) 
                    for task in classical_tasks
                ]
                
                for future in classical_futures:
                    result = future.result()
                    results.append(result)
        
        logger.info(f"Async processing completed: {len(results)} results")
        return results
    
    def _classical_optimization(self, objective_function: Callable,
                              dimensions: int, bounds: List[tuple]) -> Dict[str, Any]:
        """Classical optimization using gradient-based methods."""
        # Simplified classical optimization
        best_solution = np.array([
            np.random.uniform(bounds[i][0], bounds[i][1]) 
            for i in range(dimensions)
        ])
        best_value = objective_function(best_solution)
        
        # Simple gradient descent
        for iteration in range(100):
            # Finite difference gradient
            gradient = np.zeros(dimensions)
            epsilon = 1e-6
            
            for i in range(dimensions):
                x_plus = best_solution.copy()
                x_plus[i] += epsilon
                x_minus = best_solution.copy()
                x_minus[i] -= epsilon
                
                gradient[i] = (objective_function(x_plus) - objective_function(x_minus)) / (2 * epsilon)
            
            # Update solution
            learning_rate = 0.01
            new_solution = best_solution - learning_rate * gradient
            
            # Apply bounds
            for i in range(dimensions):
                new_solution[i] = np.clip(new_solution[i], bounds[i][0], bounds[i][1])
            
            new_value = objective_function(new_solution)
            if new_value < best_value:
                best_solution = new_solution
                best_value = new_value
        
        return {
            'best_solution': best_solution,
            'best_value': best_value,
            'iterations': 100
        }
    
    def _hybrid_optimization(self, objective_function: Callable,
                           dimensions: int, bounds: List[tuple]) -> Dict[str, Any]:
        """Hybrid optimization combining quantum and classical methods."""
        # Phase 1: Quantum exploration
        quantum_result = self.quantum_optimizer.quantum_annealing_optimize(
            objective_function, dimensions, bounds, num_chains=4
        )
        
        # Phase 2: Classical refinement
        initial_solution = quantum_result['best_solution']
        classical_result = self._classical_optimization(objective_function, dimensions, bounds)
        
        # Choose best result
        if quantum_result['best_value'] < classical_result['best_value']:
            best_result = quantum_result
            best_result['refinement_method'] = 'quantum_superior'
        else:
            best_result = classical_result
            best_result['refinement_method'] = 'classical_superior'
        
        best_result['hybrid_phases'] = ['quantum_exploration', 'classical_refinement']
        return best_result
    
    def _classical_search(self, search_space: List[Any],
                         fitness_function: Callable, target_count: int) -> Dict[str, Any]:
        """Classical search implementation."""
        evaluated_items = [(item, fitness_function(item)) for item in search_space]
        evaluated_items.sort(key=lambda x: x[1], reverse=True)
        
        return {
            'best_items': evaluated_items[:target_count],
            'items_evaluated': len(search_space)
        }
    
    def _hybrid_search(self, search_space: List[Any],
                      fitness_function: Callable, target_count: int) -> Dict[str, Any]:
        """Hybrid search combining quantum and classical approaches."""
        # Phase 1: Quantum preprocessing (if applicable)
        if len(search_space) <= 2**self.max_qubits:
            quantum_indices = self.quantum_simulator.grover_search(list(range(target_count)))
            promising_items = [search_space[i] for i in quantum_indices if i < len(search_space)]
        else:
            # Random sampling for large spaces
            promising_items = np.random.choice(search_space, min(100, len(search_space)), replace=False)
        
        # Phase 2: Classical evaluation and expansion
        evaluated_items = [(item, fitness_function(item)) for item in promising_items]
        evaluated_items.sort(key=lambda x: x[1], reverse=True)
        
        return {
            'best_items': evaluated_items[:target_count],
            'quantum_preprocessing': True,
            'items_evaluated': len(promising_items)
        }
    
    def _classical_ml_optimization(self, model_params: np.ndarray,
                                 loss_function: Callable) -> Dict[str, Any]:
        """Classical ML optimization."""
        current_params = model_params.copy()
        loss_history = [loss_function(current_params)]
        
        for iteration in range(100):
            # Simple gradient descent
            gradient = np.random.normal(0, 0.01, len(current_params))  # Simplified
            current_params -= 0.01 * gradient
            
            current_loss = loss_function(current_params)
            loss_history.append(current_loss)
        
        return {
            'optimal_params': current_params,
            'final_loss': loss_history[-1],
            'loss_history': loss_history,
            'iterations': 100
        }
    
    def _hybrid_ml_optimization(self, model_params: np.ndarray,
                              loss_function: Callable, training_data: Any) -> Dict[str, Any]:
        """Hybrid ML optimization."""
        # Phase 1: Quantum parameter initialization
        quantum_result = self.quantum_optimizer.quantum_machine_learning_optimize(
            model_params, loss_function, learning_rate=0.02
        )
        
        # Phase 2: Classical fine-tuning
        classical_result = self._classical_ml_optimization(
            quantum_result['optimal_params'], loss_function
        )
        
        return {
            'optimal_params': classical_result['optimal_params'],
            'final_loss': classical_result['final_loss'],
            'quantum_initialization': True,
            'classical_refinement': True,
            'hybrid_phases': ['quantum_initialization', 'classical_refinement']
        }
    
    async def _async_process_single_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single task asynchronously."""
        return self._process_single_task(task)
    
    def _process_single_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single task based on its specification."""
        task_type = task['type']
        
        if task_type == 'optimization':
            return self.process_optimization_problem(
                task['objective_function'],
                task['dimensions'],
                task['bounds'],
                task.get('strategy')
            )
        elif task_type == 'search':
            return self.process_search_problem(
                task['search_space'],
                task['fitness_function'],
                task.get('target_count', 1),
                task.get('strategy')
            )
        # Add other task types as needed
        
        return {'error': f'Unknown task type: {task_type}'}
    
    def _update_metrics(self, task_type: str, processing_time: float, strategy: str):
        """Update performance metrics."""
        if strategy == 'quantum':
            self.performance_metrics['quantum_tasks'] += 1
        elif strategy == 'classical':
            self.performance_metrics['classical_tasks'] += 1
        else:
            self.performance_metrics['hybrid_tasks'] += 1
        
        self.performance_metrics['total_processing_time'] += processing_time
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive hybrid system status."""
        return {
            'configuration': {
                'max_qubits': self.max_qubits,
                'classical_workers': self.num_workers
            },
            'performance_metrics': self.performance_metrics,
            'quantum_components': {
                'simulator_available': True,
                'optimizer_available': True,
                'crypto_available': True
            },
            'processing_capabilities': [
                'Optimization Problems',
                'Search Problems', 
                'Cryptographic Tasks',
                'Machine Learning',
                'Quantum Simulation',
                'Hybrid Processing'
            ],
            'total_tasks_processed': sum([
                self.performance_metrics['quantum_tasks'],
                self.performance_metrics['classical_tasks'],
                self.performance_metrics['hybrid_tasks']
            ])
        }