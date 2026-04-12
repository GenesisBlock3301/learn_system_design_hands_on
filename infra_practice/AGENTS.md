# AGENTS.md - Infrastructure Practice

> **Goal**: Learn CI/CD + Container Deployment with GitHub Actions, Docker Hub, and Local Docker Compose

---

## 📋 Project Overview

This directory contains infrastructure learning exercises focused on:
1. Building a simple FastAPI "Hello World" application
2. Setting up GitHub Actions to build and push Docker images to Docker Hub
3. Creating local infrastructure (Makefile + Docker Compose) to:
   - **Develop locally**: Build from local Dockerfile
   - **Deploy production**: Pull specific version from Docker Hub with validation

---

## 🏗️ Architecture

### Local Development Flow (make run)
```
┌─────────────────┐     ┌──────────────┐     ┌──────────────┐
│  Your Local PC  │────▶│  docker build│────▶│  docker run  │
│  (source code)  │     │  (../app/)   │     │  (local)     │
└─────────────────┘     └──────────────┘     └──────────────┘
```

### Production Deployment Flow (make deploy)
```
┌─────────────────┐     ┌──────────────┐     ┌──────────────┐
│  GitHub Repo    │────▶│ GitHub Action │────▶│  Docker Hub  │
│  (FastAPI app)  │     │ (build & tag) │     │ (your image) │
└─────────────────┘     └──────────────┘     └──────────────┘
                                                        │
                               ┌──────────────────────┘
                               ▼
┌─────────────────┐     ┌──────────────┐     ┌──────────────┐
│   Your Local PC │◀────│  make deploy │◀────│ docker pull  │
│  (docker run)   │     │  (validate)  │     │ (from Hub)   │
└─────────────────┘     └──────────────┘     └──────────────┘
```

---

## 🔄 Tag Flow Design

### GitHub Action Side
- **Trigger**: On push to main, or on release
- **Tag Strategy Options**:
  - Semantic versioning: `1.0.0`, `1.0.1`, etc.
  - Git SHA: `sha-abc123`
  - `latest` (always overwritten)
- **Build & Push**:
  ```bash
  docker build -t yourname/app:1.0.0 .
  docker push yourname/app:1.0.0
  ```

---

## 📁 Structure

```
infra_practice/
├── AGENTS.md              # This file
├── README.md              # User guide
├── .env.example           # Environment variables template
├── .dockerignore          # Docker build exclusions
├── app/                   # FastAPI application
│   ├── main.py            # 2 endpoints: /health, /hello
│   ├── requirements.txt   # fastapi + uvicorn
│   └── Dockerfile         # Multi-stage build
├── .github/
│   └── workflows/
│       └── docker-build-push.yml  # CI/CD pipeline
├── infra/                 # Local deployment infra
│   ├── docker-compose.yml         # Production: pull from Docker Hub
│   ├── docker-compose.dev.yml     # Local: build from ../app/
│   ├── docker-compose.prod.yml    # Production scaling config
│   └── Makefile           # Commands using docker compose
└── scripts/
    └── test_api.sh        # API testing script
```

---

## 🔌 API Endpoints

### 1. `GET /health` - Health Check
Returns service status (useful for Docker health checks and load balancers):

```json
{
  "status": "healthy",
  "timestamp": "2026-04-12T10:30:00Z",
  "version": "1.0.0"
}
```

### 2. `GET /hello` - Hello World
Accepts optional `name` query parameter:

- `GET /hello` → "Hello, World!"
- `GET /hello?name=Alice` → "Hello, Alice!"

```json
{
  "message": "Hello, Alice!",
  "service": "infra-practice-app"
}
```

### 3. `GET /` - Root
Returns service info and available endpoints.

---

## 🚀 Usage

### Step 1: Configure GitHub Secrets
Go to your GitHub repo → Settings → Secrets and variables → Actions:
- `DOCKERHUB_USERNAME` - Your Docker Hub username
- `DOCKERHUB_TOKEN` - Your Docker Hub access token

