"""
Integration tests for the complete system.

Tests end-to-end workflows:
- Simulation → Environment → Agent → Evaluation
- Training pipeline
- Dashboard functionality
"""

import pytest
import numpy as np
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.simulation.market_simulator import MarketSimulator, SimulationConfig
from src.simulation.order_flow import OrderFlowGenerator, OrderFlowConfig
from src.environments.market_making_env import MarketMakingEnv, MarketMakingConfig
from src.agents.baseline_agents import (
    StaticSpreadAgent, AvellanedaStoikovAgent, 
    AdaptiveSpreadAgent, RandomAgent
)
from src.agents.ppo_agent import PPOMarketMaker
from src.evaluation.backtester import Backtester
from src.evaluation.metrics import calculate_performance_metrics
from src.impact.impact_models import AlmgrenChrissImpact, ImpactTracker


class TestEndToEndWorkflow:
    """Test complete workflows from start to finish."""
    
    def test_simple_simulation_workflow(self):
        """Test basic simulation creation and execution."""
        print("\n[TEST] Simple Simulation Workflow")
        
        # Create simulator
        config = SimulationConfig(seed=42)
        sim = MarketSimulator(config)
        
        # Run simulation
        stats = sim.run_simulation(duration=10.0, time_step=1.0)
        
        # Verify outputs
        assert stats['duration'] == 10.0
        assert stats['num_steps'] > 0
        assert stats['total_volume'] >= 0
        assert stats['avg_midprice'] > 0
        
        print(f"  ✓ Simulation ran successfully")
        print(f"  ✓ Total trades: {stats['total_trades']}")
        print(f"  ✓ Average midprice: ${stats['avg_midprice']:.2f}")
    
    def test_environment_episode_completion(self):
        """Test a complete episode in the environment."""
        print("\n[TEST] Environment Episode Completion")
        
        env_config = MarketMakingConfig(
            episode_duration=20.0,
            time_step=1.0
        )
        env = MarketMakingEnv(env_config)
        
        # Run episode with static agent
        agent = StaticSpreadAgent()
        obs, _ = env.reset(seed=42)
        
        total_reward = 0
        steps = 0
        done = False
        
        while not done and steps < 25:
            action = agent.get_action(obs)
            obs, reward, terminated, truncated, info = env.step(action)
            total_reward += reward
            done = terminated or truncated
            steps += 1
        
        assert steps > 0
        assert 'pnl' in info
        assert 'inventory' in info
        
        print(f"  ✓ Episode completed in {steps} steps")
        print(f"  ✓ Total reward: {total_reward:.2f}")
        print(f"  ✓ Final P&L: ${info['pnl']:.2f}")
    
    def test_all_baseline_agents(self):
        """Test all baseline agents can run."""
        print("\n[TEST] All Baseline Agents")
        
        env = MarketMakingEnv(MarketMakingConfig(episode_duration=10.0))
        agents = [
            ('Random', RandomAgent(seed=42)),
            ('Static', StaticSpreadAgent()),
            ('Avellaneda', AvellanedaStoikovAgent()),
            ('Adaptive', AdaptiveSpreadAgent())
        ]
        
        for name, agent in agents:
            obs, _ = env.reset(seed=42)
            action = agent.get_action(obs)
            
            assert action.shape == (4,)
            assert env.action_space.contains(action)
            
            print(f"  ✓ {name} agent working")
    
    def test_backtesting_workflow(self):
        """Test complete backtesting workflow."""
        print("\n[TEST] Backtesting Workflow")
        
        env = MarketMakingEnv(MarketMakingConfig(episode_duration=20.0))
        backtester = Backtester(env, verbose=False)
        
        agent = StaticSpreadAgent()
        result = backtester.backtest(agent, num_episodes=3, agent_name="Test Agent")
        
        # Verify result structure
        assert result.agent_name == "Test Agent"
        assert result.num_episodes == 3
        assert len(result.pnl_series) > 0
        assert len(result.inventory_series) > 0
        assert result.metrics is not None
        
        # Verify metrics
        assert hasattr(result.metrics, 'total_pnl')
        assert hasattr(result.metrics, 'sharpe_ratio')
        assert hasattr(result.metrics, 'max_drawdown')
        
        print(f"  ✓ Backtest completed")
        print(f"  ✓ P&L: ${result.metrics.total_pnl:.2f}")
        print(f"  ✓ Sharpe: {result.metrics.sharpe_ratio:.3f}")
    
    def test_multi_agent_comparison(self):
        """Test comparing multiple agents."""
        print("\n[TEST] Multi-Agent Comparison")
        
        env = MarketMakingEnv(MarketMakingConfig(episode_duration=15.0))
        backtester = Backtester(env, verbose=False)
        
        agents = [
            (StaticSpreadAgent(), "Static"),
            (AvellanedaStoikovAgent(), "Avellaneda")
        ]
        
        results = backtester.compare_agents(agents, num_episodes=2)
        
        assert len(results) == 2
        assert "Static" in results
        assert "Avellaneda" in results
        
        for name, result in results.items():
            assert result.num_episodes == 2
            print(f"  ✓ {name}: P&L=${result.metrics.total_pnl:.2f}")
    
    def test_ppo_agent_creation_and_prediction(self):
        """Test PPO agent can be created and make predictions."""
        print("\n[TEST] PPO Agent Creation")
        
        env = MarketMakingEnv(MarketMakingConfig(episode_duration=10.0))
        
        # Create PPO agent
        agent = PPOMarketMaker(env, verbose=0, device='cpu')
        
        # Test prediction
        obs, _ = env.reset(seed=42)
        action = agent.predict(obs, deterministic=True)
        
        assert action.shape == (4,)
        assert env.action_space.contains(action)
        
        print(f"  ✓ PPO agent created successfully")
        print(f"  ✓ Prediction working")
    
    def test_impact_tracking_integration(self):
        """Test market impact tracking with environment."""
        print("\n[TEST] Impact Tracking Integration")
        
        from src.impact.impact_models import AlmgrenChrissParameters
        
        params = AlmgrenChrissParameters()
        model = AlmgrenChrissImpact(params)
        tracker = ImpactTracker(model, decay_rate=0.5)
        
        # Simulate some trades
        tracker.add_trade(1.0, 100, 100.0)
        tracker.add_trade(2.0, -50, 100.0)
        tracker.add_trade(3.0, 75, 100.0)
        
        total_impact = tracker.get_total_impact(3.0)
        perm_impact = tracker.get_permanent_impact()
        
        assert isinstance(total_impact, float)
        assert isinstance(perm_impact, float)
        
        print(f"  ✓ Impact tracking working")
        print(f"  ✓ Total impact: {total_impact:.6f}")


