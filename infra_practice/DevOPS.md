# 🗺️ Realistic DevOps Learning Path — Step-by-Step Granular Guide

> **A-to-Z, concept-by-concept, command-by-command** guide. You should NOT need to search the web after reading this. Every topic includes: **concept explanation → why it matters → step-by-step practice → validation.**

---

## 📍 How to Use This Guide

1. **Read the concept first.** Understand the "why" before the "how."
2. **Type every command yourself.** Copy-paste teaches nothing.
3. **Break it.** Change values, delete things, see what errors you get.
4. **Build the deliverable.** Each phase ends with a project. Complete it before moving on.
5. **Time estimate:** 8–12 hours/week = 6–8 months total.

---

## Phase 1: Foundation (Weeks 1–2)

> **Goal:** Master the building blocks so deeply that using Docker, Git, and CI/CD becomes instinctive.

---

### Week 1, Day 1–2: How Docker Actually Works (Linux Internals)

#### Concept: Containers Are NOT VMs

A **Virtual Machine** includes an entire operating system with its own kernel. It virtualizes hardware.

A **Container** shares the host's Linux kernel. It virtualizes the **process** — not the hardware. Containers use three Linux kernel features:

1. **Namespaces** — Isolate what a process can *see* (process IDs, network, filesystem, users)
2. **cgroups (Control Groups)** — Limit what a process can *use* (CPU, memory, disk I/O)
3. **OverlayFS** — Provide a layered filesystem so each container gets its own writable layer on top of read-only image layers

> **Analogy:** A VM is like building a separate house. A container is like adding a partition wall inside an existing house — same foundation, separate rooms.

#### Why It Matters

If you don't understand this, you'll never debug container issues properly. When a container "escapes" or uses too much memory, you're debugging Linux kernel behavior — not Docker magic.

#### Step-by-Step Practice

> 🎯 **Purpose:** Understand that Docker images are made of stacked read-only layers. This demystifies how image sharing and caching work — when 50 containers use the same base image, they share the same underlying layers on disk.

**Step 1: See Docker's storage layers**

```bash
# Pull an image and inspect its layers
docker pull nginx:alpine
docker image inspect nginx:alpine --format='{{range .RootFS.Layers}}{{println .}}{{end}}'

# Each line is a SHA256 hash representing one layer
# These layers are stored on disk and shared between containers
```

> 🎯 **Purpose:** Connect abstract Docker concepts to real files on disk. When you run out of disk space or need to debug image corruption, you'll know exactly where to look.

**Step 2: Find where Docker stores layers on your machine**

```bash
# On macOS/Linux:
ls -la /var/lib/docker/overlay2/ 2>/dev/null || \
  ls -la ~/Library/Containers/com.docker.docker/Data/vms/0/data/ 2>/dev/null

# You'll see directories named with long hashes — each is a layer
```

> 🎯 **Purpose:** Prove to yourself that containers are just Linux features, not magic. This is the foundation for debugging container escapes, resource limits, and runtime issues in production.

**Step 3: Build a container manually with Linux primitives**

```bash
# Create a root filesystem from an Alpine image
mkdir -p /tmp/mycontainer/rootfs
docker export $(docker create alpine:latest) | tar -C /tmp/mycontainer/rootfs -xf -

# Create a cgroup for memory limiting
sudo cgcreate -g cpu,memory:/mycontainer

# Set a 100MB memory limit
echo 100000000 | sudo tee /sys/fs/cgroup/memory/mycontainer/memory.limit_in_bytes

# Run an isolated shell using unshare (creates namespaces)
sudo unshare --pid --net --mount --uts --ipc --fork --mount-proc \
  --root=/tmp/mycontainer/rootfs /bin/sh

# Inside this shell, run:
ps aux          # You are PID 1! Only see your own processes
hostname        # Hostname is isolated
ip addr         # Network is isolated (only loopback)
```

> 🎯 **Purpose:** See how Docker automates the same manual steps you just performed. This builds intuition for what Docker is actually doing under the hood when things go wrong.

**Step 4: Compare with `docker run`**

```bash
# In another terminal, compare:
docker run --rm -it --memory=100m alpine sh
ps aux
hostname
ip addr

# Docker is doing EXACTLY what you did manually:
# - unshare (namespaces)
# - cgcreate (cgroups)
# - overlay mount (filesystem)
# But automated and with a nice CLI
```

#### Validation Checklist

- [ ] Can you explain the difference between a VM and a container in one sentence?
- [ ] Can you list the 7 Linux namespaces Docker uses?
- [ ] Can you manually create an isolated process without `docker run`?
- [ ] Can you find a container's cgroup limits on the host filesystem?

---

### Week 1, Day 3–4: Dockerfile Mastery & Image Optimization

#### Concept: Image Layers & Caching

Every instruction in a Dockerfile creates a **read-only layer**. When you build, Docker caches each layer. If a layer hasn't changed, Docker reuses it.

**Layer order matters:** Put instructions that change LEAST often at the TOP. Put instructions that change MOST often at the BOTTOM.

```dockerfile
# BAD: Code changes often, but dependencies are reinstalled every time
COPY . /app           # ← Changes on every code edit
RUN pip install -r requirements.txt   # ← Must re-run because COPY changed

# GOOD: Dependencies change rarely, code changes often
COPY requirements.txt .   # ← Only changes when dependencies change
RUN pip install -r requirements.txt   # ← Cached most of the time
COPY . /app               # ← Only this layer rebuilds on code changes
```

#### Why It Matters

A poorly ordered Dockerfile means 5-minute builds instead of 10-second builds. In CI/CD, this costs money and slows developer feedback.

#### Step-by-Step Practice

> 🎯 **Purpose:** Learn to spot wasted space and poor layer ordering in Docker images. In production, bloated images slow deployments, increase storage costs, and expand the attack surface.

**Step 1: Analyze your current image with `dive`**

```bash
# Install dive (image analyzer)
brew install dive

# Analyze your infra_practice image
cd infra_practice/app
dive $(docker build -q .)

# Look for:
# - Red-colored layers (wasted space)
# - Layers with low "cache hit" potential
# - Large files that shouldn't be in the image
```

> 🎯 **Purpose:** Speed up CI/CD builds by caching package downloads between builds. This turns 5-minute dependency installs into 10-second cache hits, saving money and developer time.

**Step 2: Enable BuildKit and add cache mounts**

Edit `infra_practice/app/Dockerfile`:

```dockerfile
# syntax=docker/dockerfile:1
# ^ This enables BuildKit features

FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .

# Cache mount: pip downloads are cached between builds
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --user -r requirements.txt

FROM python:3.11-slim
WORKDIR /app

# Copy only installed packages, not build tools
COPY --from=builder /root/.local /root/.local
COPY . /app

ENV PATH=/root/.local/bin:$PATH
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build it:
```bash
DOCKER_BUILDKIT=1 docker build -t myapp:optimized .
```

> 🎯 **Purpose:** Reduce image size and attack surface by removing unnecessary tools and libraries. Smaller images deploy faster, start quicker, and contain fewer CVEs to patch.

**Step 3: Use a minimal base image**

```dockerfile
# Even smaller: use distroless or Wolfi
FROM cgr.dev/chainguard/python:latest-dev as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM cgr.dev/chainguard/python:latest
WORKDIR /app
COPY --from=builder /app/venv /app/venv
COPY . /app
ENV PATH="/app/venv/bin:$PATH"
USER nonroot
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

> 🎯 **Purpose:** Ensure your application runs on both Intel and ARM servers (including AWS Graviton and Apple Silicon). This prevents architecture mismatches when deploying across heterogeneous environments.

**Step 4: Build for multiple architectures**

```bash
# Create a buildx builder
docker buildx create --use --name multiarch || true

# Build for AMD64 and ARM64 (M1/M2 Macs, Graviton on AWS)
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t yourusername/infra-practice-app:latest \
  --push .
```

#### Validation Checklist

- [ ] Can you reduce your image size by at least 40%?
- [ ] Can you explain why `COPY requirements.txt` before `COPY .` matters?
- [ ] Can you build for both `amd64` and `arm64`?
- [ ] Can you scan your image for vulnerabilities with `trivy image myapp:optimized`?

---

### Week 1, Day 5: Docker Security Hardening

#### Concept: Defense in Depth for Containers

Containers are **not inherently secure**. They share the host kernel. A container escape vulnerability (like CVE-2024-21626) can give an attacker host access.

Defense layers:
1. **Image level:** Minimal base, no secrets, scanned for CVEs
2. **Runtime level:** Non-root user, read-only filesystem, dropped capabilities, seccomp
3. **Network level:** Custom bridge networks, no unnecessary port exposure

#### Step-by-Step Practice

> 🎯 **Purpose:** Prevent attackers who compromise your application from gaining root access on the host. Running as root inside a container is one of the most common and preventable security mistakes.

**Step 1: Run your container as non-root**

```bash
# Check: does your current image run as root?
docker run --rm yourimage id
# If it says "uid=0(root)", you have a problem.

# Fix: Add to Dockerfile
USER 65534:65534   # nobody:nobody
```

> 🎯 **Purpose:** Stop attackers from modifying binaries, installing malware, or changing configuration inside a compromised container. Writable root filesystems make persistence trivial for intruders.

**Step 2: Run with read-only root filesystem**

```bash
docker run -d \
  --read-only \
  --tmpfs /tmp:noexec,nosuid,size=100m \
  --tmpfs /var/tmp:noexec,nosuid,size=50m \
  --user 65534:65534 \
  -p 8000:8000 \
  yourimage
```

> 🎯 **Purpose:** Apply the principle of least privilege by removing unnecessary kernel powers from your container. Most applications need almost no special privileges to run.

**Step 3: Drop all Linux capabilities**

```bash
docker run -d \
  --cap-drop=ALL \
  --cap-add=NET_BIND_SERVICE \
  --security-opt no-new-privileges:true \
  -p 8000:8000 \
  yourimage
```

> 🎯 **Purpose:** Restrict which system calls your container can make, reducing the kernel attack surface. Seccomp is a critical last line of defense against container escape vulnerabilities.

**Step 4: Write and apply a custom seccomp profile**

```bash
# Download the default profile
curl -sL https://raw.githubusercontent.com/moby/moby/master/profiles/seccomp/default.json \
  > default-seccomp.json

# Run with it
docker run -d \
  --security-opt seccomp=default-seccomp.json \
  -p 8000:8000 \
  yourimage
```

> 🎯 **Purpose:** Catch known CVEs in your image before they reach production. Regular scanning is a non-negotiable part of any secure software supply chain.

**Step 5: Scan for vulnerabilities**

```bash
# Install trivy
brew install trivy

# Scan your image
trivy image --severity HIGH,CRITICAL yourimage

# Fix all HIGH and CRITICAL findings before production
```

#### Validation Checklist

- [ ] Can you run your container with `--read-only` without crashes?
- [ ] Can you run your container with `--cap-drop=ALL`?
- [ ] Are there zero HIGH/CRITICAL vulnerabilities in your image?
- [ ] Can you explain what `seccomp` does in one sentence?

---

### Week 1, Day 6–7: Docker Networking Deep Dive

#### Concept: Container Networking Is Linux Networking

Docker networking uses Linux primitives:
- **Network namespaces** — Each container gets its own network stack (interfaces, routes, firewall rules)
- **Virtual Ethernet pairs (veth)** — A virtual cable connecting the container namespace to the host bridge
- **Linux bridge (docker0)** — A virtual switch that connects containers on the same host
- **iptables NAT rules** — Docker manipulates iptables to route traffic from host ports to containers

#### Step-by-Step Practice

> 🎯 **Purpose:** Understand the default networking setup so you can diagnose connectivity issues and know when custom networks are needed.

**Step 1: Inspect the default bridge network**

```bash
# See Docker's default bridge
docker network inspect bridge

# Note the subnet (usually 172.17.0.0/16) and gateway (172.17.0.1)
# These are the defaults for the docker0 bridge on the host
```

> 🎯 **Purpose:** Enable container-to-container DNS resolution and network isolation. Custom networks are essential for microservices that need to discover and talk to each other securely.

**Step 2: Create a custom bridge network and observe DNS**

```bash
# Create a custom network
docker network create --driver bridge --subnet 172.28.0.0/16 mynet

# Run two containers on it
docker run -d --name web --network mynet nginx:alpine
docker run -d --name api --network mynet your-fastapi-image

# From the api container, ping web by NAME (DNS resolution!)
docker exec api ping -c 3 web

# This works because Docker's embedded DNS server (127.0.0.11)
# resolves container names to IPs on custom networks
```

> 🎯 **Purpose:** Map exactly how packets flow from the host into a container. This skill is essential for debugging port conflicts, firewall issues, and mysterious connection failures.

**Step 3: Trace the network path with `ip` and `iptables`**

```bash
# On the HOST (not inside container), find the veth pair
ip link show
# You'll see something like: vethabc123@if4 — this is one end of the virtual cable

# Find which container owns it
docker inspect -f '{{.State.Pid}}' web
sudo nsenter -t <PID> -n ip addr
# Compare interface indices to match veth pair

# See Docker's iptables NAT rules
sudo iptables -t nat -L -n -v | grep DOCKER
# These rules say: "if traffic comes to port 8000 on the host,
# DNAT it to the container's IP:8000"
```

> 🎯 **Purpose:** Implement network segmentation so that only authorized services can communicate. This limits blast radius if one service is compromised.

**Step 4: Create an isolated network for a microservices demo**

