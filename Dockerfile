# Production Dockerfile for Adaptive Liquidity Provision Engine

FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY experiments/ ./experiments/
COPY examples/ ./examples/
COPY README.md ./

# Create directories for outputs
RUN mkdir -p /app/experiments/runs /app/experiments/evaluation /app/logs

# Expose ports for Streamlit and Tensorboard
EXPOSE 8501 6006

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import src; print('OK')"

# Default command (can be overridden)
CMD ["streamlit", "run", "src/visualization/advanced_dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
