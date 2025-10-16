#!/bin/bash

# ============================================================================
# QUICK DEPLOYMENT SCRIPT FOR STREAMLIT CLOUD (FREE)
# ============================================================================

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  ADAPTIVE LIQUIDITY PROVISION ENGINE - QUICK DEPLOY          ║"
echo "║  Deploy to Streamlit Cloud (100% FREE)                       ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if git is initialized
if [ ! -d .git ]; then
    echo "📦 Initializing Git repository..."
    git init
    echo "✅ Git initialized"
else
    echo "✅ Git already initialized"
fi

# Create .gitignore for large files
echo "📝 Creating .gitignore..."
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*.so
*.egg-info/

# Virtual environments
venv/
env/

# Experiments (large files)
experiments/runs/*/
*.pth
*.zip

# Logs
logs/
*.log

# Data files
*.csv
*.parquet
data/

# IDE
.vscode/
.idea/

# OS
.DS_Store
EOF
echo "✅ .gitignore created"

# Add all files
echo "📦 Adding files to git..."
git add .

# Commit
echo "💾 Committing files..."
git commit -m "Deploy to Streamlit Cloud - Production Ready"

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  NEXT STEPS TO DEPLOY (FREE):                                ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "1️⃣  CREATE GITHUB REPOSITORY:"
echo "   - Go to: https://github.com/new"
echo "   - Name: QUANT-P1"
echo "   - Make it Public (required for free tier)"
echo "   - DON'T initialize with README"
echo "   - Click 'Create repository'"
echo ""
echo "2️⃣  PUSH TO GITHUB:"
echo "   Run these commands:"
echo "   ┌────────────────────────────────────────────────────────┐"
echo "   │ git remote add origin https://github.com/YOUR_USERNAME/QUANT-P1.git"
echo "   │ git branch -M main"
echo "   │ git push -u origin main"
echo "   └────────────────────────────────────────────────────────┘"
echo ""
echo "3️⃣  DEPLOY TO STREAMLIT CLOUD (FREE):"
echo "   - Go to: https://share.streamlit.io/"
echo "   - Click 'New app'"
echo "   - Connect GitHub account"
echo "   - Select repository: QUANT-P1"
echo "   - Main file: src/visualization/advanced_dashboard.py"
echo "   - Click 'Deploy!'"
echo ""
echo "4️⃣  YOUR APP WILL BE LIVE AT:"
echo "   https://YOUR_USERNAME-quant-p1-advanced-xxxxx.streamlit.app"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "⏱️  Total deployment time: ~2 minutes"
echo "💰 Cost: $0.00 (100% FREE)"
echo "🚀 Features: Auto-updates, HTTPS, No credit card needed"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "✅ Git repository prepared and ready for deployment!"
echo ""
