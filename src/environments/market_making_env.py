"""
Market Making Gymnasium Environment

A custom Gym environment for training RL agents to provide liquidity.

Observation Space:
    - Midprice, spread, inventory, volatility
    - Queue imbalance, position
    - Recent P&L, fills

Action Space:
    - Bid/ask offsets from midprice
    - Quote sizes
    - (Optionally) cancel existing orders

Reward Function:
    R = PnL - λ_I * inventory² - λ_V * volatility² - λ_Q * impact_cost
"""

import gymnasium as gym
from gymnasium import spaces
import numpy as np
from typing import Optional, Dict, Tuple, Any
from dataclasses import dataclass

from ..simulation.market_simulator import MarketSimulator, SimulationConfig
from ..simulation.order_book import OrderSide
from ..impact.impact_models import AlmgrenChrissImpact, ImpactTracker, AlmgrenChrissParameters


@dataclass
class MarketMakingConfig:
    """Configuration for market making environment."""
    # Episode parameters
    episode_duration: float = 100.0  # seconds
    time_step: float = 1.0  # seconds per step
    
    # Initial conditions
    initial_cash: float = 100000.0
    initial_inventory: int = 0
    
    # Action space bounds
    max_spread_offset_ticks: int = 10  # Max distance from mid in ticks
    min_quote_size: int = 10
    max_quote_size: int = 500
    
    # Reward parameters
    inventory_penalty_lambda: float = 0.01
    volatility_penalty_lambda: float = 0.001
    impact_penalty_lambda: float = 0.1
    
    # Risk limits
    max_inventory: int = 1000
    max_position_value: float = 50000.0
    
    # Simulation config
    simulation_config: Optional[SimulationConfig] = None
    
    # Impact model
    enable_impact: bool = True
    impact_decay_rate: float = 0.5


