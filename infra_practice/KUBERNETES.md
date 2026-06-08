# Kubernetes — Architecture First, Then Everything Else

> **Assumption**: You know Docker, multi-stage builds, and Docker Compose.
> **Goal**: Understand how Kubernetes works architecturally, then deploy the FastAPI app from this repo in minutes.
> **Style**: Short, opinionated, 2026-updated. Architecture first, hands-on second.

---

## The Big Idea (60 Seconds)

Kubernetes is a **distributed operating system for containers**.

| Without K8s                                         | With K8s                                                              |
|-----------------------------------------------------|-----------------------------------------------------------------------|
| You manage containers manually on each server       | You declare "I want 3 copies of my app" — K8s makes it happen forever |
| A server dies → your app is down                    | A node dies → K8s moves your app to a healthy node automatically      |
| Scaling means provisioning VMs and installing stuff | Scaling is one command: `kubectl scale --replicas=10`                 |
| You write bash scripts to deploy                    | You apply YAML files; K8s reconciles reality to match                 |

The core pattern: **You declare desired state → Kubernetes continuously reconciles.**

---

## Part 1: Architecture — How Kubernetes Actually Works

### The Two Planes

```
┌─────────────────────────────────────────────┐
│           CONTROL PLANE (The Brain)          │
│  ┌─────────────┐  ┌─────────┐  ┌─────────┐  │
│  │ API Server  │  │Scheduler│  │Controller│ │
│  │   (Gateway) │  │(Picks    │  │ Manager │  │
│  │             │  │  nodes)  │  │(Heals)  │  │
│  └──────┬──────┘  └─────────┘  └─────────┘  │
│  ┌───────────────────────────────────────┐  │
│  │              etcd                     │  │
│  │    (Source of Truth — key/value DB)   │  │
│  └───────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Worker Node │ │  Worker Node │ │  Worker Node │
│ ┌──────────┐ │ │ ┌──────────┐ │ │ ┌──────────┐ │
│ │  Kubelet │ │ │ │  Kubelet │ │ │ │  Kubelet │ │
│ │(Agent)   │ │ │ │(Agent)   │ │ │ │(Agent)   │ │
│ ├──────────┤ │ │ ├──────────┤ │ │ ├──────────┤ │
│ │ Kube-    │ │ │ │ Kube-    │ │ │ │ Kube-    │ │
│ │ Proxy    │ │ │ │ Proxy    │ │ │ │ Proxy    │ │
│ ├──────────┤ │ │ ├──────────┤ │ │ ├──────────┤ │
│ │containerd│ │ │ │containerd│ │ │ │containerd│ │
│ │(Runtime) │ │ │ │(Runtime) │ │ │ │(Runtime) │ │
│ └──────────┘ │ │ └──────────┘ │ │ └──────────┘ │
│   Pods run   │ │   Pods run   │ │   Pods run   │
│     here     │ │     here     │ │     here     │
└──────────────┘ └──────────────┘ └──────────────┘
```

### Control Plane Components

| Component                   | What It Does                                                                                       | 2026 Note                                                 |
|-----------------------------|----------------------------------------------------------------------------------------------------|-----------------------------------------------------------|
| **kube-apiserver**          | The **only** entry point. Every command, every internal component talks through here.              | Now supports GraphQL access in some distributions         |
| **etcd**                    | Distributed key-value store. The **source of truth**. If it isn't in etcd, it doesn't exist.       | etcd 5.0 adds distributed encryption and faster snapshots |
| **kube-scheduler**          | Watches for new Pods and picks the best Worker Node based on resources, constraints, and policies. | ML-powered scheduling is emerging in enterprise distros   |
| **kube-controller-manager** | Runs loops that compare desired state vs actual state. If they differ, it takes action.            | The true "self-healing" engine                            |

### Worker Node Components

| Component             | What It Does                                                                               |
|-----------------------|--------------------------------------------------------------------------------------------|
| **kubelet**           | Talks to API Server, ensures containers are running as specified, reports health           |
| **kube-proxy**        | Manages network rules so Services can route traffic to Pods                                |
| **container runtime** | Runs containers. **containerd** is the standard (Docker as a runtime was removed in 1.24+) |

### The Request Flow (What Happens When You Run `kubectl apply`)

```
1. kubectl → sends YAML to API Server
2. API Server → validates YAML, writes to etcd
3. Controller Manager → notices new desired state
4. Scheduler → assigns Pod to a healthy Worker Node
5. Kubelet on that node → talks to containerd → starts container
6. Controller Manager → continuously watches. If a Pod dies, it creates a replacement.
```

This loop runs forever. That's why Kubernetes is called a **reconciliation engine**.

---

## Part 2: The Mental Model — Compose → Kubernetes

You already know Docker Compose. Here's the translation:

