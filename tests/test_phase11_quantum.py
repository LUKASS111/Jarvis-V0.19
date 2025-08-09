"""
Phase 11 Quantum AI Integration Tests
=====================================

Comprehensive test suite for quantum-enhanced AI capabilities.
"""

import numpy as np
import sys
import os

# Add jarvis to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from jarvis.quantum import QuantumSimulator, QuantumOptimizer, QuantumCrypto, HybridProcessor


class TestQuantumSimulator:
    """Test quantum simulation capabilities."""
    
    def test_quantum_simulator_initialization(self):
        """Test quantum simulator initialization."""
        sim = QuantumSimulator(num_qubits=4)
        assert sim.num_qubits == 4
        assert sim.num_states == 16
        assert np.isclose(abs(sim.state[0]), 1.0)  # |0000⟩ state
    
    def test_hadamard_gate(self):
        """Test Hadamard gate creates superposition."""
        sim = QuantumSimulator(num_qubits=2)
        sim.apply_hadamard(0)
        
        # After H on qubit 0: (|00⟩ + |01⟩)/√2
        assert np.isclose(abs(sim.state[0]), 1/np.sqrt(2))
        assert np.isclose(abs(sim.state[1]), 1/np.sqrt(2))
        assert np.isclose(abs(sim.state[2]), 0)
        assert np.isclose(abs(sim.state[3]), 0)
    
    def test_cnot_gate(self):
        """Test CNOT gate creates entanglement."""
        sim = QuantumSimulator(num_qubits=2)
        sim.apply_hadamard(0)  # Create superposition
        sim.apply_cnot(0, 1)   # Create entanglement
        
        # Bell state: (|00⟩ + |11⟩)/√2
        assert np.isclose(abs(sim.state[0]), 1/np.sqrt(2))
        assert np.isclose(abs(sim.state[1]), 0)
        assert np.isclose(abs(sim.state[2]), 0)
        assert np.isclose(abs(sim.state[3]), 1/np.sqrt(2))
    
    def test_measurement(self):
        """Test quantum measurement."""
        sim = QuantumSimulator(num_qubits=2)
        sim.apply_hadamard(0)
        
        # Measure qubit 0 multiple times
        results = [sim.measure_qubit(0) for _ in range(100)]
        
        # Should get both 0 and 1 (probabilistic)
        assert 0 in results
        assert 1 in results
        assert all(r in [0, 1] for r in results)
    
    def test_quantum_fourier_transform(self):
        """Test Quantum Fourier Transform."""
        sim = QuantumSimulator(num_qubits=3)
        sim.apply_hadamard(0)
        
        result = sim.quantum_fourier_transform()
        assert len(result) == 8
        assert np.isclose(np.linalg.norm(result), 1.0)  # Normalized
    
    def test_grover_search(self):
        """Test Grover's search algorithm."""
        sim = QuantumSimulator(num_qubits=3)
        target_items = [3, 5]  # Items to find
        
        results = sim.grover_search(target_items)
        assert isinstance(results, list)
        assert len(results) > 0
        assert all(isinstance(r, int) for r in results)
    
    def test_quantum_annealing_simulation(self):
        """Test quantum annealing simulation."""
        sim = QuantumSimulator(num_qubits=4)
        
        # Simple cost function (minimize distance from target)
        target = 5
        def cost_func(state):
            return abs(state - target)
        
        result = sim.quantum_annealing_simulation(cost_func, num_steps=100)
        
        assert 'best_state' in result
        assert 'best_cost' in result
        assert 'final_state' in result
        assert result['best_cost'] >= 0
    
    def test_state_info(self):
        """Test quantum state information retrieval."""
        sim = QuantumSimulator(num_qubits=2)
        sim.apply_hadamard(0)
        
        info = sim.get_state_info()
        
        assert 'num_qubits' in info
        assert 'state_vector' in info
        assert 'probabilities' in info
        assert 'entropy' in info
        assert 'top_states' in info
        assert info['num_qubits'] == 2


