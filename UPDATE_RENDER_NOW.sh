#!/bin/bash

# ============================================================================
# UPDATE RENDER DEPLOYMENT - Push All Fixes
# Run this to update your live Render deployment
# ============================================================================

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  🔄 UPDATING RENDER DEPLOYMENT                              ║"
echo "║  Pushing UI fixes + Documentation                            ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if in correct directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: Must run from QUANT-P1 directory"
    exit 1
fi

echo "📦 Files being updated:"
echo "   ✅ .streamlit/config.toml (UI fixes)"
echo "   ✅ src/visualization/advanced_dashboard.py (Better title)"
echo "   ✅ docs/USER_MANUAL.md (Complete user guide)"
echo "   ✅ docs/QUICK_START_GUIDE.md (5-minute quickstart)"
echo "   ✅ README.md (Live demo link)"
echo ""

# Add all changes
echo "💾 Staging changes..."
git add .streamlit/config.toml
git add src/visualization/advanced_dashboard.py
git add docs/USER_MANUAL.md
git add docs/QUICK_START_GUIDE.md
git add README.md

echo ""
echo "📝 Committing..."
git commit -m "Update: UI improvements + comprehensive documentation

- Fixed page title and configuration
- Added complete user manual (docs/USER_MANUAL.md)
- Added quick start guide (docs/QUICK_START_GUIDE.md)
- Updated README with live demo link
- Improved Streamlit config for better UX

What's new:
- ✅ Better page title (stays visible)
- ✅ Complete usage guide for all features
- ✅ Step-by-step tutorials
- ✅ Troubleshooting section
- ✅ Metric explanations
- ✅ Best practices guide"

echo ""
echo "🚀 Pushing to GitHub..."
git push

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  ✅ UPDATE PUSHED!                                          ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "⏳ Render is rebuilding your app (2-3 minutes)..."
echo ""
echo "📍 Your dashboard: https://quant-p1.onrender.com"
echo ""
echo "📖 New Documentation:"
echo "   • Quick Start: docs/QUICK_START_GUIDE.md"
echo "   • User Manual: docs/USER_MANUAL.md"
echo "   • README: Updated with live link"
echo ""
echo "🔄 Refresh your browser in 2-3 minutes to see updates!"
echo ""
