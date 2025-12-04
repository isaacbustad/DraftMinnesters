#!/bin/bash

# Build script for Docker container
# Usage: ./docker/build-docker.sh [tag]
# Run from project root directory

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default tag
TAG=${1:-draft-ministers:latest}

# Get script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

echo -e "${GREEN}Building Docker container for Draft Ministers Flask App...${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if Dockerfile exists
if [ ! -f "$SCRIPT_DIR/Dockerfile" ]; then
    echo -e "${RED}Error: Dockerfile not found in docker/ directory.${NC}"
    exit 1
fi

# Change to project root for build context
cd "$PROJECT_ROOT"

# Build the Docker image
echo -e "${YELLOW}Building image with tag: ${TAG}${NC}"
docker build -f docker/Dockerfile -t ${TAG} .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Build successful!${NC}"
    echo -e "${GREEN}Image tagged as: ${TAG}${NC}"
    echo ""
    echo "To run the container:"
    echo "  docker run -p 5000:5000 ${TAG}"
    echo ""
    echo "Or use docker-compose (from project root):"
    echo "  docker-compose -f docker/docker-compose.yml up -d"
else
    echo -e "${RED}✗ Build failed!${NC}"
    exit 1
fi

