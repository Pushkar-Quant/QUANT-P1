"""
Market Simulator: Integrates LOB and order flow with market impact.

Simulates realistic market dynamics including:
- Event-driven order processing
- Market impact feedback
- Latency effects
- Historical replay capability
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field

from .order_book import LimitOrderBook, Order, OrderType, OrderSide, Fill
from .order_flow import OrderFlowGenerator, OrderFlowConfig


@dataclass
class MarketState:
    """Snapshot of market state at a point in time."""
    timestamp: float
    midprice: float
    spread: float
    best_bid: Optional[float]
    best_ask: Optional[float]
    imbalance: float
    volatility: float
    total_volume: int
    num_trades: int


@dataclass
class SimulationConfig:
    """Configuration for market simulation."""
    initial_midprice: float = 100.0
    initial_spread: float = 0.02
    tick_size: float = 0.01
    
    # Order flow configuration
    order_flow_config: Optional[OrderFlowConfig] = None
    
    # Market impact parameters (will be integrated with impact module)
    enable_impact: bool = True
    impact_decay_rate: float = 0.5
    
    # Simulation parameters
    time_step: float = 0.1  # seconds
    seed: Optional[int] = None


class MarketSimulator:
    """
    Event-driven market simulator with realistic microstructure.
    
    Combines:
    - Limit order book
    - Stochastic order flow
    - Market impact
    - Latency effects
    """
    
    def __init__(self, config: Optional[SimulationConfig] = None):
        self.config = config or SimulationConfig()
        
        # Initialize components
        self.lob = LimitOrderBook(tick_size=self.config.tick_size)
        self.order_flow = OrderFlowGenerator(
            config=self.config.order_flow_config,
            seed=self.config.seed
        )
        
        # State tracking
        self.current_time = 0.0
        self.market_states: List[MarketState] = []
        
        # Initialize book with liquidity
        self._initialize_book()
        
        # Market maker tracking
        self.mm_orders: Dict[str, List[int]] = {}  # mm_id -> order_ids
        self.mm_inventory: Dict[str, int] = {}  # mm_id -> inventory
        self.mm_cash: Dict[str, float] = {}  # mm_id -> cash
        self.mm_pnl: Dict[str, List[float]] = {}  # mm_id -> pnl history
    
    def _initialize_book(self):
        """Initialize the order book with initial liquidity."""
        mid = self.config.initial_midprice
        spread = self.config.initial_spread
        tick = self.config.tick_size
        
        # Add initial liquidity on both sides
        for i in range(10):
            # Bid side
            bid_price = mid - spread/2 - i * tick
            bid_order = Order(
                order_id=self.lob.get_next_order_id(),
                side=OrderSide.BUY,
                order_type=OrderType.LIMIT,
                price=bid_price,
                size=100 + i * 10,
                timestamp=0.0,
                trader_id="liquidity_provider"
            )
            self.lob.submit_order(bid_order)
            
            # Ask side
            ask_price = mid + spread/2 + i * tick
            ask_order = Order(
                order_id=self.lob.get_next_order_id(),
                side=OrderSide.SELL,
                order_type=OrderType.LIMIT,
                price=ask_price,
                size=100 + i * 10,
                timestamp=0.0,
                trader_id="liquidity_provider"
            )
            self.lob.submit_order(ask_order)
    
    def step(self, duration: float) -> List[Fill]:
        """
        Simulate market for a time step.
        
        Args:
            duration: Time step duration
        
        Returns:
            List of fills that occurred during this step
        """
        # Generate orders for this time step
        orders, volatilities = self.order_flow.generate_order_flow_sequence(
            duration=duration,
            initial_midprice=self.lob.get_midprice() or self.config.initial_midprice,
            initial_spread=self.lob.get_spread() or self.config.initial_spread
        )
        
        # Process all orders
        all_fills = []
        for order in orders:
            order.timestamp += self.current_time
            fills = self.lob.submit_order(order)
            all_fills.extend(fills)
        
        # Update time
        self.current_time += duration
        self.lob.current_time = self.current_time
        
        # Record state
        state = self._get_current_state(
            volatility=self.order_flow.get_current_volatility()
        )
        self.market_states.append(state)
        
        return all_fills
    
    def register_market_maker(self, mm_id: str, initial_cash: float = 100000.0):
        """Register a market maker agent."""
        self.mm_orders[mm_id] = []
        self.mm_inventory[mm_id] = 0
        self.mm_cash[mm_id] = initial_cash
        self.mm_pnl[mm_id] = [0.0]
    
    def submit_mm_order(self, mm_id: str, side: OrderSide, price: float, size: int) -> int:
        """
        Submit a market maker order.
        
        Returns:
            Order ID
        """
        if mm_id not in self.mm_orders:
            self.register_market_maker(mm_id)
        
        order = Order(
            order_id=self.lob.get_next_order_id(),
            side=side,
            order_type=OrderType.LIMIT,
            price=price,
            size=size,
            timestamp=self.current_time,
            trader_id=mm_id
        )
        
        fills = self.lob.submit_order(order)
        
        # Track order
        self.mm_orders[mm_id].append(order.order_id)
        
        # Update inventory and cash from fills
        self._update_mm_positions(mm_id, fills)
        
        return order.order_id
    
    def cancel_mm_order(self, mm_id: str, order_id: int) -> bool:
        """Cancel a market maker order."""
        if order_id not in self.mm_orders.get(mm_id, []):
            return False
        
        success = self.lob.cancel_order(order_id)
        if success:
            self.mm_orders[mm_id].remove(order_id)
        
        return success
    
    def _update_mm_positions(self, mm_id: str, fills: List[Fill]):
        """Update market maker positions based on fills."""
        for fill in fills:
            # Check if this MM was involved
            passive_order = self.lob.orders.get(fill.passive_order_id)
            if passive_order and passive_order.trader_id == mm_id:
                # MM provided liquidity
                if fill.side == OrderSide.BUY:
                    # MM sold (short)
                    self.mm_inventory[mm_id] -= fill.size
                    self.mm_cash[mm_id] += fill.price * fill.size
                else:
                    # MM bought (long)
                    self.mm_inventory[mm_id] += fill.size
                    self.mm_cash[mm_id] -= fill.price * fill.size
    
    def get_mm_pnl(self, mm_id: str, mark_to_market: bool = True) -> float:
        """
        Calculate market maker P&L.
        
        Args:
            mm_id: Market maker ID
            mark_to_market: If True, mark inventory to current midprice
        
        Returns:
            Current P&L
        """
        if mm_id not in self.mm_inventory:
            return 0.0
        
        cash = self.mm_cash[mm_id]
        inventory = self.mm_inventory[mm_id]
        
        pnl = cash
        
        if mark_to_market:
            midprice = self.lob.get_midprice()
            if midprice:
                pnl += inventory * midprice
        
        return pnl
    
    def get_mm_state(self, mm_id: str) -> Dict:
        """Get current state of a market maker."""
        if mm_id not in self.mm_inventory:
            return {}
        
        return {
            'inventory': self.mm_inventory[mm_id],
            'cash': self.mm_cash[mm_id],
            'pnl': self.get_mm_pnl(mm_id),
            'num_orders': len(self.mm_orders[mm_id]),
            'order_ids': self.mm_orders[mm_id].copy()
        }
    
    def _get_current_state(self, volatility: float = 0.0) -> MarketState:
        """Get current market state snapshot."""
        midprice = self.lob.get_midprice()
        spread = self.lob.get_spread()
        
        return MarketState(
            timestamp=self.current_time,
            midprice=midprice or self.config.initial_midprice,
            spread=spread or self.config.initial_spread,
            best_bid=self.lob.get_best_bid(),
            best_ask=self.lob.get_best_ask(),
            imbalance=self.lob.get_order_book_imbalance(),
            volatility=volatility,
            total_volume=self.lob.total_volume,
            num_trades=self.lob.total_trades
        )
    
    def get_market_state(self) -> MarketState:
        """Get current market state."""
        return self._get_current_state(
            volatility=self.order_flow.get_current_volatility()
        )
    
    def get_state_history(self) -> List[MarketState]:
        """Get historical market states."""
        return self.market_states
    
    def get_book_snapshot(self) -> Dict:
        """Get current order book snapshot."""
        return self.lob.get_state_snapshot()
    
    def reset(self):
        """Reset the simulator."""
        self.lob = LimitOrderBook(tick_size=self.config.tick_size)
        self.order_flow.reset()
        self.current_time = 0.0
        self.market_states = []
        self.mm_orders = {}
        self.mm_inventory = {}
        self.mm_cash = {}
        self.mm_pnl = {}
        self._initialize_book()
    
    def run_simulation(self, duration: float, time_step: Optional[float] = None) -> Dict:
        """
        Run complete simulation for specified duration.
        
        Args:
            duration: Total simulation time
            time_step: Time step size (uses config default if None)
        
        Returns:
            Summary statistics
        """
        time_step = time_step or self.config.time_step
        num_steps = int(duration / time_step)
        
        all_fills = []
        
        for _ in range(num_steps):
            fills = self.step(time_step)
            all_fills.extend(fills)
        
        # Compute statistics
        states = self.get_state_history()
        
        midprices = [s.midprice for s in states]
        spreads = [s.spread for s in states]
        imbalances = [s.imbalance for s in states]
        volatilities = [s.volatility for s in states]
        
        return {
            'duration': duration,
            'num_steps': num_steps,
            'total_trades': self.lob.total_trades,
            'total_volume': self.lob.total_volume,
            'num_fills': len(all_fills),
            'avg_midprice': np.mean(midprices),
            'midprice_std': np.std(midprices),
            'avg_spread': np.mean(spreads),
            'spread_std': np.std(spreads),
            'avg_imbalance': np.mean(imbalances),
            'avg_volatility': np.mean(volatilities),
            'final_state': states[-1] if states else None
        }
