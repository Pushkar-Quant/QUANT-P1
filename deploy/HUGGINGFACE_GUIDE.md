# 🤗 Hugging Face Spaces Deployment Guide

## Complete Guide for Deploying to Hugging Face

**Free Tier**: 16GB RAM, 2 vCPUs, Persistent Storage

---

## Step 1: Create Account (1 minute)

1. Go to: https://huggingface.co/join
2. Sign up (free)
3. Verify your email

## Step 2: Create New Space (30 seconds)

1. Go to: https://huggingface.co/new-space
2. Settings:
   - **Space name**: `adaptive-liquidity-provision`
   - **License**: MIT
   - **SDK**: Select **Streamlit**
   - **Hardware**: CPU basic (FREE)
   - **Visibility**: Public
3. Click **"Create Space"**

## Step 3: Deploy Your Code (2 minutes)

```bash
# Run the deployment script
bash HUGGINGFACE_DEPLOY.sh

# Clone your space
git clone https://huggingface.co/spaces/YOUR_USERNAME/adaptive-liquidity-provision
cd adaptive-liquidity-provision

# Copy files
cp -r ../QUANT-P1/src .
cp -r ../QUANT-P1/experiments .
cp ../QUANT-P1/app.py .
cp ../QUANT-P1/requirements.txt .
cp ../QUANT-P1/README_SPACE.md README.md

# Deploy
git add .
git commit -m "Deploy dashboard"
git push
```

## Step 4: Wait for Build (2-3 minutes)

Hugging Face will automatically build your Space.

## Step 5: Your Space is Live! 🎉

URL: `https://huggingface.co/spaces/YOUR_USERNAME/adaptive-liquidity-provision`

---

## Advantages of Hugging Face Spaces

- ✅ 16GB RAM (vs 1GB on Streamlit)
- ✅ 2 vCPUs
- ✅ Persistent storage
- ✅ GPU available (paid tier)
- ✅ Great ML community
- ✅ 100% FREE

---

See full guide: `deploy/FREE_DEPLOYMENT_GUIDE.md`
