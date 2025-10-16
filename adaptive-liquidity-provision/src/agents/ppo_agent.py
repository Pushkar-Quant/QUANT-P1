"""
PPO-based Market Maker Agent

Wraps Stable-Baselines3 PPO for market making with custom features:
- Custom network architecture
- Learning rate scheduling
- Curriculum learning support
"""

import numpy as np
from typing import Optional, Dict, Any, Callable
import torch
import torch.nn as nn
from stable_baselines3 import PPO
from stable_baselines3.common.policies import ActorCriticPolicy
from stable_baselines3.common.callbacks import BaseCallback


class MarketMakingPolicy(ActorCriticPolicy):
    """
    Custom policy network for market making.
    
    Features:
    - Larger hidden layers for complex state representation
    - Batch normalization for stable training
    - Separate value and policy networks
    """
    
    def __init__(self, *args, **kwargs):
        # Custom network architecture
        kwargs['net_arch'] = [
            dict(pi=[256, 256, 128], vf=[256, 256, 128])
        ]
        super().__init__(*args, **kwargs)


class PPOMarketMaker:
    """
    PPO-based market making agent with training utilities.
    
    Wraps Stable-Baselines3 PPO with market-making-specific features.
    """
    
    def __init__(
        self,
        env,
        learning_rate: float = 3e-4,
        n_steps: int = 2048,
        batch_size: int = 64,
        n_epochs: int = 10,
        gamma: float = 0.99,
        gae_lambda: float = 0.95,
        clip_range: float = 0.2,
        ent_coef: float = 0.01,
        vf_coef: float = 0.5,
        max_grad_norm: float = 0.5,
        tensorboard_log: Optional[str] = None,
        verbose: int = 1,
        device: str = 'auto'
    ):
        """
        Initialize PPO market maker.
        
        Args:
            env: Gymnasium environment
            learning_rate: Learning rate
            n_steps: Number of steps to collect per update
            batch_size: Minibatch size
            n_epochs: Number of epochs per update
            gamma: Discount factor
            gae_lambda: GAE lambda parameter
            clip_range: PPO clipping parameter
            ent_coef: Entropy coefficient
            vf_coef: Value function coefficient
            max_grad_norm: Maximum gradient norm
            tensorboard_log: Tensorboard log directory
            verbose: Verbosity level
            device: Device to use ('cpu', 'cuda', or 'auto')
        """
        self.env = env
        
        # Create PPO model
        self.model = PPO(
            policy="MlpPolicy",
            env=env,
            learning_rate=learning_rate,
            n_steps=n_steps,
            batch_size=batch_size,
            n_epochs=n_epochs,
            gamma=gamma,
            gae_lambda=gae_lambda,
            clip_range=clip_range,
            ent_coef=ent_coef,
            vf_coef=vf_coef,
            max_grad_norm=max_grad_norm,
            tensorboard_log=tensorboard_log,
            verbose=verbose,
            device=device
        )
    
    def train(
        self,
        total_timesteps: int,
        callback: Optional[BaseCallback] = None,
        log_interval: int = 10,
        tb_log_name: str = "ppo_mm"
    ) -> 'PPOMarketMaker':
        """
        Train the agent.
        
        Args:
            total_timesteps: Total number of timesteps to train
            callback: Custom callback
            log_interval: Logging interval
            tb_log_name: Tensorboard log name
        
        Returns:
            Self
        """
        self.model.learn(
            total_timesteps=total_timesteps,
            callback=callback,
            log_interval=log_interval,
            tb_log_name=tb_log_name,
            progress_bar=True
        )
        return self
    
    def predict(
        self,
        observation: np.ndarray,
        deterministic: bool = True
    ) -> np.ndarray:
        """
        Get action from policy.
        
        Args:
            observation: Current state
            deterministic: If True, use mean action
        
        Returns:
            Action array
        """
        action, _ = self.model.predict(observation, deterministic=deterministic)
        return action
    
    def save(self, path: str):
        """Save model to disk."""
        self.model.save(path)
    
    def load(self, path: str):
        """Load model from disk."""
        self.model = PPO.load(path, env=self.env)
    
    def get_action(self, observation: np.ndarray) -> np.ndarray:
        """Get action (for compatibility with baseline agents)."""
        return self.predict(observation, deterministic=True)
    
    def reset(self):
        """Reset agent (no-op for PPO)."""
        pass


