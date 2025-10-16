#!/bin/bash

# ============================================================================
# RENDER DEPLOYMENT - QUICK SETUP
# Prepares your project for Render deployment
# ============================================================================

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  🚀 RENDER DEPLOYMENT SETUP                                 ║"
echo "║  Adaptive Liquidity Provision Engine                         ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: Must run from QUANT-P1 directory"
    exit 1
fi

echo "✅ Found project files"
echo ""

# Create render.yaml configuration
echo "📝 Creating render.yaml configuration..."
cat > render.yaml << 'EOF'
services:
  - type: web
    name: adaptive-liquidity-provision
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true
    envVars:
      - key: PYTHON_VERSION
        value: 3.9.18
    plan: free
EOF

echo "✅ Created render.yaml"
echo ""

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    echo "📝 Creating .gitignore..."
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Data
data/
*.csv
*.parquet

# Model checkpoints
experiments/runs/*/
*.pth
*.zip

# Jupyter
.ipynb_checkpoints/

# Streamlit
.streamlit/secrets.toml
EOF
    echo "✅ Created .gitignore"
else
    echo "✅ .gitignore already exists"
fi
echo ""

# Initialize git if needed
if [ ! -d ".git" ]; then
    echo "🔧 Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit: Production-ready ML market making system"
    echo "✅ Git repository initialized"
else
    echo "✅ Git repository already initialized"
fi
echo ""

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  ✅ SETUP COMPLETE!                                         ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

echo "📋 NEXT STEPS:"
echo ""
echo "1️⃣  CREATE GITHUB REPOSITORY:"
echo "   → Go to: https://github.com/new"
echo "   → Name: adaptive-liquidity-provision"
echo "   → Visibility: Public (required for free tier)"
echo "   → Click 'Create repository'"
echo ""
echo "2️⃣  PUSH TO GITHUB:"
echo "   → Copy and run these commands:"
echo ""
echo "   git remote add origin https://github.com/YOUR_USERNAME/adaptive-liquidity-provision.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "3️⃣  DEPLOY ON RENDER:"
echo "   → Go to: https://dashboard.render.com/"
echo "   → Click 'New +' → 'Web Service'"
echo "   → Connect your GitHub repository"
echo "   → Render will detect render.yaml and auto-configure!"
echo "   → Click 'Create Web Service'"
echo ""
echo "4️⃣  WAIT FOR BUILD (3-5 minutes)"
echo "   → Watch the build logs"
echo "   → Your URL: https://adaptive-liquidity-provision.onrender.com"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "📖 FULL GUIDE: See RENDER_DEPLOY_GUIDE.md for detailed instructions"
echo ""
echo "💡 TIP: Render free tier spins down after 15min inactivity."
echo "    First request takes ~30s to wake up."
echo ""
echo "🎉 Your dashboard will be live in ~10 minutes total!"
echo ""
