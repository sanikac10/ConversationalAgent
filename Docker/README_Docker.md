```markdown
# Docker Deployment Guide

## Overview

This guide explains how to deploy the Conversational Agent RAG system using Docker containers for production environments.

## Prerequisites

- Docker 20.10+
- Docker Compose 1.29+
- 4GB+ RAM
- Internet connection

## Quick Start

### 1. Build and Run

```bash
# Navigate to project root
cd ConversationalAgent_CurrentSubmission

# Build and start services
docker-compose -f Docker/docker-compose.yml up --build
2. Access Services
RAG API: http://localhost:5000 
Health Check: http://localhost:5000/api/health 
Nginx (if enabled): http://localhost:80 
Configuration
Environment Variables
Create .env file in project root:

# API Configuration
FLASK_ENV=production
API_PORT=5000
API_HOST=0.0.0.0

# Database
DATABASE_PATH=/app/Database/data/rag_store.db

# RAG Settings
EMBEDDING_MODEL=all-MiniLM-L6-v2
TOP_K_RESULTS=5
CONTEXT_WINDOW=2000

# Logging
LOG_LEVEL=INFO
LOG_FILE=/app/Logs/api.log
Docker Compose Override
Create docker-compose.override.yml for local development:

version: '3.8'

services:
  rag-api:
    environment:
      - FLASK_ENV=development
      - FLASK_DEBUG=1
    ports:
      - "5001:5000"  # Different port for dev
    volumes:
      - ./:/app  # Live code reloading
Production Deployment
1. Multi-stage Build
# Production Dockerfile
FROM python:3.10-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.10-slim

WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .

ENV PATH=/root/.local/bin:\$PATH
EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "API_Server.rag_api:app"]
2. Production Compose
version: '3.8'

services:
  rag-api:
    build: .
    environment:
      - FLASK_ENV=production
    volumes:
      - rag_data:/app/Database
      - rag_logs:/app/Logs
    restart: unless-stopped
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - rag-api
    restart: unless-stopped

  redis:
    image: redis:alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  rag_data:
  rag_logs:
  redis_data:
3. Nginx Configuration
upstream rag_api {
    server rag-api:5000;
}

server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://rag_api;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    location /health {
        proxy_pass http://rag_api/api/health;
    }
}
Scaling
Horizontal Scaling
services:
  rag-api:
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '0.5'
          memory: 1G
        reservations:
          cpus: '0.25'
          memory: 512M
Load Balancing
services:
  haproxy:
    image: haproxy:alpine
    ports:
      - "80:80"
    volumes:
      - ./haproxy.cfg:/usr/local/etc/haproxy/haproxy.cfg
    depends_on:
      - rag-api
Monitoring
Health Checks
services:
  rag-api:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
Logging
services:
  rag-api:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
Prometheus Metrics
# Add to rag_api.py
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter('api_requests_total', 'Total API requests')
REQUEST_DURATION = Histogram('api_request_duration_seconds', 'API request duration')

@app.route('/metrics')
def metrics():
    return generate_latest()
Security
SSL/TLS
services:
  nginx:
    volumes:
      - ./ssl/cert.pem:/etc/nginx/ssl/cert.pem
      - ./ssl/key.pem:/etc/nginx/ssl/key.pem
Secrets Management
secrets:
  api_key:
    file: ./secrets/api_key.txt

services:
  rag-api:
    secrets:
      - api_key
    environment:
      - API_KEY_FILE=/run/secrets/api_key
Backup and Recovery
Database Backup
# Backup script
docker exec rag-api-db sqlite3 /app/Database/data/rag_store.db ".backup /backup/rag_\$(date +%Y%m%d).db"
Volume Backup
# Backup volumes
docker run --rm -v rag_data:/data -v \$(pwd):/backup alpine tar czf /backup/rag_data_backup.tar.gz -C /data .
Troubleshooting
Container Logs
# View logs
docker-compose logs rag-api

# Follow logs
docker-compose logs -f rag-api

# Specific service logs
docker logs container_name
Debug Mode
# Run in debug mode
docker-compose -f docker-compose.yml -f docker-compose.debug.yml up
Container Shell Access
# Access running container
docker exec -it rag-api bash

# Run one-time container
docker run --rm -it rag-api bash
Performance Tuning
Memory Optimization
services:
  rag-api:
    deploy:
      resources:
        limits:
          memory: 2G
    environment:
      - PYTHONUNBUFFERED=1
      - MALLOC_ARENA_MAX=2
CPU Optimization
services:
  rag-api:
    deploy:
      resources:
        limits:
          cpus: '2.0'
    environment:
      - WORKERS=4
      - THREADS=2
Deployment Commands
# Production deployment
docker-compose -f docker-compose.prod.yml up -d

# Update services
docker-compose pull && docker-compose up -d

# Scale services
docker-compose up -d --scale rag-api=3

# Stop services
docker-compose down

# Clean up
docker-compose down -v --remove-orphans
This Docker setup provides a production-ready deployment solution with proper scaling, monitoring, and security considerations.