class MarketMakingEnv(gym.Env):
    """
    Gymnasium environment for market making with RL.
    
    An agent learns to quote bid/ask prices to maximize P&L while managing
    inventory risk, market impact, and adverse selection.
    """
    
    metadata = {'render_modes': ['human', 'rgb_array'], 'render_fps': 4}
    
    def __init__(
        self, 
        config: Optional[MarketMakingConfig] = None,
        render_mode: Optional[str] = None
    ):
        super().__init__()
        
        self.config = config or MarketMakingConfig()
        self.render_mode = render_mode
        
        # Initialize market simulator
        sim_config = self.config.simulation_config or SimulationConfig()
        self.simulator = MarketSimulator(sim_config)
        
        # Market maker ID
        self.mm_id = "rl_agent"
        self.simulator.register_market_maker(self.mm_id, self.config.initial_cash)
        
        # Impact tracking
        if self.config.enable_impact:
            impact_model = AlmgrenChrissImpact(AlmgrenChrissParameters())
            self.impact_tracker = ImpactTracker(
                impact_model, 
                decay_rate=self.config.impact_decay_rate
            )
        else:
            self.impact_tracker = None
        
        # Episode tracking
        self.current_step = 0
        self.max_steps = int(self.config.episode_duration / self.config.time_step)
        self.episode_pnl = []
        self.episode_inventory = []
        
        # Define observation space
        # [midprice, spread, inventory, volatility, imbalance, 
        #  queue_bid_pos, queue_ask_pos, recent_pnl, num_fills]
        self.observation_space = spaces.Box(
            low=np.array([0, 0, -self.config.max_inventory, 0, -1, 0, 0, -np.inf, 0]),
            high=np.array([np.inf, np.inf, self.config.max_inventory, np.inf, 1, 1, 1, np.inf, np.inf]),
            dtype=np.float32
        )
        
        # Define action space
        # [bid_offset_ticks, ask_offset_ticks, bid_size, ask_size]
        self.action_space = spaces.Box(
            low=np.array([0, 0, self.config.min_quote_size, self.config.min_quote_size]),
            high=np.array([
                self.config.max_spread_offset_ticks,
                self.config.max_spread_offset_ticks,
                self.config.max_quote_size,
                self.config.max_quote_size
            ]),
            dtype=np.float32
        )
        
        # Active orders
        self.active_bid_id = None
        self.active_ask_id = None
        
        # Previous state for reward calculation
        self.prev_pnl = 0.0
        self.prev_inventory = 0
    
    def reset(
        self, 
        seed: Optional[int] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Reset the environment to initial state."""
        super().reset(seed=seed)
        
        # Reset simulator
        self.simulator.reset()
        self.simulator.register_market_maker(self.mm_id, self.config.initial_cash)
        
        # Reset tracking
        self.current_step = 0
        self.episode_pnl = []
        self.episode_inventory = []
        self.active_bid_id = None
        self.active_ask_id = None
        self.prev_pnl = 0.0
        self.prev_inventory = 0
        
        if self.impact_tracker:
            self.impact_tracker.reset()
        
        # Get initial observation
        obs = self._get_observation()
        info = self._get_info()
        
        return obs, info
    
    def step(self, action: np.ndarray) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        """
        Execute one time step.
        
        Args:
            action: [bid_offset_ticks, ask_offset_ticks, bid_size, ask_size]
        
        Returns:
            (observation, reward, terminated, truncated, info)
        """
        # Parse action
        bid_offset_ticks, ask_offset_ticks, bid_size, ask_size = action
        
        # Cancel existing orders
        if self.active_bid_id is not None:
            self.simulator.cancel_mm_order(self.mm_id, self.active_bid_id)
            self.active_bid_id = None
        
        if self.active_ask_id is not None:
            self.simulator.cancel_mm_order(self.mm_id, self.active_ask_id)
            self.active_ask_id = None
        
        # Get current market state
        market_state = self.simulator.get_market_state()
        midprice = market_state.midprice
        tick_size = self.simulator.lob.tick_size
        
        # Place new orders
        bid_price = midprice - (bid_offset_ticks * tick_size)
        ask_price = midprice + (ask_offset_ticks * tick_size)
        
        bid_size = int(np.clip(bid_size, self.config.min_quote_size, self.config.max_quote_size))
        ask_size = int(np.clip(ask_size, self.config.min_quote_size, self.config.max_quote_size))
        
        # Submit orders
        self.active_bid_id = self.simulator.submit_mm_order(
            self.mm_id, OrderSide.BUY, bid_price, bid_size
        )
        self.active_ask_id = self.simulator.submit_mm_order(
            self.mm_id, OrderSide.SELL, ask_price, ask_size
        )
        
        # Simulate market for one time step
        fills = self.simulator.step(self.config.time_step)
        
        # Track impact if enabled
        if self.impact_tracker:
            for fill in fills:
                # Check if our MM was involved
                if (fill.passive_order_id == self.active_bid_id or 
                    fill.passive_order_id == self.active_ask_id):
                    # Our order was filled
                    volume = fill.size if fill.side == OrderSide.BUY else -fill.size
                    self.impact_tracker.add_trade(
                        timestamp=self.simulator.current_time,
                        volume=volume,
                        midprice=fill.price
                    )
        
        # Calculate reward
        reward = self._calculate_reward()
        
        # Update tracking
        self.current_step += 1
        mm_state = self.simulator.get_mm_state(self.mm_id)
        self.episode_pnl.append(mm_state['pnl'])
        self.episode_inventory.append(mm_state['inventory'])
        
        # Check termination conditions
        terminated = self._check_termination()
        truncated = self.current_step >= self.max_steps
        
        # Get new observation
        obs = self._get_observation()
        info = self._get_info()
        
        return obs, reward, terminated, truncated, info
    
    def _get_observation(self) -> np.ndarray:
        """Construct observation vector."""
        market_state = self.simulator.get_market_state()
        mm_state = self.simulator.get_mm_state(self.mm_id)
        
        # Get queue positions (normalized)
        bid_queue_pos = 0.0
        ask_queue_pos = 0.0
        
        if self.active_bid_id:
            queue_info = self.simulator.lob.get_queue_position(self.active_bid_id)
            if queue_info:
                position, total = queue_info
                bid_queue_pos = position / max(total, 1)
        
        if self.active_ask_id:
            queue_info = self.simulator.lob.get_queue_position(self.active_ask_id)
            if queue_info:
                position, total = queue_info
                ask_queue_pos = position / max(total, 1)
        
        # Recent P&L change
        current_pnl = mm_state['pnl']
        recent_pnl = current_pnl - self.prev_pnl
        
        # Count fills in this step
        num_fills = len([oid for oid in mm_state.get('order_ids', []) 
                        if oid not in [self.active_bid_id, self.active_ask_id]])
        
        obs = np.array([
            market_state.midprice,
            market_state.spread,
            mm_state['inventory'],
            market_state.volatility,
            market_state.imbalance,
            bid_queue_pos,
            ask_queue_pos,
            recent_pnl,
            num_fills
        ], dtype=np.float32)
        
        return obs
    
    def _calculate_reward(self) -> float:
        """
        Calculate reward for the current step.
        
        Reward = ΔP&L - λ_I * inventory² - λ_V * σ² - λ_Q * impact_cost
        """
        mm_state = self.simulator.get_mm_state(self.mm_id)
        market_state = self.simulator.get_market_state()
        
        # P&L change
        current_pnl = mm_state['pnl']
        pnl_change = current_pnl - self.prev_pnl
        
        # Inventory penalty (quadratic)
        inventory = mm_state['inventory']
        inventory_penalty = self.config.inventory_penalty_lambda * (inventory ** 2)
        
        # Volatility penalty (risk aversion)
        volatility_penalty = (self.config.volatility_penalty_lambda * 
                            (market_state.volatility ** 2))
        
        # Impact cost penalty
        impact_penalty = 0.0
        if self.impact_tracker:
            total_impact = self.impact_tracker.get_total_impact(
                self.simulator.current_time
            )
            impact_penalty = self.config.impact_penalty_lambda * abs(total_impact)
        
        # Total reward
        reward = pnl_change - inventory_penalty - volatility_penalty - impact_penalty
        
        # Update previous state
        self.prev_pnl = current_pnl
        self.prev_inventory = inventory
        
        return reward
    
    def _check_termination(self) -> bool:
        """Check if episode should terminate early."""
        mm_state = self.simulator.get_mm_state(self.mm_id)
        
        # Check inventory limits
        if abs(mm_state['inventory']) > self.config.max_inventory:
            return True
        
        # Check position value limits
        market_state = self.simulator.get_market_state()
        position_value = abs(mm_state['inventory'] * market_state.midprice)
        if position_value > self.config.max_position_value:
            return True
        
        # Check if insolvent
        if mm_state['pnl'] < -self.config.initial_cash * 0.5:  # Lost 50% of capital
            return True
        
        return False
    
    def _get_info(self) -> Dict[str, Any]:
        """Get additional info for logging."""
        mm_state = self.simulator.get_mm_state(self.mm_id)
        market_state = self.simulator.get_market_state()
        
        info = {
            'step': self.current_step,
            'time': self.simulator.current_time,
            'pnl': mm_state['pnl'],
            'inventory': mm_state['inventory'],
            'midprice': market_state.midprice,
            'spread': market_state.spread,
            'volatility': market_state.volatility,
            'imbalance': market_state.imbalance,
            'num_trades': market_state.num_trades,
            'total_volume': market_state.total_volume
        }
        
        if self.impact_tracker:
            info['total_impact'] = self.impact_tracker.get_total_impact(
                self.simulator.current_time
            )
        
        return info
    
    def render(self):
        """Render the environment (optional)."""
        if self.render_mode == "human":
            market_state = self.simulator.get_market_state()
            mm_state = self.simulator.get_mm_state(self.mm_id)
            
            print(f"\n=== Step {self.current_step} ===")
            print(f"Time: {self.simulator.current_time:.2f}s")
            print(f"Midprice: {market_state.midprice:.2f}")
            print(f"Spread: {market_state.spread:.4f}")
            print(f"Inventory: {mm_state['inventory']}")
            print(f"P&L: ${mm_state['pnl']:.2f}")
            print(f"Volatility: {market_state.volatility:.4f}")
    
    def close(self):
        """Clean up resources."""
        pass
