"""
Comprehensive Edge Case Testing
Tests all order generation and validation edge cases
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
from src.simulation.order_book import Order, OrderSide, OrderType, LimitOrderBook
from src.simulation.order_flow import OrderFlowGenerator, OrderFlowConfig
from src.environments.market_making_env import MarketMakingEnv

def test_order_size_generation():
    """Test that order size generation always returns positive values."""
    print("\n1️⃣  Testing Order Size Generation...")
    
    config = OrderFlowConfig(
        mean_order_size=100,
        order_size_std=50,
        min_order_size=10,
        max_order_size=500
    )
    
    order_flow = OrderFlowGenerator(config, seed=42)
    
    # Generate many sizes to test edge cases
    sizes = [order_flow.generate_order_size() for _ in range(1000)]
    
    min_size = min(sizes)
    max_size = max(sizes)
    
    if min_size > 0 and max_size <= 500:
        print(f"   ✅ PASS: All sizes positive and within bounds")
        print(f"   Range: [{min_size}, {max_size}]")
        return True
    else:
        print(f"   ❌ FAIL: Invalid sizes found")
        print(f"   Min: {min_size}, Max: {max_size}")
        return False

def test_limit_order_creation():
    """Test limit order creation with various parameters."""
    print("\n2️⃣  Testing Limit Order Creation...")
    
    config = OrderFlowConfig()
    order_flow = OrderFlowGenerator(config, seed=42)
    
    try:
        # Generate several limit orders
        for i in range(10):
            order = order_flow.generate_limit_order(
                timestamp=i * 0.1,
                midprice=100.0,
                spread=0.02
            )
            
            # Validate order
            assert order.size > 0, f"Invalid size: {order.size}"
            assert order.price > 0, f"Invalid price: {order.price}"
            assert order.timestamp >= 0, f"Invalid timestamp: {order.timestamp}"
            assert order.latency >= 0, f"Invalid latency: {order.latency}"
        
        print("   ✅ PASS: All limit orders created successfully")
        print(f"   Generated {10} orders with valid parameters")
        return True
        
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
        return False

def test_market_order_creation():
    """Test market order creation."""
    print("\n3️⃣  Testing Market Order Creation...")
    
    config = OrderFlowConfig()
    order_flow = OrderFlowGenerator(config, seed=42)
    
    try:
        # Generate several market orders
        for i in range(10):
            order = order_flow.generate_market_order(
                timestamp=i * 0.1,
                midprice=100.0
            )
            
            # Validate order
            assert order.size > 0, f"Invalid size: {order.size}"
            assert order.order_type == OrderType.MARKET
            assert order.timestamp >= 0, f"Invalid timestamp: {order.timestamp}"
        
        print("   ✅ PASS: All market orders created successfully")
        print(f"   Generated {10} orders with valid parameters")
        return True
        
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
        return False

def test_cancellation_orders():
    """Test cancellation order creation."""
    print("\n4️⃣  Testing Cancellation Orders...")
    
    config = OrderFlowConfig()
    order_flow = OrderFlowGenerator(config, seed=42)
    
    try:
        # Add some active orders first
        order_flow.active_orders = [1, 2, 3, 4, 5]
        
        # Generate cancellations
        for i in range(5):
            cancel = order_flow.generate_cancellation(timestamp=i * 0.1)
            
            if cancel is not None:
                # Validate cancellation order
                assert cancel.order_type == OrderType.CANCEL
                assert cancel.size > 0, "Size must be positive (even for cancels)"
                assert cancel.timestamp >= 0
        
        print("   ✅ PASS: All cancellation orders created successfully")
        print("   Cancellations use size=1 placeholder (ignored by LOB)")
        return True
        
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
        return False

def test_order_flow_sequence():
    """Test full order flow sequence generation."""
    print("\n5️⃣  Testing Order Flow Sequence Generation...")
    
    config = OrderFlowConfig()
    order_flow = OrderFlowGenerator(config, seed=42)
    
    try:
        orders, volatilities = order_flow.generate_order_flow_sequence(
            duration=10.0,
            initial_midprice=100.0,
            initial_spread=0.02
        )
        
        # Validate all orders in sequence
        for order in orders:
            assert order.size > 0, f"Invalid order size: {order.size}"
            assert order.timestamp >= 0, f"Invalid timestamp"
            
            if order.order_type == OrderType.LIMIT:
                assert order.price > 0, "Limit order must have positive price"
        
        print(f"   ✅ PASS: Generated {len(orders)} orders in sequence")
        print(f"   All orders have valid parameters")
        return True
        
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_lob_order_processing():
    """Test LOB can process all order types."""
    print("\n6️⃣  Testing LOB Order Processing...")
    
    try:
        lob = LimitOrderBook(tick_size=0.01)
        
        # Test limit order
        limit_order = Order(
            order_id=1,
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            price=100.0,
            size=100,
            timestamp=0.0
        )
        lob.submit_order(limit_order)
        
        # Test market order
        market_order = Order(
            order_id=2,
            side=OrderSide.SELL,
            order_type=OrderType.MARKET,
            price=0,
            size=50,
            timestamp=0.1
        )
        lob.submit_order(market_order)
        
        # Test cancellation
        cancel_order = Order(
            order_id=1,
            side=OrderSide.BUY,
            order_type=OrderType.CANCEL,
            price=0,
            size=1,  # Placeholder
            timestamp=0.2
        )
        lob.submit_order(cancel_order)
        
        print("   ✅ PASS: LOB processed all order types successfully")
        return True
        
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_environment_episode():
    """Test that environment can run complete episode without errors."""
    print("\n7️⃣  Testing Full Environment Episode...")
    
    try:
        env = MarketMakingEnv()
        obs, _ = env.reset(seed=42)
        
        # Run several steps
        for _ in range(50):
            # Random action
            action = env.action_space.sample()
            obs, reward, terminated, truncated, info = env.step(action)
            
            if terminated or truncated:
                break
        
        print("   ✅ PASS: Environment ran 50 steps without errors")
        print(f"   Final P&L: ${info.get('pnl', 0):.2f}")
        return True
        
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_negative_edge_cases():
    """Test that invalid orders are properly rejected."""
    print("\n8️⃣  Testing Negative Edge Cases (Should Fail)...")
    
    passed = 0
    total = 3
    
    # Test 1: Zero size for non-cancel order
    try:
        Order(
            order_id=1,
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            price=100.0,
            size=0,  # Invalid
            timestamp=0.0
        )
        print("   ❌ Should have rejected size=0 for limit order")
    except ValueError:
        print("   ✅ Correctly rejected size=0 for limit order")
        passed += 1
    
    # Test 2: Negative timestamp
    try:
        Order(
            order_id=2,
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            price=100.0,
            size=100,
            timestamp=-1.0  # Invalid
        )
        print("   ❌ Should have rejected negative timestamp")
    except ValueError:
        print("   ✅ Correctly rejected negative timestamp")
        passed += 1
    
    # Test 3: Negative latency
    try:
        Order(
            order_id=3,
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            price=100.0,
            size=100,
            timestamp=0.0,
            latency=-0.1  # Invalid
        )
        print("   ❌ Should have rejected negative latency")
    except ValueError:
        print("   ✅ Correctly rejected negative latency")
        passed += 1
    
    if passed == total:
        print(f"   ✅ PASS: All {total} negative cases correctly handled")
        return True
    else:
        print(f"   ❌ FAIL: Only {passed}/{total} negative cases handled")
        return False

if __name__ == "__main__":
    print("="*70)
    print(" 🧪 COMPREHENSIVE EDGE CASE TESTING")
    print("="*70)
    
    tests = [
        test_order_size_generation,
        test_limit_order_creation,
        test_market_order_creation,
        test_cancellation_orders,
        test_order_flow_sequence,
        test_lob_order_processing,
        test_environment_episode,
        test_negative_edge_cases
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"   ❌ TEST CRASHED: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    print("\n" + "="*70)
    print(" 📊 TEST RESULTS")
    print("="*70)
    
    passed = sum(results)
    total = len(results)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"\nPassed: {passed}/{total} ({percentage:.1f}%)")
    
    if passed == total:
        print("\n✅ ✅ ✅  ALL EDGE CASES HANDLED CORRECTLY  ✅ ✅ ✅")
        print("\n🚀 System is ROBUST and ready for deployment!")
        sys.exit(0)
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        print("\n⚠️  Please review failed tests before deployment")
        sys.exit(1)
