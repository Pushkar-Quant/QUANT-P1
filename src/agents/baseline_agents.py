"""
Baseline Market Making Agents

Implements simple market making strategies for benchmarking:
- Random: Random quote placement
- Static Spread: Fixed spread around midprice
- Avellaneda-Stoikov: Optimal market making with inventory control
"""

import numpy as np
from abc import ABC, abstractmethod
from typing import Tuple
from dataclasses import dataclass


class BaseAgent(ABC):
    """Abstract base class for market making agents."""
    
    @abstractmethod
    def get_action(self, observation: np.ndarray) -> np.ndarray:
        """
        Get action given observation.
        
        Args:
            observation: Current state observation
        
        Returns:
            Action array [bid_offset_ticks, ask_offset_ticks, bid_size, ask_size]
        """
        pass
    
    @abstractmethod
    def reset(self):
        """Reset agent state."""
        pass


class RandomAgent(BaseAgent):
    """
    Random market maker that places quotes randomly.
    
    Useful as a baseline to ensure learning is happening.
    """
    
    def __init__(
        self, 
        max_spread_offset: int = 10,
        min_size: int = 10,
        max_size: int = 500,
        seed: int = None
    ):
        self.max_spread_offset = max_spread_offset
        self.min_size = min_size
        self.max_size = max_size
        self.rng = np.random.default_rng(seed)
    
    def get_action(self, observation: np.ndarray) -> np.ndarray:
        """Generate random action."""
        bid_offset = self.rng.uniform(0, self.max_spread_offset)
        ask_offset = self.rng.uniform(0, self.max_spread_offset)
        bid_size = self.rng.uniform(self.min_size, self.max_size)
        ask_size = self.rng.uniform(self.min_size, self.max_size)
        
        return np.array([bid_offset, ask_offset, bid_size, ask_size], dtype=np.float32)
    
    def reset(self):
        """Reset RNG state."""
        pass  # Stateless agent


class StaticSpreadAgent(BaseAgent):
    """
    Static spread market maker.
    
    Places quotes at fixed distance from midprice with symmetric sizes.
    Simple but effective baseline strategy.
    """
    
    def __init__(
        self,
        spread_ticks: int = 2,
        quote_size: int = 100,
        inventory_skew: bool = True
    ):
        """
        Args:
            spread_ticks: Distance from mid in ticks
            quote_size: Size of each quote
            inventory_skew: If True, adjust quotes based on inventory
        """
        self.spread_ticks = spread_ticks
        self.quote_size = quote_size
        self.inventory_skew = inventory_skew
    
    def get_action(self, observation: np.ndarray) -> np.ndarray:
        """
        Get action with optional inventory skewing.
        
        Observation: [midprice, spread, inventory, volatility, imbalance, ...]
        """
        inventory = observation[2]  # inventory is 3rd element
        
        bid_offset = self.spread_ticks
        ask_offset = self.spread_ticks
        
        if self.inventory_skew and inventory != 0:
            # If long inventory, widen bid and narrow ask (encourage selling)
            # If short inventory, narrow bid and widen ask (encourage buying)
            skew = np.tanh(inventory / 100) * 2  # Normalize and scale
            bid_offset += skew
            ask_offset -= skew
            
            # Ensure positive offsets
            bid_offset = max(0.5, bid_offset)
            ask_offset = max(0.5, ask_offset)
        
        return np.array([
            bid_offset,
            ask_offset,
            self.quote_size,
            self.quote_size
        ], dtype=np.float32)
    
    def reset(self):
        """Reset agent state."""
        pass  # Stateless agent


@dataclass
class AvellanedaStoikovParams:
    """Parameters for Avellaneda-Stoikov market making model."""
    gamma: float = 0.1  # Risk aversion parameter
    k: float = 1.5      # Order arrival rate
    T: float = 1.0      # Time horizon
    A: float = 0.01     # Permanent impact parameter