```bash
# frontend network (public-facing)
docker network create frontend

# backend network (database only)
docker network create backend

# Nginx: connected to frontend only
docker run -d --name nginx --network frontend nginx

# API: connected to BOTH frontend and backend
docker run -d --name api --network frontend your-api-image
docker network connect backend api

# Database: connected to backend ONLY
docker run -d --name postgres --network backend postgres

# Result: nginx cannot reach postgres directly.
# Only api can talk to both.
```

#### Validation Checklist

- [ ] Can you draw how a packet flows from `curl localhost:8000` to the container?
- [ ] Can you find the veth pair for a running container?
- [ ] Can you create a network where Container A can reach B, but B cannot reach C?
- [ ] Can you explain the difference between `bridge`, `host`, and `none` network modes?

---

### Week 2, Day 1–2: Git Deep Dive (Beyond `add/commit/push`)

#### Concept: Git Is a DAG (Directed Acyclic Graph)

Git doesn't store "changes." It stores **snapshots** of your entire project. Each commit is a node in a graph pointing to its parent(s).

Understanding this graph model is the key to mastering rebase, merge, and cherry-pick.

#### Step-by-Step Practice

> 🎯 **Purpose:** Develop a mental model of Git as a graph rather than a linear timeline. This makes rebase, merge, and conflict resolution intuitive instead of scary.

**Step 1: Visualize your Git history as a graph**

```bash
# The best git log format — memorize this alias
git log --oneline --graph --all --decorate

# Add it to your ~/.gitconfig:
# [alias]
#     lg = log --oneline --graph --all --decorate
```

> 🎯 **Purpose:** Clean up messy commit history before sharing code with your team. A clean history makes code reviews faster and `git bisect` actually useful when hunting bugs.

**Step 2: Interactive rebase — rewrite history safely**

```bash
# Scenario: You have 5 messy commits on a feature branch.
# You want to squash them into 2 clean commits.

git checkout feature-branch
git log --oneline -10

# Start interactive rebase on the last 5 commits
git rebase -i HEAD~5

# In the editor, change:
#   pick abc123 Add feature part 1
#   pick def456 Fix bug in part 1
#   pick ghi789 Add feature part 2
#   pick jkl012 WIP
#   pick mno345 Final fix
#
# To:
#   pick abc123 Add feature part 1
#   squash def456 Fix bug in part 1
#   pick ghi789 Add feature part 2
#   squash jkl012 WIP
#   squash mno345 Final fix
#
# Save and exit. Git will open another editor to write the combined commit message.
```

> 🎯 **Purpose:** Move individual commits between branches or safely undo changes without rewriting shared history. These are essential tools for hotfixes and production incident response.

**Step 3: Cherry-pick and revert**

```bash
# Cherry-pick: copy ONE commit from another branch to current branch
git cherry-pick abc123

# Revert: create a NEW commit that undoes an OLD commit (safe for shared history)
git revert abc123
```

> 🎯 **Purpose:** Save work-in-progress without committing half-baked code. Named stashes prevent the 'what was stash@{3} again?' confusion that wastes time during context switches.

**Step 4: Stash with named stashes**

```bash
# Don't just "git stash" — name your stashes!
git stash push -m "half-done refactoring of auth module"

# List stashes
git stash list

# Apply a specific stash
git stash apply stash@{2}
```

> 🎯 **Purpose:** Enforce code quality automatically so bad code never enters the repository. Pre-commit hooks catch formatting errors, type issues, and secrets before they waste CI time.

**Step 5: Git hooks for automation**

```bash
# Install pre-commit framework
pip install pre-commit

# Create .pre-commit-config.yaml in your repo:
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
  - repo: https://github.com/PyCQA/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.0.0
    hooks:
      - id: mypy
EOF

pre-commit install
pre-commit run --all-files
```

#### Validation Checklist

- [ ] Can you draw the Git DAG for a feature branch with 2 merge commits?
- [ ] Can you squash 5 commits into 2 without losing any changes?
- [ ] Can you recover a "lost" commit using `git reflog`?
- [ ] Can you set up pre-commit hooks that block commits with formatting errors?

---

### Week 2, Day 3–4: CI/CD with GitHub Actions (Production-Level)

#### Concept: CI/CD Is a Pipeline of Trust

Every code change goes through stages:
1. **Lint/Format** — Is the code well-formed?
2. **Test** — Does it behave correctly?
3. **Build** — Can we package it?
4. **Scan** — Is it secure?
5. **Deploy** — Can we push it to an environment?

Each stage is a **gate**. If any gate fails, the pipeline stops.

#### Step-by-Step Practice

> 🎯 **Purpose:** Ensure your code works across all supported Python versions before merging. Catching version-specific bugs in CI prevents production outages.

**Step 1: Create a matrix build (test multiple Python versions)**

```yaml
# .github/workflows/ci.yml
name: CI Pipeline

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11', '3.12']
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Cache pip dependencies
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run tests
        run: pytest -v
```

> 🎯 **Purpose:** Block deployments that contain known vulnerabilities. Shifting security left into CI is cheaper and faster than discovering CVEs in production.

**Step 2: Add security scanning gates**

```yaml
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'myapp:${{ github.sha }}'
          format: 'sarif'
          output: 'trivy-results.sarif'

      - name: Upload scan results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'
```

> 🎯 **Purpose:** Eliminate long-lived AWS credentials that can be leaked or stolen. OIDC lets GitHub Actions authenticate securely using short-lived tokens.

**Step 3: Build and push with OIDC (no long-lived secrets)**

```yaml
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789:role/GitHubActionsRole
          aws-region: us-east-1

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Build and push
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
        run: |
          docker build -t $ECR_REGISTRY/myapp:${{ github.sha }} .
          docker push $ECR_REGISTRY/myapp:${{ github.sha }}
```

> 🎯 **Purpose:** DRY up your CI configuration by sharing build logic across repositories. Reusable workflows reduce maintenance burden and enforce consistency.

**Step 4: Reusable workflows**

Create `.github/workflows/build-docker.yml`:
```yaml
name: Reusable Docker Build
on:
  workflow_call:
    inputs:
      image_name:
        required: true
        type: string
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t ${{ inputs.image_name }} .
```

Use it from another workflow:
```yaml
jobs:
  build:
    uses: ./.github/workflows/build-docker.yml
    with:
      image_name: myapp:latest
```

#### Validation Checklist

- [ ] Can you set up a matrix build for Python 3.9–3.12?
- [ ] Can you cache dependencies so CI runs in under 2 minutes?
- [ ] Can you scan Docker images for vulnerabilities in CI?
- [ ] Can you authenticate to AWS without storing long-lived secrets?

---

### Week 2, Day 5–7: Networking Fundamentals (OSI, TCP/IP, DNS, HTTP)

#### Concept: The OSI Model Is a Mental Framework

| Layer | Name | What It Does | Example |
|-------|------|-------------|---------|
| 7 | Application | Human-readable protocols | HTTP, HTTPS, SSH, FTP |
| 6 | Presentation | Data formatting, encryption | SSL/TLS, JSON, XML |
| 5 | Session | Connection management | TCP sessions, cookies |
| 4 | Transport | Reliable delivery | TCP, UDP, ports |
| 3 | Network | Routing between networks | IP, ICMP, routers |
| 2 | Data Link | Device-to-device on same network | Ethernet, MAC addresses, switches |
| 1 | Physical | Raw bits over wire/cable | Cables, fiber, Wi-Fi radio |

> **Docker containers operate at Layers 2–7.** They use Linux bridges (Layer 2), IP addresses (Layer 3), TCP/UDP ports (Layer 4), and HTTP (Layer 7).

#### Step-by-Step Practice

> 🎯 **Purpose:** See the full lifecycle of an HTTP request — from DNS to TLS to headers. This is your first diagnostic tool when APIs fail or behave unexpectedly.

**Step 1: Use `curl -v` to trace an HTTP request through the layers**

```bash
curl -v http://localhost:8000/health

# Observe:
# - TCP connection establishment (Layer 4)
# - TLS handshake if HTTPS (Layer 6)
# - HTTP request/response headers (Layer 7)
```

> 🎯 **Purpose:** Understand how domain names become IP addresses so you can diagnose resolution failures, cache issues, and TTL problems in production.

**Step 2: DNS resolution step by step**

```bash
# Step 1: Check local hosts file
cat /etc/hosts

# Step 2: Query DNS recursively
dig +trace google.com

# Step 3: See what your system resolver is using
scutil --dns  # macOS
systemd-resolve --status  # Linux

# Step 4: Query specific record types
dig A google.com         # IPv4 address
dig AAAA google.com      # IPv6 address
dig MX google.com        # Mail servers
dig TXT google.com       # Text records
dig NS google.com        # Name servers
```

> 🎯 **Purpose:** Identify which processes own which ports, spot connection leaks, and observe the TCP handshake. These tools are essential for debugging 'port already in use' and connection timeout errors.

**Step 3: TCP connection analysis with `netstat` and `ss`**

```bash
# See all listening ports
sudo ss -tlnp

# See established connections
ss -tn state established

# See which process owns a port
sudo lsof -i :8000

# Trace a full TCP handshake with tcpdump
sudo tcpdump -i lo port 8000 -nn -S
# Then in another terminal: curl http://localhost:8000
# Observe: SYN → SYN-ACK → ACK → DATA → FIN
```

> 🎯 **Purpose:** Calculate whether two IPs can talk directly or need a router. This is fundamental for designing VPCs, security groups, and network ACLs in the cloud.

**Step 4: Subnetting and CIDR**

```bash
# Calculate if two IPs are in the same subnet
# IP: 10.0.1.5/24
# Subnet mask: /24 = 255.255.255.0
# Network: 10.0.1.0
# Range: 10.0.1.1 - 10.0.1.254

# Can 10.0.1.5 talk to 10.0.2.5 with /24?
# NO — they're on different networks (10.0.1.0 vs 10.0.2.0)

# Practice with ipcalc
brew install ipcalc
ipcalc 10.0.1.5/24
ipcalc 192.168.0.0/16
```

> 🎯 **Purpose:** Distribute traffic across multiple backend instances and terminate TLS in one place. Reverse proxies are the entry point to almost every production web architecture.

**Step 5: Set up Nginx as a reverse proxy (Layer 7 load balancing)**

```bash
# Create nginx.conf
cat > nginx.conf << 'EOF'
upstream backend {
    server localhost:8001;
    server localhost:8002;
    server localhost:8003;
}

server {
    listen 80;
    location / {
        proxy_pass http://backend;
    }
}
EOF

# Run Nginx
docker run -d -p 80:80 -v $(pwd)/nginx.conf:/etc/nginx/conf.d/default.conf nginx

# Now requests to port 80 are load-balanced across 3 backend instances
```

#### Validation Checklist

- [ ] Can you explain what happens at each OSI layer when you `curl google.com`?
- [ ] Can you trace a DNS query from start to finish?
- [ ] Can you identify which process is listening on port 8080?
- [ ] Can you calculate if two IPs are in the same /24 subnet?
- [ ] Can you set up an Nginx reverse proxy to 3 backend servers?

---

### Phase 1 Deliverable

Build and push to GitHub:
1. An optimized, hardened Dockerfile (multi-stage, distroless, non-root, scanned)
2. A GitHub Actions CI pipeline with: matrix builds, caching, security scanning, ECR push
3. A `docker-compose.yml` with custom networks and health checks
4. An Nginx reverse proxy config
5. A pre-commit hook config for code quality

**Do NOT proceed to Phase 2 until these are done.**

---


## Phase 2: Core DevOps Skills (Weeks 3–10)

> **Goal:** Build the infrastructure engineer's core toolkit — Linux, Cloud, IaC, and automation.

---

### Week 3, Day 1–2: Linux Filesystem, Permissions & Process Management

#### Concept: Everything in Linux Is a File

In Linux, **everything** is a file:
- Regular files (`-`) — text, binary, images
- Directories (`d`) — containers for files
- Links (`l`) — pointers to other files
- Devices (`c` or `b`) — hardware interfaces (`/dev/sda`, `/dev/null`)
- Sockets (`s`) — network endpoints
- Pipes (`p`) — inter-process communication

The **Filesystem Hierarchy Standard (FHS)** defines where things go:
| Path | Purpose |
|------|---------|
| `/` | Root filesystem |
| `/bin` | Essential user binaries (ls, cp, mv) |
| `/sbin` | System binaries (fdisk, mkfs, reboot) |
| `/etc` | Configuration files |
| `/var` | Variable data (logs, caches, mail) |
| `/tmp` | Temporary files (cleared on reboot) |
| `/proc` | Virtual filesystem — process info and kernel state |
| `/sys` | Virtual filesystem — kernel objects and devices |
| `/dev` | Device files |
| `/usr` | User programs, libraries |
| `/opt` | Optional add-on software |
| `/home` | User home directories |

#### Step-by-Step Practice

> 🎯 **Purpose:** Learn to read kernel state in real time without special tools. `/proc` and `/sys` are indispensable for debugging performance, hardware, and process issues.

**Step 1: Explore `/proc` and `/sys`**

```bash
# See CPU info (pulled from kernel in real-time)
cat /proc/cpuinfo | grep "model name" | head -1

# See memory info
cat /proc/meminfo | grep MemTotal

# See your own process info
ls /proc/$$
cat /proc/$$/cmdline
cat /proc/$$/status | grep -E "Uid|Gid|VmRSS"

# See kernel modules
ls /sys/module/
```

> 🎯 **Purpose:** Control exactly who can read, write, or execute files. Misconfigured permissions are a leading cause of both security breaches and deployment failures.

**Step 2: Master permissions with chmod, chown, and ACLs**