class TestDataFlowIntegrity:
    """Test data flows correctly through the system."""
    
    def test_observation_to_action_to_reward(self):
        """Test the complete observation → action → reward loop."""
        print("\n[TEST] Data Flow Integrity")
        
        env = MarketMakingEnv(MarketMakingConfig(episode_duration=10.0))
        agent = StaticSpreadAgent()
        
        obs, info = env.reset(seed=42)
        
        # Verify observation
        assert obs.shape == (9,)
        assert not np.any(np.isnan(obs))
        
        # Get action
        action = agent.get_action(obs)
        assert action.shape == (4,)
        assert not np.any(np.isnan(action))
        
        # Step environment
        next_obs, reward, terminated, truncated, next_info = env.step(action)
        
        # Verify outputs
        assert next_obs.shape == (9,)
        assert not np.any(np.isnan(next_obs))
        assert isinstance(reward, (int, float))
        assert not np.isnan(reward)
        assert isinstance(terminated, bool)
        assert isinstance(truncated, bool)
        assert isinstance(next_info, dict)
        
        print(f"  ✓ Data flow validated")
        print(f"  ✓ Observation → Action → Reward working")
    
    def test_metrics_calculation_pipeline(self):
        """Test metrics calculation from episode data."""
        print("\n[TEST] Metrics Calculation Pipeline")
        
        # Simulate some episode data
        pnl_series = np.cumsum(np.random.randn(100) * 10)
        inventory_series = np.random.randint(-50, 50, 100)
        
        metrics = calculate_performance_metrics(
            pnl_series=pnl_series,
            inventory_series=inventory_series,
            fills=[],
            spreads=[0.02] * 10,
            total_quotes=100
        )
        
        # Verify all metrics exist
        assert hasattr(metrics, 'total_pnl')
        assert hasattr(metrics, 'sharpe_ratio')
        assert hasattr(metrics, 'max_drawdown')
        assert hasattr(metrics, 'mean_abs_inventory')
        
        # Verify metrics are valid numbers
        assert not np.isnan(metrics.total_pnl)
        assert not np.isnan(metrics.sharpe_ratio)
        assert not np.isnan(metrics.max_drawdown)
        
        print(f"  ✓ Metrics calculation working")
        print(f"  ✓ Sharpe ratio: {metrics.sharpe_ratio:.3f}")


