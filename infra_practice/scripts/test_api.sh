#!/bin/bash

# API Test Script for Infra Practice App
# Usage: ./test_api.sh [PORT]

set -e

PORT=${1:-8000}
BASE_URL="http://localhost:${PORT}"
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=============================================${NC}"
echo -e "${BLUE}  Testing Infra Practice API on port ${PORT}${NC}"
echo -e "${BLUE}=============================================${NC}"
echo ""

# Function to make API call and check response
test_endpoint() {
    local name=$1
    local url=$2
    local expected=$3
    
    echo -e "${YELLOW}Testing: ${name}${NC}"
    echo "  URL: ${url}"
    
    response=$(curl -s -w "\n%{http_code}" "${url}" 2>/dev/null || echo -e "\n000")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" -eq 200 ]; then
        echo -e "  Status: ${GREEN}✓ PASS (HTTP ${http_code})${NC}"
        if [ -n "$expected" ]; then
            if echo "$body" | grep -q "$expected"; then
                echo -e "  Response: ${GREEN}✓ Contains expected content${NC}"
            else
                echo -e "  Response: ${RED}✗ Missing expected content: ${expected}${NC}"
            fi
        fi
        echo "  Body: $body"
    else
        echo -e "  Status: ${RED}✗ FAIL (HTTP ${http_code})${NC}"
        echo "  Body: $body"
        return 1
    fi
    echo ""
}

# Wait for service to be ready
echo -e "${YELLOW}Waiting for service to be ready...${NC}"
for i in {1..30}; do
    if curl -s "${BASE_URL}/health" > /dev/null 2>&1; then
        echo -e "${GREEN}Service is ready!${NC}"
        echo ""
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}Service failed to start within 30 seconds${NC}"
        exit 1
    fi
    sleep 1
done

# Run tests
test_endpoint "Root Endpoint" "${BASE_URL}/" "infra-practice-app"
test_endpoint "Health Check" "${BASE_URL}/health" "healthy"
test_endpoint "Hello World (default)" "${BASE_URL}/hello" "Hello, World!"
test_endpoint "Hello World (custom name)" "${BASE_URL}/hello?name=Developer" "Hello, Developer!"

# Summary
echo -e "${BLUE}=============================================${NC}"
echo -e "${GREEN}  All tests passed! ✓${NC}"
echo -e "${BLUE}=============================================${NC}"
echo ""
echo "Quick links:"
echo "  - API Docs:  ${BASE_URL}/docs"
echo "  - Health:    ${BASE_URL}/health"
echo "  - Hello:     ${BASE_URL}/hello"
