#!/bin/bash
echo "Detecting Docker Compose..."
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
else
    DOCKER_COMPOSE="docker compose"
fi

echo "Using: $DOCKER_COMPOSE"
echo "----------------------------------------"
echo "CONTAINER STATUS:"
$DOCKER_COMPOSE ps
echo "----------------------------------------"
echo "FLASK APP LOGS (Last 50 lines):"
$DOCKER_COMPOSE logs flask-app --tail 50
echo "----------------------------------------"
echo "MYSQL LOGS (Last 20 lines):"
$DOCKER_COMPOSE logs mysql --tail 20
