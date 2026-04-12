# Infrastructure Practice Project

A hands-on project to learn CI/CD, Docker, and GitHub Actions with a simple FastAPI application.

## 🎯 Learning Goals

- Build and containerize a FastAPI application
- Set up GitHub Actions for automated Docker image builds
- Push images to Docker Hub with proper tagging
- Deploy specific image versions locally using Make and Docker Compose

## 📁 Project Structure

```
infra_practice/
├── app/                          # FastAPI Application
│   ├── main.py                   # API endpoints
│   ├── requirements.txt          # Python dependencies
│   ├── Dockerfile                # Multi-stage Docker build
│   └── .dockerignore             # Docker build exclusions
├── .github/
│   └── workflows/
│       └── docker-build-push.yml # CI/CD pipeline
├── infra/                        # Local Deployment
│   ├── docker-compose.yml        # Docker Compose config
│   └── Makefile                  # Deployment commands
├── scripts/
│   └── test_api.sh               # API testing script
└── README.md                     # This file
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose installed
- Make installed (optional but recommended)
- GitHub account
- Docker Hub account

### Step 1: Local Development

```bash
# Navigate to app directory
cd app

# Install dependencies
pip install -r requirements.txt

# Run locally
uvicorn main:app --reload

# Test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/hello
curl "http://localhost:8000/hello?name=Alice"
```

Visit http://localhost:8000/docs for interactive API documentation.

### Step 2: Configure GitHub Secrets

1. Go to your GitHub repository → Settings → Secrets and variables → Actions
2. Add these secrets:
   - `DOCKERHUB_USERNAME` - Your Docker Hub username
   - `DOCKERHUB_TOKEN` - Your Docker Hub access token (create at https://hub.docker.com/settings/security)

### Step 3: Push to Trigger CI/CD

```bash
git add .
git commit -m "Initial commit"
git push origin main
```

GitHub Actions will automatically:
- Build the Docker image
- Tag it with git SHA and `latest`
- Push to Docker Hub

### Step 4: Deploy Locally

**Local Development** (Build from source using docker-compose.dev.yml):

```bash
cd infra

# Build from ../app/Dockerfile and run
make run

# Force rebuild
make run-build

# Run on different port
make run PORT=8080
```

**Production Deployment** (Pull from Docker Hub using docker-compose.yml):

```bash
cd infra

# Interactive - prompts for version and validates on Docker Hub
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

# Non-interactive (for CI/CD scripts)
make deploy TAG=v1.0.0
```

**Other Commands**

```bash
# List available tags on Docker Hub
make list-tags

# Test the deployment
make test

# View logs
make logs

# Stop the container
make stop
```

## 🔌 API Endpoints

| Endpoint | Method | Description | Example |
|----------|--------|-------------|---------|
| `/` | GET | Service info | `curl http://localhost:8000/` |
| `/health` | GET | Health check | `curl http://localhost:8000/health` |
| `/hello` | GET | Hello message | `curl "http://localhost:8000/hello?name=Alice"` |

## 🏷️ Image Tagging Strategy

GitHub Actions generates the following tags:

| Event | Tags Generated |
|-------|----------------|
| Push to `main` | `latest`, `sha-{short-sha}` |
| Push tag `v1.0.0` | `1.0.0`, `1.0`, `latest` |
| Pull request | `pr-{number}` |

## 🛠️ Makefile Commands

### Local Development (docker-compose.dev.yml)
```bash
make run              # Build from ../app/ & start
make run-build        # Force rebuild & start
```

### Production Deployment (docker-compose.yml)
```bash
make deploy           # Interactive - prompts for version
make deploy TAG=v1.0.0 # Deploy specific version with validation
```

### Lifecycle Commands
```bash
make stop             # Stop all containers
make restart          # Restart services
make ps               # Container status
make logs             # View logs
```

### Utility
```bash
make test             # Test API endpoints
make list-tags        # List available tags on Docker Hub
make clean            # Remove containers and images
make help             # Show all commands
```

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `IMAGE_NAME` | `your-dockerhub-username/infra-practice-app` | Docker image name |
| `TAG` | `latest` | Image tag to deploy |
| `PORT` | `8000` | Local port mapping |

### Customizing

Edit `infra/Makefile` line 6 to set your Docker Hub username:

```makefile
IMAGE_NAME ?= yourusername/infra-practice-app
```

## 🧪 Testing

### Automated Test Script

```bash
# Make script executable and run
chmod +x scripts/test_api.sh
./scripts/test_api.sh
```

### Manual Testing

```bash
# Health check
curl -s http://localhost:8000/health | python -m json.tool

# Hello endpoint
curl -s http://localhost:8000/hello | python -m json.tool

# With name parameter
curl -s "http://localhost:8000/hello?name=Developer" | python -m json.tool
```

## 📝 Troubleshooting

### Image pull fails

```bash
# Check if image exists on Docker Hub
docker pull yourusername/infra-practice-app:sha-abc123

# Verify tag name matches exactly
```

### Port already in use

```bash
# Use a different port
make run TAG=sha-abc123 PORT=8080
```

### Container won't start

```bash
# Check logs
make logs

# Check container status
make status
```

## 📚 Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Dockerfile Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

## 🎓 What You'll Learn

1. **Containerization**: Building efficient Docker images
2. **CI/CD**: Automating builds with GitHub Actions
3. **Image Registry**: Publishing to Docker Hub
4. **Version Management**: Deploying specific image versions
5. **Local DevOps**: Using Make and Docker Compose for deployment

---

Happy learning! 🚀
