"""
Final Edge Case Test - Core Order Generation
Tests without heavy dependencies
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.simulation.order_book import Order, OrderSide, OrderType

def test_all_order_types():
    """Test creating all order types with proper validation."""
    print("="*70)
    print(" 🧪 FINAL EDGE CASE TEST - ALL ORDER TYPES")
    print("="*70)
    
    passed = 0
    total = 0
    
    # Test 1: Valid Limit Order
    print("\n1️⃣  Valid Limit Order...")
    total += 1
    try:
        order = Order(
            order_id=1,
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            price=100.0,
            size=100,
            timestamp=0.0
        )
        print("   ✅ PASS: Created limit order successfully")
        passed += 1
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
    
    # Test 2: Valid Market Order
    print("\n2️⃣  Valid Market Order...")
    total += 1
    try:
        order = Order(
            order_id=2,
            side=OrderSide.SELL,
            order_type=OrderType.MARKET,
            price=0,
            size=50,
            timestamp=0.1
        )
        print("   ✅ PASS: Created market order successfully")
        passed += 1
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
    
    # Test 3: Valid Cancellation Order (NEW FIX)
    print("\n3️⃣  Valid Cancellation Order (uses size=1 placeholder)...")
    total += 1
    try:
        order = Order(
            order_id=3,
            side=OrderSide.BUY,
            order_type=OrderType.CANCEL,
            price=0,
            size=1,  # Placeholder (validation requires positive)
            timestamp=0.2
        )
        print("   ✅ PASS: Created cancellation order with size=1")
        print("      (size is placeholder, ignored by LOB)")
        passed += 1
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
    
    # Test 4: Invalid - Zero size limit order
    print("\n4️⃣  Invalid - Zero size limit order (should fail)...")
    total += 1
    try:
        order = Order(
            order_id=4,
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            price=100.0,
            size=0,  # INVALID
            timestamp=0.3
        )
        print("   ❌ FAIL: Should have rejected size=0")
    except ValueError as e:
        print(f"   ✅ PASS: Correctly rejected - {e}")
        passed += 1
    
    # Test 5: Invalid - Negative size
    print("\n5️⃣  Invalid - Negative size (should fail)...")
    total += 1
    try:
        order = Order(
            order_id=5,
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            price=100.0,
            size=-10,  # INVALID
            timestamp=0.4
        )
        print("   ❌ FAIL: Should have rejected negative size")
    except ValueError as e:
        print(f"   ✅ PASS: Correctly rejected - {e}")
        passed += 1
    
    # Test 6: Invalid - Zero/negative price for limit order
    print("\n6️⃣  Invalid - Zero price for limit order (should fail)...")
    total += 1
    try:
        order = Order(
            order_id=6,
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            price=0,  # INVALID for limit orders
            size=100,
            timestamp=0.5
        )
        print("   ❌ FAIL: Should have rejected price=0 for limit order")
    except ValueError as e:
        print(f"   ✅ PASS: Correctly rejected - {e}")
        passed += 1
    
    # Test 7: Invalid - Negative timestamp
    print("\n7️⃣  Invalid - Negative timestamp (should fail)...")
    total += 1
    try:
        order = Order(
            order_id=7,
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            price=100.0,
            size=100,
            timestamp=-1.0  # INVALID
        )
        print("   ❌ FAIL: Should have rejected negative timestamp")
    except ValueError as e:
        print(f"   ✅ PASS: Correctly rejected - {e}")
        passed += 1
    
    # Test 8: Invalid - Negative latency
    print("\n8️⃣  Invalid - Negative latency (should fail)...")
    total += 1
    try:
        order = Order(
            order_id=8,
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            price=100.0,
            size=100,
            timestamp=0.0,
            latency=-0.1  # INVALID
        )
        print("   ❌ FAIL: Should have rejected negative latency")
    except ValueError as e:
        print(f"   ✅ PASS: Correctly rejected - {e}")
        passed += 1
    
    # Test 9: Edge case - Very large size
    print("\n9️⃣  Edge Case - Very large size...")
    total += 1
    try:
        order = Order(
            order_id=9,
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            price=100.0,
            size=1000000,  # Very large but valid
            timestamp=0.0
        )
        print("   ✅ PASS: Handled large size correctly")
        passed += 1
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
    
    # Test 10: Edge case - Very high price
    print("\n🔟 Edge Case - Very high price...")
    total += 1
    try:
        order = Order(
            order_id=10,
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            price=999999.99,  # Very high but valid
            size=100,
            timestamp=0.0
        )
        print("   ✅ PASS: Handled high price correctly")
        passed += 1
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
    
    # Results
    print("\n" + "="*70)
    print(" 📊 FINAL RESULTS")
    print("="*70)
    print(f"\nPassed: {passed}/{total} ({100*passed/total:.1f}%)")
    
    if passed == total:
        print("\n✅ ✅ ✅  ALL EDGE CASES HANDLED CORRECTLY  ✅ ✅ ✅")
        print("\n🎉 The fix is COMPLETE and ROBUST!")
        print("\n📝 Summary of changes:")
        print("   • Cancellation orders now use size=1 as placeholder")
        print("   • Order size validation ensures all orders have positive size")
        print("   • Added validation for timestamps and latency")
        print("   • Comprehensive error handling for all edge cases")
        print("\n🚀 READY TO DEPLOY TO HUGGING FACE!")
        return True
    else:
        print(f"\n❌ {total-passed} test(s) failed")
        return False

if __name__ == "__main__":
    success = test_all_order_types()
    sys.exit(0 if success else 1)