| Docker Compose      | Kubernetes Equivalent                   | Why It's Different                                                     |
|---------------------|-----------------------------------------|------------------------------------------------------------------------|
| `services:`         | **Deployment**                          | K8s adds self-healing, scaling, rolling updates                        |
| `image:`            | `spec.template.spec.containers[].image` | K8s pulls from a registry; no local build                              |
| `ports:`            | **Service**                             | Pods get ephemeral IPs; a Service provides stable DNS + load balancing |
| `environment:`      | **ConfigMap** + **Secret**              | Separated into sensitive vs non-sensitive                              |
| `volumes:`          | **PersistentVolumeClaim**               | Storage outlives Pod lifecycle                                         |
| `depends_on:`       | Readiness probes + retries              | K8s doesn't sequence startup; apps must tolerate missing deps          |
| `restart: always`   | Built-in + liveness probes              | Automatic restart, but with health-based intelligence                  |
| `docker compose up` | `kubectl apply -f .`                    | Both declarative, but K8s continuously reconciles                      |

Two concepts that have **no Compose equivalent**:
- **Pod**: A wrapper around 1+ containers sharing network and storage. The scheduling unit.
- **Controller**: A loop that watches and heals. Deployment, StatefulSet, Job are all controllers.

---

## Part 3: Hands-On — Deploy Your App in 10 Minutes

### Prerequisites

```bash
# Install kind (recommended for 2026 — fastest, most CI-like)
brew install kind
kind create cluster --name learn-k8s

# Verify
kubectl version --client
kubectl cluster-info
kubectl get nodes
```

> 2026 context: **kind** is preferred over minikube for local development. It's faster and behaves more like a real cloud cluster.

### Build and Load Your Image

```bash
cd app
docker build -t infra-practice-app:v1 .
kind load docker-image infra-practice-app:v1 --name learn-k8s
```

> 2026 context: Docker is no longer a container runtime inside Kubernetes. **containerd** is the standard. But you still use Docker (or podman) to *build* images.

### Deploy Everything at Once

Create `k8s/app.yaml` (one file, all objects):

```yaml
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-deployment
  labels:
    app: fastapi-infra
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fastapi-infra
  template:
    metadata:
      labels:
        app: fastapi-infra
    spec:
      containers:
        - name: app
          image: infra-practice-app:v1
          ports:
            - containerPort: 8000
          envFrom:
            - configMapRef:
                name: fastapi-config
            - secretRef:
                name: fastapi-secret
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 3
            periodSeconds: 5
          resources:
            requests:
              memory: "128Mi"
              cpu: "100m"
            limits:
              memory: "256Mi"
              cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: fastapi-service
spec:
  type: NodePort
  selector:
    app: fastapi-infra
  ports:
    - port: 80
      targetPort: 8000
      nodePort: 30080
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: fastapi-config
data:
  SERVICE_NAME: "infra-practice-app"
  LOG_LEVEL: "info"
  APP_ENV: "production"
  VERSION: "1.0.0-k8s"
---
apiVersion: v1
kind: Secret
metadata:
  name: fastapi-secret
type: Opaque
stringData:
  API_KEY: "super-secret-api-key-12345"
```

Apply it:

```bash
kubectl apply -f k8s/app.yaml
```

### Verify

```bash
# See everything running
kubectl get all -l app=fastapi-infra

# Port-forward and test
curl http://localhost:30080/health
curl http://localhost:30080/config
```

### Test Self-Healing

```bash
# Delete a pod — watch it come back
kubectl delete pod -l app=fastapi-infra --wait=false
kubectl get pods -l app=fastapi-infra -w
```

### Scale

```bash
kubectl scale deployment fastapi-deployment --replicas=5
```

That's it. Those 5 commands + 1 YAML file are 80% of what you'll do daily.

---

## Part 4: The Essential Objects — What to Know

You don't need to memorize everything. Know these 6 objects and you can figure out the rest.

### 1. Pod
The smallest unit. Usually 1 container. Disposable.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  containers:
    - name: app
      image: my-image
```

> You almost never create Pods directly. Deployments create them for you.

### 2. Deployment
Manages Pods. Self-healing, scalable, rolling updates.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
        - name: app
          image: my-image:v1
```

### 3. Service
Stable IP + DNS + load balancing for Pods.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  selector:
    app: my-app        # Routes to Pods with this label
  ports:
    - port: 80
      targetPort: 8000
```

| Type | Use Case |
|---|---|
| `ClusterIP` | Internal only (default, most common) |
| `NodePort` | Exposes on a node port (30000-32767) |
| `LoadBalancer` | Cloud load balancer |

### 4. ConfigMap
Non-sensitive configuration.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: my-config
data:
  LOG_LEVEL: "info"
```

### 5. Secret
Sensitive data. Base64-encoded, **not encrypted by default**.

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: my-secret
type: Opaque
stringData:
  API_KEY: "secret-value"
```

> 2026 best practice: Use **External Secrets Operator** or **Sealed Secrets** in production. Never commit raw Secret YAMLs to Git.

### 6. Ingress
HTTP routing. Needs an **Ingress Controller** (NGINX, Traefik) to work.

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-ingress
spec:
  rules:
    - host: myapp.local
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: my-service
                port:
                  number: 80
```

