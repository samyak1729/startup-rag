# Deployment Guide

## Local Development Setup

### Prerequisites
- Python 3.10+
- Docker & Docker Compose
- UV package manager (optional but recommended)

### Quick Start (5 minutes)

```bash
# 1. Clone and enter directory
git clone <repo-url>
cd biotech-startup-rag

# 2. Run quick start script
bash scripts/quick_start.sh

# 3. Start Qdrant (if not already running)
docker run -d -p 6333:6333 qdrant/qdrant

# 4. Terminal 1 - Start FastAPI backend
uv run python -m uvicorn src.api:app --host 0.0.0.0 --port 8000

# 5. Terminal 2 - Start Streamlit frontend
uv run streamlit run app.py

# 6. Open in browser
# Streamlit: http://localhost:8501
# API Docs: http://localhost:8000/docs
```

## Docker Deployment

### Using Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

This starts:
- Qdrant on `http://localhost:6333`
- FastAPI on `http://localhost:8000`
- Streamlit on `http://localhost:8501`

### Individual Docker Containers

```bash
# Start Qdrant only
docker run -d --name qdrant-rag \
  -p 6333:6333 \
  -v qdrant_storage:/qdrant/storage \
  qdrant/qdrant

# Build and run API
docker build -f Dockerfile.api -t biotech-rag-api .
docker run -d --name rag-api \
  -p 8000:8000 \
  --link qdrant-rag \
  -e QDRANT_URL=http://qdrant-rag:6333 \
  biotech-rag-api

# Build and run Streamlit
docker build -f Dockerfile.streamlit -t biotech-rag-web .
docker run -d --name rag-web \
  -p 8501:8501 \
  --link rag-api \
  biotech-rag-web
```

## Production Deployment

### Environment Setup

Create `.env` with production settings:

```ini
# Qdrant (use cloud instance or cluster)
QDRANT_URL=https://qdrant.yourdomain.com:6333
QDRANT_API_KEY=your_api_key_here

COLLECTION_NAME=biotech_documents_prod

# API Settings
API_HOST=0.0.0.0
API_PORT=8000

# Search settings
TOP_K=5
```

### Kubernetes Deployment

Example `k8s-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: biotech-rag-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: biotech-rag-api
  template:
    metadata:
      labels:
        app: biotech-rag-api
    spec:
      containers:
      - name: api
        image: biotech-rag-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: QDRANT_URL
          valueFrom:
            configMapKeyRef:
              name: rag-config
              key: qdrant-url
        - name: QDRANT_API_KEY
          valueFrom:
            secretKeyRef:
              name: rag-secrets
              key: qdrant-api-key
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

Deploy:
```bash
kubectl apply -f k8s-deployment.yaml
kubectl expose deployment biotech-rag-api --type=LoadBalancer --port=80 --target-port=8000
```

### Cloud Deployment Options

#### 1. AWS Deployment

**Using ECS:**
```bash
# Create ECR repositories
aws ecr create-repository --repository-name biotech-rag-api
aws ecr create-repository --repository-name biotech-rag-web

# Push images
docker tag biotech-rag-api:latest <aws-account>.dkr.ecr.<region>.amazonaws.com/biotech-rag-api:latest
docker push <aws-account>.dkr.ecr.<region>.amazonaws.com/biotech-rag-api:latest

# Create ECS task definition and service
# (Use AWS console or CloudFormation)
```

**Using Elastic Beanstalk:**
```bash
# Create .ebextensions/docker-compose.config
# Deploy
eb create biotech-rag-env
eb deploy
```

#### 2. Google Cloud Deployment

**Using Cloud Run:**
```bash
# Build and push to Container Registry
gcloud builds submit --tag gcr.io/<project-id>/biotech-rag-api

# Deploy
gcloud run deploy biotech-rag-api \
  --image gcr.io/<project-id>/biotech-rag-api \
  --platform managed \
  --memory 512Mi \
  --set-env-vars QDRANT_URL=https://your-qdrant-instance.com

# Deploy Streamlit frontend
gcloud run deploy biotech-rag-web \
  --image gcr.io/<project-id>/biotech-rag-web \
  --platform managed \
  --allow-unauthenticated
```

#### 3. Azure Deployment

**Using Container Instances:**
```bash
# Build and push to ACR
az acr build --registry <registry-name> --image biotech-rag-api:latest .

# Deploy container group
az container create \
  --resource-group <resource-group> \
  --name biotech-rag-api \
  --image <registry-name>.azurecr.io/biotech-rag-api:latest \
  --cpu 1 \
  --memory 1 \
  --ports 8000 \
  --environment-variables QDRANT_URL=<qdrant-url>