```bash
# Create a test file
touch permissions.txt
ls -l permissions.txt
# Output: -rw-r--r-- 1 user group 0 date permissions.txt

# Change permissions with symbolic notation
chmod u+x permissions.txt    # Add execute for owner
chmod go-w permissions.txt   # Remove write for group and others
chmod a+r permissions.txt    # Add read for all

# Change permissions with octal notation
chmod 600 permissions.txt    # rw------- (owner only)
chmod 755 permissions.txt    # rwxr-xr-x (standard executable)
chmod 644 permissions.txt    # rw-r--r-- (standard file)
chmod 777 permissions.txt    # rwxrwxrwx (avoid this!)

# Special bits
chmod u+s myprogram          # SUID: run as file owner (like sudo)
chmod g+s mydir              # SGID: new files inherit group
chmod +t mydir               # Sticky bit: only owner can delete their files

# ACLs (Access Control Lists) for granular permissions
setfacl -m u:alice:rwx mydir   # Give alice full access
setfacl -m u:bob:r mydir       # Give bob read-only
getfacl mydir                   # View ACLs
```

> 🎯 **Purpose:** Find, signal, and control running processes on a Linux system. Whether an app is stuck, consuming too much CPU, or needs graceful restart, these commands save the day.

**Step 3: Process management**

```bash
# List all processes with full details
ps aux

# Find processes using the most CPU/memory
top -o %CPU
htop  # (install with: brew install htop)

# Find a specific process
pgrep -a python
pgrep -f uvicorn

# Send signals to processes
kill -15 <PID>   # SIGTERM — polite shutdown (default)
kill -9 <PID>    # SIGKILL — force kill (last resort)
kill -1 <PID>    # SIGHUP — reload config

# Run a process in background
python main.py &
bg
fg %1

# nohup — survive terminal logout
nohup python main.py > app.log 2>&1 &
```

> 🎯 **Purpose:** Ensure your application starts on boot, restarts on crash, and logs properly. Systemd is the standard for production service management on virtually all Linux distributions.

**Step 4: Systemd — the modern Linux init system**

```bash
# Check Docker service status
systemctl status docker

# Create a systemd service for YOUR app
sudo tee /etc/systemd/system/myapp.service << 'EOF'
[Unit]
Description=My FastAPI App
After=network.target

[Service]
Type=simple
User=appuser
WorkingDirectory=/opt/myapp
ExecStart=/opt/myapp/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5
Environment=LOG_LEVEL=info

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable myapp
sudo systemctl start myapp
sudo systemctl status myapp
journalctl -u myapp -f  # Watch logs
```

#### Validation Checklist

- [ ] Can you explain what `/proc/$$` contains?
- [ ] Can you set up a shared directory where 3 users can collaborate?
- [ ] Can you write a systemd service that auto-restarts on crash?
- [ ] Can you explain the difference between SIGTERM and SIGKILL?

---

### Week 3, Day 3–4: Shell Scripting Mastery

#### Concept: Bash Is the Glue of DevOps

Every time you automate a deployment, rotate logs, or check health — you're writing a script. Bash is the universal automation language on Linux.

#### Step-by-Step Practice

> 🎯 **Purpose:** Write scripts that handle filenames with spaces and special characters correctly. Quoting mistakes are among the most common and dangerous shell scripting bugs.

**Step 1: Variables and quoting**

```bash
#!/bin/bash
set -euo pipefail  # Best practice: exit on error, undefined vars, pipe failures

# Variables
name="DevOps"
echo "Hello, $name"      # Double quotes: variable expansion
echo 'Hello, $name'      # Single quotes: literal string

# Command substitution (modern syntax)
current_date=$(date +%Y-%m-%d)
file_count=$(ls -1 | wc -l)

# Default values
port="${PORT:-8000}"     # Use $PORT if set, otherwise 8000
env="${ENV:-development}"

# Arrays
services=("nginx" "postgres" "redis")
echo "First service: ${services[0]}"
echo "All services: ${services[@]}"
echo "Count: ${#services[@]}"
```

> 🎯 **Purpose:** Make scripts make decisions — check files, handle arguments, loop over servers. Real deployments require conditional logic, not just sequential commands.

**Step 2: Control flow**

```bash
#!/bin/bash
set -euo pipefail

# if/else with file checks
if [ -f "docker-compose.yml" ]; then
    echo "Compose file exists"
elif [ -d "infra/" ]; then
    echo "Infra directory exists"
else
    echo "Nothing found"
fi

# case statement
case "$1" in
    start)
        echo "Starting..."
        ;;
    stop)
        echo "Stopping..."
        ;;
    restart)
        echo "Restarting..."
        ;;
    *)
        echo "Usage: $0 {start|stop|restart}"
        exit 1
        ;;
esac

# for loops
for svc in nginx postgres redis; do
    echo "Checking $svc..."
done

# while loop with counter
counter=0
while [ $counter -lt 5 ]; do
    echo "Iteration $counter"
    ((counter++))
done

# Reading files line by line
while IFS= read -r line; do
    echo "Line: $line"
done < "servers.txt"
```

> 🎯 **Purpose:** Build reusable, robust scripts that fail fast and clean up after themselves. `set -euo pipefail` and trap handlers separate professional scripts from fragile one-liners.

**Step 3: Functions and error handling**

```bash
#!/bin/bash
set -euo pipefail

# Logging function
log() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message"
}

# Health check function
check_health() {
    local url="$1"
    local max_retries="${2:-3}"
    local retry=0

    while [ $retry -lt $max_retries ]; do
        if curl -sf "$url" > /dev/null 2>&1; then
            log "INFO" "Health check passed: $url"
            return 0
        fi
        retry=$((retry + 1))
        log "WARN" "Health check failed (attempt $retry/$max_retries)"
        sleep 2
    done

    log "ERROR" "Health check failed after $max_retries attempts"
    return 1
}

# Trap for cleanup
cleanup() {
    log "INFO" "Cleaning up temporary files..."
    rm -f /tmp/myapp_*.tmp
}
trap cleanup EXIT

# Main
log "INFO" "Starting deployment..."
check_health "http://localhost:8000/health" 5 || exit 1
log "INFO" "Deployment complete!"
```

> 🎯 **Purpose:** Extract and transform data from logs, configs, and APIs without writing a full program. These tools are the Swiss Army knives of DevOps troubleshooting.

**Step 4: Text processing — grep, sed, awk, jq**

```bash
# grep: find patterns
grep "ERROR" app.log                    # Find ERROR lines
grep -v "DEBUG" app.log                 # Exclude DEBUG lines
grep -E "ERROR|FATAL" app.log           # Multiple patterns
grep -i "error" app.log                 # Case-insensitive

# sed: stream editor
sed 's/localhost/0.0.0.0/g' config.txt  # Replace all occurrences
sed -n '10,20p' file.txt                # Print lines 10-20 only
sed '/^#/d' config.txt                  # Delete comment lines

# awk: column processing
awk '{print $1}' access.log             # Print first column
awk -F: '{print $1}' /etc/passwd        # Use : as delimiter
awk '$9 >= 400 {print $1, $7, $9}' access.log  # Filter by status code

# jq: JSON processing
curl -s http://localhost:8000/health | jq '.'
curl -s http://localhost:8000/health | jq '.status'
curl -s http://localhost:8000/health | jq -r '.timestamp'

# Practical: Parse docker ps output
docker ps --format '{{.Names}}\t{{.Status}}' | awk -F'\t' '{print "Container:", $1, "| Status:", $2}'
```

#### Validation Checklist

- [ ] Can you write a script that checks if a service is healthy, retries 3 times, and logs everything?
- [ ] Can you parse a log file and extract all unique IP addresses?
- [ ] Can you use `jq` to extract nested JSON fields from an API response?
- [ ] Can you explain what `set -euo pipefail` does and why it's important?

---

### Week 3, Day 5–7: Linux Networking from the Command Line

#### Concept: Linux Networking Is Configured via Files and Commands

Everything you see in Docker networking (`docker network`, port mapping, DNS) is built on Linux networking primitives. Understanding these primitives makes you a better troubleshooter.

#### Step-by-Step Practice

> 🎯 **Purpose:** Inspect and manipulate the network configuration of any Linux host. This is the first step when a server can't reach the internet or another service.

**Step 1: Network interfaces and IP addresses**

```bash
# Show all network interfaces
ip addr show

# Show specific interface
ip addr show eth0

# Show routing table
ip route show

# Show ARP table (IP to MAC mapping)
ip neigh show

# Bring interface up/down
sudo ip link set eth0 down
sudo ip link set eth0 up
```

> 🎯 **Purpose:** Control exactly what traffic is allowed in, out, and through your systems. iptables (and its successors nftables/firewalld) are the backbone of Linux network security.

**Step 2: iptables — Linux firewall**

```bash
# Show all rules
sudo iptables -L -n -v

# Show NAT rules (what Docker uses for port forwarding)
sudo iptables -t nat -L -n -v

# Add a rule: block incoming traffic on port 3306 (MySQL)
sudo iptables -A INPUT -p tcp --dport 3306 -j DROP

# Add a rule: allow SSH only from one IP
sudo iptables -A INPUT -p tcp -s 192.168.1.100 --dport 22 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 22 -j DROP

# Save rules (Debian/Ubuntu)
sudo apt-get install iptables-persistent
sudo netfilter-persistent save
```

> 🎯 **Purpose:** Pinpoint why a hostname won't resolve — whether it's a local config issue, DNS server problem, or cached stale record. DNS is the #1 cause of mysterious connectivity issues.

**Step 3: DNS troubleshooting**

```bash
# Check your DNS resolver
cat /etc/resolv.conf

# Query DNS directly
dig @8.8.8.8 google.com         # Use Google's DNS
dig +trace google.com            # Full recursive trace

# Check DNS cache
sudo systemd-resolve --statistics

# Test DNS resolution time
dig +stats google.com | grep "Query time"
```

> 🎯 **Purpose:** See the actual bytes on the wire to debug protocol errors, dropped packets, and latency. tcpdump is the definitive tool when application logs aren't enough.

**Step 4: Packet capture with tcpdump**

```bash
# Capture all traffic on port 8000
sudo tcpdump -i any port 8000 -nn

# Capture to file, then analyze
sudo tcpdump -i any -w capture.pcap
# Open with Wireshark, or:
tcpdump -r capture.pcap

# Capture only SYN packets (connection attempts)
sudo tcpdump -i any 'tcp[tcpflags] & tcp-syn != 0'
```

> 🎯 **Purpose:** Test connectivity, send manual requests, and build simple network servers. Netcat is the fastest way to verify if a port is open or a service is responding.

**Step 5: Netcat — the network swiss army knife**

```bash
# Test if a port is open
nc -zv localhost 8000

# Start a simple TCP server
nc -l 9999
# In another terminal:
echo "Hello" | nc localhost 9999

# Port scan a host
nc -zv localhost 8000-8010
```

#### Validation Checklist

- [ ] Can you find your default gateway?
- [ ] Can you block a port with iptables and verify it's blocked?
- [ ] Can you capture and analyze HTTP traffic with tcpdump?
- [ ] Can you diagnose a DNS resolution failure?

---

### Week 4, Day 1–7: Build 10 Bash Scripts (The Linux Deliverable)

Create a `scripts/` directory in your repo. Write and test each script:

| # | Script Name | What It Does | Concepts Practiced |
|---|-------------|-------------|-------------------|
| 1 | `health_check.sh` | Calls `/health` endpoint, retries 3x, exits with error code on failure | curl, loops, functions, exit codes |
| 2 | `backup_logs.sh` | Compresses `/var/log/app/` into dated tar.gz, deletes files older than 7 days | tar, find, cron, date |
| 3 | `deploy.sh` | Pulls latest Docker image, stops old container, starts new one | docker CLI, error handling, rollback |
| 4 | `disk_usage_alert.sh` | Checks disk usage, sends alert (echo) if above 80% | df, awk, conditionals |
| 5 | `parse_access_log.sh` | Parses Nginx access log, shows top 10 IPs and status code distribution | awk, sort, uniq, regex |
| 6 | `rotate_secrets.sh` | Rotates database password, updates environment file | openssl, file manipulation |
| 7 | `port_scanner.sh` | Scans a range of ports on a host, reports which are open | nc, loops, parallel processing |
| 8 | `sync_to_s3.sh` | Syncs a local directory to S3 using AWS CLI | aws cli, error handling, logging |
| 9 | `cleanup_docker.sh` | Removes unused images, volumes, networks, containers | docker system prune, filtering |
| 10 | `setup_server.sh` | Idempotent server setup: updates packages, installs Docker, creates user | package managers, idempotency, conditionals |

**Each script must:**
- Start with `#!/bin/bash` and `set -euo pipefail`
- Include a `--help` flag
- Log with timestamps
- Handle errors gracefully
- Include comments explaining each section

#### Validation Checklist

- [ ] Can you run all 10 scripts without errors?
- [ ] Can you run `shellcheck script.sh` on each and fix all warnings? (`brew install shellcheck`)
- [ ] Can you schedule `backup_logs.sh` with a systemd timer or cron?

---

### Week 5, Day 1–2: AWS Fundamentals — IAM, VPC, EC2

#### Concept: AWS Is API-Driven Infrastructure

Everything in AWS is an API call. The console is just a pretty wrapper around REST APIs. The CLI and Terraform call the same APIs.

#### Step-by-Step Practice

> 🎯 **Purpose:** Establish a secure, scriptable connection to AWS so you can automate infrastructure instead of clicking through the console.

**Step 1: Set up AWS CLI and configure credentials**

```bash
# Install AWS CLI
brew install awscli

# Configure (use Access Key from IAM console)
aws configure
# Enter: AWS Access Key ID
# Enter: AWS Secret Access Key
# Enter: Default region (e.g., us-east-1)
# Enter: Output format (json)

# Verify
aws sts get-caller-identity
```

