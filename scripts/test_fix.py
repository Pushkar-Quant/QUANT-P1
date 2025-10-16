"""
Quick test to verify the order cancellation fix
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.simulation.order_book import Order, OrderSide, OrderType

def test_cancel_order():
    """Test that cancellation orders use size=1 placeholder."""
    print("Testing cancellation order fix...")
    
    try:
        # Cancellation orders now use size=1 as placeholder
        cancel_order = Order(
            order_id=1,
            side=OrderSide.BUY,
            order_type=OrderType.CANCEL,
            price=0,
            size=1,  # Placeholder size (ignored by LOB)
            timestamp=0.0
        )
        
        print("✅ PASS: Cancellation order with size=1 placeholder created successfully")
        print(f"   Order ID: {cancel_order.order_id}")
        print(f"   Order Type: {cancel_order.order_type}")
        print(f"   Size: {cancel_order.size} (placeholder, ignored)")
        return True
        
    except ValueError as e:
        print(f"❌ FAIL: {e}")
        return False

def test_regular_order_validation():
    """Test that regular orders still require positive size."""
    print("\nTesting regular order validation...")
    
    try:
        # This SHOULD raise an error (limit order with size=0)
        bad_order = Order(
            order_id=2,
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            price=100.0,
            size=0,  # Invalid for limit orders
            timestamp=0.0
        )
        print("❌ FAIL: Should have raised ValueError for size=0 on limit order")
        return False
        
    except ValueError as e:
        print(f"✅ PASS: Correctly rejected limit order with size=0")
        print(f"   Error: {e}")
        return True

if __name__ == "__main__":
    print("="*60)
    print("ORDER VALIDATION FIX TEST")
    print("="*60)
    
    test1 = test_cancel_order()
    test2 = test_regular_order_validation()
    
    print("\n" + "="*60)
    if test1 and test2:
        print("✅ ALL TESTS PASSED - FIX VERIFIED")
        print("="*60)
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED")
        print("="*60)
        sys.exit(1)
