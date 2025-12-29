#!/usr/bin/env bash
set -euo pipefail

# Simple deploy script to pull the latest image and run the container
# Adjust `DOCKER_IMAGE` and mount paths as needed on the remote server.

DOCKER_IMAGE="yourdockerhubuser/verset-app:latest"
CONTAINER_NAME="verset-app"

echo "Stopping and removing existing container (if any)..."
if docker ps -q -f name=${CONTAINER_NAME} | grep -q .; then
  docker rm -f ${CONTAINER_NAME} || true
fi

echo "Pulling latest image: ${DOCKER_IMAGE}"
docker pull ${DOCKER_IMAGE}

echo "Running new container..."
docker run -d --name ${CONTAINER_NAME} -p 80:8000 \
  -v $(pwd)/verset.db:/app/verset.db \
  -v $(pwd)/static:/app/static \
  -e SECRET_KEY="${SECRET_KEY:-please_set_secret}" \
  --restart unless-stopped \
  ${DOCKER_IMAGE}

echo "Deployment finished. Container ${CONTAINER_NAME} running." 
