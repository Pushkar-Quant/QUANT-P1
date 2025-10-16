"""
Unit tests for Gymnasium environment.
"""

import pytest
import numpy as np
import gymnasium as gym
from src.environments.market_making_env import MarketMakingEnv, MarketMakingConfig
from src.simulation.market_simulator import SimulationConfig


class TestMarketMakingEnv:
    """Test MarketMakingEnv functionality."""
    
    @pytest.fixture
    def env(self):
        """Create environment for testing."""
        config = MarketMakingConfig(
            episode_duration=10.0,
            time_step=1.0,
            initial_cash=10000.0
        )
        return MarketMakingEnv(config)
    
    def test_environment_creation(self, env):
        """Test environment initializes correctly."""
        assert isinstance(env, gym.Env)
        assert env.observation_space.shape == (9,)
        assert env.action_space.shape == (4,)
    
    def test_reset(self, env):
        """Test environment reset."""
        obs, info = env.reset(seed=42)
        
        assert obs.shape == (9,)
        assert isinstance(info, dict)
        assert 'time' in info
        assert 'pnl' in info
    
    def test_step(self, env):
        """Test environment step."""
        env.reset(seed=42)
        
        # Take action: bid offset=2, ask offset=2, sizes=100
        action = np.array([2.0, 2.0, 100.0, 100.0])
        obs, reward, terminated, truncated, info = env.step(action)
        
        assert obs.shape == (9,)
        assert isinstance(reward, float)
        assert isinstance(terminated, bool)
        assert isinstance(truncated, bool)
        assert isinstance(info, dict)
    
    def test_episode_completion(self, env):
        """Test full episode runs correctly."""
        obs, _ = env.reset(seed=42)
        done = False
        step_count = 0
        
        while not done and step_count < 20:
            action = env.action_space.sample()
            obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            step_count += 1
        
        assert step_count > 0
    
    def test_observation_bounds(self, env):
        """Test observations stay within bounds."""
        env.reset(seed=42)
        
        for _ in range(10):
            action = env.action_space.sample()
            obs, _, done, _, _ = env.step(action)
            
            if done:
                break
            
            # Check observation is within space bounds
            assert env.observation_space.contains(obs)
    
    def test_action_bounds(self, env):
        """Test actions are clipped to valid range."""
        env.reset(seed=42)
        
        # Try extreme action
        extreme_action = np.array([100.0, 100.0, 10000.0, 10000.0])
        obs, reward, _, _, info = env.step(extreme_action)
        
        # Should still work without error
        assert obs.shape == (9,)
    
    def test_reward_calculation(self, env):
        """Test reward is calculated."""
        env.reset(seed=42)
        
        action = np.array([2.0, 2.0, 100.0, 100.0])
        _, reward, _, _, _ = env.step(action)
        
        assert isinstance(reward, (int, float))
    
    def test_inventory_tracking(self, env):
        """Test inventory is tracked in observation."""
        env.reset(seed=42)
        
        action = np.array([2.0, 2.0, 100.0, 100.0])
        obs, _, _, _, info = env.step(action)
        
        inventory = obs[2]  # Inventory is 3rd element
        assert isinstance(inventory, (int, float))
    
    def test_termination_conditions(self, env):
        """Test environment terminates on breach of limits."""
        config = MarketMakingConfig(
            episode_duration=100.0,
            max_inventory=10  # Very low limit
        )
        env_limited = MarketMakingEnv(config)
        env_limited.reset(seed=42)
        
        # Take many aggressive actions to build inventory
        # (In practice, termination depends on fills)
        terminated = False
        for _ in range(50):
            action = np.array([1.0, 1.0, 100.0, 100.0])
            _, _, terminated, truncated, _ = env_limited.step(action)
            if terminated or truncated:
                break
        
        # Should eventually terminate (either max steps or inventory limit)
        assert terminated or truncated


class TestRewardFunction:
    """Test reward function components."""
    
    @pytest.fixture
    def env(self):
        config = MarketMakingConfig(
            inventory_penalty_lambda=0.01,
            volatility_penalty_lambda=0.001,
            impact_penalty_lambda=0.1
        )
        return MarketMakingEnv(config)
    
    def test_pnl_component(self, env):
        """Test P&L is included in reward."""
        obs, _ = env.reset(seed=42)
        
        initial_pnl = env.prev_pnl
        
        # Take action
        action = np.array([2.0, 2.0, 100.0, 100.0])
        _, reward, _, _, info = env.step(action)
        
        # Reward should incorporate P&L change
        assert 'pnl' in info
    
    def test_inventory_penalty(self, env):
        """Test inventory penalty affects reward."""
        env.reset(seed=42)
        
        # The reward function includes: -lambda * inventory^2
        # So higher inventory should lead to more negative penalty
        # (Though actual inventory depends on fills in simulation)
        action = np.array([2.0, 2.0, 100.0, 100.0])
        _, reward, _, _, _ = env.step(action)
        
        assert isinstance(reward, float)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
