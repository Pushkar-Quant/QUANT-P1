# Deployment Guide

## Production Deployment for Adaptive Liquidity Provision Engine

This guide covers deployment options for production environments.

---

## Table of Contents

1. [Docker Deployment](#docker-deployment)
2. [Cloud Deployment](#cloud-deployment)
3. [Monitoring & Logging](#monitoring--logging)
4. [Security Considerations](#security-considerations)
5. [Scaling Strategies](#scaling-strategies)

---

## Docker Deployment

### Quick Start with Docker

#### 1. Build the Image

```bash
docker build -t alpe:latest .
```

#### 2. Run Dashboard

```bash
docker run -p 8501:8501 -v $(pwd)/experiments:/app/experiments alpe:latest
```

Access dashboard at `http://localhost:8501`

#### 3. Using Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

Services:
- **Dashboard**: http://localhost:8501
- **Advanced Dashboard**: http://localhost:8502
- **Tensorboard**: http://localhost:6006

#### 4. Run Training in Docker

```bash
docker-compose --profile training up training
```

### Docker Commands Reference

```bash
# Build
docker-compose build

# Start specific service
docker-compose up dashboard

# Scale services
docker-compose up --scale dashboard=3

# View service status
docker-compose ps

# Execute commands in container
docker-compose exec dashboard python scripts/evaluate.py --compare-all
```

---

## Cloud Deployment

### AWS Deployment

#### Option 1: AWS ECS (Elastic Container Service)

1. **Push image to ECR**:
```bash
# Authenticate
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Tag and push
docker tag alpe:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/alpe:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/alpe:latest
```

2. **Create ECS task definition** (see `deploy/aws/task-definition.json`)

3. **Deploy service**:
```bash
aws ecs create-service \
    --cluster alpe-cluster \
    --service-name alpe-dashboard \
    --task-definition alpe-task \
    --desired-count 2 \
    --launch-type FARGATE
```

#### Option 2: AWS EC2 with Docker

```bash
# SSH to EC2 instance
ssh -i key.pem ec2-user@<instance-ip>

# Install Docker
sudo yum update -y
sudo yum install docker -y
sudo service docker start

# Clone and run
git clone <repo-url>
cd QUANT-P1
docker-compose up -d
```

### Google Cloud Platform (GCP)

#### Cloud Run Deployment

```bash
# Build and push to GCR
gcloud builds submit --tag gcr.io/<project-id>/alpe

# Deploy to Cloud Run
gcloud run deploy alpe-dashboard \
    --image gcr.io/<project-id>/alpe \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --port 8501
```

### Azure Deployment

#### Azure Container Instances

```bash
# Create resource group
az group create --name alpe-rg --location eastus

# Deploy container
az container create \
    --resource-group alpe-rg \
    --name alpe-dashboard \
    --image alpe:latest \
    --dns-name-label alpe-unique \
    --ports 8501
```

---

## Monitoring & Logging

### Application Logging

Create `src/utils/logging_config.py`:

```python
import logging
import sys
from pathlib import Path

def setup_logging(log_dir="logs", level=logging.INFO):
    """Configure logging for the application."""
    log_dir = Path(log_dir)
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "app.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)
```

### Prometheus Metrics

Install prometheus client:
```bash
pip install prometheus-client
```

Add to dashboard:
```python
from prometheus_client import Counter, Histogram, start_http_server

# Metrics
trade_counter = Counter('trades_total', 'Total number of trades')
pnl_histogram = Histogram('pnl_distribution', 'P&L distribution')

# Start metrics server
start_http_server(8000)
```

### Health Checks

Add to `src/utils/health.py`:

```python
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "alpe-dashboard",
        "version": "1.0.0"
    }

@app.get("/ready")
async def readiness_check():
    # Check dependencies
    return {"ready": True}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## Security Considerations

### 1. Environment Variables

Never hardcode secrets. Use environment variables:

```bash
# .env file
DATABASE_URL=postgresql://user:pass@localhost/db
API_KEY=your-secret-key
AWS_ACCESS_KEY=xxx
```

Load in application:
```python
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('API_KEY')
```

### 2. Authentication

Add authentication to Streamlit:

```python
import streamlit as st
import hmac

def check_password():
    """Returns `True` if the user had the correct password."""
    def password_entered():
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    st.text_input("Password", type="password", on_change=password_entered, key="password")
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False

if not check_password():
    st.stop()
```

### 3. HTTPS/SSL

Use reverse proxy (nginx) with Let's Encrypt:

```nginx
server {
    listen 443 ssl;
    server_name alpe.yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/alpe.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/alpe.yourdomain.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 4. Rate Limiting

Implement rate limiting for APIs:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@limiter.limit("10/minute")
@app.get("/api/train")
async def train_endpoint():
    # Training logic
    pass
```

---

## Scaling Strategies

### Horizontal Scaling

Use load balancer with multiple instances:

```yaml
# docker-compose.yml
services:
  dashboard:
    deploy:
      replicas: 3
    # ... other config
```

### Vertical Scaling

Allocate more resources:

```yaml
services:
  training:
    deploy:
      resources:
        limits:
          cpus: '4.0'
          memory: 16G
        reservations:
          cpus: '2.0'
          memory: 8G
```

### Kubernetes Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: alpe-dashboard
spec:
  replicas: 3
  selector:
    matchLabels:
      app: alpe-dashboard
  template:
    metadata:
      labels:
        app: alpe-dashboard
    spec:
      containers:
      - name: dashboard
        image: alpe:latest
        ports:
        - containerPort: 8501
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
```

---

## Performance Optimization

### 1. Caching

Use Redis for caching:

```python
import redis
import pickle

r = redis.Redis(host='localhost', port=6379, db=0)

def get_cached_result(key):
    cached = r.get(key)
    if cached:
        return pickle.loads(cached)
    return None

def cache_result(key, value, expiry=3600):
    r.setex(key, expiry, pickle.dumps(value))
```

### 2. Database

For persistence, use PostgreSQL:

```python
from sqlalchemy import create_engine
import pandas as pd

engine = create_engine('postgresql://user:pass@localhost/alpe')

# Store results
df.to_sql('backtest_results', engine, if_exists='append')

# Query results
results = pd.read_sql('SELECT * FROM backtest_results WHERE sharpe > 1.0', engine)
```

### 3. Async Processing

Use Celery for background tasks:

```python
from celery import Celery

app = Celery('tasks', broker='redis://localhost:6379/0')

@app.task
def train_agent_async(config):
    # Long-running training task
    pass

# Queue task
result = train_agent_async.delay(config)
```

---

## Backup & Recovery

### Automated Backups

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"

# Backup experiments
tar -czf $BACKUP_DIR/experiments_$DATE.tar.gz experiments/

# Backup to S3
aws s3 cp $BACKUP_DIR/experiments_$DATE.tar.gz s3://alpe-backups/

# Cleanup old backups (keep last 30 days)
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

Add to crontab:
```bash
0 2 * * * /path/to/backup.sh
```

---

## Troubleshooting

### Common Issues

**Port already in use**:
```bash
# Find process using port
lsof -i :8501

# Kill process
kill -9 <PID>
```

**Container out of memory**:
```bash
# Increase Docker memory limit
# Docker Desktop → Settings → Resources → Memory
```

**GPU not available**:
```bash
# Install nvidia-docker
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update && sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```

---

## Maintenance

### Regular Tasks

1. **Weekly**: Review logs and metrics
2. **Monthly**: Update dependencies
3. **Quarterly**: Security audit
4. **Yearly**: Infrastructure review

### Update Procedure

```bash
# 1. Pull latest code
git pull origin main

# 2. Rebuild images
docker-compose build

# 3. Rolling update (zero downtime)
docker-compose up -d --no-deps --build dashboard

# 4. Verify
curl http://localhost:8501/_stcore/health
```

---

## Support

For deployment issues:
1. Check logs: `docker-compose logs -f`
2. Review health checks: `docker-compose ps`
3. Consult documentation
4. Open GitHub issue

---

*Last updated: 2025*