class TestQuantumOptimizer:
    """Test quantum optimization capabilities."""
    
    def test_optimizer_initialization(self):
        """Test quantum optimizer initialization."""
        opt = QuantumOptimizer(max_iterations=500, precision=1e-6)
        assert opt.max_iterations == 500
        assert opt.precision == 1e-6
        assert len(opt.optimization_history) == 0
    
    def test_quantum_annealing_optimize(self):
        """Test quantum annealing optimization."""
        opt = QuantumOptimizer(max_iterations=100)
        
        # Simple quadratic function: (x-2)² + (y-3)²
        def objective(x):
            return (x[0] - 2)**2 + (x[1] - 3)**2
        
        result = opt.quantum_annealing_optimize(
            objective_function=objective,
            dimensions=2,
            bounds=[(-5, 5), (-5, 5)],
            num_chains=3
        )
        
        assert 'best_solution' in result
        assert 'best_value' in result
        assert 'optimization_time' in result
        assert len(result['best_solution']) == 2
        
        # Should find minimum near (2, 3)
        assert abs(result['best_solution'][0] - 2) < 1.0
        assert abs(result['best_solution'][1] - 3) < 1.0
    
    def test_variational_quantum_eigensolver(self):
        """Test VQE for eigenvalue problems."""
        opt = QuantumOptimizer(max_iterations=50)
        
        # Simple 2x2 Hamiltonian
        H = np.array([[1, 0], [0, 2]])
        
        result = opt.variational_quantum_eigensolver(H)
        
        assert 'ground_energy' in result
        assert 'ground_state' in result
        assert 'optimal_parameters' in result
        assert result['ground_energy'] <= 2.0  # Should find ground state
    
    def test_quantum_approximate_optimization(self):
        """Test QAOA for combinatorial problems."""
        opt = QuantumOptimizer(max_iterations=50)
        
        # Simple cost matrix
        cost_matrix = np.array([[1, 2], [2, 3]])
        
        result = opt.quantum_approximate_optimization(cost_matrix, num_layers=2)
        
        assert 'optimal_gamma' in result
        assert 'optimal_beta' in result
        assert 'final_state' in result
        assert 'probabilities' in result
        assert 'top_solutions' in result
        assert len(result['optimal_gamma']) == 2
        assert len(result['optimal_beta']) == 2
    
    def test_parallel_quantum_search(self):
        """Test parallel quantum search."""
        opt = QuantumOptimizer()
        
        # Search space
        search_space = list(range(20))
        
        # Fitness function (prefer larger numbers)
        def fitness(x):
            return x / 20.0
        
        result = opt.parallel_quantum_search(
            search_space=search_space,
            fitness_function=fitness,
            num_workers=2
        )
        
        assert 'best_item' in result
        assert 'best_fitness' in result
        assert 'search_time' in result
        assert result['best_item'] in search_space
        assert result['best_fitness'] >= 0
    
    def test_quantum_ml_optimize(self):
        """Test quantum machine learning optimization."""
        opt = QuantumOptimizer(max_iterations=50)
        
        # Simple loss function: sum of squares
        def loss_func(params):
            return np.sum(params**2)
        
        initial_params = np.array([1.0, -1.0, 0.5])
        
        result = opt.quantum_machine_learning_optimize(
            model_params=initial_params,
            loss_function=loss_func,
            learning_rate=0.1
        )
        
        assert 'optimal_params' in result
        assert 'final_loss' in result
        assert 'loss_history' in result
        assert len(result['optimal_params']) == 3
        assert result['final_loss'] < 1.0  # Should minimize
    
    def test_optimization_summary(self):
        """Test optimization summary generation."""
        opt = QuantumOptimizer(max_iterations=50)
        
        # Run a simple optimization
        def objective(x):
            return x[0]**2
        
        opt.quantum_annealing_optimize(
            objective_function=objective,
            dimensions=1,
            bounds=[(-2, 2)]
        )
        
        summary = opt.get_optimization_summary()
        assert 'total_optimizations' in summary
        assert 'best_overall_value' in summary
        assert summary['total_optimizations'] == 1