> 🎯 **Purpose:** Implement the principle of least privilege in AWS. Proper IAM configuration prevents costly data breaches and accidental resource deletions.

**Step 2: IAM — Users, Groups, Roles, Policies**

```bash
# Create an IAM group for developers
aws iam create-group --group-name Developers

# Create a policy (JSON file)
cat > dev-policy.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeInstances",
                "ec2:DescribeVolumes"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": "s3:ListBucket",
            "Resource": "arn:aws:s3:::my-app-bucket"
        }
    ]
}
EOF

aws iam create-policy --policy-name DevReadOnly --policy-document file://dev-policy.json

# Attach policy to group
aws iam attach-group-policy \
    --group-name Developers \
    --policy-arn arn:aws:iam::123456789:policy/DevReadOnly

# Create a role for EC2 to access S3
cat > trust-policy.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {"Service": "ec2.amazonaws.com"},
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF

aws iam create-role --role-name EC2S3Access --assume-role-policy-document file://trust-policy.json
```

> 🎯 **Purpose:** Design isolated network environments with public and private subnets. This is the networking foundation for every secure, scalable AWS architecture.

**Step 3: VPC — Virtual Private Cloud**

```bash
# Create a VPC
aws ec2 create-vpc --cidr-block 10.0.0.0/16 --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=MyVPC}]'

# Note the VPC ID from output
VPC_ID="vpc-xxxxxxxx"

# Create public subnet
aws ec2 create-subnet \
    --vpc-id $VPC_ID \
    --cidr-block 10.0.1.0/24 \
    --availability-zone us-east-1a \
    --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=PublicSubnet}]'

# Create private subnet
aws ec2 create-subnet \
    --vpc-id $VPC_ID \
    --cidr-block 10.0.2.0/24 \
    --availability-zone us-east-1a \
    --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=PrivateSubnet}]'

# Create Internet Gateway and attach to VPC
aws ec2 create-internet-gateway --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=MyIGW}]'
aws ec2 attach-internet-gateway --internet-gateway-id igw-xxxxxxxx --vpc-id $VPC_ID

# Create route table for public subnet
aws ec2 create-route-table --vpc-id $VPC_ID
aws ec2 create-route --route-table-id rtb-xxxxxxxx --destination-cidr-block 0.0.0.0/0 --gateway-id igw-xxxxxxxx
aws ec2 associate-route-table --route-table-id rtb-xxxxxxxx --subnet-id subnet-xxxxxxxx
```

> 🎯 **Purpose:** Provision your first compute resource and understand how security groups, subnets, and key pairs work together. EC2 is the building block of most AWS workloads.

**Step 4: Launch an EC2 instance**

```bash
# Create a security group
aws ec2 create-security-group \
    --group-name MyAppSG \
    --description "Security group for my app" \
    --vpc-id $VPC_ID

# Allow SSH (port 22) and HTTP (port 80)
aws ec2 authorize-security-group-ingress \
    --group-id sg-xxxxxxxx \
    --protocol tcp --port 22 --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
    --group-id sg-xxxxxxxx \
    --protocol tcp --port 80 --cidr 0.0.0.0/0

# Launch instance
aws ec2 run-instances \
    --image-id ami-0c55b159cbfafe1f0 \
    --instance-type t2.micro \
    --key-name MyKeyPair \
    --security-group-ids sg-xxxxxxxx \
    --subnet-id subnet-xxxxxxxx \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=MyAppServer}]'
```

#### Validation Checklist

- [ ] Can you create a VPC with public and private subnets from the CLI?
- [ ] Can you launch an EC2 instance and SSH into it?
- [ ] Can you create an IAM role and attach it to an EC2 instance?
- [ ] Can you explain the difference between a security group and a NACL?

---

### Week 5, Day 3–4: AWS Core Services — S3, RDS, ALB

#### Step-by-Step Practice

> 🎯 **Purpose:** Store files durably and cost-effectively with versioning, lifecycle policies, and access controls. S3 is the default object store for backups, assets, and data lakes.

**Step 1: S3 — Simple Storage Service**

```bash
# Create a bucket (names must be globally unique)
aws s3 mb s3://my-unique-app-bucket-12345 --region us-east-1

# Upload a file
aws s3 cp app.zip s3://my-unique-app-bucket-12345/

# Enable versioning
aws s3api put-bucket-versioning \
    --bucket my-unique-app-bucket-12345 \
    --versioning-configuration Status=Enabled

# Set lifecycle policy (delete old versions after 30 days)
cat > lifecycle.json << 'EOF'
{
    "Rules": [
        {
            "ID": "DeleteOldVersions",
            "Status": "Enabled",
            "NoncurrentVersionExpiration": {"NoncurrentDays": 30}
        }
    ]
}
EOF
aws s3api put-bucket-lifecycle-configuration \
    --bucket my-unique-app-bucket-12345 \
    --lifecycle-configuration file://lifecycle.json

# Block all public access
aws s3api put-public-access-block \
    --bucket my-unique-app-bucket-12345 \
    --public-access-block-configuration \
    "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
```

> 🎯 **Purpose:** Offload database administration (backups, patching, failover) to AWS so your team can focus on application logic. RDS is the production standard for relational databases in the cloud.

**Step 2: RDS — Managed Database**

```bash
# Create a DB subnet group (needs 2 AZs)
aws rds create-db-subnet-group \
    --db-subnet-group-name my-db-subnet-group \
    --db-subnet-group-description "Subnets for RDS" \
    --subnet-ids '["subnet-public-xxx","subnet-private-xxx"]'

# Create a PostgreSQL instance
aws rds create-db-instance \
    --db-instance-identifier my-postgres \
    --db-instance-class db.t3.micro \
    --engine postgres \
    --master-username dbadmin \
    --master-user-password 'SuperSecretPassword123!' \
    --allocated-storage 20 \
    --vpc-security-group-ids sg-xxxxxxxx \
    --db-subnet-group-name my-db-subnet-group

# Wait for it to be available
aws rds wait db-instance-available --db-instance-identifier my-postgres

# Get the endpoint
aws rds describe-db-instances \
    --db-instance-identifier my-postgres \
    --query 'DBInstances[0].Endpoint.Address'
```

> 🎯 **Purpose:** Distribute HTTP traffic across multiple servers with health checks and automatic failover. ALBs are the entry point for scalable, highly available web applications.

**Step 3: Application Load Balancer (ALB)**

```bash
# Create ALB
aws elbv2 create-load-balancer \
    --name my-alb \
    --subnets subnet-public-1 subnet-public-2 \
    --security-groups sg-xxxxxxxx \
    --scheme internet-facing

# Create target group
aws elbv2 create-target-group \
    --name my-targets \
    --protocol HTTP --port 8000 \
    --vpc-id $VPC_ID \
    --health-check-path /health

# Register targets (EC2 instances)
aws elbv2 register-targets \
    --target-group-arn arn:aws:elasticloadbalancing:... \
    --targets Id=i-xxxxxxxx Id=i-yyyyyyyy

# Create listener
aws elbv2 create-listener \
    --load-balancer-arn arn:aws:elasticloadbalancing:... \
    --protocol HTTP --port 80 \
    --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:...
```

#### Validation Checklist

- [ ] Can you create an S3 bucket with versioning and lifecycle rules?
- [ ] Can you launch an RDS instance and connect from your EC2 instance?
- [ ] Can you set up an ALB that routes traffic to 2 EC2 instances?

---

### Week 6, Day 1–7: AWS Project — 3-Tier Architecture

Build this manually via AWS CLI or Console, then document every step:

```
Internet
    |
    v
[ ALB ]  (public subnets in 2 AZs)
    |
    v
[ EC2 Auto Scaling Group ]  (min: 2, max: 4)
    |    Docker + your FastAPI app
    v
[ RDS PostgreSQL ]  (private subnet, Multi-AZ)
    |
    v
[ S3 ]  (static assets, backups)
```

**Components to build:**
1. VPC with public and private subnets across 2 AZs
2. Internet Gateway + NAT Gateway (for private subnet outbound)
3. Security groups: ALG, EC2, RDS (least privilege)
4. RDS PostgreSQL in private subnet
5. EC2 Launch Template with user-data that installs Docker and runs your app
6. Auto Scaling Group with target tracking (CPU > 60%)
7. ALB with health checks on `/health`
8. S3 bucket for app logs
9. CloudWatch alarms for CPU, disk, and RDS connections

**Deliverable:** A working URL that serves your FastAPI app, load-balanced across 2+ instances, backed by RDS.

#### Validation Checklist

- [ ] Can you access your app via the ALB DNS name?
- [ ] If you terminate one EC2 instance, does Auto Scaling replace it?
- [ ] Can you connect to RDS only from EC2 instances (not from internet)?
- [ ] Are logs being sent to S3 or CloudWatch?

---


### Week 7, Day 1–3: Terraform Fundamentals

#### Concept: Terraform Is Declarative Infrastructure

With **imperative** tools (AWS CLI, Ansible), you say: *"Create a VPC, then create a subnet, then launch an EC2."*

With **declarative** tools (Terraform), you say: *"I want a VPC, a subnet, and an EC2. Figure out the order and make it so."*

Terraform maintains a **state file** that maps your configuration to real-world resources. This state is the source of truth.

#### Step-by-Step Practice

> 🎯 **Purpose:** Experience the power of declarative infrastructure — describe what you want, and Terraform figures out how to create it.

**Step 1: Install Terraform and create your first resource**

```bash
# Install
brew install terraform

# Verify
terraform version

# Create a project directory
mkdir -p ~/terraform-aws-lab && cd ~/terraform-aws-lab

# Create main.tf
cat > main.tf << 'EOF'
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

resource "aws_s3_bucket" "my_bucket" {
  bucket = "my-terraform-lab-bucket-12345"
}
EOF

# Initialize (downloads provider plugins)
terraform init

# Preview changes
terraform plan

# Apply
terraform apply

# Destroy when done
terraform destroy
```

> 🎯 **Purpose:** Make your Terraform code reusable and composable across environments. Hardcoded values don't scale; variables and outputs enable team-wide collaboration.

**Step 2: Variables and outputs**

```bash
cat > variables.tf << 'EOF'
variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "bucket_name" {
  description = "Name of the S3 bucket"
  type        = string
}

variable "enable_versioning" {
  description = "Enable S3 versioning"
  type        = bool
  default     = true
}
EOF

cat > outputs.tf << 'EOF'
output "bucket_arn" {
  description = "ARN of the S3 bucket"
  value       = aws_s3_bucket.my_bucket.arn
}

output "bucket_id" {
  description = "ID of the S3 bucket"
  value       = aws_s3_bucket.my_bucket.id
}
EOF

# Update main.tf to use variables
# resource "aws_s3_bucket" "my_bucket" {
#   bucket = var.bucket_name
# }

# Apply with variables
terraform apply -var="bucket_name=my-custom-bucket"
```

> 🎯 **Purpose:** Prevent conflicts and state loss when multiple team members run Terraform simultaneously. Remote state with locking is mandatory for any production Terraform workflow.

**Step 3: Remote state with S3 + DynamoDB locking**

```bash
cat > backend.tf << 'EOF'
terraform {
  backend "s3" {
    bucket         = "my-terraform-state-bucket"
    key            = "infra/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}
EOF

# Create the state bucket and lock table FIRST (bootstrap)
aws s3 mb s3://my-terraform-state-bucket
aws dynamodb create-table \
    --table-name terraform-locks \
    --attribute-definitions AttributeName=LockID,AttributeType=S \
    --key-schema AttributeName=LockID,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST

# Now reinitialize with remote backend
terraform init
```

> **Why remote state?** Teams share state. If two people run Terraform simultaneously, they might create duplicate resources or delete each other's work. S3 stores the state; DynamoDB provides locking so only one person can run Terraform at a time.

#### Validation Checklist

- [ ] Can you create an S3 bucket with Terraform?
- [ ] Can you use variables to make your code reusable?
- [ ] Can you set up remote state with S3 and DynamoDB locking?
- [ ] Can you explain why `terraform plan` is important before `apply`?

---

### Week 7, Day 4–7: Terraform Intermediate — Modules, Loops, Conditionals

#### Step-by-Step Practice

> 🎯 **Purpose:** Package infrastructure patterns into reusable components. Modules turn 500 lines of VPC code into a 5-line reference that your whole team can use.

**Step 1: Create reusable modules**

```bash
mkdir -p modules/vpc

# modules/vpc/main.tf
cat > modules/vpc/main.tf << 'EOF'
resource "aws_vpc" "this" {
  cidr_block           = var.cidr_block
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = var.name
  }
}

resource "aws_subnet" "public" {
  count             = length(var.availability_zones)
  vpc_id            = aws_vpc.this.id
  cidr_block        = cidrsubnet(var.cidr_block, 8, count.index)
  availability_zone = var.availability_zones[count.index]

  map_public_ip_on_launch = true

  tags = {
    Name = "${var.name}-public-${count.index + 1}"
    Type = "public"
  }
}

resource "aws_internet_gateway" "this" {
  vpc_id = aws_vpc.this.id

  tags = {
    Name = "${var.name}-igw"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.this.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.this.id
  }

  tags = {
    Name = "${var.name}-public-rt"
  }
}

resource "aws_route_table_association" "public" {
  count          = length(aws_subnet.public)
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}
EOF

# modules/vpc/variables.tf
cat > modules/vpc/variables.tf << 'EOF'
variable "name" {
  type = string
}

variable "cidr_block" {
  type    = string
  default = "10.0.0.0/16"
}

variable "availability_zones" {
  type    = list(string)
  default = ["us-east-1a", "us-east-1b"]
}
EOF

# modules/vpc/outputs.tf
cat > modules/vpc/outputs.tf << 'EOF'
output "vpc_id" {
  value = aws_vpc.this.id
}

output "public_subnet_ids" {
  value = aws_subnet.public[*].id
}
EOF
```

