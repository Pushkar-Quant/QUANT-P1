"""
Order Flow Generator with stochastic arrival processes.

Implements realistic order arrival patterns including:
- Poisson arrival processes
- Order size distributions
- Price clustering near best quotes
- Volatility-dependent cancellation rates
"""

import numpy as np
from typing import Optional, Tuple
from dataclasses import dataclass

from .order_book import Order, OrderType, OrderSide


@dataclass
class OrderFlowConfig:
    """Configuration for order flow generation."""
    # Arrival rates (orders per unit time)
    limit_order_rate: float = 10.0
    market_order_rate: float = 2.0
    cancellation_rate: float = 5.0
    
    # Order size parameters
    mean_order_size: int = 100
    order_size_std: int = 30
    min_order_size: int = 10
    max_order_size: int = 500
    
    # Price placement parameters
    tick_size: float = 0.01
    mean_spread_offset_ticks: int = 2  # Mean distance from mid in ticks
    spread_offset_std_ticks: int = 3
    
    # Market order aggressiveness
    market_order_prob_buy: float = 0.5
    
    # Volatility parameters
    base_volatility: float = 0.02  # Base volatility per time unit
    volatility_regime_prob: float = 0.1  # Prob of regime switch per step
    high_vol_multiplier: float = 3.0
    
    # Latency parameters
    mean_latency: float = 0.001  # seconds
    latency_std: float = 0.0005


class VolatilityRegime:
    """Manages volatility regime switching."""
    
    def __init__(self, base_vol: float, high_vol_multiplier: float, switch_prob: float):
        self.base_vol = base_vol
        self.high_vol_multiplier = high_vol_multiplier
        self.switch_prob = switch_prob
        self.is_high_vol = False
        self.current_vol = base_vol
    
    def update(self, rng: np.random.Generator) -> float:
        """Update volatility regime."""
        if rng.random() < self.switch_prob:
            self.is_high_vol = not self.is_high_vol
        
        self.current_vol = (self.base_vol * self.high_vol_multiplier 
                           if self.is_high_vol else self.base_vol)
        return self.current_vol
    
    def get_current(self) -> float:
        """Get current volatility."""
        return self.current_vol


