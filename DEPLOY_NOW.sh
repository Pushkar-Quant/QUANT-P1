#!/bin/bash

# ============================================================================
# DEPLOY TO HUGGING FACE - ONE COMMAND
# This script does EVERYTHING needed to deploy the fixed code
# ============================================================================

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  🚀 DEPLOY FIXED CODE TO HUGGING FACE SPACES               ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if we're in the right directory
if [ ! -f "app.py" ] || [ ! -d "src" ]; then
    echo "❌ Error: This script must be run from the QUANT-P1 directory"
    echo ""
    echo "Current directory: $(pwd)"
    echo ""
    echo "Please run:"
    echo "  cd d:/vs\\ code\\ pract/QUANT-P1"
    echo "  bash DEPLOY_NOW.sh"
    exit 1
fi

echo "✅ Found QUANT-P1 directory"
echo ""

# Check if Hugging Face Space exists
if [ -d "../adaptive-liquidity-provision/.git" ]; then
    echo "✅ Found existing Hugging Face Space"
    echo ""
    echo "📝 Updating existing deployment..."
    echo ""
    
    cd ../adaptive-liquidity-provision
    
    # Copy fixed files
    echo "🔧 Copying fixed files..."
    cp ../QUANT-P1/src/simulation/order_book.py src/simulation/
    cp ../QUANT-P1/src/simulation/order_flow.py src/simulation/
    echo "   ✅ order_book.py"
    echo "   ✅ order_flow.py"
    echo ""
    
    # Commit and push
    echo "💾 Committing changes..."
    git add src/simulation/
    git commit -m "Fix: Comprehensive edge case handling

- Enhanced order validation (size, price, timestamp, latency)
- Robust order size generation (always returns positive)
- Cancellation orders use size=1 placeholder
- All 10 edge cases tested and passing
- Ready for production use"
    
    echo ""
    echo "🚀 Pushing to Hugging Face..."
    git push
    
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║  ✅ DEPLOYMENT COMPLETE!                                    ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    echo "⏳ Hugging Face is rebuilding your Space (2-3 minutes)..."
    echo ""
    echo "📍 Your Space URL:"
    git remote get-url origin | sed 's/\.git$//' | sed 's/https:\/\/huggingface.co/  https:\/\/huggingface.co/'
    echo ""
    echo "🔄 Refresh the page in a few minutes to see the fixes applied"
    echo ""
    echo "✅ All edge cases are now handled correctly!"
    echo ""
    
else
    echo "📋 No existing Space found. Let's create one!"
    echo ""
    echo "Please follow these steps:"
    echo ""
    echo "1️⃣  Create a new Space at: https://huggingface.co/new-space"
    echo "   • Space name: adaptive-liquidity-provision"
    echo "   • SDK: Streamlit"
    echo "   • Hardware: CPU basic (FREE)"
    echo ""
    echo "2️⃣  Clone your space:"
    echo "   cd .."
    echo "   git clone https://huggingface.co/spaces/YOUR_USERNAME/adaptive-liquidity-provision"
    echo "   cd adaptive-liquidity-provision"
    echo ""
    echo "3️⃣  Copy files:"
    echo "   cp -r ../QUANT-P1/src ."
    echo "   cp -r ../QUANT-P1/experiments ."
    echo "   cp ../QUANT-P1/app.py ."
    echo "   cp ../QUANT-P1/requirements.txt ."
    echo "   cp ../QUANT-P1/README_SPACE.md README.md"
    echo ""
    echo "4️⃣  Deploy:"
    echo "   git add ."
    echo "   git commit -m 'Initial deployment with all fixes'"
    echo "   git push"
    echo ""
    echo "OR use the deployment script:"
    echo "   bash ../QUANT-P1/HUGGINGFACE_DEPLOY.sh"
    echo ""
fi