```

### Qdrant Production Setup

#### Self-Hosted Cluster

```yaml
# docker-compose-prod.yml
version: '3.8'
services:
  qdrant-node-1:
    image: qdrant/qdrant:latest
    environment:
      - QDRANT_API_KEY=${QDRANT_API_KEY}
    volumes:
      - qdrant_data_1:/qdrant/storage
    ports:
      - "6333:6333"
  
  qdrant-node-2:
    image: qdrant/qdrant:latest
    environment:
      - QDRANT_API_KEY=${QDRANT_API_KEY}
    volumes:
      - qdrant_data_2:/qdrant/storage
  
  qdrant-node-3:
    image: qdrant/qdrant:latest
    environment:
      - QDRANT_API_KEY=${QDRANT_API_KEY}
    volumes:
      - qdrant_data_3:/qdrant/storage

volumes:
  qdrant_data_1:
  qdrant_data_2:
  qdrant_data_3:
```

#### Qdrant Cloud

1. Sign up at https://qdrant.tech/cloud/
2. Create a cluster
3. Get API key and endpoint
4. Update `.env`:
   ```ini
   QDRANT_URL=https://your-cluster.qdrant.io:6333
   QDRANT_API_KEY=your_api_key
   ```

### Load Balancing & Reverse Proxy

**Using Nginx:**

```nginx
upstream api_backend {
    server api1:8000;
    server api2:8000;
    server api3:8000;
}

upstream streamlit_backend {
    server web:8501;
}

server {
    listen 80;
    server_name yourdomain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate /etc/ssl/certs/your_cert.crt;
    ssl_certificate_key /etc/ssl/private/your_key.key;

    # API endpoints
    location /api/ {
        proxy_pass http://api_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Streamlit frontend
    location / {
        proxy_pass http://streamlit_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

### CI/CD Pipeline

#### GitHub Actions Example

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Build Docker images
      run: |
        docker build -f Dockerfile.api -t biotech-rag-api:latest .
        docker build -f Dockerfile.streamlit -t biotech-rag-web:latest .
    
    - name: Push to registry
      run: |
        echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USER }} --password-stdin
        docker tag biotech-rag-api:latest myregistry/biotech-rag-api:latest
        docker push myregistry/biotech-rag-api:latest
    
    - name: Deploy to Kubernetes
      run: |
        kubectl set image deployment/biotech-rag-api \
          biotech-rag-api=myregistry/biotech-rag-api:latest \
          -n production
```

## Monitoring & Maintenance

### Health Checks

```bash
# Check API health
curl http://localhost:8000/health

# Check Qdrant health  
curl http://localhost:6333/health

# Get system stats
curl http://localhost:8000/stats
```

### Logging

View container logs:
```bash
# Docker Compose
docker-compose logs -f api
docker-compose logs -f web

# Kubernetes
kubectl logs -f deployment/biotech-rag-api
```

### Backups

Backup Qdrant snapshots:
```bash
# Create snapshot
curl -X POST http://localhost:6333/snapshots

# Download snapshot
curl http://localhost:6333/snapshots/snapshot_name.tar.gz > backup.tar.gz
```

### Performance Tuning

```bash
# Monitor Qdrant metrics
curl http://localhost:6333/metrics

# Adjust vector size for memory
# Edit config.py: EMBEDDING_MODEL

# Increase Qdrant worker threads
# Set QDRANT_WORK_POOL_SIZE environment variable
```

## Troubleshooting

### API Connection Issues
```bash
# Check if Qdrant is accessible
curl http://localhost:6333/health

# Check API logs
docker-compose logs api

# Verify environment variables
env | grep QDRANT
```

### Out of Memory
```bash
# Increase container limits
docker update --memory 2g biotech-rag-api

# Or in docker-compose.yml
# mem_limit: 2g
```

### Slow Searches
```bash
# Check Qdrant metrics
curl http://localhost:6333/metrics

# Verify collection is properly indexed
curl http://localhost:6333/collections/biotech_documents

# Consider adding more replicas/shards
```

### Document Processing Failures
```bash
# Check file format support
# Supported: .pdf, .docx, .txt

# Review error logs
docker-compose logs api | grep "ERROR"

# Test with sample documents first
```

## Security Hardening

### Production Checklist

- [ ] Enable HTTPS/TLS
- [ ] Set `QDRANT_API_KEY`
- [ ] Configure CORS properly
- [ ] Enable authentication on API
- [ ] Set up rate limiting
- [ ] Enable audit logging
- [ ] Run security scanning
- [ ] Configure backup strategy
- [ ] Setup monitoring alerts
- [ ] Document disaster recovery

### Security Best Practices

```python
# Add authentication to FastAPI
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from fastapi import Depends

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthCredentials = Depends(security)):
    if credentials.credentials != os.getenv("API_KEY"):
        raise HTTPException(status_code=403, detail="Invalid token")
    return credentials.credentials

# Apply to endpoints
@app.post("/search")
async def search_documents(query: SearchQuery, token: str = Depends(verify_token)):
    # endpoint logic
```

## Support & Documentation

- **API Documentation**: `http://localhost:8000/docs` (Swagger UI)
- **README**: See README.md for usage examples
- **Architecture**: See ARCHITECTURE.md for technical details
- **Issues**: Create GitHub issue for bugs
