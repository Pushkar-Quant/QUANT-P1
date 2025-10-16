# 🆓 FREE Deployment Guide

## Where to Deploy Your Adaptive Liquidity Provision Engine for FREE

---

## 🎯 Best Free Options (Ranked)

### ⭐ 1. **Streamlit Community Cloud** (RECOMMENDED for Dashboards)
**Best for**: Dashboards and visualization  
**Free Tier**: Unlimited public apps, 1GB RAM per app  
**Deployment Time**: 2 minutes  

#### Deploy Now:

1. **Push to GitHub**:
```bash
cd d:/vs\ code\ pract/QUANT-P1
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/QUANT-P1.git
git push -u origin main
```

2. **Deploy on Streamlit Cloud**:
   - Go to: https://share.streamlit.io/
   - Click "New app"
   - Connect GitHub
   - Select repository: `QUANT-P1`
   - Main file: `src/visualization/dashboard.py` or `src/visualization/advanced_dashboard.py`
   - Click "Deploy"

3. **Your app will be live at**:
```
https://YOUR_USERNAME-quant-p1-srcvisualizationdashboard-xxxxx.streamlit.app
```

**✅ FREE FEATURES**:
- Unlimited public apps
- Auto-updates from GitHub
- HTTPS included
- No credit card required

---

### ⭐ 2. **Hugging Face Spaces** (Great for ML Apps)
**Best for**: ML models and interactive demos  
**Free Tier**: Unlimited public Spaces, 16GB RAM, 2 vCPUs  
**Deployment Time**: 5 minutes  

#### Deploy Now:

1. **Create Space**:
   - Go to: https://huggingface.co/spaces
   - Click "Create new Space"
   - Name: `adaptive-liquidity-provision`
   - SDK: Select "Streamlit"
   - Click "Create Space"

2. **Upload Files**:
```bash
# Install git-lfs
git lfs install

# Clone your space
git clone https://huggingface.co/spaces/YOUR_USERNAME/adaptive-liquidity-provision

# Copy files
cp -r src requirements.txt adaptive-liquidity-provision/
cd adaptive-liquidity-provision

# Create app.py
cat > app.py << 'EOF'
import sys
sys.path.insert(0, '.')
from src.visualization.advanced_dashboard import main
if __name__ == "__main__":
    main()
EOF

# Commit and push
git add .
git commit -m "Deploy dashboard"
git push
```

3. **Your app will be live at**:
```
https://huggingface.co/spaces/YOUR_USERNAME/adaptive-liquidity-provision
```

**✅ FREE FEATURES**:
- GPU access available
- Persistent storage
- Custom domains
- No credit card needed

---

### ⭐ 3. **Render** (Full-Stack Deployment)
**Best for**: Complete applications with background services  
**Free Tier**: 750 hours/month, 512MB RAM, auto-sleep after 15 min  
**Deployment Time**: 10 minutes  

#### Deploy Now:

1. **Create `render.yaml`**:
```bash
cat > render.yaml << 'EOF'
services:
  - type: web
    name: alpe-dashboard
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: streamlit run src/visualization/advanced_dashboard.py --server.port=$PORT --server.address=0.0.0.0
    plan: free
    healthCheckPath: /_stcore/health
    envVars:
      - key: PYTHONPATH
        value: /opt/render/project/src
EOF
```

2. **Deploy**:
   - Go to: https://dashboard.render.com/
   - Click "New +" → "Web Service"
   - Connect GitHub repository
   - Select `QUANT-P1`
   - Render will auto-detect `render.yaml`
   - Click "Create Web Service"

3. **Your app will be live at**:
```
https://alpe-dashboard.onrender.com
```

**✅ FREE FEATURES**:
- Auto HTTPS
- Environment variables
- Automatic deploys from GitHub
- No credit card required

---

### ⭐ 4. **Railway** (Developer-Friendly)
**Best for**: Quick deployment with database support  
**Free Tier**: $5 credit/month (enough for 24/7 small app)  
**Deployment Time**: 3 minutes  

#### Deploy Now:

1. **One-Click Deploy**:
   - Go to: https://railway.app/
   - Click "Start a New Project"
   - Select "Deploy from GitHub repo"
   - Choose `QUANT-P1`

2. **Configure**:
   - Add environment variable: `PORT=8501`
   - Set start command: `streamlit run src/visualization/advanced_dashboard.py --server.port=$PORT --server.address=0.0.0.0`

3. **Your app will be live at**:
```
https://quant-p1-production.up.railway.app
```

**✅ FREE FEATURES**:
- $5/month free credit
- Instant scaling
- PostgreSQL database
- Auto HTTPS

---

### 5. **Google Colab** (Temporary/Testing)
**Best for**: Quick testing and notebooks  
**Free Tier**: Unlimited sessions, 12GB RAM, GPU access  
**Deployment Time**: 1 minute  

#### Run Now:

```python
# In Google Colab
!git clone https://github.com/YOUR_USERNAME/QUANT-P1.git
%cd QUANT-P1
!pip install -r requirements.txt

# Run dashboard with public URL
!streamlit run src/visualization/advanced_dashboard.py & npx localtunnel --port 8501
```

**✅ FREE FEATURES**:
- Free GPU access
- No account limits
- Great for training
- Jupyter environment

---

### 6. **PythonAnywhere** (Simple Hosting)
**Best for**: Python web apps and APIs  
**Free Tier**: 1 web app, 512MB storage  
**Deployment Time**: 15 minutes  

#### Deploy Now:

1. **Sign up**: https://www.pythonanywhere.com/
2. **Upload code**:
```bash
# In PythonAnywhere Bash console
git clone https://github.com/YOUR_USERNAME/QUANT-P1.git
cd QUANT-P1
pip3 install --user -r requirements.txt
```

3. **Configure Web App**:
   - Go to "Web" tab
   - Add new web app
   - Select "Manual configuration"
   - Python 3.10
   - Set working directory: `/home/YOUR_USERNAME/QUANT-P1`

**✅ FREE FEATURES**:
- Always-on (no sleep)
- SSH access
- Scheduled tasks
- No credit card

---

## 🚀 QUICK START: Deploy to Streamlit Cloud (Fastest)

### **Complete Deployment in 5 Commands**:

```bash
# 1. Initialize git (if not already)
git init

# 2. Create .gitignore for large files
echo "experiments/runs/*
*.pth
*.zip
logs/*
*.log" >> .gitignore

# 3. Commit everything
git add .
git commit -m "Deploy to Streamlit Cloud"

# 4. Create GitHub repo and push
git remote add origin https://github.com/YOUR_USERNAME/QUANT-P1.git
git push -u origin main

# 5. Deploy
# Go to https://share.streamlit.io/ and click "New app"
```

**Your dashboard will be live in 2 minutes!** 🎉

---

## 💡 Deployment Strategy by Use Case

### For **Quick Demo/Portfolio**:
✅ **Streamlit Cloud** - Easiest, no config needed

### For **Research/Training**:
✅ **Google Colab** - Free GPU access

### For **Production Dashboard**:
✅ **Hugging Face Spaces** - Best features, persistent

### For **Full Application**:
✅ **Render** or **Railway** - Complete stack support

### For **Long-Running Tasks**:
✅ **PythonAnywhere** - No auto-sleep

---

## 📋 Pre-Deployment Checklist

Before deploying, ensure:

```bash
# 1. Test locally
streamlit run src/visualization/advanced_dashboard.py

# 2. Check requirements.txt includes all dependencies
pip freeze > requirements.txt

# 3. Validate system
python scripts/validate_system.py

# 4. Test with minimal resources (simulate free tier)
docker run -m 512m -p 8501:8501 alpe:latest
```

---

## 🆓 Free Tier Comparison

| Platform | RAM | Storage | Always-On | GPU | Deploy Time |
|----------|-----|---------|-----------|-----|-------------|
| **Streamlit Cloud** | 1GB | 1GB | ✅ | ❌ | 2 min |
| **Hugging Face** | 16GB | 50GB | ✅ | ✅ (paid) | 5 min |
| **Render** | 512MB | Limited | ❌* | ❌ | 10 min |
| **Railway** | Variable | 1GB | ✅ | ❌ | 3 min |
| **Google Colab** | 12GB | 100GB | ❌ | ✅ | 1 min |
| **PythonAnywhere** | 512MB | 512MB | ✅ | ❌ | 15 min |

*Render free tier sleeps after 15 minutes of inactivity

---

## 🎯 RECOMMENDED: Deploy to Streamlit Cloud + Hugging Face

### Why Both?

1. **Streamlit Cloud**: For interactive dashboard
2. **Hugging Face**: For training and model hosting

### Quick Setup:

```bash
# Dashboard on Streamlit Cloud
# File: src/visualization/advanced_dashboard.py
# URL: https://share.streamlit.io/

# Training on Hugging Face Spaces
# With GPU for faster training
# URL: https://huggingface.co/spaces/
```

---

## 🔧 Optimization for Free Tiers

### 1. Reduce Memory Usage

```python
# In your config files, use smaller values:
episode_duration = 50  # Instead of 100
num_episodes = 10      # Instead of 50
```

### 2. Lazy Loading

```python
# Load heavy modules only when needed
if st.button("Train Agent"):
    from src.agents.ppo_agent import PPOMarketMaker
    # Training code here
```

### 3. Caching

```python
# Use Streamlit caching
@st.cache_data
def load_results():
    return pd.read_csv("results.csv")
```

---

## 📱 Mobile-Friendly Deployment

All platforms provide mobile-responsive dashboards automatically!

---

## 🆘 Troubleshooting Free Deployments

### **Issue**: Out of Memory
**Solution**: Reduce batch size, episode duration
```python
env_config.episode_duration = 30  # Smaller episodes
```

### **Issue**: App Sleeps (Render)
**Solution**: Use Streamlit Cloud or Hugging Face instead

### **Issue**: Slow Performance
**Solution**: 
- Use caching aggressively
- Reduce visualization complexity
- Pre-compute results

### **Issue**: Build Timeout
**Solution**: Remove unnecessary dependencies
```bash
# Create minimal requirements.txt
numpy
pandas
streamlit
plotly
```

---

## 🎓 Learning Resources

- **Streamlit Docs**: https://docs.streamlit.io/
- **Hugging Face Spaces**: https://huggingface.co/docs/hub/spaces
- **Render Docs**: https://render.com/docs
- **Railway Docs**: https://docs.railway.app/

---

## ✅ Final Deployment Command

```bash
# ONE-LINE DEPLOY to Streamlit Cloud
streamlit hello  # Test streamlit works
# Then visit https://share.streamlit.io/ and connect your GitHub repo
```

---

## 🎉 Congratulations!

Your Adaptive Liquidity Provision Engine can now be deployed **100% FREE** to showcase your work, run experiments, or build your portfolio!

**Best Free Option**: Streamlit Cloud (2-minute deploy)
**URL**: https://share.streamlit.io/

---

*Last Updated: October 2025*
