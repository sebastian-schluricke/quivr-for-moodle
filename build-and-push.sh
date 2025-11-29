#!/bin/bash
# Build and push Docker images to Docker Hub
# Usage: ./build-and-push.sh [backend|frontend|all] [--login]
#
# Configuration via environment variables:
#   DOCKER_USER - Docker Hub username (required)
#   VERSION     - Image tag (default: latest)

set -e

# Configuration - set DOCKER_USER in your environment or .env file
DOCKER_USER="${DOCKER_USER:-}"
VERSION="${VERSION:-latest}"
DOCKER_CONFIG_DIR="$HOME/.docker-quivr"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if DOCKER_USER is set
if [ -z "$DOCKER_USER" ]; then
    echo -e "${RED}Error: DOCKER_USER environment variable is not set.${NC}"
    echo -e "${YELLOW}Please set it before running this script:${NC}"
    echo -e "  export DOCKER_USER=yourdockerhubuser"
    exit 1
fi

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}  Quivr Docker Build & Push${NC}"
echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}  Docker User: ${DOCKER_USER}${NC}"
echo -e "${YELLOW}  Using config: ${DOCKER_CONFIG_DIR}${NC}"
echo -e "${YELLOW}========================================${NC}"

# Create config directory if it doesn't exist
mkdir -p "${DOCKER_CONFIG_DIR}"

# Docker command with custom config
DOCKER="docker --config ${DOCKER_CONFIG_DIR}"

# Check for --login flag
if [[ "$*" == *"--login"* ]]; then
    echo -e "\n${GREEN}Logging in to Docker Hub as ${DOCKER_USER}...${NC}"
    ${DOCKER} login -u ${DOCKER_USER}
    echo -e "${GREEN}Login saved to ${DOCKER_CONFIG_DIR}${NC}"
    exit 0
fi

# Check if logged in to Docker Hub with this config
if ! ${DOCKER} info 2>/dev/null | grep -q "Username"; then
    # Check if config file exists
    if [ ! -f "${DOCKER_CONFIG_DIR}/config.json" ]; then
        echo -e "${RED}Not logged in to Docker Hub with Quivr config.${NC}"
        echo -e "${YELLOW}Please run: ./build-and-push.sh --login${NC}"
        exit 1
    fi
fi

build_backend() {
    echo -e "\n${GREEN}Building Backend...${NC}"
    docker build \
        -t ${DOCKER_USER}/quivr-backend:${VERSION} \
        -f backend/Dockerfile \
        ./backend

    echo -e "${GREEN}Pushing Backend...${NC}"
    ${DOCKER} push ${DOCKER_USER}/quivr-backend:${VERSION}
    echo -e "${GREEN}Backend done!${NC}"
}

build_frontend() {
    echo -e "\n${GREEN}Building Frontend...${NC}"
    echo -e "${YELLOW}Note: Frontend build requires build args for your staging environment${NC}"

    # These should be set for your staging environment
    docker build \
        -t ${DOCKER_USER}/quivr-frontend:${VERSION} \
        --build-arg NEXT_PUBLIC_ENV=production \
        --build-arg NEXT_PUBLIC_BACKEND_URL=${NEXT_PUBLIC_BACKEND_URL:-http://localhost:5050} \
        --build-arg NEXT_PUBLIC_SUPABASE_URL=${NEXT_PUBLIC_SUPABASE_URL:-http://localhost:54321} \
        --build-arg NEXT_PUBLIC_SUPABASE_ANON_KEY=${NEXT_PUBLIC_SUPABASE_ANON_KEY:-your-anon-key} \
        --build-arg NEXT_PUBLIC_FRONTEND_URL=${NEXT_PUBLIC_FRONTEND_URL:-http://localhost:3000} \
        --build-arg NEXT_PUBLIC_AUTH_MODES=${NEXT_PUBLIC_AUTH_MODES:-password} \
        -f frontend/Dockerfile \
        ./frontend

    echo -e "${GREEN}Pushing Frontend...${NC}"
    ${DOCKER} push ${DOCKER_USER}/quivr-frontend:${VERSION}
    echo -e "${GREEN}Frontend done!${NC}"
}

case "${1:-all}" in
    backend)
        build_backend
        ;;
    frontend)
        build_frontend
        ;;
    all)
        build_backend
        build_frontend
        ;;
    *)
        echo "Usage: $0 [backend|frontend|all]"
        exit 1
        ;;
esac

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}  Build complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "Images pushed to Docker Hub:"
echo -e "  - ${DOCKER_USER}/quivr-backend:${VERSION}"
echo -e "  - ${DOCKER_USER}/quivr-frontend:${VERSION}"
