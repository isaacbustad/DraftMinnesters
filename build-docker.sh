#!/bin/bash

# Build script for Docker container
# Usage: ./build-docker.sh [tag]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default tag
TAG=${1:-draft-ministers:latest}

echo -e "${GREEN}Building Docker container for Draft Ministers Flask App...${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if Dockerfile exists
if [ ! -f "Dockerfile" ]; then
    echo -e "${RED}Error: Dockerfile not found.${NC}"
    exit 1
fi

# Build the Docker image
echo -e "${YELLOW}Building image with tag: ${TAG}${NC}"
docker build -t ${TAG} .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Build successful!${NC}"
    echo -e "${GREEN}Image tagged as: ${TAG}${NC}"
    echo ""
    echo "To run the container:"
    echo "  docker run -p 5000:5000 ${TAG}"
    echo ""
    echo "Or use docker-compose:"
    echo "  docker-compose up -d"
else
    echo -e "${RED}✗ Build failed!${NC}"
    exit 1
fi