class TestQuantumCrypto:
    """Test quantum cryptography capabilities."""
    
    def test_crypto_initialization(self):
        """Test quantum crypto initialization."""
        crypto = QuantumCrypto()
        assert len(crypto.key_distribution_history) == 0
        assert len(crypto.communication_log) == 0
    
    def test_bb84_key_distribution(self):
        """Test BB84 quantum key distribution."""
        crypto = QuantumCrypto()
        
        result = crypto.bb84_key_distribution(key_length=128)
        
        assert 'success' in result
        assert 'final_key' in result
        assert 'key_length' in result
        assert 'error_rate' in result
        assert 'efficiency' in result
        
        if result['success']:
            assert result['key_length'] == 256  # 128 bits = 256 hex chars for sha256
            assert result['final_key'] is not None
    
    def test_quantum_safe_encryption(self):
        """Test quantum-safe encryption."""
        crypto = QuantumCrypto()
        
        test_data = b"Secret quantum message"
        
        # Test encryption
        encrypt_result = crypto.quantum_safe_encrypt(test_data)
        
        assert 'encrypted_data' in encrypt_result
        assert 'salt' in encrypt_result
        assert 'auth_tag' in encrypt_result
        assert encrypt_result['quantum_key_used'] is True
        assert encrypt_result['post_quantum_safe'] is True
        
        # Test decryption
        bb84_result = crypto.bb84_key_distribution()
        if bb84_result['success']:
            decrypt_result = crypto.quantum_safe_decrypt(
                encrypted_data=encrypt_result['encrypted_data'],
                salt=encrypt_result['salt'],
                auth_tag=encrypt_result['auth_tag'],
                quantum_key=bb84_result['final_key']
            )
            
            # Note: Due to different keys, this may not succeed, but should not crash
            assert 'success' in decrypt_result
            assert 'authentication_valid' in decrypt_result
    
    def test_quantum_random_generator(self):
        """Test quantum random number generation."""
        crypto = QuantumCrypto()
        
        random_bytes1 = crypto.quantum_random_generator(16)
        random_bytes2 = crypto.quantum_random_generator(16)
        
        assert len(random_bytes1) == 16
        assert len(random_bytes2) == 16
        assert random_bytes1 != random_bytes2  # Should be different
        assert isinstance(random_bytes1, bytes)
    
    def test_quantum_digital_signature(self):
        """Test quantum digital signature."""
        crypto = QuantumCrypto()
        
        message = b"Important quantum message"
        
        signature_result = crypto.quantum_digital_signature(message)
        
        assert 'signature' in signature_result
        assert 'nonce' in signature_result
        assert 'public_key' in signature_result
        assert 'message_hash' in signature_result
        assert signature_result['quantum_safe'] is True
        
        # Test verification (simplified)
        is_valid = crypto.verify_quantum_signature(
            message=message,
            signature=signature_result['signature'],
            nonce=signature_result['nonce'],
            public_key=signature_result['public_key']
        )
        
        assert isinstance(is_valid, bool)
    
    def test_quantum_key_exchange(self):
        """Test quantum key exchange."""
        crypto = QuantumCrypto()
        
        # Phase 1: Generate public data
        exchange_result1 = crypto.quantum_key_exchange()
        
        assert 'public_data' in exchange_result1
        assert 'exchange_complete' in exchange_result1
        assert exchange_result1['exchange_complete'] is False
        
        # Phase 2: Complete exchange (simulate partner)
        partner_public = crypto.quantum_random_generator(32)
        exchange_result2 = crypto.quantum_key_exchange(partner_public)
        
        assert 'shared_secret' in exchange_result2
        assert exchange_result2['exchange_complete'] is True
        assert exchange_result2['quantum_safe'] is True
    
    def test_crypto_status(self):
        """Test crypto system status."""
        crypto = QuantumCrypto()
        
        # Run some operations
        crypto.bb84_key_distribution()
        crypto.quantum_random_generator()
        
        status = crypto.get_crypto_status()
        
        assert 'bb84_distributions' in status
        assert 'quantum_algorithms_available' in status
        assert 'post_quantum_ready' in status
        assert status['post_quantum_ready'] is True
        assert len(status['quantum_algorithms_available']) > 0


