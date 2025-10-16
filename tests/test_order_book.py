"""
Unit tests for Limit Order Book implementation.
"""

import pytest
import numpy as np
from src.simulation.order_book import (
    LimitOrderBook, Order, OrderType, OrderSide, PriceLevel
)


class TestPriceLevel:
    """Test PriceLevel functionality."""
    
    def test_add_order(self):
        level = PriceLevel(price=100.0)
        order = Order(
            order_id=1,
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            price=100.0,
            size=100,
            timestamp=0.0
        )
        
        level.add_order(order)
        assert level.total_size == 100
        assert len(level.orders) == 1
    
    def test_remove_order(self):
        level = PriceLevel(price=100.0)
        order1 = Order(1, OrderSide.BUY, OrderType.LIMIT, 100.0, 100, 0.0)
        order2 = Order(2, OrderSide.BUY, OrderType.LIMIT, 100.0, 50, 0.0)
        
        level.add_order(order1)
        level.add_order(order2)
        
        removed = level.remove_order(1)
        assert removed.order_id == 1
        assert level.total_size == 50
        assert len(level.orders) == 1
    
    def test_queue_position(self):
        level = PriceLevel(price=100.0)
        
        for i in range(5):
            order = Order(i, OrderSide.BUY, OrderType.LIMIT, 100.0, 100, float(i))
            level.add_order(order)
        
        assert level.get_queue_position(0) == 0
        assert level.get_queue_position(2) == 2
        assert level.get_queue_position(4) == 4
        assert level.get_queue_position(99) is None


class TestLimitOrderBook:
    """Test LimitOrderBook functionality."""
    
    @pytest.fixture
    def lob(self):
        """Create a fresh LOB for each test."""
        return LimitOrderBook(tick_size=0.01)
    
    def test_initialization(self, lob):
        """Test LOB initializes correctly."""
        assert lob.tick_size == 0.01
        assert len(lob.bids) == 0
        assert len(lob.asks) == 0
        assert lob.get_midprice() is None
    
    def test_submit_limit_order_bid(self, lob):
        """Test submitting a bid limit order."""
        order = Order(
            order_id=1,
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            price=100.0,
            size=100,
            timestamp=0.0
        )
        
        fills = lob.submit_order(order)
        
        assert len(fills) == 0
        assert lob.get_best_bid() == 100.0
        assert 1 in lob.orders
    
    def test_submit_limit_order_ask(self, lob):
        """Test submitting an ask limit order."""
        order = Order(
            order_id=1,
            side=OrderSide.SELL,
            order_type=OrderType.LIMIT,
            price=100.0,
            size=100,
            timestamp=0.0
        )
        
        fills = lob.submit_order(order)
        
        assert len(fills) == 0
        assert lob.get_best_ask() == 100.0
    
    def test_market_order_no_liquidity(self, lob):
        """Test market order when no liquidity exists."""
        order = Order(
            order_id=1,
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            price=0,
            size=100,
            timestamp=0.0
        )
        
        fills = lob.submit_order(order)
        assert len(fills) == 0
    
    def test_market_order_full_fill(self, lob):
        """Test market order that fully executes."""
        # Place limit order
        limit_order = Order(1, OrderSide.SELL, OrderType.LIMIT, 100.0, 100, 0.0)
        lob.submit_order(limit_order)
        
        # Execute market order
        market_order = Order(2, OrderSide.BUY, OrderType.MARKET, 0, 50, 1.0)
        fills = lob.submit_order(market_order)
        
        assert len(fills) == 1
        assert fills[0].size == 50
        assert fills[0].price == 100.0
        assert lob.orders[1].size == 50
    
    def test_market_order_partial_fill(self, lob):
        """Test market order that partially fills."""
        # Place small limit order
        limit_order = Order(1, OrderSide.SELL, OrderType.LIMIT, 100.0, 50, 0.0)
        lob.submit_order(limit_order)
        
        # Try to buy 100
        market_order = Order(2, OrderSide.BUY, OrderType.MARKET, 0, 100, 1.0)
        fills = lob.submit_order(market_order)
        
        assert len(fills) == 1
        assert fills[0].size == 50
        assert 1 not in lob.orders  # Limit order fully consumed
    
    def test_crossing_limit_order(self, lob):
        """Test limit order that crosses the spread."""
        # Place ask at 100.0
        ask_order = Order(1, OrderSide.SELL, OrderType.LIMIT, 100.0, 100, 0.0)
        lob.submit_order(ask_order)
        
        # Place aggressive bid at 100.0 (crosses)
        bid_order = Order(2, OrderSide.BUY, OrderType.LIMIT, 100.0, 50, 1.0)
        fills = lob.submit_order(bid_order)
        
        assert len(fills) == 1
        assert fills[0].size == 50
        assert fills[0].price == 100.0
    
    def test_cancel_order(self, lob):
        """Test order cancellation."""
        order = Order(1, OrderSide.BUY, OrderType.LIMIT, 100.0, 100, 0.0)
        lob.submit_order(order)
        
        assert 1 in lob.orders
        success = lob.cancel_order(1)
        
        assert success
        assert 1 not in lob.orders
        assert lob.get_best_bid() is None
    
    def test_midprice_calculation(self, lob):
        """Test midprice calculation."""
        bid_order = Order(1, OrderSide.BUY, OrderType.LIMIT, 99.0, 100, 0.0)
        ask_order = Order(2, OrderSide.SELL, OrderType.LIMIT, 101.0, 100, 0.0)
        
        lob.submit_order(bid_order)
        lob.submit_order(ask_order)
        
        assert lob.get_midprice() == 100.0
        assert lob.get_spread() == 2.0
    
    def test_order_book_imbalance(self, lob):
        """Test order book imbalance calculation."""
        # More bids than asks
        for i in range(3):
            bid = Order(i, OrderSide.BUY, OrderType.LIMIT, 99.0 - i*0.01, 100, 0.0)
            lob.submit_order(bid)
        
        ask = Order(10, OrderSide.SELL, OrderType.LIMIT, 101.0, 100, 0.0)
        lob.submit_order(ask)
        
        imbalance = lob.get_order_book_imbalance()
        assert imbalance > 0  # Positive = more buy pressure
    
    def test_queue_position_tracking(self, lob):
        """Test queue position is tracked correctly."""
        # Add orders at same price
        for i in range(3):
            order = Order(i, OrderSide.BUY, OrderType.LIMIT, 100.0, 100, float(i))
            lob.submit_order(order)
        
        # Check positions
        pos0 = lob.get_queue_position(0)
        pos1 = lob.get_queue_position(1)
        pos2 = lob.get_queue_position(2)
        
        assert pos0 == (0, 300)
        assert pos1 == (1, 300)
        assert pos2 == (2, 300)
    
    def test_price_rounding(self, lob):
        """Test prices are rounded to tick size."""
        order = Order(1, OrderSide.BUY, OrderType.LIMIT, 100.005, 100, 0.0)
        lob.submit_order(order)
        
        assert lob.get_best_bid() == 100.0  # Rounded to nearest tick
    
    def test_multiple_price_levels(self, lob):
        """Test handling of multiple price levels."""
        # Add bids at different prices
        for i in range(5):
            price = 100.0 - i * 0.01
            order = Order(i, OrderSide.BUY, OrderType.LIMIT, price, 100, 0.0)
            lob.submit_order(order)
        
        depth = lob.get_book_depth(levels=5)
        assert len(depth['bids']) == 5
        assert depth['bids'][0][0] == 100.0  # Best bid
        assert depth['bids'][4][0] == 99.96  # Worst bid in depth