> 🎯 **Purpose:** Consume your own modules to build complex infrastructure from simple, tested building blocks. This is how mature platform teams enable developer self-service.

**Step 2: Use the module**

```bash
cat > main.tf << 'EOF'
module "vpc" {
  source             = "./modules/vpc"
  name               = "my-app"
  cidr_block         = "10.0.0.0/16"
  availability_zones = ["us-east-1a", "us-east-1b"]
}

resource "aws_security_group" "app" {
  name        = "app-sg"
  description = "Security group for app servers"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
EOF

terraform init
terraform plan
terraform apply
```

> 🎯 **Purpose:** Manage dev, staging, and prod from the same codebase without copy-paste. Workspaces reduce drift between environments and deployment mistakes.

**Step 3: Terraform workspaces (environment separation)**

```bash
# Create workspaces for each environment
terraform workspace new dev
terraform workspace new staging
terraform workspace new prod

# Switch workspace
terraform workspace select dev

# The workspace name is available as terraform.workspace
# Use it in your code:
# resource "aws_instance" "app" {
#   tags = {
#     Environment = terraform.workspace
#   }
# }
```

> 🎯 **Purpose:** Catch misconfigurations, security issues, and cost surprises before applying. Automated validation is how you keep infrastructure quality high at scale.

**Step 4: Terraform testing and validation**

```bash
# Format code
terraform fmt -recursive

# Validate syntax
terraform validate

# Security scanning with tfsec
brew install tfsec
tfsec .

# Cost estimation with Infracost
brew install infracost
infracost breakdown --path .
```

#### Validation Checklist

- [ ] Can you create a reusable VPC module?
- [ ] Can you use `count` and `for_each` to create multiple resources?
- [ ] Can you manage dev/staging/prod with workspaces?
- [ ] Can you run `tfsec` and fix all HIGH/CRITICAL issues?

---

### Week 8, Day 1–7: Terraform Project — Full AWS Infrastructure

Rewrite your entire Week 6 AWS 3-tier architecture in Terraform:

**Directory structure:**
```
terraform-aws-app/
├── main.tf
├── variables.tf
├── outputs.tf
├── backend.tf
├── providers.tf
├── envs/
│   ├── dev.tfvars
│   ├── staging.tfvars
│   └── prod.tfvars
└── modules/
    ├── vpc/
    ├── alb/
    ├── ec2_asg/
    ├── rds/
    └── s3/
```

**Requirements:**
- All resources tagged with `Environment`, `Project`, `Owner`
- Remote state with locking
- Variables for all configurable values
- Outputs for ALB DNS, RDS endpoint, S3 bucket name
- `tfsec` scan passes with zero HIGH/CRITICAL
- Separate `.tfvars` files per environment

**Deliverable:** Run `terraform apply` and get a working URL. Run `terraform destroy` and everything is gone.

#### Validation Checklist

- [ ] Can you deploy the full stack with one `terraform apply`?
- [ ] Can you switch between dev/staging/prod by changing workspace and tfvars?
- [ ] Can you destroy everything cleanly with `terraform destroy`?
- [ ] Can you import a manually created resource into Terraform state?

---

### Week 9, Day 1–3: Ansible Fundamentals

#### Concept: Ansible Is Idempotent Configuration Management

**Imperative** (Bash script): *"Install nginx. Start nginx."* — If you run it twice, it might fail because nginx is already installed.

**Idempotent** (Ansible): *"Ensure nginx is installed. Ensure nginx is running."* — If you run it 100 times, the result is the same: nginx is installed and running.

Ansible uses **SSH** (no agent needed) and **YAML** playbooks. It connects to your inventory of servers and brings them to the desired state.

#### Step-by-Step Practice

> 🎯 **Purpose:** Define the servers you manage and verify connectivity. The inventory is the foundation of all Ansible automation.

**Step 1: Install Ansible and create inventory**

```bash
brew install ansible

# Create inventory file
cat > inventory.ini << 'EOF'
[webservers]
web1 ansible_host=54.123.45.67 ansible_user=ubuntu ansible_ssh_private_key_file=~/.ssh/mykey.pem
web2 ansible_host=54.123.45.68 ansible_user=ubuntu ansible_ssh_private_key_file=~/.ssh/mykey.pem

[dbservers]
db1 ansible_host=10.0.2.10 ansible_user=ubuntu ansible_ssh_private_key_file=~/.ssh/mykey.pem

[all:vars]
ansible_python_interpreter=/usr/bin/python3
EOF

# Test connectivity
ansible all -i inventory.ini -m ping
```

> 🎯 **Purpose:** Declare the desired state of your servers in YAML instead of writing imperative scripts. Playbooks are readable, auditable, and idempotent.

**Step 2: Write your first playbook**

```bash
cat > playbook.yml << 'EOF'
---
- name: Configure web servers
  hosts: webservers
  become: yes  # Run as root (sudo)

  tasks:
    - name: Update apt cache
      apt:
        update_cache: yes
        cache_valid_time: 3600

    - name: Install nginx
      apt:
        name: nginx
        state: present

    - name: Ensure nginx is running
      service:
        name: nginx
        state: started
        enabled: yes

    - name: Copy index.html
      template:
        src: index.html.j2
        dest: /var/www/html/index.html
      notify: Restart nginx

  handlers:
    - name: Restart nginx
      service:
        name: nginx
        state: restarted
EOF
```

> 🎯 **Purpose:** Customize configurations per environment or server role without duplicating files. Jinja2 templates turn one nginx.conf into dozens of context-aware configs.

**Step 3: Variables and templates**

```bash
# group_vars/webservers.yml
cat > group_vars/webservers.yml << 'EOF'
nginx_port: 80
server_name: myapp.example.com
app_version: "1.0.0"
EOF

# templates/index.html.j2
cat > index.html.j2 << 'EOF'
<!DOCTYPE html>
<html>
<head><title>{{ server_name }}</title></head>
<body>
  <h1>Welcome to {{ server_name }}</h1>
  <p>Version: {{ app_version }}</p>
  <p>Server: {{ inventory_hostname }}</p>
</body>
</html>
EOF
```

> 🎯 **Purpose:** Package related tasks, files, and templates into self-contained units. Roles are how you share and reuse automation logic across projects.

**Step 4: Roles — reusable playbook components**

```bash
# Create a role structure
ansible-galaxy init roles/docker

# roles/docker/tasks/main.yml
cat > roles/docker/tasks/main.yml << 'EOF'
---
- name: Install prerequisites
  apt:
    name:
      - apt-transport-https
      - ca-certificates
      - curl
      - gnupg
      - lsb-release
    state: present

- name: Add Docker GPG key
  apt_key:
    url: https://download.docker.com/linux/ubuntu/gpg
    state: present

- name: Add Docker repository
  apt_repository:
    repo: "deb [arch=amd64] https://download.docker.com/linux/ubuntu {{ ansible_distribution_release }} stable"
    state: present

- name: Install Docker
  apt:
    name:
      - docker-ce
      - docker-ce-cli
      - containerd.io
    state: present
    update_cache: yes

- name: Ensure Docker is running
  service:
    name: docker
    state: started
    enabled: yes

- name: Add user to docker group
  user:
    name: "{{ ansible_user }}"
    groups: docker
    append: yes
EOF
```

#### Validation Checklist

- [ ] Can you run `ansible all -m ping` successfully?
- [ ] Can you write a playbook that installs and starts nginx?
- [ ] Can you use Jinja2 templates to generate config files?
- [ ] Can you create an Ansible role for Docker installation?

---

### Week 9, Day 4–7: Ansible Advanced — Vault, Dynamic Inventory, Molecule

#### Step-by-Step Practice

> 🎯 **Purpose:** Store sensitive data like database passwords in version control without exposing plaintext. Vault lets teams share secrets securely through Git.

**Step 1: Encrypt secrets with Ansible Vault**

```bash
# Create an encrypted file
ansible-vault create secrets.yml
# Enter password, then type:
# db_password: SuperSecret123!
# Save and exit

# Edit encrypted file
ansible-vault edit secrets.yml

# Run playbook with vault
ansible-playbook -i inventory.ini playbook.yml --ask-vault-pass

# Or use a password file (for CI/CD)
echo "myvaultpassword" > .vault_pass
chmod 600 .vault_pass
ansible-playbook -i inventory.ini playbook.yml --vault-password-file .vault_pass
```

> 🎯 **Purpose:** Automatically discover and target servers based on tags or regions. Dynamic inventory eliminates the toil of maintaining static server lists.

**Step 2: Dynamic inventory with AWS**

```bash
# Install AWS dynamic inventory plugin
pip install boto3

# Create aws_ec2.yml
cat > aws_ec2.yml << 'EOF'
plugin: aws_ec2
regions:
  - us-east-1
filters:
  tag:Environment: dev
  instance-state-name: running
keyed_groups:
  - key: tags.Role
    prefix: role
hostnames:
  - ip-address
EOF

# Test dynamic inventory
ansible-inventory -i aws_ec2.yml --graph

# Run playbook against dynamic inventory
ansible-playbook -i aws_ec2.yml playbook.yml
```

> 🎯 **Purpose:** Verify that your Ansible roles actually work before applying them to production. Automated testing for infrastructure code is just as important as application code testing.

**Step 3: Molecule — test your roles**

```bash
pip install molecule molecule-docker

# Initialize molecule in your role
cd roles/docker
molecule init scenario

# This creates:
# molecule/default/
#   ├── converge.yml    # What to apply
#   ├── molecule.yml    # Test config (uses Docker)
#   ├── verify.yml      # Validation tests
#   └── prepare.yml     # Setup before test

# Run the test
molecule test

# Molecule will:
# 1. Create a Docker container
# 2. Run your role on it
# 3. Run verify.yml to check assertions
# 4. Destroy the container
```

#### Validation Checklist

- [ ] Can you encrypt a database password with Ansible Vault?
- [ ] Can you target EC2 instances by tag using dynamic inventory?
- [ ] Can you run `molecule test` and have it pass?

---

### Week 10: Ansible + Terraform Integration Project

**Goal:** Chain Terraform and Ansible so that Terraform provisions infrastructure, and Ansible configures it automatically.

**Architecture:**
```
Terraform:
  - Creates VPC, subnets, security groups
  - Launches EC2 instances
  - Outputs: instance IPs, VPC ID

Ansible:
  - Reads Terraform outputs as inventory
  - Installs Docker on EC2 instances
  - Deploys your FastAPI app container
  - Configures Nginx reverse proxy
  - Sets up log rotation
```

**Step 1: Terraform outputs for Ansible**

```hcl
# terraform/outputs.tf
output "web_server_ips" {
  value = aws_instance.web[*].public_ip
}

output "db_endpoint" {
  value = aws_db_instance.main.endpoint
}
```

**Step 2: Generate Ansible inventory from Terraform outputs**

```bash
# After terraform apply
cat > generate_inventory.sh << 'EOF'
#!/bin/bash
IPS=$(terraform -chdir=../terraform output -json web_server_ips | jq -r '.[]')
echo "[webservers]" > inventory.ini
for ip in $IPS; do
  echo "$ip ansible_user=ubuntu ansible_ssh_private_key_file=~/.ssh/mykey.pem" >> inventory.ini
done
EOF
chmod +x generate_inventory.sh
./generate_inventory.sh
```

**Step 3: Ansible playbook that deploys the app**

```yaml
---
- name: Deploy FastAPI application
  hosts: webservers
  become: yes

  vars:
    app_image: "yourusername/infra-practice-app:v1.0.0"
    app_port: 8000

  roles:
    - docker

  tasks:
    - name: Pull application image
      docker_image:
        name: "{{ app_image }}"
        source: pull

    - name: Run application container
      docker_container:
        name: fastapi-app
        image: "{{ app_image }}"
        state: started
        restart_policy: always
        ports:
          - "8000:8000"
        env:
          LOG_LEVEL: "info"

    - name: Install nginx
      apt:
        name: nginx
        state: present

    - name: Configure nginx reverse proxy
      template:
        src: nginx.conf.j2
        dest: /etc/nginx/sites-available/default
      notify: Restart nginx

  handlers:
    - name: Restart nginx
      service:
        name: nginx
        state: restarted
```

**Deliverable:** Run one script that:
1. Runs `terraform apply`
2. Generates Ansible inventory from Terraform outputs
3. Runs `ansible-playbook` to configure all servers
4. Outputs the ALB URL where your app is live

#### Validation Checklist

- [ ] Can you provision infrastructure with Terraform and configure it with Ansible in one workflow?
- [ ] Can you add a new EC2 instance and have Ansible configure it automatically?
- [ ] Can you rotate the database password and update it across all servers?

---


## Phase 3: Kubernetes (Weeks 11–18)

> **Goal:** Master container orchestration at a level where you can design, deploy, debug, and secure production clusters.

---

### Week 11, Day 1–2: Kubernetes Architecture — Understand Before You Deploy

#### Concept: Kubernetes Is a Distributed System for Running Containers

When you run `kubectl apply`, you're talking to the **API Server**. The API Server writes your desired state to **etcd** (a distributed key-value store). Other controllers watch etcd and make the actual state match the desired state.

