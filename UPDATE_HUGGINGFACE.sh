#!/bin/bash

# ============================================================================
# UPDATE HUGGING FACE SPACE WITH BUG FIX
# Run this if you've already deployed to Hugging Face
# ============================================================================

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  🔧 UPDATING HUGGING FACE SPACE WITH BUG FIX               ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if we're in a HF Space directory
if [ ! -d ".git" ]; then
    echo "❌ Error: Not in a git repository"
    echo "Please navigate to your cloned Hugging Face Space directory"
    echo ""
    echo "Example:"
    echo "  cd adaptive-liquidity-provision"
    echo "  bash ../QUANT-P1/UPDATE_HUGGINGFACE.sh"
    exit 1
fi

echo "✅ Found git repository"
echo ""

# Check if this is a HF Space
if git remote -v | grep -q "huggingface.co"; then
    echo "✅ Confirmed Hugging Face Space"
else
    echo "⚠️  Warning: This doesn't appear to be a Hugging Face Space"
    echo "Remote URL should contain: huggingface.co/spaces"
    echo ""
    echo "Current remotes:"
    git remote -v
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "🔧 Applying bug fix..."
echo ""

# Find the QUANT-P1 directory
QUANT_DIR=""
if [ -d "../QUANT-P1" ]; then
    QUANT_DIR="../QUANT-P1"
elif [ -d "../../QUANT-P1" ]; then
    QUANT_DIR="../../QUANT-P1"
else
    echo "❌ Error: Cannot find QUANT-P1 directory"
    echo "Please ensure QUANT-P1 is in the parent directory"
    exit 1
fi

echo "✅ Found QUANT-P1 at: $QUANT_DIR"
echo ""

# Copy fixed file
if [ -f "$QUANT_DIR/src/simulation/order_book.py" ]; then
    cp "$QUANT_DIR/src/simulation/order_book.py" src/simulation/
    echo "✅ Copied fixed order_book.py"
else
    echo "❌ Error: order_book.py not found in $QUANT_DIR/src/simulation/"
    exit 1
fi

echo ""
echo "📝 Committing changes..."
git add src/simulation/order_book.py
git commit -m "Fix: Allow zero size for cancellation orders

- Fixed ValueError when generating cancellation orders
- Cancellation orders no longer require positive size
- Added validation exception for CANCEL order type
- Dashboard now runs without errors"

echo ""
echo "🚀 Pushing to Hugging Face..."
git push

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  ✅ UPDATE COMPLETE!                                        ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "⏳ Hugging Face is rebuilding your Space (2-3 minutes)..."
echo ""
echo "📍 Your Space URL:"
git remote get-url origin | sed 's/\.git$//' | sed 's/https:\/\/huggingface.co/  https:\/\/huggingface.co/'
echo ""
echo "🔄 Refresh the page in a few minutes to see the fix applied"
echo ""
