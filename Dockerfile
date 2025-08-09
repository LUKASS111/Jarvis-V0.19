# Jarvis v1.0.0 Production Docker Image
# Enterprise-grade AI assistant with CRDT distributed architecture

FROM python:3.11-slim-bullseye

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    sqlite3 \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data logs config/environments

# Set environment variables
ENV PYTHONPATH=/app
ENV JARVIS_ENV=production
ENV JARVIS_CONFIG_PATH=/app/config/environments/production.yaml

# Create non-root user for security
RUN useradd -m -u 1000 jarvis && \
    chown -R jarvis:jarvis /app
USER jarvis

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Expose port
EXPOSE 8000

# Default command - run in backend service mode
CMD ["python", "main.py", "--backend", "--production"]