**Control Plane (Master) components:**
| Component | What It Does |
|-----------|-------------|
| **API Server** | Front door. All requests (kubectl, controllers, everything) go through here. |
| **etcd** | The database. Stores ALL cluster state. If etcd dies, the cluster has amnesia. |
| **Scheduler** | Decides which node a new pod should run on based on resources, affinity, taints. |
| **Controller Manager** | Runs background controllers: Deployment controller, ReplicaSet controller, Node controller, etc. |
| **Cloud Controller Manager** | Integrates with cloud provider for LoadBalancers, storage, node lifecycle. |

**Worker Node components:**
| Component | What It Does |
|-----------|-------------|
| **kubelet** | Agent on each node. Talks to API Server, starts/stops containers, reports status. |
| **kube-proxy** | Network proxy. Implements Services via iptables or IPVS. |
| **Container Runtime** | Actually runs containers (containerd, CRI-O). |

#### Step-by-Step Practice

> 🎯 **Purpose:** Get a safe, free environment to experiment with Kubernetes without cloud costs. Local clusters are essential for learning and pre-production testing.

**Step 1: Set up a local cluster**

```bash
# Option A: kind (lightweight, runs in Docker)
brew install kind
kind create cluster --name mycluster
kubectl cluster-info
kubectl get nodes

# Option B: minikube (more features)
brew install minikube
minikube start --driver=docker
minikube status
```

> 🎯 **Purpose:** Meet the components that make Kubernetes work — API Server, etcd, Scheduler, and Controllers. You can't debug a cluster if you don't know what these do.

**Step 2: Explore the control plane**

```bash
# See all pods in kube-system namespace (control plane components)
kubectl get pods -n kube-system

# You'll see:
# - kube-apiserver-xxx
# - kube-controller-manager-xxx
# - kube-scheduler-xxx
# - etcd-xxx
# - coredns-xxx
# - kube-proxy-xxx

# Describe the API server pod
kubectl describe pod kube-apiserver-mycluster-control-plane -n kube-system

# Check etcd health
kubectl exec -it etcd-mycluster-control-plane -n kube-system -- \
  etcdctl endpoint health \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key
```

> 🎯 **Purpose:** Trace exactly what happens from `kubectl apply` to a running container. This mental model is the key to debugging scheduling failures, image pull errors, and networking issues.

**Step 3: Understand the request flow**

```bash
# When you run this:
kubectl apply -f deployment.yaml

# Here's what happens:
# 1. kubectl sends YAML to API Server (authenticated + authorized)
# 2. API Server validates the YAML against the schema
# 3. API Server writes the object to etcd
# 4. Deployment controller watches for new Deployments
# 5. Deployment controller creates a ReplicaSet
# 6. ReplicaSet controller watches for new ReplicaSets
# 7. ReplicaSet controller creates Pods
# 8. Scheduler watches for unscheduled Pods
# 9. Scheduler picks a node, writes the node name to the Pod
# 10. kubelet on that node sees the Pod is assigned to it
# 11. kubelet tells containerd to start the container
# 12. kubelet reports status back to API Server

# You can watch this in real time:
kubectl get pods -w
```

#### Validation Checklist

- [ ] Can you name all 5 control plane components and what they do?
- [ ] Can you explain the exact flow from `kubectl apply` to a running container?
- [ ] Can you check etcd health?
- [ ] Can you list all pods on a specific node?

---

### Week 11, Day 3–4: Pods, Deployments, and Services

#### Concept: Pods Are the Smallest Deployable Unit

A **Pod** is not a container. A Pod is a **wrapper** around one or more containers that share:
- Network namespace (same IP, same localhost)
- Storage volumes
- Lifecycle (they start and stop together)

Most pods have **1 container**. But sometimes you need **sidecars** (e.g., nginx + app) or **init containers** (run before main container starts).

#### Step-by-Step Practice

> 🎯 **Purpose:** Understand the smallest deployable unit in Kubernetes and the difference between imperative and declarative management. Pods are the foundation everything else builds on.

**Step 1: Create your first pod manually**

```bash
# Imperative way (quick, not for production)
kubectl run nginx --image=nginx:alpine --port=80
kubectl get pods
kubectl describe pod nginx
kubectl delete pod nginx

# Declarative way (the right way for production)
cat > pod.yaml << 'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
  labels:
    app: nginx
spec:
  containers:
  - name: nginx
    image: nginx:alpine
    ports:
    - containerPort: 80
EOF

kubectl apply -f pod.yaml
```

> 🎯 **Purpose:** Enable self-healing, rolling updates, and easy scaling for your application. Deployments are how you run production workloads in Kubernetes.

**Step 2: Create a Deployment**

```bash
# Imperative
kubectl create deployment fastapi-app \
  --image=yourusername/infra-practice-app:v1.0.0 \
  --replicas=3 \
  --port=8000

# Declarative
cat > deployment.yaml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-app
  labels:
    app: fastapi
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fastapi
  template:
    metadata:
      labels:
        app: fastapi
    spec:
      containers:
      - name: app
        image: yourusername/infra-practice-app:v1.0.0
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
EOF

kubectl apply -f deployment.yaml
kubectl get deployments
kubectl get pods -l app=fastapi
kubectl describe deployment fastapi-app
```

> 🎯 **Purpose:** Provide stable networking to your pods regardless of which node they're on. Services abstract away the ephemeral nature of pod IPs.

**Step 3: Expose the Deployment with a Service**

```bash
# Imperative
kubectl expose deployment fastapi-app --type=NodePort --port=8000

# Declarative
cat > service.yaml << 'EOF'
apiVersion: v1
kind: Service
metadata:
  name: fastapi-service
spec:
  type: NodePort
  selector:
    app: fastapi
  ports:
    - port: 8000
      targetPort: 8000
      nodePort: 30080
EOF

kubectl apply -f service.yaml
kubectl get svc

# Access it
curl http://localhost:30080/health  # Docker Desktop
# OR
curl http://$(minikube ip):30080/health  # minikube
```

> 🎯 **Purpose:** Choose the right Service type for your use case — internal-only, node-exposed, or cloud load balancer. Picking wrong leads to security holes or unnecessary cloud costs.

**Step 4: Understand Service types**

| Type | How It Works | When to Use |
|------|-------------|-------------|
| **ClusterIP** | Assigns an internal IP. Only reachable from inside the cluster. | Microservice-to-microservice communication |
| **NodePort** | Opens a port (30000-32767) on every node. | Learning, small demos, quick testing |
| **LoadBalancer** | Provisions a cloud load balancer (AWS ELB, etc.). | Production apps in cloud |
| **ExternalName** | DNS CNAME to an external service. | Pointing to external APIs |

> 🎯 **Purpose:** Prove that Kubernetes automatically recovers from pod failures. This is the core promise of Kubernetes: your desired state is continuously maintained.

**Step 5: Test self-healing**

```bash
# Delete one pod manually
kubectl get pods
kubectl delete pod fastapi-app-xxxxxxxxxx-yyyyy

# Watch Kubernetes recreate it automatically
kubectl get pods -w
```

#### Validation Checklist

- [ ] Can you create a Deployment with 3 replicas?
- [ ] Can you expose it as a NodePort Service and curl it?
- [ ] If you delete a pod, does it get recreated automatically?
- [ ] Can you explain the difference between a Pod and a Deployment?

---

### Week 11, Day 5–7: ConfigMaps, Secrets, and Probes

#### Step-by-Step Practice

> 🎯 **Purpose:** Externalize configuration so you can change behavior without rebuilding images. ConfigMaps separate code from config, enabling environment-specific deployments.

**Step 1: ConfigMap for non-sensitive configuration**

```bash
# Create from literal values
kubectl create configmap app-config \
  --from-literal=LOG_LEVEL=info \
  --from-literal=SERVICE_NAME=k8s-fastapi

# Create from file
kubectl create configmap nginx-config --from-file=nginx.conf

# Or declarative
cat > configmap.yaml << 'EOF'
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  LOG_LEVEL: "info"
  SERVICE_NAME: "k8s-fastapi"
  database.conf: |
    host=postgres
    port=5432
    pool_size=10
EOF

kubectl apply -f configmap.yaml
```

> 🎯 **Purpose:** Store passwords, tokens, and keys outside of container images and source code. Even though Secrets aren't encrypted by default, they're still better than hardcoding credentials.

**Step 2: Secret for sensitive data**

```bash
# Create from literal (values are base64 encoded automatically)
kubectl create secret generic app-secrets \
  --from-literal=DB_PASSWORD=SuperSecret123 \
  --from-literal=API_KEY=abc123def456

# Create from files
kubectl create secret tls my-tls-secret \
  --cert=path/to/cert.crt \
  --key=path/to/key.key

# Declarative (values must be base64 encoded yourself)
echo -n 'SuperSecret123' | base64  # U3VwZXJTZWNyZXQxMjM=

cat > secret.yaml << 'EOF'
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
type: Opaque
data:
  DB_PASSWORD: U3VwZXJTZWNyZXQxMjM=
  API_KEY: YWJjMTIzZGVmNDU2
EOF
```

> **IMPORTANT:** Secrets are only **base64 encoded**, not encrypted. Anyone with cluster access can read them. For production, use:
> - **Sealed Secrets** (encrypt secrets for Git storage)
> - **External Secrets Operator** (fetch from AWS Secrets Manager/Vault)
> - **HashiCorp Vault** (dedicated secret management)

> 🎯 **Purpose:** Make configuration and secrets available to your application as environment variables or files. This is how real-world apps consume Kubernetes-managed config.

**Step 3: Inject ConfigMap and Secret into a Pod**

```bash
cat > deployment-with-config.yaml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: fastapi
  template:
    metadata:
      labels:
        app: fastapi
    spec:
      containers:
      - name: app
        image: yourusername/infra-practice-app:v1.0.0
        ports:
        - containerPort: 8000
        env:
        - name: LOG_LEVEL
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: LOG_LEVEL
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: DB_PASSWORD
        volumeMounts:
        - name: config-vol
          mountPath: /etc/config
        volumes:
        - name: config-vol
          configMap:
            name: app-config
EOF

kubectl apply -f deployment-with-config.yaml

# Verify
cubectl exec -it <pod-name> -- env | grep -E 'LOG_LEVEL|DB_PASSWORD'
kubectl exec -it <pod-name> -- ls /etc/config
```

> 🎯 **Purpose:** Tell Kubernetes when your app is healthy, ready for traffic, or needs restarting. Without probes, Kubernetes might send traffic to crashed pods or leave unhealthy ones running.

**Step 4: Liveness and Readiness Probes**

```bash
cat > deployment-with-probes.yaml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: fastapi
  template:
    metadata:
      labels:
        app: fastapi
    spec:
      containers:
      - name: app
        image: yourusername/infra-practice-app:v1.0.0
        ports:
        - containerPort: 8000
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
          timeoutSeconds: 3
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 3
          periodSeconds: 5
          timeoutSeconds: 2
          failureThreshold: 2
        startupProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 1
          periodSeconds: 5
          failureThreshold: 30
EOF
```

**Probe behavior:**
| Probe | Fails? | Kubernetes Action |
|-------|--------|-------------------|
| **Liveness** | Container is dead | **Restart the container** |
| **Readiness** | Container is not ready for traffic | **Remove from Service endpoints** |
| **Startup** | App hasn't started yet | **Kill and restart** (disables other probes until success) |

#### Validation Checklist