### Step 2: Push to Trigger Build
```bash
git add .
git commit -m "Add FastAPI app with CI/CD"
git push origin main
```

GitHub Action will build and push with tags like:
- `sha-abc123` (short git SHA)
- `latest` (on main branch)
- `v1.0.0` (if you push a git tag)

---

### Step 3: Local Development (make run)

For **local development** - **build from local Dockerfile**:

```bash
cd infra

# Build from ../app/Dockerfile and run
make run
```

**Characteristics:**
- Builds from local `../app/Dockerfile`
- Uses local source code (../app/main.py)
- No Docker Hub needed - works offline
- Fast for development iterations
- No tag validation (builds whatever is in your code)

---

### Step 4: Production Deployment (make deploy)

For **production** - **pull from Docker Hub** with validation:

```bash
cd infra

# Interactive mode - prompts for version, validates on Docker Hub
make deploy
# Enter version tag to deploy (e.g., v1.0.0, sha-abc123): v1.0.0
# 
# Validating tag on Docker Hub...
# Image: yourusername/infra-practice-app:v1.0.0
# 
# ✓ Tag validation successful!
# ✓ Found: yourusername/infra-practice-app:v1.0.0
# 
# Pulling image from Docker Hub...
# Starting container...
# ✓ Container started successfully!

# Non-interactive mode (CI/CD friendly)
make deploy TAG=v1.0.0
```

**Production Mode Rules:**
- Pulls from Docker Hub (remote)
- Must provide specific tag (not `latest`)
- Validates tag exists on Docker Hub before running
- Fails fast if tag is invalid

---

### Utility Commands

```bash
# List available tags on Docker Hub
make list-tags

# Check container status
make status

# View logs
make logs

# Stop container
make stop

# Test endpoints
make test

# See all commands
make help
```

---

## 🔧 Configuration

### Environment Variables (for Makefile/docker-compose)

| Variable | Default | Description |
|----------|---------|-------------|
| `IMAGE_NAME` | `your-dockerhub-username/infra-practice-app` | Docker image name |
| `TAG` | `latest` | Image tag to deploy |
| `PORT` | `8000` | Local port mapping |

### Examples

```bash
# Local development - build from source
make run

# Production deployment with validation
make deploy TAG=v1.0.0

# Run on different port
make run PORT=8080
make deploy TAG=v1.0.0 PORT=8080
```

### Environment Files

Copy `.env.example` to `.env` and customize:
```bash
cp .env.example .env
# Edit .env with your values
```

---

## 🏢 Multiple Environments

### Development (Default)
```bash
cd infra
make run
# Builds locally from ../app/
```

### Production-like
```bash
cd infra
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## 📋 Generated Image Tags (GitHub Actions)

| Git Event | Generated Tag(s) |
|-----------|------------------|
| Push to `main` | `latest`, `sha-abc123` |
| Push `v1.0.0` tag | `1.0.0`, `1.0`, `latest` |
| Pull request | `pr-42` |

The `sha-abc123` format is most useful for tracking specific commits.

---

## 🧪 Testing

### Automated Test Script
```bash
# Run all tests
./scripts/test_api.sh

# Test on different port
./scripts/test_api.sh 8080
```

### Makefile Test
```bash
cd infra
make test
```

---

## 🎯 Learning Outcomes

After completing this practice, you should understand:
- How GitHub Actions work (triggers, jobs, steps)
- Docker image tagging strategies
- Docker Hub authentication (secrets)
- Makefile basics (variables, targets)
- Docker Compose with environment variables
- Version-specific deployments (reproducible infrastructure)
- Multi-environment configuration
- Local development vs production deployment workflows

---

## 📝 Notes from Discussion

- **Date**: 2026-04-12
- **Goal**: Full CI/CD pipeline from code commit → Docker image → local deployment
- **Key Challenge**: Separate local development (build from source) from production (pull from Docker Hub)
- **Prerequisites**: Docker Hub account, GitHub repo

---

## 🔗 Related Files

- Parent project: `/Users/sifat/Desktop/learn_system_design_hands_on/AGENTS.md`