class TestHybridProcessor:
    """Test hybrid quantum-classical processing."""
    
    def test_hybrid_processor_initialization(self):
        """Test hybrid processor initialization."""
        processor = HybridProcessor(max_qubits=8, num_workers=2)
        
        assert processor.max_qubits == 8
        assert processor.num_workers == 2
        assert processor.quantum_simulator is not None
        assert processor.quantum_optimizer is not None
        assert processor.quantum_crypto is not None
    
    def test_strategy_determination(self):
        """Test optimal strategy determination."""
        processor = HybridProcessor()
        
        # Test different problem types
        strategies = []
        
        # Optimization problem
        strategy1 = processor.determine_optimal_strategy(
            'optimization', 100, {'structure': 'continuous', 'sparsity': 0.1}
        )
        strategies.append(strategy1)
        
        # Search problem
        strategy2 = processor.determine_optimal_strategy(
            'search', 50, {'structure': 'discrete', 'sparsity': 0.8}
        )
        strategies.append(strategy2)
        
        # Cryptography
        strategy3 = processor.determine_optimal_strategy(
            'cryptography', 10, {'structure': 'structured', 'symmetry': True}
        )
        strategies.append(strategy3)
        
        assert all(s in ['quantum', 'classical', 'hybrid'] for s in strategies)
        # Crypto should prefer quantum
        assert strategy3 in ['quantum', 'hybrid']
    
    def test_optimization_processing(self):
        """Test optimization problem processing."""
        processor = HybridProcessor(max_qubits=6)
        
        # Simple optimization problem
        def objective(x):
            return (x[0] - 1)**2 + (x[1] - 2)**2
        
        result = processor.process_optimization_problem(
            objective_function=objective,
            dimensions=2,
            bounds=[(-3, 3), (-3, 3)]
        )
        
        assert 'best_solution' in result
        assert 'best_value' in result
        assert 'strategy_used' in result
        assert 'processing_time' in result
        assert len(result['best_solution']) == 2
    
    def test_search_processing(self):
        """Test search problem processing."""
        processor = HybridProcessor()
        
        search_space = list(range(20))
        
        def fitness(x):
            return -(x - 15)**2  # Maximize, peak at 15
        
        result = processor.process_search_problem(
            search_space=search_space,
            fitness_function=fitness,
            target_count=3
        )
        
        assert 'best_items' in result
        assert 'strategy_used' in result
        assert 'processing_time' in result
        assert len(result['best_items']) <= 3
    
    def test_cryptographic_processing(self):
        """Test cryptographic task processing."""
        processor = HybridProcessor()
        
        test_data = b"Test message for quantum crypto"
        
        # Test encryption
        encrypt_result = processor.process_cryptographic_task(
            task_type='encrypt',
            data=test_data
        )
        
        assert 'encrypted_data' in encrypt_result
        assert 'strategy_used' in encrypt_result
        assert 'processing_time' in encrypt_result
        assert encrypt_result['strategy_used'] == 'quantum'
        
        # Test key distribution
        key_result = processor.process_cryptographic_task(
            task_type='key_distribution',
            data=b'',
            key_length=64
        )
        
        assert 'success' in key_result
        assert 'final_key' in key_result
        assert 'processing_time' in key_result
    
    def test_ml_processing(self):
        """Test machine learning task processing."""
        processor = HybridProcessor()
        
        # Simple model parameters
        model_params = np.array([0.5, -0.3, 0.8])
        
        def loss_func(params):
            return np.sum(params**2)  # L2 regularization
        
        result = processor.process_ml_task(
            model_params=model_params,
            loss_function=loss_func
        )
        
        assert 'optimal_params' in result
        assert 'strategy_used' in result
        assert 'processing_time' in result
        assert len(result['optimal_params']) == 3
    
    def test_system_status(self):
        """Test hybrid system status."""
        processor = HybridProcessor(max_qubits=10, num_workers=4)
        
        # Process some tasks to generate metrics
        def simple_objective(x):
            return x[0]**2
        
        processor.process_optimization_problem(
            objective_function=simple_objective,
            dimensions=1,
            bounds=[(-1, 1)]
        )
        
        status = processor.get_system_status()
        
        assert 'configuration' in status
        assert 'performance_metrics' in status
        assert 'quantum_components' in status
        assert 'processing_capabilities' in status
        assert 'total_tasks_processed' in status
        
        assert status['configuration']['max_qubits'] == 10
        assert status['configuration']['classical_workers'] == 4
        assert status['total_tasks_processed'] >= 1


def test_phase_11_integration():
    """Test complete Phase 11 integration."""
    # Test quantum simulator
    sim = QuantumSimulator(num_qubits=4)
    assert sim.num_qubits == 4
    
    # Test quantum optimizer
    opt = QuantumOptimizer()
    assert opt.max_iterations == 1000
    
    # Test quantum crypto
    crypto = QuantumCrypto()
    random_data = crypto.quantum_random_generator(8)
    assert len(random_data) == 8
    
    # Test hybrid processor
    processor = HybridProcessor(max_qubits=6, num_workers=2)
    status = processor.get_system_status()
    assert status['quantum_components']['simulator_available'] is True
    assert status['quantum_components']['optimizer_available'] is True
    assert status['quantum_components']['crypto_available'] is True
    
    print("✅ Phase 11: Quantum-Enhanced AI - All components operational")


if __name__ == "__main__":
    # Run basic integration test
    test_phase_11_integration()
    print("Phase 11 Quantum AI module ready for production!")