class TestOrderBookStatistics:
    """Test order book statistics and state tracking."""
    
    @pytest.fixture
    def lob_with_orders(self):
        """Create LOB with some orders."""
        lob = LimitOrderBook(tick_size=0.01)
        
        # Add bids
        for i in range(3):
            bid = Order(i, OrderSide.BUY, OrderType.LIMIT, 99.0 + i*0.01, 100, 0.0)
            lob.submit_order(bid)
        
        # Add asks
        for i in range(3):
            ask = Order(10+i, OrderSide.SELL, OrderType.LIMIT, 101.0 + i*0.01, 100, 0.0)
            lob.submit_order(ask)
        
        return lob
    
    def test_state_snapshot(self, lob_with_orders):
        """Test state snapshot contains all necessary info."""
        snapshot = lob_with_orders.get_state_snapshot()
        
        assert 'timestamp' in snapshot
        assert 'best_bid' in snapshot
        assert 'best_ask' in snapshot
        assert 'midprice' in snapshot
        assert 'spread' in snapshot
        assert 'imbalance' in snapshot
        assert 'depth' in snapshot
        assert 'total_volume' in snapshot
    
    def test_volume_tracking(self, lob_with_orders):
        """Test volume is tracked correctly."""
        initial_volume = lob_with_orders.total_volume
        
        # Execute market order
        market_order = Order(100, OrderSide.BUY, OrderType.MARKET, 0, 50, 1.0)
        lob_with_orders.submit_order(market_order)
        
        assert lob_with_orders.total_volume == initial_volume + 50
        assert lob_with_orders.total_trades == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