- [ ] Can you create a ConfigMap and mount it as both env vars and a file?
- [ ] Can you create a Secret and inject it as an environment variable?
- [ ] Can you explain why Secrets are not truly encrypted by default?
- [ ] If readiness fails, does the pod restart? (Hint: NO)
- [ ] If liveness fails, does traffic still route to the pod? (Hint: NO, it's restarting)

---

### Week 12, Day 1–3: Ingress and TLS

#### Concept: Ingress Is HTTP Routing for Kubernetes

A **Service** routes traffic to pods. An **Ingress** routes HTTP/HTTPS traffic to different Services based on:
- **Hostname:** `api.example.com` → api-service
- **Path:** `/users` → user-service, `/orders` → order-service

You need BOTH:
- **Ingress Resource** — the rule ("route /api to api-service")
- **Ingress Controller** — the software that enforces the rule (NGINX, Traefik)

#### Step-by-Step Practice

> 🎯 **Purpose:** Deploy the component that actually enforces your Ingress routing rules. The controller is the traffic cop; without it, Ingress resources do nothing.

**Step 1: Install NGINX Ingress Controller**

```bash
# For minikube
minikube addons enable ingress

# For Docker Desktop or other clusters
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml

# Wait for it to be ready
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=120s
```

> 🎯 **Purpose:** Route HTTP traffic to different services based on hostname and path. Ingress is the standard way to expose multiple apps through a single entry point.

**Step 2: Create an Ingress resource**

```bash
cat > ingress.yaml << 'EOF'
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: fastapi-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
  - host: fastapi.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: fastapi-service
            port:
              number: 8000
EOF

kubectl apply -f ingress.yaml
```

> 🎯 **Purpose:** Simulate DNS for local development so you can test hostname-based routing before buying a domain or configuring real DNS.

**Step 3: Add `/etc/hosts` entry**

```bash
# Get the Ingress controller IP
kubectl get svc -n ingress-nginx
# For minikube:
minikube ip
# For Docker Desktop: it's localhost

# Add to /etc/hosts
sudo sh -c 'echo "127.0.0.1 fastapi.local" >> /etc/hosts'  # Docker Desktop
# OR
sudo sh -c 'echo "$(minikube ip) fastapi.local" >> /etc/hosts'  # minikube

# Test
curl http://fastapi.local/health
```

> 🎯 **Purpose:** Automate TLS certificate issuance and renewal from Let's Encrypt. Manual certificate management is error-prone and inevitably leads to expired-cert outages.

**Step 4: Enable HTTPS with cert-manager**

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create a ClusterIssuer for Let's Encrypt (staging first!)
cat > cluster-issuer.yaml << 'EOF'
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-staging
spec:
  acme:
    server: https://acme-staging-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-staging
    solvers:
    - http01:
        ingress:
          class: nginx
EOF

kubectl apply -f cluster-issuer.yaml

# Update Ingress to use TLS
cat > ingress-tls.yaml << 'EOF'
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: fastapi-ingress
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-staging
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - fastapi.local
    secretName: fastapi-tls
  rules:
  - host: fastapi.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: fastapi-service
            port:
              number: 8000
EOF

kubectl apply -f ingress-tls.yaml
```

#### Validation Checklist

- [ ] Can you access your app via `fastapi.local`?
- [ ] Can you explain the difference between an Ingress and a Service?
- [ ] Can you install cert-manager and request a TLS certificate?
- [ ] Can you route `/api` to one service and `/blog` to another?

---

### Week 12, Day 4–7: Storage — Volumes, PVCs, StatefulSets

#### Concept: Kubernetes Storage Is Request-Based

| Object | What It Is |
|--------|-----------|
| **PersistentVolume (PV)** | A piece of storage in the cluster (like an AWS EBS volume). Provisioned by an admin or dynamic provisioner. |
| **PersistentVolumeClaim (PVC)** | A user's request for storage ("I need 10Gi of fast SSD"). Kubernetes finds or creates a matching PV. |
| **StorageClass** | Defines "classes" of storage (e.g., `fast-ssd`, `standard`, `archive`). Enables dynamic provisioning. |

#### Step-by-Step Practice

> 🎯 **Purpose:** Request storage without knowing the underlying infrastructure details. StorageClasses abstract away AWS EBS, GCP Persistent Disk, or local volumes.

**Step 1: Dynamic provisioning with StorageClass**

```bash
# For local clusters (kind/minikube), use the default StorageClass
kubectl get storageclass

# For AWS (EKS), you'd use gp3:
# kubectl apply -f https://raw.githubusercontent.com/kubernetes-sigs/aws-ebs-csi-driver/master/examples/kubernetes/dynamic-provisioning/manifests/storageclass.yaml

# Create a PVC
kubectl apply -f - << 'EOF'
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
  storageClassName: standard
EOF

kubectl get pvc
# Wait for status to be "Bound"
```

> 🎯 **Purpose:** Run stateful workloads that survive pod restarts and rescheduling. Databases are the ultimate test of Kubernetes storage reliability.

**Step 2: Deploy PostgreSQL with persistent storage**

```bash
cat > postgres.yaml << 'EOF'
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_DB
          value: myapp
        - name: POSTGRES_USER
          value: dbuser
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: DB_PASSWORD
        volumeMounts:
        - name: postgres-data
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata:
      name: postgres-data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 10Gi
EOF

kubectl apply -f postgres.yaml
```

> 🎯 **Purpose:** Verify that your storage setup actually works by deleting a pod and confirming data survives. This test separates working persistence from broken assumptions.

**Step 3: Test data persistence**

```bash
# Connect to Postgres
kubectl exec -it postgres-0 -- psql -U dbuser -d myapp

# Inside psql:
CREATE TABLE test (id SERIAL PRIMARY KEY, name VARCHAR(50));
INSERT INTO test (name) VALUES ('Kubernetes');
\q

# Delete the pod
kubectl delete pod postgres-0

# Wait for it to restart
kubectl get pods -w

# Connect again
kubectl exec -it postgres-0 -- psql -U dbuser -d myapp -c "SELECT * FROM test;"
# Data is still there! The PVC survived the pod deletion.
```

> 🎯 **Purpose:** Choose the right access mode for your workload — single-writer databases need RWO, while shared file servers need RWX. Wrong choices cause data corruption or mount failures.

**Step 4: Understand access modes**

| Access Mode | Meaning | Use Case |
|-------------|---------|----------|
| **ReadWriteOnce (RWO)** | One node can mount as read-write | Most databases (PostgreSQL, MySQL) |
| **ReadOnlyMany (ROX)** | Many nodes can mount as read-only | Shared config, static assets |
| **ReadWriteMany (RWX)** | Many nodes can mount as read-write | Shared file systems (NFS, EFS) |
| **ReadWriteOncePod (RWOP)** | Only one pod can mount (K8s 1.22+) | Strict single-writer scenarios |

#### Validation Checklist

- [ ] Can you create a PVC and see it bind to a PV?
- [ ] Can you deploy Postgres with a StatefulSet and persistent storage?
- [ ] If you delete the Postgres pod, does the data survive?
- [ ] Can you explain why StatefulSets are better than Deployments for databases?

---


### Week 13, Day 1–3: Kubernetes Networking Deep Dive

#### Concept: Kubernetes Networking Has 4 Problems to Solve

1. **Container-to-Container communication** (inside a pod) — Shared network namespace, localhost
2. **Pod-to-Pod communication** — Every pod gets a unique IP. All pods can talk to all pods without NAT.
3. **Pod-to-Service communication** — Services provide stable IPs/DNS. `kube-proxy` implements this.
4. **External-to-Service communication** — NodePort, LoadBalancer, Ingress

**CNI (Container Network Interface):** The plugin that makes pod networking work. Popular options:
- **Calico** — Policy-rich, BGP-based, great for security
- **Cilium** — eBPF-based, high performance, observability built-in
- **Flannel** — Simple, easy to set up, fewer features
- **Weave Net** — Easy setup, encryption support

#### Step-by-Step Practice

> 🎯 **Purpose:** See the actual IP addresses, interfaces, and routes inside a pod's network namespace. This demystifies pod-to-pod communication and CNI plugin behavior.

**Step 1: Inspect pod networking**

```bash
# Get a pod's IP
kubectl get pod fastapi-app-xxx -o wide

# Exec into a pod and see its network
kubectl exec -it fastapi-app-xxx -- ip addr
kubectl exec -it fastapi-app-xxx -- ip route

# Ping another pod from inside a pod
kubectl exec -it fastapi-app-xxx -- ping <other-pod-ip>
```

> 🎯 **Purpose:** Understand how services discover each other by name instead of hardcoding IPs. Kubernetes DNS is the backbone of microservice communication.

**Step 2: DNS in Kubernetes**

```bash
# Kubernetes runs CoreDNS for cluster DNS
kubectl get pods -n kube-system -l k8s-app=kube-dns

# Test DNS resolution from inside a pod
kubectl run -it --rm debug --image=busybox:1.28 --restart=Never -- nslookup kubernetes.default

# Service DNS format: <service-name>.<namespace>.svc.cluster.local
kubectl run -it --rm debug --image=busybox:1.28 --restart=Never -- nslookup fastapi-service.default.svc.cluster.local
```

> 🎯 **Purpose:** Deploy a production-grade CNI plugin and verify it's managing pod IPs correctly. Calico adds network policy capabilities that default CNI plugins lack.

**Step 3: Install Calico and inspect**

```bash
# For kind cluster with Calico
kind create cluster --config=- << 'EOF'
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
networking:
  disableDefaultCNI: true
  podSubnet: 192.168.0.0/16
EOF

kubectl apply -f https://raw.githubusercontent.com/projectcalico/calico/v3.26.0/manifests/calico.yaml

# Inspect Calico pods
kubectl get pods -n kube-system -l k8s-app=calico-node

# See IP pools
kubectl get ippools

# See network policies (none yet)
kubectl get networkpolicies --all-namespaces
```

> 🎯 **Purpose:** Explicitly allow only necessary traffic between pods and deny everything else by default. NetworkPolicies are your firewall inside the cluster.

**Step 4: Network Policies (Zero-Trust Networking)**

```bash
# Default: deny ALL ingress traffic
cat > default-deny.yaml << 'EOF'
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
  namespace: default
spec:
  podSelector: {}  # All pods
  policyTypes:
  - Ingress
EOF

# Allow traffic TO fastapi-app FROM nginx ONLY
cat > allow-nginx-to-app.yaml << 'EOF'
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-nginx-to-app
  namespace: default
spec:
  podSelector:
    matchLabels:
      app: fastapi
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: nginx
    ports:
    - protocol: TCP
      port: 8000
EOF

kubectl apply -f default-deny.yaml
kubectl apply -f allow-nginx-to-app.yaml

# Test: nginx can reach fastapi, but other pods cannot
```

#### Validation Checklist

- [ ] Can you explain the 4 networking problems K8s solves?
- [ ] Can you resolve a service name from inside a pod using DNS?
- [ ] Can you write a NetworkPolicy that blocks all traffic by default?
- [ ] Can you whitelist only specific pods to talk to your app?

---

### Week 13, Day 4–7: Kubernetes Security — RBAC, Pod Security, Sealed Secrets

#### Concept: Defense in Depth for Kubernetes

Security in K8s has multiple layers:
1. **Authentication** — Who are you? (certificates, OIDC, AWS IAM)
2. **Authorization (RBAC)** — What can you do? (Roles, RoleBindings)
3. **Admission Control** — Is this request allowed? (OPA, Gatekeeper)
4. **Pod Security** — Can this pod run? (Security contexts, policies)
5. **Network Security** — Who can talk to whom? (NetworkPolicies)
6. **Secrets Management** — Are secrets actually secret? (Vault, Sealed Secrets)

#### Step-by-Step Practice

> 🎯 **Purpose:** Limit what users and services can do in your cluster to the minimum required. RBAC prevents both accidental damage and malicious lateral movement.

**Step 1: RBAC — Role-Based Access Control**

```bash
# Create a ServiceAccount
cat > serviceaccount.yaml << 'EOF'
apiVersion: v1
kind: ServiceAccount
metadata:
  name: app-reader
  namespace: default
EOF

# Create a Role (permissions limited to one namespace)
cat > role.yaml << 'EOF'
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]
- apiGroups: [""]
  resources: ["pods/log"]
  verbs: ["get", "list"]
EOF

# Bind the Role to the ServiceAccount
cat > rolebinding.yaml << 'EOF'
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: default
subjects:
- kind: ServiceAccount
  name: app-reader
  namespace: default
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
EOF

kubectl apply -f serviceaccount.yaml
kubectl apply -f role.yaml
kubectl apply -f rolebinding.yaml

# Test: Create a pod that uses this ServiceAccount
kubectl run test-reader --rm -it --serviceaccount=app-reader --image=bitnami/kubectl -- get pods
# This works!

kubectl run test-reader --rm -it --serviceaccount=app-reader --image=bitnami/kubectl -- delete pod nginx
# This FAILS! (no delete permission)
```

> 🎯 **Purpose:** Enforce security baselines at the namespace level so dangerous pods are rejected before they start. This shifts security left to admission time.

**Step 2: Pod Security Standards**

```bash
# Enforce the "restricted" profile (most secure) namespace-wide
cat > namespace-restricted.yaml << 'EOF'
apiVersion: v1
kind: Namespace
metadata:
  name: restricted-ns
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/enforce-version: latest
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
EOF

kubectl apply -f namespace-restricted.yaml

# Try to run a privileged pod in this namespace — it will be REJECTED
kubectl run bad-pod --image=nginx --privileged -n restricted-ns
# Error: violates PodSecurity "restricted:latest": privileged
```

> 🎯 **Purpose:** Run pods as non-root, with read-only filesystems and dropped capabilities. Security contexts bring container hardening principles into Kubernetes manifests.

**Step 3: Security contexts on pods**

```bash
cat > secure-pod.yaml << 'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: secure-app
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 65534
    runAsGroup: 65534
    fsGroup: 65534
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: app
    image: yourusername/infra-practice-app:v1.0.0
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop:
        - ALL
    volumeMounts:
    - name: tmp
      mountPath: /tmp
    - name: cache
      mountPath: /root/.cache
  volumes:
  - name: tmp
    emptyDir: {}
  - name: cache
    emptyDir: {}
EOF

kubectl apply -f secure-pod.yaml
```

> 🎯 **Purpose:** Encrypt secrets so they can be stored in Git without exposing plaintext. This enables GitOps workflows where all configuration is version-controlled.

**Step 4: Sealed Secrets for Git-safe secrets**

```bash
# Install kubeseal CLI
brew install kubeseal

# Install Sealed Secrets controller
kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.24.0/controller.yaml

# Create a regular secret
kubectl create secret generic db-creds \
  --from-literal=password=MySecret123 \
  --dry-run=client -o yaml > secret.yaml

# Encrypt it into a SealedSecret
kubeseal --controller-namespace=kube-system --controller-name=sealed-secrets-controller < secret.yaml > sealed-secret.yaml

# sealed-secret.yaml is SAFE to commit to Git!
cat sealed-secret.yaml

# Apply the sealed secret — controller decrypts it automatically
kubectl apply -f sealed-secret.yaml

# Verify the secret was created
kubectl get secret db-creds
```

#### Validation Checklist

- [ ] Can you create a ServiceAccount that can only read pods in one namespace?
- [ ] Can you enforce the `restricted` Pod Security Standard on a namespace?
- [ ] Can you run a pod with `runAsNonRoot`, `readOnlyRootFilesystem`, and dropped capabilities?
- [ ] Can you encrypt a secret with `kubeseal` and commit it to Git safely?

---

### Week 14, Day 1–4: Observability — Prometheus, Grafana, Loki

#### Concept: The Three Pillars of Observability

| Pillar | What It Answers | Tool |
|--------|----------------|------|
| **Metrics** | "What is happening?" (CPU, memory, request rate, error rate) | Prometheus + Grafana |
| **Logs** | "Why is it happening?" (error messages, stack traces) | Loki / ELK / Fluentd |
| **Traces** | "Where is the time going?" (request path, latency per service) | Jaeger / Zipkin |

#### Step-by-Step Practice

> 🎯 **Purpose:** Deploy the industry-standard metrics collection system for Kubernetes. Metrics are the first pillar of observability — they tell you what is happening.

**Step 1: Install Prometheus with Helm**

```bash
# Add Helm repositories
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