class AvellanedaStoikovAgent(BaseAgent):
    """
    Avellaneda-Stoikov optimal market making strategy.
    
    Based on the seminal paper:
    Avellaneda, M., & Stoikov, S. (2008). High-frequency trading in a limit order book.
    Quantitative Finance, 8(3), 217-224.
    
    Computes optimal bid/ask spreads based on:
    - Risk aversion (gamma)
    - Inventory position
    - Volatility
    - Time remaining
    
    Formula:
        δ_bid = δ_ask = γ * σ² * (T - t) + (2/γ) * ln(1 + γ/k)
        Reservation price: r = mid - q * γ * σ² * (T - t)
        Bid: r - δ_bid
        Ask: r + δ_ask
    """
    
    def __init__(
        self,
        params: AvellanedaStoikovParams = None,
        quote_size: int = 100,
        tick_size: float = 0.01,
        episode_duration: float = 100.0
    ):
        self.params = params or AvellanedaStoikovParams()
        self.quote_size = quote_size
        self.tick_size = tick_size
        self.episode_duration = episode_duration
        self.current_time = 0.0
    
    def get_action(self, observation: np.ndarray) -> np.ndarray:
        """
        Compute optimal quotes using Avellaneda-Stoikov formula.
        
        Observation: [midprice, spread, inventory, volatility, imbalance, ...]
        """
        midprice = observation[0]
        inventory = observation[2]
        volatility = max(observation[3], 1e-6)  # Avoid division by zero
        
        # Time remaining
        time_remaining = max(self.episode_duration - self.current_time, 0.1)
        
        # Optimal spread (symmetric component)
        spread_component = (
            self.params.gamma * volatility**2 * time_remaining +
            (2 / self.params.gamma) * np.log(1 + self.params.gamma / self.params.k)
        )
        
        # Reservation price (includes inventory penalty)
        reservation_price = (
            midprice - inventory * self.params.gamma * volatility**2 * time_remaining
        )
        
        # Optimal bid and ask prices
        optimal_bid = reservation_price - spread_component / 2
        optimal_ask = reservation_price + spread_component / 2
        
        # Convert to offsets in ticks
        bid_offset = max(0.5, (midprice - optimal_bid) / self.tick_size)
        ask_offset = max(0.5, (optimal_ask - midprice) / self.tick_size)
        
        # Update time (approximate)
        self.current_time += 1.0
        
        return np.array([
            bid_offset,
            ask_offset,
            self.quote_size,
            self.quote_size
        ], dtype=np.float32)
    
    def reset(self):
        """Reset time counter."""
        self.current_time = 0.0


class AdaptiveSpreadAgent(BaseAgent):
    """
    Adaptive spread agent that adjusts based on market conditions.
    
    Features:
    - Widens spread in high volatility
    - Narrows spread in liquid markets (tight imbalance)
    - Adjusts size based on inventory
    """
    
    def __init__(
        self,
        base_spread_ticks: int = 2,
        base_size: int = 100,
        vol_sensitivity: float = 10.0,
        inventory_sensitivity: float = 0.5
    ):
        self.base_spread_ticks = base_spread_ticks
        self.base_size = base_size
        self.vol_sensitivity = vol_sensitivity
        self.inventory_sensitivity = inventory_sensitivity
    
    def get_action(self, observation: np.ndarray) -> np.ndarray:
        """Compute adaptive quotes."""
        spread = observation[1]
        inventory = observation[2]
        volatility = observation[3]
        imbalance = observation[4]
        
        # Adjust spread for volatility
        vol_adjustment = self.vol_sensitivity * volatility
        adjusted_spread = self.base_spread_ticks + vol_adjustment
        
        # Adjust for inventory
        inventory_factor = np.tanh(inventory * self.inventory_sensitivity / 100)
        bid_offset = adjusted_spread * (1 + inventory_factor)
        ask_offset = adjusted_spread * (1 - inventory_factor)
        
        # Adjust sizes based on inventory (reduce size if large position)
        size_factor = np.exp(-abs(inventory) / 500)
        bid_size = self.base_size * size_factor
        ask_size = self.base_size * size_factor
        
        # Ensure positive and bounded
        bid_offset = max(0.5, min(bid_offset, 20))
        ask_offset = max(0.5, min(ask_offset, 20))
        bid_size = max(10, min(bid_size, 500))
        ask_size = max(10, min(ask_size, 500))
        
        return np.array([
            bid_offset,
            ask_offset,
            bid_size,
            ask_size
        ], dtype=np.float32)
    
    def reset(self):
        """Reset agent state."""
        pass