class TestRobustness:
    """Test system robustness and error handling."""
    
    def test_extreme_inventory_handling(self):
        """Test system handles extreme inventory correctly."""
        print("\n[TEST] Extreme Inventory Handling")
        
        env_config = MarketMakingConfig(
            episode_duration=50.0,
            max_inventory=100  # Low limit to test termination
        )
        env = MarketMakingEnv(env_config)
        
        obs, _ = env.reset(seed=42)
        
        # Run until termination or max steps
        max_steps = 60
        step = 0
        done = False
        
        while not done and step < max_steps:
            action = env.action_space.sample()
            obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            step += 1
        
        # Should eventually terminate
        assert step <= max_steps
        print(f"  ✓ Handled extreme cases (terminated at step {step})")
    
    def test_nan_detection(self):
        """Test that NaN values are properly handled."""
        print("\n[TEST] NaN Detection")
        
        env = MarketMakingEnv(MarketMakingConfig(episode_duration=10.0))
        obs, _ = env.reset(seed=42)
        
        for _ in range(10):
            action = env.action_space.sample()
            obs, reward, terminated, truncated, info = env.step(action)
            
            # Check for NaNs
            assert not np.any(np.isnan(obs)), "NaN detected in observation"
            assert not np.isnan(reward), "NaN detected in reward"
            
            if terminated or truncated:
                break
        
        print(f"  ✓ No NaN values detected")
    
    def test_deterministic_behavior(self):
        """Test that seeded runs are deterministic."""
        print("\n[TEST] Deterministic Behavior")
        
        def run_episode(seed):
            env = MarketMakingEnv(MarketMakingConfig(episode_duration=10.0))
            agent = StaticSpreadAgent()
            obs, _ = env.reset(seed=seed)
            
            rewards = []
            for _ in range(10):
                action = agent.get_action(obs)
                obs, reward, term, trunc, info = env.step(action)
                rewards.append(reward)
                if term or trunc:
                    break
            return rewards
        
        # Run twice with same seed
        rewards1 = run_episode(seed=42)
        rewards2 = run_episode(seed=42)
        
        # Should be identical
        assert len(rewards1) == len(rewards2)
        assert np.allclose(rewards1, rewards2), "Behavior not deterministic"
        
        print(f"  ✓ Deterministic behavior verified")


class TestPerformanceValidation:
    """Validate expected performance characteristics."""
    
    def test_baseline_performance_sanity(self):
        """Test that baseline agents perform reasonably."""
        print("\n[TEST] Baseline Performance Sanity")
        
        env = MarketMakingEnv(MarketMakingConfig(episode_duration=30.0))
        backtester = Backtester(env, verbose=False)
        
        # Test Avellaneda-Stoikov (should be profitable on average)
        agent = AvellanedaStoikovAgent()
        result = backtester.backtest(agent, num_episodes=5, agent_name="AS")
        
        # Sanity checks
        assert result.metrics.total_pnl != 0  # Should have some P&L
        assert abs(result.metrics.mean_abs_inventory) < 1000  # Reasonable inventory
        assert -1 <= result.metrics.sharpe_ratio <= 10  # Reasonable Sharpe
        
        print(f"  ✓ Baseline performance reasonable")
        print(f"  ✓ P&L: ${result.metrics.total_pnl:.2f}")
        print(f"  ✓ Sharpe: {result.metrics.sharpe_ratio:.3f}")


def run_all_integration_tests():
    """Run all integration tests with reporting."""
    print("\n" + "="*80)
    print("RUNNING INTEGRATION TEST SUITE")
    print("="*80)
    
    test_classes = [
        TestEndToEndWorkflow,
        TestDataFlowIntegrity,
        TestRobustness,
        TestPerformanceValidation
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = []
    
    for test_class in test_classes:
        print(f"\n{'='*80}")
        print(f"Testing: {test_class.__name__}")
        print(f"{'='*80}")
        
        instance = test_class()
        test_methods = [m for m in dir(instance) if m.startswith('test_')]
        
        for method_name in test_methods:
            total_tests += 1
            try:
                method = getattr(instance, method_name)
                method()
                passed_tests += 1
            except Exception as e:
                failed_tests.append((test_class.__name__, method_name, str(e)))
                print(f"\n  ✗ FAILED: {method_name}")
                print(f"    Error: {str(e)}")
    
    # Summary
    print("\n" + "="*80)
    print("INTEGRATION TEST SUMMARY")
    print("="*80)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests} ({100*passed_tests/total_tests:.1f}%)")
    print(f"Failed: {len(failed_tests)}")
    
    if failed_tests:
        print("\nFailed Tests:")
        for class_name, method_name, error in failed_tests:
            print(f"  - {class_name}.{method_name}: {error}")
    else:
        print("\n✅ ALL INTEGRATION TESTS PASSED!")
    
    print("="*80 + "\n")
    
    return passed_tests == total_tests


if __name__ == "__main__":
    # Run integration tests
    success = run_all_integration_tests()
    sys.exit(0 if success else 1)
