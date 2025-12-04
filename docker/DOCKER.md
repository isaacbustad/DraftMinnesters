# Docker Deployment Guide

This guide explains how to build and run the Draft Ministers Flask application using Docker.

## Prerequisites

- Docker installed and running
  - Windows: [Docker Desktop](https://www.docker.com/products/docker-desktop)
  - Linux: `sudo apt-get install docker.io` or equivalent
  - Mac: [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop)

- Docker Compose (optional, for easier management)
  - Usually included with Docker Desktop
  - Linux: `sudo apt-get install docker-compose`

## Quick Start

### Option 1: Using Docker Compose (Recommended)

From the **project root directory**:

```bash
# Build and start the container
docker-compose -f docker/docker-compose.yml up -d

# View logs
docker-compose -f docker/docker-compose.yml logs -f

# Stop the container
docker-compose -f docker/docker-compose.yml down
```

The application will be available at `http://localhost:5000`

### Option 2: Using Build Scripts

**Linux/Mac:**
```bash
# Make scripts executable (first time only)
chmod +x docker/build-docker.sh docker/run-docker.sh

# Build the image (from project root)
./docker/build-docker.sh

# Run the container (from project root)
./docker/run-docker.sh
```

**Windows:**
```cmd
REM Build the image (from project root)
docker\build-docker.bat

REM Run the container (from project root)
docker\run-docker.bat
```

### Option 3: Manual Docker Commands

**Build the image** (from project root):
```bash
docker build -f docker/Dockerfile -t draft-ministers:latest .
```

**Run the container** (from project root):
```bash
docker run -d \
  --name draft-ministers-app \
  -p 5000:5000 \
  -v $(pwd)/draft_ministers.db:/app/draft_ministers.db \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/machine_learning/football_database.sqlite:/app/machine_learning/football_database.sqlite \
  --restart unless-stopped \
  draft-ministers:latest
```

**Windows (PowerShell):**
```powershell
docker run -d `
  --name draft-ministers-app `
  -p 5000:5000 `
  -v ${PWD}/draft_ministers.db:/app/draft_ministers.db `
  -v ${PWD}/logs:/app/logs `
  -v ${PWD}/machine_learning/football_database.sqlite:/app/machine_learning/football_database.sqlite `
  --restart unless-stopped `
  draft-ministers:latest
```

## Container Management

### View Logs
```bash
docker logs draft-ministers-app
docker logs -f draft-ministers-app  # Follow logs
```

### Stop Container
```bash
docker stop draft-ministers-app
```

### Start Container
```bash
docker start draft-ministers-app
```

### Remove Container
```bash
docker stop draft-ministers-app
docker rm draft-ministers-app
```

### Execute Commands in Container
```bash
docker exec -it draft-ministers-app bash
docker exec -it draft-ministers-app python -c "print('Hello')"
```

### View Container Status
```bash
docker ps -a | grep draft-ministers
```

## Volume Mounts

The Docker setup uses volume mounts to persist data:

- **Database**: `./draft_ministers.db` → `/app/draft_ministers.db`
- **Logs**: `./logs` → `/app/logs`
- **ML Database**: `./machine_learning/football_database.sqlite` → `/app/machine_learning/football_database.sqlite`

This ensures data persists even if the container is removed.

## Customization

### Change Port

Edit `docker/docker-compose.yml` or use:
```bash
docker run -p 8080:5000 draft-ministers:latest
```

### Environment Variables

Add to `docker/docker-compose.yml`:
```yaml
environment:
  - FLASK_ENV=production
  - API_KEY=your-api-key
```

Or use `-e` flag:
```bash
docker run -e FLASK_ENV=production draft-ministers:latest
```

### Build with Custom Tag
```bash
docker build -f docker/Dockerfile -t draft-ministers:v1.0.0 .
```

## Troubleshooting

### Container Won't Start

1. Check logs: `docker logs draft-ministers-app`
2. Verify port is not in use: `netstat -an | grep 5000`
3. Check Docker is running: `docker ps`

### Database Issues

- Ensure database file has correct permissions
- Check volume mount paths are correct
- Verify database file exists before mounting

### Build Failures

- Check Dockerfile syntax
- Verify all files are present
- Review build logs: `docker build -f docker/Dockerfile -t draft-ministers:latest . 2>&1 | tee build.log`

### Permission Issues (Linux)

If you encounter permission issues:
```bash
sudo chown -R $USER:$USER draft_ministers.db
sudo chmod 664 draft_ministers.db
```

## Production Deployment

For production, consider:

1. **Use a production WSGI server** (update Dockerfile):
```dockerfile
RUN pip install gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

2. **Add reverse proxy** (Nginx):
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

3. **Use environment variables** for sensitive data
4. **Enable HTTPS** with Let's Encrypt
5. **Set up monitoring** and logging
6. **Use Docker secrets** for API keys

## Multi-Stage Build (Optional)

For smaller images, use multi-stage build:

```dockerfile
# Build stage
FROM python:3.9-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Runtime stage
FROM python:3.9-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
CMD ["python", "app.py"]
```

## Health Checks

The container includes a health check. View status:
```bash
docker inspect --format='{{.State.Health.Status}}' draft-ministers-app
```

## Cleanup

Remove unused images:
```bash
docker image prune -a
```

Remove all stopped containers:
```bash
docker container prune
```

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Flask Deployment Guide](https://flask.palletsprojects.com/en/2.0.x/deploying/)

