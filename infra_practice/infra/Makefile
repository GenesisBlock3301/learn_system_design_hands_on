# Infra Practice - Deployment Makefile
# Usage: make run     (local dev - build from ../app/)
#        make deploy  (production - pull from Docker Hub)

# Configuration
IMAGE_NAME ?= genesisblock1033/infra-practice-app
TAG ?= latest
PORT ?= 8000

# Docker Compose
COMPOSE := docker compose
COMPOSE_FILE := -f docker-compose.yml
COMPOSE_DEV_FILE := -f docker-compose.dev.yml

# Colors for output
BLUE := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
NC := \033[0m

.PHONY: help run deploy validate-and-deploy stop logs status test clean

## Show all available commands
help:
	@echo ""
	@echo "$(BLUE)Infra Practice Commands$(NC)"
	@echo ""
	@echo "$(YELLOW)Local Development (Build from ../app/):$(NC)"
	@echo "  $(GREEN)make run$(NC)              - Build locally & start"
	@echo "  $(GREEN)make run-build$(NC)        - Force rebuild & start"
	@echo ""
	@echo "$(YELLOW)Production Deployment (Pull from Docker Hub):$(NC)"
	@echo "  $(GREEN)make deploy$(NC)           - Deploy with tag validation (interactive)"
	@echo "  $(GREEN)make deploy TAG=v1.0.0$(NC)- Deploy specific version"
	@echo ""
	@echo "$(YELLOW)Lifecycle:$(NC)"
	@echo "  $(GREEN)make stop$(NC)             - Stop and remove container"
	@echo "  $(GREEN)make restart$(NC)          - Restart services"
	@echo "  $(GREEN)make ps$(NC)               - Container status"
	@echo "  $(GREEN)make logs$(NC)             - View logs"
	@echo ""
	@echo "$(YELLOW)Utility:$(NC)"
	@echo "  $(GREEN)make test$(NC)             - Test API endpoints"
	@echo "  $(GREEN)make list-tags$(NC)        - List available tags on Docker Hub"

## ============================================
## LOCAL DEVELOPMENT (docker-compose.dev.yml)
## ============================================

run:
	@echo ""
	@echo "$(BLUE)=============================================$(NC)"
	@echo "$(BLUE)  LOCAL DEVELOPMENT MODE$(NC)"
	@echo "$(BLUE)=============================================$(NC)"
	@echo ""
	@echo "$(YELLOW)Building from: ../app/Dockerfile$(NC)"
	@echo "$(YELLOW)Image: $(IMAGE_NAME):$(TAG)$(NC)"
	@echo ""
	@echo "$(BLUE)Stopping any existing container...$(NC)"
	@docker stop infra-practice-app 2>/dev/null || true
	@docker rm infra-practice-app 2>/dev/null || true
	@$(COMPOSE) $(COMPOSE_DEV_FILE) down 2>/dev/null || true
	@$(COMPOSE) $(COMPOSE_FILE) down 2>/dev/null || true
	@echo ""
	@$(COMPOSE) $(COMPOSE_DEV_FILE) up -d --build
	@echo ""
	@echo "$(GREEN)✓ Local development server started!$(NC)"
	@echo ""
	@$(MAKE) show-urls

run-build:
	@echo ""
	@echo "$(BLUE)=============================================$(NC)"
	@echo "$(BLUE)  LOCAL DEVELOPMENT (Force Rebuild)$(NC)"
	@echo "$(BLUE)=============================================$(NC)"
	@echo ""
	@$(COMPOSE) $(COMPOSE_DEV_FILE) down
	@$(COMPOSE) $(COMPOSE_DEV_FILE) up -d --build --no-cache
	@echo ""
	@echo "$(GREEN)✓ Local development server started!$(NC)"
	@echo ""
	@$(MAKE) show-urls

## ============================================
## PRODUCTION DEPLOYMENT (docker-compose.yml)
## ============================================

deploy:
	@if [ -z "$(TAG)" ] || [ "$(TAG)" = "latest" ]; then \
		$(MAKE) deploy-interactive; \
	else \
		$(MAKE) validate-and-deploy TAG=$(TAG); \
	fi

deploy-interactive:
	@echo ""
	@echo "$(BLUE)=============================================$(NC)"
	@echo "$(BLUE)  PRODUCTION DEPLOYMENT MODE$(NC)"
	@echo "$(BLUE)=============================================$(NC)"
	@echo ""
	@echo "$(YELLOW)Source: Docker Hub ($(IMAGE_NAME))$(NC)"
	@echo ""
	@read -p "Enter version tag to deploy (e.g., v1.0.0, sha-abc123): " INPUT_TAG; \
	if [ -z "$$INPUT_TAG" ]; then \
		echo "$(RED)Error: Version tag is required$(NC)"; \
		exit 1; \
	fi; \
	if [ "$$INPUT_TAG" = "latest" ]; then \
		echo "$(RED)Error: 'latest' not allowed for production$(NC)"; \
		exit 1; \
	fi; \
	$(MAKE) validate-and-deploy TAG="$$INPUT_TAG"

validate-and-deploy:
	@echo ""
	@echo "$(BLUE)Validating tag on Docker Hub...$(NC)"
	@echo "$(BLUE)Image: $(IMAGE_NAME):$(TAG)$(NC)"
	@echo ""
	@if docker manifest inspect $(IMAGE_NAME):$(TAG) > /dev/null 2>&1; then \
		echo "$(GREEN)✓ Tag validation successful!$(NC)"; \
		echo "$(GREEN)✓ Found: $(IMAGE_NAME):$(TAG)$(NC)"; \
		echo ""; \
		$(MAKE) do-deploy TAG=$(TAG); \
	else \
		echo "$(RED)✗ Validation FAILED!$(NC)"; \
		echo "$(RED)✗ Tag '$(TAG)' not found on Docker Hub$(NC)"; \
		echo ""; \
		echo "$(YELLOW)Run 'make list-tags' to see available tags$(NC)"; \
		exit 1; \
	fi

do-deploy:
	@echo "$(BLUE)Pulling and starting container...$(NC)"
	@$(COMPOSE) $(COMPOSE_FILE) down 2>/dev/null || true
	@IMAGE_NAME=$(IMAGE_NAME) TAG=$(TAG) $(COMPOSE) $(COMPOSE_FILE) up -d
	@echo ""
	@echo "$(GREEN)✓ Production deployment complete!$(NC)"
	@echo ""
	@$(MAKE) show-urls

## ============================================
## LIFECYCLE COMMANDS
## ============================================

stop:
	@echo "$(BLUE)Stopping containers...$(NC)"
	@$(COMPOSE) $(COMPOSE_DEV_FILE) down 2>/dev/null || true
	@$(COMPOSE) $(COMPOSE_FILE) down 2>/dev/null || true
	@echo "$(GREEN)✓ Containers stopped$(NC)"

restart:
	@$(MAKE) stop
	@$(MAKE) run

ps:
	@echo "$(BLUE)Container Status:$(NC)"
	@echo ""
	@$(COMPOSE) $(COMPOSE_DEV_FILE) ps 2>/dev/null || $(COMPOSE) $(COMPOSE_FILE) ps

logs:
	@echo "$(BLUE)Showing logs (Ctrl+C to exit)...$(NC)"
	@echo ""
	@$(COMPOSE) $(COMPOSE_DEV_FILE) logs -f 2>/dev/null || $(COMPOSE) $(COMPOSE_FILE) logs -f

## ============================================
## UTILITY
## ============================================

show-urls:
	@echo "$(YELLOW)Access your app at:$(NC)"
	@echo "  • API Root:    http://localhost:$(PORT)/"
	@echo "  • Health:      http://localhost:$(PORT)/health"
	@echo "  • Hello:       http://localhost:$(PORT)/hello"
	@echo "  • Swagger UI:  http://localhost:$(PORT)/docs"
	@echo ""
	@echo "$(YELLOW)Commands:$(NC)"
	@echo "  make logs     - View logs"
	@echo "  make stop     - Stop container"
	@echo "  make test     - Test endpoints"

list-tags:
	@echo "$(BLUE)Fetching available tags for $(IMAGE_NAME)...$(NC)"
	@echo ""
	@curl -s "https://hub.docker.com/v2/repositories/$(shell echo $(IMAGE_NAME) | cut -d'/' -f1)/$(shell echo $(IMAGE_NAME) | cut -d'/' -f2)/tags?page_size=10" | \
		jq -r '.results[] | "  • " + .name' 2>/dev/null || \
		echo "$(YELLOW)Visit: https://hub.docker.com/r/$(IMAGE_NAME)/tags$(NC)"

test:
	@echo "$(BLUE)Testing endpoints...$(NC)"
	@echo ""
	@echo "$(YELLOW)Health Check:$(NC)"
	@curl -s http://localhost:$(PORT)/health | python -m json.tool 2>/dev/null || curl -s http://localhost:$(PORT)/health
	@echo ""
	@echo "$(YELLOW)Hello World:$(NC)"
	@curl -s http://localhost:$(PORT)/hello | python -m json.tool 2>/dev/null || curl -s http://localhost:$(PORT)/hello
	@echo ""

clean:
	@echo "$(BLUE)Cleaning up...$(NC)"
	@$(COMPOSE) $(COMPOSE_DEV_FILE) down -v --rmi all 2>/dev/null || true
	@$(COMPOSE) $(COMPOSE_FILE) down -v --rmi all 2>/dev/null || true
	@echo "$(GREEN)✓ Cleanup complete$(NC)"
