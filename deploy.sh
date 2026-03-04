#!/bin/bash

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}======================================${NC}"
echo -e "${YELLOW}   Namaste Bali API Deployment Script ${NC}"
echo -e "${YELLOW}======================================${NC}"

# 1. Pull latest changes
echo -e "\n${YELLOW}[1/4] Pulling latest changes from git...${NC}"
if git pull origin main; then
    echo -e "${GREEN}✓ Git pull successful.${NC}"
else
    echo -e "${RED}✗ Git pull failed! Aborting.${NC}"
    exit 1
fi

# Show current commit
COMMIT=$(git rev-parse --short HEAD)
echo -e "Current commit: ${GREEN}${COMMIT}${NC}"

# 2. Stop existing containers
echo -e "\n${YELLOW}[2/4] Stopping existing containers...${NC}"
docker compose down

# 3. Rebuild and start
echo -e "\n${YELLOW}[3/4] Rebuilding and starting containers...${NC}"
if docker compose up -d --build; then
    echo -e "${GREEN}✓ Containers started successfully.${NC}"
else
    echo -e "${RED}✗ Deployment failed during build/start!${NC}"
    exit 1
fi

# 4. Show status
echo -e "\n${YELLOW}[4/4] Checking container status...${NC}"
docker compose ps

echo -e "\n${GREEN}======================================${NC}"
echo -e "${GREEN}   Deployment Completed Successfully  ${NC}"
echo -e "${GREEN}======================================${NC}"