---

## Part 5: Production Readiness (2026 Edition)

Before you call it "production," check these. This is condensed from current industry best practices.

| # | Check | Why |
|---|---|---|
| 1 | **Immutable image tags** — never `latest` | Reproducible deployments |
| 2 | **Liveness + readiness probes** | Self-healing and traffic routing |
| 3 | **Resource requests + limits** | Prevents starvation, helps scheduling |
| 4 | **Rolling update strategy** (`maxUnavailable: 0`) | Zero-downtime deployments |
| 5 | **HPA** (Horizontal Pod Autoscaler) | Auto-scales with traffic |
| 6 | **Secrets from external vaults** (ESO, Vault) | K8s Secrets are not encrypted at rest |
| 7 | **Network Policies** (default deny, explicit allow) | 2026 must-have for security |
| 8 | **Pod Security Standards** (restricted profile) | Prevents privileged containers |
| 9 | **RBAC** — least privilege, no `cluster-admin` for apps | Limits blast radius |
| 10 | **Logs to stdout/stderr**, metrics to Prometheus | Observability |
| 11 | **Ingress with TLS** (cert-manager + Let's Encrypt) | Secure traffic |
| 12 | **GitOps** (ArgoCD / Flux) — Git is the source of truth | No `kubectl apply` from laptops |
| 13 | **eBPF-based CNI** (Cilium) | 2026 standard for performance, security, observability |

---

## Part 6: kubectl — The Only Commands You Need

```bash
# Inspect
kubectl get pods,svc,deploy -l app=fastapi-infra   # Filtered list
kubectl get pods -A                                # All namespaces
kubectl describe pod <name>                        # Why is it stuck?
kubectl logs <pod> -f --tail=100                   # Stream logs
kubectl logs <pod> --previous                      # Crashed container logs
kubectl exec -it <pod> -- /bin/sh                  # Shell into container
kubectl get events --sort-by=.lastTimestamp        # What just happened?

# Workloads
kubectl apply -f file.yaml                         # Create / update
kubectl apply -f directory/                        # Apply all YAMLs
kubectl diff -f file.yaml                          # Preview changes
kubectl delete -f file.yaml                        # Remove
kubectl scale deployment <name> --replicas=5
kubectl rollout status deployment <name>
kubectl rollout undo deployment <name>

# Port-forward (bypass Service/Ingress for quick tests)
kubectl port-forward deploy/fastapi-deployment 8000:8000

# Config and secrets
kubectl get configmap fastapi-config -o yaml
kubectl get secret fastapi-secret -o jsonpath='{.data.API_KEY}' | base64 -d
```

---

## Troubleshooting Quick Reference

| Symptom | First Check | Likely Fix |
|---|---|---|
| `ImagePullBackOff` | `kubectl describe pod` → Events | Wrong image name/tag, or image not loaded/pushed |
| `CrashLoopBackOff` | `kubectl logs <pod> --previous` | App crashes on start — missing env var, wrong port |
| `Pending` forever | `kubectl describe pod` → Events | No node has resources, or PVC can't bind |
| `OOMKilled` | `kubectl describe pod` → Last State | Raise `resources.limits.memory` |
| Service returns 503 | `kubectl get endpoints <svc>` | Readiness probe failing → 0 healthy endpoints |

---

## What to Learn Next (Pick Your Path)

Once the architecture clicks and you can deploy your app, deepen based on what you need:

| If you care about… | Learn Next |
|---|---|
| Running real workloads | **Namespaces**, **RBAC**, **NetworkPolicies** |
| Scaling automatically | **HPA**, **Cluster Autoscaler**, **PodDisruptionBudget** |
| Packaging for teams | **Helm** or **Kustomize** |
| Delivery automation | **ArgoCD** / **Flux** (GitOps) |
| Security hardening | **Pod Security Standards**, **NetworkPolicies**, **Falco/Tetragon** |
| Observing production | **Prometheus + Grafana**, **Loki** (logs) |
| Certifications | **CKAD** (developer focus), then **CKA** (admin focus) |

---

## Sources & 2026 References

- [Kubernetes Official Docs — Components](https://kubernetes.io/docs/concepts/overview/components/)
- [Kubernetes Tutorial for Beginners 2026 — KodeKloud](https://kodekloud.com/blog/kubernetes-tutorial-for-beginners-2025/)
- [Kubernetes Architecture 2026 — GeeksforGeeks](https://www.geeksforgeeks.org/devops/kubernetes-architecture/)
- [Kubernetes Security Best Practices 2026](https://core.cz/en/know-how/security-kubernetes-best-practices-2026/)
- [Top 10 Kubernetes Best Practices for 2026](https://devopsconnecthub.com/latest-article/kubernetes-best-practices/)
- [Kubernetes Controller Manager Explained — 2026](https://learnkube.com/kubernetes-controller-manager-explained)
- [Kubernetes RBAC Best Practices 2026](https://novaaiops.com/blog/kubernetes-rbac-best-practices-2026)
