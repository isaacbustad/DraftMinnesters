#!/bin/bash

# Run script for Docker container
# Usage: ./docker/run-docker.sh [tag] [port]
# Run from project root directory

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
TAG=${1:-draft-ministers:latest}
PORT=${2:-5000}

# Get script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

echo -e "${GREEN}Running Draft Ministers Flask App in Docker...${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed.${NC}"
    exit 1
fi

# Check if image exists
if ! docker images | grep -q "draft-ministers"; then
    echo -e "${YELLOW}Image not found. Building first...${NC}"
    "$SCRIPT_DIR/build-docker.sh" ${TAG}
fi

# Change to project root
cd "$PROJECT_ROOT"

# Create necessary directories if they don't exist
mkdir -p logs
mkdir -p machine_learning

# Run the container
echo -e "${YELLOW}Starting container on port ${PORT}...${NC}"
docker run -d \
    --name draft-ministers-app \
    -p ${PORT}:5000 \
    -v "$PROJECT_ROOT/draft_ministers.db:/app/draft_ministers.db" \
    -v "$PROJECT_ROOT/logs:/app/logs" \
    -v "$PROJECT_ROOT/machine_learning/football_database.sqlite:/app/machine_learning/football_database.sqlite" \
    --restart unless-stopped \
    ${TAG}

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Container started successfully!${NC}"
    echo -e "${GREEN}Application available at: http://localhost:${PORT}${NC}"
    echo ""
    echo "Useful commands:"
    echo "  docker logs draft-ministers-app          # View logs"
    echo "  docker stop draft-ministers-app          # Stop container"
    echo "  docker start draft-ministers-app         # Start container"
    echo "  docker rm draft-ministers-app            # Remove container"
else
    echo -e "${RED}✗ Failed to start container!${NC}"
    exit 1
fi