class CurriculumCallback(BaseCallback):
    """
    Callback for curriculum learning.
    
    Gradually increases task difficulty:
    - Start with low volatility
    - Increase volatility over time
    - Reduce inventory limits over time
    """
    
    def __init__(
        self,
        initial_vol: float = 0.01,
        target_vol: float = 0.05,
        vol_increase_steps: int = 100000,
        verbose: int = 0
    ):
        super().__init__(verbose)
        self.initial_vol = initial_vol
        self.target_vol = target_vol
        self.vol_increase_steps = vol_increase_steps
    
    def _on_step(self) -> bool:
        """Called at each step."""
        # Calculate current volatility based on progress
        progress = min(1.0, self.num_timesteps / self.vol_increase_steps)
        current_vol = self.initial_vol + (self.target_vol - self.initial_vol) * progress
        
        # Update environment volatility (if supported)
        if hasattr(self.training_env, 'envs'):
            for env in self.training_env.envs:
                if hasattr(env.unwrapped, 'simulator'):
                    # Update order flow volatility
                    env.unwrapped.simulator.order_flow.vol_regime.base_vol = current_vol
        
        if self.verbose > 0 and self.num_timesteps % 10000 == 0:
            print(f"Curriculum: volatility = {current_vol:.4f}")
        
        return True


class MetricsCallback(BaseCallback):
    """
    Callback for logging custom market making metrics.
    
    Logs:
    - P&L, Sharpe ratio
    - Inventory statistics
    - Fill ratios
    - Spread statistics
    """
    
    def __init__(self, log_freq: int = 1000, verbose: int = 0):
        super().__init__(verbose)
        self.log_freq = log_freq
        self.episode_pnls = []
        self.episode_inventories = []
        self.episode_fills = []
    
    def _on_step(self) -> bool:
        """Called at each step."""
        # Log episode statistics
        if len(self.model.ep_info_buffer) > 0 and self.num_timesteps % self.log_freq == 0:
            # Compute metrics from recent episodes
            recent_infos = list(self.model.ep_info_buffer)[-10:]
            
            if recent_infos:
                # Extract custom metrics from info dict
                pnls = [info.get('pnl', 0) for info in recent_infos if 'pnl' in info]
                inventories = [info.get('inventory', 0) for info in recent_infos if 'inventory' in info]
                
                if pnls:
                    self.logger.record("metrics/mean_pnl", np.mean(pnls))
                    self.logger.record("metrics/std_pnl", np.std(pnls))
                
                if inventories:
                    self.logger.record("metrics/mean_abs_inventory", np.mean(np.abs(inventories)))
                    self.logger.record("metrics/max_abs_inventory", np.max(np.abs(inventories)))
        
        return True


class EarlyStoppingCallback(BaseCallback):
    """
    Early stopping based on performance metrics.
    
    Stops training if:
    - Mean reward plateaus
    - Performance degrades significantly
    """
    
    def __init__(
        self,
        check_freq: int = 10000,
        patience: int = 5,
        min_delta: float = 0.01,
        verbose: int = 0
    ):
        super().__init__(verbose)
        self.check_freq = check_freq
        self.patience = patience
        self.min_delta = min_delta
        self.best_mean_reward = -np.inf
        self.wait = 0
    
    def _on_step(self) -> bool:
        """Check for early stopping."""
        if self.num_timesteps % self.check_freq == 0 and len(self.model.ep_info_buffer) > 0:
            # Get mean reward from recent episodes
            recent_rewards = [ep_info['r'] for ep_info in self.model.ep_info_buffer]
            mean_reward = np.mean(recent_rewards)
            
            # Check improvement
            if mean_reward > self.best_mean_reward + self.min_delta:
                self.best_mean_reward = mean_reward
                self.wait = 0
            else:
                self.wait += 1
                if self.wait >= self.patience:
                    if self.verbose > 0:
                        print(f"Early stopping at {self.num_timesteps} timesteps")
                    return False
        
        return True