# Create monitoring namespace
kubectl create namespace monitoring

# Install Prometheus
helm install prometheus prometheus-community/prometheus \
  --namespace monitoring \
  --set server.persistentVolume.enabled=false

# Check pods
kubectl get pods -n monitoring

# Port-forward to access Prometheus UI
kubectl port-forward -n monitoring svc/prometheus-server 9090:80
# Open http://localhost:9090
```

> 🎯 **Purpose:** Extract meaningful insights from raw time-series data. PromQL is the language of Kubernetes monitoring; mastering it accelerates incident response.

**Step 2: Query metrics with PromQL**

```promql
# CPU usage by pod
rate(container_cpu_usage_seconds_total{pod!=""}[5m])

# Memory usage by pod
container_memory_usage_bytes{pod!=""}

# Number of running pods
kube_pod_status_phase{phase="Running"}

# HTTP request rate
rate(http_requests_total[5m])

# Error rate
rate(http_requests_total{status=~"5.."}[5m])
```

> 🎯 **Purpose:** Transform metrics into visual dashboards that the whole team can understand. Dashboards make trends obvious and help communicate system health.

**Step 3: Install Grafana and create dashboards**

```bash
# Install Grafana
helm install grafana grafana/grafana \
  --namespace monitoring \
  --set adminPassword='admin123' \
  --set datasources."datasources\\.yaml".apiVersion=1 \
  --set datasources."datasources\\.yaml".datasources[0].name=Prometheus \
  --set datasources."datasources\\.yaml".datasources[0].type=prometheus \
  --set datasources."datasources\\.yaml".datasources[0].url=http://prometheus-server.monitoring.svc.cluster.local \
  --set datasources."datasources\\.yaml".datasources[0].access=proxy \
  --set datasources."datasources\\.yaml".datasources[0].isDefault=true

# Port-forward
kubectl port-forward -n monitoring svc/grafana 3000:80

# Login: admin / admin123
# Open http://localhost:3000
```

> 🎯 **Purpose:** Centralize logs from all pods so you can search them in one place. Logs answer 'why' when metrics tell you 'what' is wrong.

**Step 4: Install Loki for log aggregation**

```bash
helm install loki grafana/loki-stack \
  --namespace monitoring \
  --set grafana.enabled=false \
  --set prometheus.enabled=false \
  --set loki.persistence.enabled=false

# Query logs in Grafana (add Loki as a data source)
# LogQL examples:
# {pod="fastapi-app-xxx"}
# {namespace="default"} |= "ERROR"
# {pod=~"fastapi-app-.*"} | json | status_code="500"
```

> 🎯 **Purpose:** Expose application-specific data like request counts and latency so you can alert on business-critical behavior, not just CPU and memory.

**Step 5: Instrument your app with custom metrics**

Add to your FastAPI app:
```python
from prometheus_client import Counter, Histogram, generate_latest
from starlette.responses import PlainTextResponse

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')

@app.middleware("http")
async def metrics_middleware(request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path, status=response.status_code).inc()
    REQUEST_DURATION.observe(duration)
    return response

@app.get("/metrics")
def metrics():
    return PlainTextResponse(content=generate_latest())
```

#### Validation Checklist

- [ ] Can you query pod CPU usage in Prometheus?
- [ ] Can you create a Grafana dashboard showing request rate and error rate?
- [ ] Can you search logs for all ERROR messages in the last hour?
- [ ] Can you instrument your app to expose custom metrics?

---

### Week 14, Day 5–7: Distributed Tracing with OpenTelemetry and Jaeger

#### Step-by-Step Practice

> 🎯 **Purpose:** Deploy a system that collects and visualizes request traces across services. Traces answer 'where is the time going?' in distributed systems.

**Step 1: Install Jaeger**

```bash
kubectl apply -f - << 'EOF'
apiVersion: v1
kind: Namespace
metadata:
  name: observability
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jaeger
  namespace: observability
spec:
  replicas: 1
  selector:
    matchLabels:
      app: jaeger
  template:
    metadata:
      labels:
        app: jaeger
    spec:
      containers:
      - name: jaeger
        image: jaegertracing/all-in-one:1.47
        ports:
        - containerPort: 16686
        - containerPort: 14268
EOF

kubectl expose deployment jaeger --type=NodePort --port=16686 -n observability
```

> 🎯 **Purpose:** Emit trace data from your application so you can follow a single request through every service it touches. Instrumentation is what makes distributed tracing useful.

**Step 2: Instrument your FastAPI app with OpenTelemetry**

```python
pip install opentelemetry-api opentelemetry-sdk opentelemetry-instrumentation-fastapi opentelemetry-exporter-jaeger

# In your main.py:
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

# Setup tracing
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

jaeger_exporter = JaegerExporter(
    agent_host_name="jaeger.observability.svc.cluster.local",
    agent_port=6831,
)
span_processor = BatchSpanProcessor(jaeger_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

FastAPIInstrumentor.instrument_app(app)
```

> 🎯 **Purpose:** Analyze the complete path of a request, identify bottlenecks, and understand service dependencies. The UI turns raw trace data into actionable insights.

**Step 3: View traces in Jaeger UI**

```bash
kubectl port-forward -n observability svc/jaeger 16686:16686
# Open http://localhost:16686
```

#### Validation Checklist

- [ ] Can you see a distributed trace for a request to your app?
- [ ] Can you identify which part of the request takes the longest?

---

### Week 15, Day 1–3: Autoscaling — HPA, VPA, Cluster Autoscaler

#### Concept: Scale at 3 Levels

| Level | What It Scales | Trigger | Tool |
|-------|---------------|---------|------|
| **Pod** | Number of pod replicas | CPU, memory, custom metrics | HPA |
| **Pod** | Resource requests/limits | Actual usage vs request | VPA |
| **Node** | Number of cluster nodes | Pending pods | Cluster Autoscaler |

#### Step-by-Step Practice

> 🎯 **Purpose:** Automatically add or remove pod replicas based on real-time demand. HPA keeps your application responsive during traffic spikes without over-provisioning.

**Step 1: Horizontal Pod Autoscaler (HPA)**

```bash
# Make sure metrics-server is installed
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# Create an HPA
cat > hpa.yaml << 'EOF'
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: fastapi-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: fastapi-app
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 50
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 100
        periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
EOF

kubectl apply -f hpa.yaml
kubectl get hpa
kubectl describe hpa fastapi-hpa
```

> 🎯 **Purpose:** Validate that your autoscaling configuration actually works under realistic conditions. Untested autoscaling is just a theory until proven with load.

**Step 2: Generate load and watch scaling**

```bash
# Install hey (HTTP load generator)
brew install hey

# Generate load
hey -z 60s -c 50 http://fastapi.local/

# Watch HPA in another terminal
kubectl get hpa -w
kubectl get pods -w
```

> 🎯 **Purpose:** Right-size your pod resource requests based on actual usage patterns. VPA prevents both resource waste (over-requesting) and out-of-memory crashes (under-requesting).

**Step 3: Vertical Pod Autoscaler (VPA)**

```bash
# Install VPA
kubectl apply -f https://github.com/kubernetes/autoscaler/releases/download/vertical-pod-autoscaler-0.14.0/vpa-v1-crd-gen.yaml
kubectl apply -f https://github.com/kubernetes/autoscaler/releases/download/vertical-pod-autoscaler-0.14.0/vpa-rbac.yaml
kubectl apply -f https://github.com/kubernetes/autoscaler/releases/download/vertical-pod-autoscaler-0.14.0/vpa-updater.yaml
kubectl apply -f https://github.com/kubernetes/autoscaler/releases/download/vertical-pod-autoscaler-0.14.0/vpa-recommender.yaml
kubectl apply -f https://github.com/kubernetes/autoscaler/releases/download/vertical-pod-autoscaler-0.14.0/vpa-admission-controller.yaml

# Create a VPA in " recommendation" mode (doesn't auto-apply)
cat > vpa.yaml << 'EOF'
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: fastapi-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: fastapi-app
  updatePolicy:
    updateMode: "Off"  # Change to "Auto" to auto-update
  resourcePolicy:
    containerPolicies:
    - containerName: '*'
      minAllowed:
        cpu: 50m
        memory: 64Mi
      maxAllowed:
        cpu: 1
        memory: 512Mi
EOF

kubectl apply -f vpa.yaml

# Check recommendations
kubectl describe vpa fastapi-vpa
```

#### Validation Checklist

- [ ] Can you create an HPA that scales based on CPU?
- [ ] Can you generate load and watch pods scale up?
- [ ] Can you get VPA recommendations for right-sizing your pods?

---

### Week 15, Day 4–7: Helm and Kustomize

#### Concept: Managing YAML at Scale

Raw YAML doesn't scale. You need templating or patching:
- **Helm** — Templating engine. Use when you need logic (loops, conditionals, functions).
- **Kustomize** — Patching engine. Use when you need environment-specific overrides (dev vs prod).

#### Step-by-Step Practice

> 🎯 **Purpose:** Package your Kubernetes manifests into a versioned, configurable, and reusable unit. Helm is the de facto package manager for Kubernetes.

**Step 1: Create a Helm chart for your app**

```bash
helm create myapp

# Directory structure:
# myapp/
#   Chart.yaml          # Metadata
#   values.yaml         # Default values
#   templates/          # Kubernetes YAML templates
#     _helpers.tpl      # Named templates
#     deployment.yaml
#     service.yaml
#     ingress.yaml

# Edit values.yaml
cat > myapp/values.yaml << 'EOF'
replicaCount: 2

image:
  repository: yourusername/infra-practice-app
  pullPolicy: IfNotPresent
  tag: "v1.0.0"

service:
  type: NodePort
  port: 8000

ingress:
  enabled: true
  className: nginx
  hosts:
    - host: fastapi.local
      paths:
        - path: /
          pathType: Prefix

resources:
  limits:
    cpu: 200m
    memory: 256Mi
  requests:
    cpu: 100m
    memory: 128Mi

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 50
EOF

# Install
helm install myapp ./myapp

# Upgrade
helm upgrade myapp ./myapp --set replicaCount=4

# See history
helm history myapp

# Rollback
helm rollback myapp 1
```

> 🎯 **Purpose:** Manage environment-specific overrides without template logic or copy-pasted YAML. Kustomize is ideal for GitOps workflows where pure YAML is preferred.

**Step 2: Kustomize for environment management**

```bash
mkdir -p kustomize/{base,overlays/{dev,staging,prod}}

# Base configuration
cat > kustomize/base/deployment.yaml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: fastapi
  template:
    metadata:
      labels:
        app: fastapi
    spec:
      containers:
      - name: app
        image: yourusername/infra-practice-app:v1.0.0
        ports:
        - containerPort: 8000
EOF

cat > kustomize/base/service.yaml << 'EOF'
apiVersion: v1
kind: Service
metadata:
  name: fastapi-service
spec:
  selector:
    app: fastapi
  ports:
  - port: 8000
    targetPort: 8000
EOF

cat > kustomize/base/kustomization.yaml << 'EOF'
resources:
  - deployment.yaml
  - service.yaml
EOF

# Dev overlay
cat > kustomize/overlays/dev/kustomization.yaml << 'EOF'
resources:
  - ../../base

namePrefix: dev-

patches:
  - target:
      kind: Deployment
      name: fastapi-app
    patch: |
      - op: replace
        path: /spec/replicas
        value: 1
      - op: replace
        path: /spec/template/spec/containers/0/image
        value: yourusername/infra-practice-app:dev-latest
EOF

# Prod overlay
cat > kustomize/overlays/prod/kustomization.yaml << 'EOF'
resources:
  - ../../base

namePrefix: prod-

patches:
  - target:
      kind: Deployment
      name: fastapi-app
    patch: |
      - op: replace
        path: /spec/replicas
        value: 5
      - op: replace
        path: /spec/template/spec/containers/0/resources/limits/memory
        value: 512Mi
EOF

# Apply dev
kubectl apply -k kustomize/overlays/dev

# Apply prod
kubectl apply -k kustomize/overlays/prod
```

#### Validation Checklist

- [ ] Can you create a Helm chart and install it?
- [ ] Can you upgrade a Helm release with new values?
- [ ] Can you rollback a Helm release?
- [ ] Can you manage dev/prod variants with Kustomize?

---

### Week 16, Day 1–7: Kubernetes Project — Production-Ready Cluster

**Deploy your entire `infra_practice` app on Kubernetes with:**

1. **Namespace** isolation (`dev`, `staging`, `prod`)
2. **Deployment** with resource requests/limits, 3+ replicas
3. **Service** (ClusterIP for internal, NodePort for dev access)
4. **Ingress** with TLS via cert-manager
5. **ConfigMap** for app configuration
6. **Secret** (SealedSecret) for DB credentials
7. **PostgreSQL StatefulSet** with PVC
8. **NetworkPolicy** — default deny + explicit allow rules
9. **HPA** for autoscaling
10. **Prometheus + Grafana** monitoring
11. **Loki** for log aggregation
12. **Helm chart** packaging everything

**Deliverable:** A Git repo with:
- `k8s/` directory with all manifests
- `helm/` directory with your chart
- `README.md` explaining how to deploy
- Screenshots of Grafana dashboard

#### Validation Checklist

- [ ] Can you deploy the entire stack with `helm install`?
- [ ] Can you scale to 10 replicas under load?
- [ ] Can you view logs, metrics, and traces in one place?
- [ ] Can you rotate the DB password and update the SealedSecret?

---