class OrderFlowGenerator:
    """
    Generates realistic order flow with stochastic arrivals.
    
    Features:
    - Poisson arrival times
    - Fat-tailed order size distribution
    - Price clustering around best quotes
    - Volatility regime switching
    - Realistic latency simulation
    """
    
    def __init__(self, config: Optional[OrderFlowConfig] = None, seed: Optional[int] = None):
        self.config = config or OrderFlowConfig()
        self.rng = np.random.default_rng(seed)
        
        # Volatility regime manager
        self.vol_regime = VolatilityRegime(
            base_vol=self.config.base_volatility,
            high_vol_multiplier=self.config.high_vol_multiplier,
            switch_prob=self.config.volatility_regime_prob
        )
        
        # Order ID tracking
        self.next_order_id = 1
        
        # Active orders for cancellation
        self.active_orders = []
    
    def generate_arrival_times(self, duration: float, rate: float) -> np.ndarray:
        """
        Generate Poisson arrival times.
        
        Args:
            duration: Time window duration
            rate: Arrival rate (events per unit time)
        
        Returns:
            Array of arrival times
        """
        n_events = self.rng.poisson(rate * duration)
        times = self.rng.uniform(0, duration, n_events)
        return np.sort(times)
    
    def generate_order_size(self) -> int:
        """Generate order size from truncated normal distribution."""
        size = int(self.rng.normal(
            self.config.mean_order_size,
            self.config.order_size_std
        ))
        # Ensure min_order_size is at least 1
        min_size = max(1, self.config.min_order_size)
        clipped_size = np.clip(size, min_size, self.config.max_order_size)
        # Final safety check: ensure positive size
        return max(1, int(clipped_size))
    
    def generate_limit_order(
        self, 
        timestamp: float, 
        midprice: float,
        spread: float
    ) -> Order:
        """
        Generate a limit order with realistic price placement.
        
        Args:
            timestamp: Order timestamp
            midprice: Current mid-price
            spread: Current spread
        
        Returns:
            Limit order
        """
        # Randomly choose side
        side = OrderSide.BUY if self.rng.random() < 0.5 else OrderSide.SELL
        
        # Generate offset from best quote (in ticks)
        offset_ticks = max(0, int(self.rng.normal(
            self.config.mean_spread_offset_ticks,
            self.config.spread_offset_std_ticks
        )))
        
        offset = offset_ticks * self.config.tick_size
        
        # Set price based on side
        if side == OrderSide.BUY:
            # Place below midprice
            price = midprice - spread/2 - offset
        else:
            # Place above midprice
            price = midprice + spread/2 + offset
        
        # Round to tick size
        price = round(price / self.config.tick_size) * self.config.tick_size
        
        # Generate latency
        latency = max(0, self.rng.normal(
            self.config.mean_latency,
            self.config.latency_std
        ))
        
        # Generate size with validation
        order_size = self.generate_order_size()
        assert order_size > 0, f"Generated invalid order size: {order_size}"
        
        order = Order(
            order_id=self.next_order_id,
            side=side,
            order_type=OrderType.LIMIT,
            price=price,
            size=order_size,
            timestamp=timestamp,
            trader_id=f"trader_{self.rng.integers(1, 100)}",
            latency=latency
        )
        
        self.next_order_id += 1
        self.active_orders.append(order.order_id)
        
        return order
    
    def generate_market_order(self, timestamp: float) -> Order:
        """
        Generate a market order.
        
        Args:
            timestamp: Order timestamp
        
        Returns:
            Market order
        """
        side = (OrderSide.BUY if self.rng.random() < self.config.market_order_prob_buy 
                else OrderSide.SELL)
        
        latency = max(0, self.rng.normal(
            self.config.mean_latency,
            self.config.latency_std
        ))
        
        order = Order(
            order_id=self.next_order_id,
            side=side,
            order_type=OrderType.MARKET,
            price=0,  # Market orders don't have a limit price
            size=self.generate_order_size(),
            timestamp=timestamp,
            trader_id=f"trader_{self.rng.integers(1, 100)}",
            latency=latency
        )
        
        self.next_order_id += 1
        return order
    
    def generate_cancellation(self, timestamp: float) -> Optional[Order]:
        """
        Generate a cancellation order for a random active order.
        
        Args:
            timestamp: Cancellation timestamp
        
        Returns:
            Cancellation order or None if no active orders
        """
        if not self.active_orders:
            return None
        
        # Select random order to cancel
        order_id = self.rng.choice(self.active_orders)
        self.active_orders.remove(order_id)
        
        # Cancellation orders use size=1 as placeholder (will be ignored by LOB)
        # This avoids validation errors while maintaining clarity
        return Order(
            order_id=order_id,
            side=OrderSide.BUY,  # Dummy value, not used for cancellations
            order_type=OrderType.CANCEL,
            price=0,  # Not used for cancellations
            size=1,  # Placeholder size (validation requires positive, but ignored)
            timestamp=timestamp
        )
    
    def generate_order_flow_sequence(
        self, 
        duration: float,
        initial_midprice: float = 100.0,
        initial_spread: float = 0.02
    ) -> Tuple[list, np.ndarray]:
        """
        Generate a complete sequence of orders for a time period.
        
        Args:
            duration: Time period duration
            initial_midprice: Starting mid-price
            initial_spread: Starting spread
        
        Returns:
            (orders, volatilities) where orders is list of Order objects
            and volatilities is array of volatility values over time
        """
        # Generate arrival times for each order type
        limit_times = self.generate_arrival_times(duration, self.config.limit_order_rate)
        market_times = self.generate_arrival_times(duration, self.config.market_order_rate)
        cancel_times = self.generate_arrival_times(duration, self.config.cancellation_rate)
        
        # Combine and sort all events
        events = []
        
        for t in limit_times:
            events.append(('limit', t))
        
        for t in market_times:
            events.append(('market', t))
        
        for t in cancel_times:
            events.append(('cancel', t))
        
        events.sort(key=lambda x: x[1])
        
        # Generate orders
        orders = []
        volatilities = []
        
        current_mid = initial_midprice
        current_spread = initial_spread
        
        for event_type, timestamp in events:
            # Update volatility regime
            vol = self.vol_regime.update(self.rng)
            volatilities.append(vol)
            
            # Generate appropriate order
            if event_type == 'limit':
                order = self.generate_limit_order(timestamp, current_mid, current_spread)
                orders.append(order)
            
            elif event_type == 'market':
                order = self.generate_market_order(timestamp)
                orders.append(order)
            
            elif event_type == 'cancel':
                order = self.generate_cancellation(timestamp)
                if order:
                    orders.append(order)
            
            # Simple price drift model (can be enhanced)
            drift = self.rng.normal(0, vol * np.sqrt(timestamp - (orders[-2].timestamp if len(orders) > 1 else 0)))
            current_mid += drift
            
            # Spread widens with volatility
            current_spread = initial_spread * (1 + vol / self.config.base_volatility)
        
        return orders, np.array(volatilities)
    
    def get_current_volatility(self) -> float:
        """Get current volatility level."""
        return self.vol_regime.get_current()
    
    def is_high_volatility_regime(self) -> bool:
        """Check if currently in high volatility regime."""
        return self.vol_regime.is_high_vol
    
    def reset(self):
        """Reset the generator state."""
        self.active_orders = []
        self.next_order_id = 1
        self.vol_regime.is_high_vol = False
        self.vol_regime.current_vol = self.vol_regime.base_vol
