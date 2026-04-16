# Kubernetes Learning Guide — infra_practice

> **Learning Mode**: You write every line. I (your guide) ask questions.  
> **Goal**: Take the existing FastAPI app from Docker Compose to a production-ready Kubernetes deployment.

---

## 🎯 Learning Philosophy

For every step, answer these four questions **before** you run any command:

1. **Architecture First**: What objects are involved? How do they talk to each other?
2. **Bottleneck Search**: What breaks if you scale to 100 pods?
3. **Active Refactoring**: How do you make it more robust?
4. **Failure Injection**: If you delete a pod, what happens? If the node dies?

---

## 📋 Prerequisites

You need a running Kubernetes cluster on your local machine. Pick **one**:

| Option | Install Command | Best For |
|--------|----------------|----------|
| Docker Desktop | Enable K8s in Settings | Easiest if Docker is already installed |
| minikube | `brew install minikube` | Most tutorials match this |
| kind | `brew install kind` | Lightweight, CI/CD realistic |

Verify your setup:

```bash
kubectl version --client
kubectl cluster-info
kubectl get nodes
```

---

## Phase 0: Know Your Starting Point

The `infra_practice` project currently has:
- `app/main.py` — FastAPI with `/`, `/health`, `/hello`
- `app/Dockerfile` — Multi-stage Docker build
- `infra/docker-compose*.yml` — Local deployment
- `infra/Makefile` — `make run`, `make deploy`, `make test`

### Your Task
1. Run the app locally via Docker Compose:
   ```bash
   cd infra_practice/infra
   make run
   make test
   ```
2. Inspect the Dockerfile. Write down **why multi-stage builds matter** when Kubernetes pulls your image.

---

## Phase 1: Image Registry

Kubernetes cannot build images from a local Dockerfile (unless you use `minikube docker-env` or `kind load`). It pulls images from a registry.

### Your Task
1. Build and tag the image for your registry:
   ```bash
   cd infra_practice/app
   docker build -t <your-dockerhub-username>/infra-practice-app:v1.0.0 .
   ```
2. Push it to Docker Hub (or any registry):
   ```bash
   docker push <your-dockerhub-username>/infra-practice-app:v1.0.0
   ```
3. If using **minikube**, you can skip the push and build directly inside minikube:
   ```bash
   eval $(minikube docker-env)
   docker build -t infra-practice-app:v1.0.0 .
   ```

### Think About It

**Q1: Why does Kubernetes need a registry, while Docker Compose can build locally?**

Docker Compose runs on your single machine and has access to your local files and Docker daemon, so it can build images directly from a local `Dockerfile`. Kubernetes is a distributed cluster with multiple nodes. When it schedules a pod, the chosen node does not have your source code or your local filesystem — it can only pull pre-built images from a remote registry (Docker Hub, ECR, GCR, etc.).

> **Analogy**: Docker Compose is like cooking in your own kitchen from your fridge. Kubernetes is like a restaurant chain across the city — you ship frozen meals from a central factory (the registry) rather than sending a chef to every kitchen.

**Q2: What happens if your image tag is `latest` and you restart a pod 3 days later?**

The `latest` tag is not "the newest version forever" — it points to whatever image was tagged `latest` at the exact moment the pod pulls it. If you push a new image tagged `latest` later, existing pods keep running the old image they already pulled. But if a pod restarts or gets rescheduled days later, it will pull `latest` again and may silently get a **different version** than before. This leads to unplanned deployments and makes debugging a nightmare.

> **Golden rule**: Always use immutable tags like `v1.0.0` or `sha-abc123` in Kubernetes. `latest` is okay for learning, but avoid it in production.

---

## Phase 2: First Deployment

A `Deployment` manages ReplicaSets, which manage Pods.

### Your Task
Create a file: `infra_practice/k8s/deployment.yaml`

Requirements:
- **3 replicas** of the FastAPI app
- Container port `8000`
- Image: the one you pushed in Phase 1
- Label: `app: fastapi-infra`

Apply it:
```bash
kubectl apply -f k8s/deployment.yaml
kubectl get pods -l app=fastapi-infra
kubectl describe deployment fastapi-infra
```

### Think About It
- If you delete one pod manually (`kubectl delete pod <name>`), what happens? Watch with `kubectl get pods -w`.
- Where is the pod's IP accessible from? Can you curl it from your laptop?

---

## Phase 3: Expose the App — Service

Pods come and go. Their IPs change. A `Service` gives a stable endpoint.

### Your Task
Create a file: `infra_practice/k8s/service.yaml`

Requirements:
- Type: `NodePort` (for local access)
- Target port: `8000`
- Selector: `app: fastapi-infra`
- NodePort: `30080` (or let Kubernetes assign one)

Apply it and test:
```bash
kubectl apply -f k8s/service.yaml
kubectl get svc
# Access it:
curl http://$(minikube ip):30080/health
# or if Docker Desktop:
curl http://localhost:30080/health
```

### Think About It
- What is the difference between `ClusterIP`, `NodePort`, and `LoadBalancer`?
- In a real cloud environment (AWS/GCP), which service type would you use?

---

## Phase 4: Health Checks — Liveness & Readiness

Your app already has `/health`. Let's wire it into Kubernetes.

### Your Task
Update `infra_practice/k8s/deployment.yaml` to add:

- **Liveness probe** on `/health` (port 8000)
  - `initialDelaySeconds: 5`
  - `periodSeconds: 10`
- **Readiness probe** on `/health` (port 8000)
  - `initialDelaySeconds: 3`
  - `periodSeconds: 5`

Apply the update:
```bash
kubectl apply -f k8s/deployment.yaml
kubectl describe pod <pod-name>
```

### Failure Injection
1. Temporarily break `/health` in `app/main.py` so it returns HTTP 500.
2. Build and push a new image tag (`v1.0.1-broken`).
3. Update the Deployment to use the broken image.
4. Watch what happens: `kubectl get pods -w` and `kubectl describe pod <name>`.
5. Fix it by rolling back to `v1.0.0`.

### Think About It
- What is the difference between liveness and readiness?
- If readiness fails, does Kubernetes restart the pod?
- If liveness fails, does traffic still route to the pod?

---

## Phase 5: Configuration & Secrets

Hardcoding values in the container is bad practice. Use `ConfigMap` for env vars and `Secret` for sensitive data.

### Your Task
1. Add a new env var to `app/main.py` (e.g., `SERVICE_NAME` or `LOG_LEVEL`). Make it appear in the `/hello` or `/` response.
2. Create `infra_practice/k8s/configmap.yaml`:
   - Key: `SERVICE_NAME`, Value: `k8s-fastapi-demo`
   - Key: `LOG_LEVEL`, Value: `info`
3. Create `infra_practice/k8s/secret.yaml`:
   - Key: `API_KEY`, Base64-encoded value: `bXktc2VjcmV0LWtleQ==` (or encode your own)
4. Update `deployment.yaml` to inject both the ConfigMap and Secret as environment variables.

Apply and verify:
```bash
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/deployment.yaml
kubectl exec -it <pod-name> -- env | grep SERVICE_NAME
```

### Think About It
- Why is a `Secret` only Base64-encoded and not encrypted by default?
- Where would you store real secrets in production? (Hint: vaults, sealed secrets, external secret operators)

---

## Phase 6: Scaling & Updates

### Part A — Manual Scaling
```bash
kubectl scale deployment fastapi-infra --replicas=5
kubectl get pods -w
kubectl scale deployment fastapi-infra --replicas=2
```

### Part B — Rolling Update
1. Update `app/main.py` (e.g., change the hello message).
2. Build and push `v1.0.2`.
3. Update `deployment.yaml` image to `v1.0.2`.
4. Apply and watch:
   ```bash
   kubectl apply -f k8s/deployment.yaml
   kubectl rollout status deployment/fastapi-infra
   kubectl get pods -w
   ```

### Part C — Rollback
```bash
kubectl rollout history deployment/fastapi-infra
kubectl rollout undo deployment/fastapi-infra
kubectl rollout undo deployment/fastapi-infra --to-revision=2
```

### Think About It
- What happens to active HTTP requests during a rolling update? Is there downtime?
- How would you ensure **zero-downtime deployments**? (Hint: readiness probes + maxUnavailable)

---

## Phase 7: Ingress

`NodePort` is fine for learning, but real clusters use `Ingress` for HTTP routing.

### Your Task
1. Enable an Ingress controller (if using minikube):
   ```bash
   minikube addons enable ingress
   ```
   On Docker Desktop, you may install NGINX Ingress Controller manually.
2. Create `infra_practice/k8s/ingress.yaml`:
   - Host: `fastapi.local`
   - Path: `/`
   - Backend service: your `fastapi-infra` service on port `8000`
3. Add `fastapi.local` to your `/etc/hosts` file pointing to your cluster IP.
4. Test: `curl http://fastapi.local/health`

### Think About It
- Why do you need an Ingress *controller* (e.g., NGINX) and an Ingress *resource*?
- What would happen if you had 10 microservices all exposed via Ingress on the same IP?

---

## Phase 8: Stateful Service — PostgreSQL

Real apps need databases. In Kubernetes, databases can run as `StatefulSets` or be managed outside the cluster.

### Your Task
1. Create `infra_practice/k8s/postgres-statefulset.yaml`:
   - 1 replica of Postgres
   - Persistent storage via a `PersistentVolumeClaim`
   - Service type: `ClusterIP`
2. Create `infra_practice/k8s/postgres-service.yaml`.
3. Update `app/main.py` to connect to Postgres using `asyncpg` or `psycopg2`.
4. Update `deployment.yaml` to inject the DB connection string via a Secret.

Or, as a simpler alternative:
- Deploy Postgres using the official Helm chart and explain what Helm did for you.

### Think About It
- Why is a `StatefulSet` better than a `Deployment` for databases?
- What happens to your data if the Postgres pod is deleted?
- In production, would you run Postgres inside Kubernetes or use a managed cloud database?

---

## Phase 9: Package Everything with Helm

Writing raw YAML for every microservice is repetitive. Helm packages Kubernetes manifests into reusable templates.

### Your Task
1. Install Helm: `brew install helm`
2. Create a chart:
   ```bash
   helm create infra-practice
   ```
3. Move your `deployment.yaml`, `service.yaml`, `configmap.yaml`, and `ingress.yaml` into the Helm chart templates.
4. Parameterize at least these values in `values.yaml`:
   - `replicaCount`
   - `image.repository`
   - `image.tag`
   - `service.port`
   - `ingress.enabled`
5. Install the chart:
   ```bash
   helm install infra-practice ./infra-practice
   helm upgrade infra-practice ./infra-practice
   ```

### Think About It
- What is the difference between `helm install` and `helm upgrade`?
- How does Helm manage revisions, and how can you roll back a Helm release?

---

## ❓ Frequently Asked Questions (FAQ)

### Q: What is the difference between a Pod, a Deployment, and a ReplicaSet?

**Pod** is the smallest deployable unit — one or more containers running together on the same node with shared networking and storage.

**ReplicaSet** ensures a specific number of pod replicas are running at all times. If a pod dies, the ReplicaSet creates a new one.

**Deployment** is a higher-level controller that manages ReplicaSets. It adds declarative updates, rolling updates, and rollbacks. You almost always interact with Deployments, not ReplicaSets directly.

> **Rule of thumb**: Users create **Deployments**. Deployments create and manage **ReplicaSets**. ReplicaSets create and manage **Pods**.

---

### Q: What is the difference between ClusterIP, NodePort, and LoadBalancer?

| Type | Scope | Use Case |
|------|-------|----------|
| **ClusterIP** | Internal to the cluster only | Microservice-to-microservice communication |
| **NodePort** | Exposes the service on a static port of each node's IP | Learning, small demos, or when you don't have a cloud load balancer |
| **LoadBalancer** | Provisions an external cloud load balancer (AWS ELB, GCP LB) | Production apps in cloud environments |

In real cloud environments, you usually use `ClusterIP` for internal services and `LoadBalancer` (or Ingress) for public-facing apps.

---

### Q: What is the difference between Liveness and Readiness probes?

**Liveness probe**: Asks "Is this pod still alive?" If it fails, Kubernetes **restarts the container**.

**Readiness probe**: Asks "Is this pod ready to accept traffic?" If it fails, Kubernetes **removes the pod from the Service endpoints** so no traffic goes to it. The pod keeps running.

> **Key difference**: Liveness = restart; Readiness = remove from traffic.

---

### Q: If readiness fails, does Kubernetes restart the pod?

**No.** A failed readiness probe only removes the pod from the Service's endpoint list. The pod continues running. This is useful during startup or temporary overload — the pod gets a chance to recover without being killed.

---

### Q: If liveness fails, does traffic still route to the pod?

**No.** When liveness fails, Kubernetes restarts the container. During the restart, the old container is terminated and a new one starts. There is a brief window where the pod is not ready, so traffic does not reach it.

---

### Q: Why is a Secret only Base64-encoded and not encrypted by default?

Base64 is **encoding**, not encryption. Anyone with access to the cluster can read a Secret. By default, Kubernetes stores Secrets in `etcd` (its database) in plain text unless you enable **encryption at rest**.

In production, use:
- **Sealed Secrets** (encrypted Secrets committed to Git)
- **External Secrets Operator** (fetches from AWS Secrets Manager, Vault, etc.)
- **HashiCorp Vault** or cloud-native secret managers

---

### Q: What happens to active HTTP requests during a rolling update? Is there downtime?

By default, Kubernetes starts new pods before terminating old ones. However, **active requests on an old pod can be dropped** if that pod is killed before finishing them.

To ensure **zero downtime**:
1. Use a **readiness probe** so traffic only goes to pods that are truly ready.
2. Set a **graceful shutdown handler** in your app (listen for SIGTERM and finish requests before exiting).
3. Configure `maxUnavailable` and `maxSurge` in the Deployment strategy.

---

### Q: Why do you need an Ingress *controller* and an Ingress *resource*?

Think of it like a traffic cop:
- **Ingress resource** is the *rulebook* — it says "requests to `fastapi.local` go to Service X."
- **Ingress controller** is the *actual cop* — it reads the rulebook and enforces it. Without the controller, the rules just sit there doing nothing.

Popular controllers: NGINX Ingress Controller, Traefik, HAProxy.

---

### Q: What would happen if you had 10 microservices all exposed via Ingress on the same IP?

That is exactly what Ingress is designed for! One Ingress controller (one external IP / load balancer) can route traffic to many services based on:
- **Hostnames** (`api.example.com` vs `blog.example.com`)
- **Paths** (`/users` → user-service, `/orders` → order-service)

This saves cost and simplifies management compared to creating 10 separate `LoadBalancer` services.

---

### Q: Why is a StatefulSet better than a Deployment for databases?

**Deployments** create identical, interchangeable pods. If a pod dies, a new one is created with a new name and new identity.

**StatefulSets** give each pod a **stable, unique identity**:
- Predictable names: `postgres-0`, `postgres-1`
- Stable network identity
- Persistent storage that follows the pod even after rescheduling

This is critical for databases because they need to keep their data and identity across restarts.

---

### Q: What happens to my data if the Postgres pod is deleted?

If you used a **PersistentVolumeClaim (PVC)** in your StatefulSet, the data survives. When Kubernetes recreates the pod, it reattaches the same volume. If you did **not** use a PVC, the data is lost forever.

> **Golden rule**: Stateless apps can use Deployments without volumes. Stateful apps (databases) must use StatefulSets + PersistentVolumes.

---

### Q: In production, should I run Postgres inside Kubernetes or use a managed cloud database?

**Most teams use managed databases** (AWS RDS, Google Cloud SQL, Azure Database) in production because:
- Automated backups, patching, and failover
- Expert support and monitoring
- Less operational complexity

Running databases in Kubernetes is possible and improving, but it requires deep expertise in storage, backups, and disaster recovery. It's a good learning exercise, but not the default for production.

---

### Q: What is the difference between `helm install` and `helm upgrade`?

- **`helm install`**: Deploys a chart for the **first time**. Creates a new "release."
- **`helm upgrade`**: Updates an **existing** release with new values or a new chart version.

If you try to `helm install` with a release name that already exists, it will fail. Use `helm upgrade --install` if you want "install if not exists, otherwise upgrade."

---

### Q: How does Helm manage revisions, and how can you roll back?

Helm stores every release as a **revision**. When you `helm upgrade`, it creates revision 2, 3, 4, etc. You can see them with:
```bash
helm history <release-name>
```

To roll back:
```bash
helm rollback <release-name> <revision-number>
```

This is similar to `kubectl rollout undo`, but works at the Helm chart level (which may include multiple resources at once).

---

### Q: What is a Namespace, and why should I care?

A **Namespace** is a virtual cluster inside your physical cluster. It lets you isolate resources.

Common pattern:
- `dev` namespace for development
- `staging` namespace for pre-production testing
- `prod` namespace for live traffic

This prevents name collisions and lets you apply different resource quotas and access rules per environment.

```bash
kubectl create namespace dev
kubectl apply -f deployment.yaml -n dev
kubectl get pods -n dev
```

---

### Q: My pod is stuck in `ImagePullBackOff`. What does that mean?

Kubernetes tried to pull your container image and **failed**. Common causes:
- Typo in the image name or tag
- Image doesn't exist in the registry
- The registry requires authentication (missing `imagePullSecret`)
- Network issue preventing the node from reaching the registry

Fix: Check `kubectl describe pod <name>` for the exact error, verify the image exists, and ensure credentials are configured.

---

### Q: My pod is stuck in `CrashLoopBackOff`. What does that mean?

The container starts but **crashes repeatedly**. Kubernetes tries to restart it, waits, tries again — creating a loop.

Common causes:
- App crashes immediately on startup (check `kubectl logs <pod-name>`)
- Missing environment variables or secrets
- Database connection failure on startup
- Port conflict or permission issue

Fix: Read the logs with `kubectl logs <pod-name> --previous` to see why it crashed.

---

### Q: What is a PersistentVolume (PV) vs a PersistentVolumeClaim (PVC)?

**PersistentVolume (PV)** is a piece of storage in the cluster (like an AWS EBS volume or a local disk). It is provisioned by an administrator or automatically by a storage class.

**PersistentVolumeClaim (PVC)** is a request for storage by a user or pod. It says "I need 10GB of storage." Kubernetes binds the PVC to a suitable PV.

> **Analogy**: PV is the actual hard drive. PVC is the request form asking for a hard drive of a certain size.

---

## 🧪 Validation Checklist

Before you say "I'm done," verify you can do all of these without looking at notes:

- [ ] Explain the difference between a Pod, Deployment, ReplicaSet, and Service
- [ ] Scale an app from 2 to 10 replicas and back
- [ ] Perform a rolling update and a rollback
- [ ] Read pod logs and exec into a running container
- [ ] Explain why liveness and readiness probes matter
- [ ] Inject environment variables from ConfigMap and Secret
- [ ] Expose an app via Ingress with a custom domain
- [ ] Install and upgrade a Helm chart

---

## 🛠️ Essential Commands Cheat Sheet

```bash
# Cluster info
kubectl cluster-info
kubectl get nodes

# Pods
kubectl get pods
kubectl get pods -w
kubectl describe pod <name>
kubectl logs <name>
kubectl logs <name> -f
kubectl exec -it <name> -- /bin/sh

# Deployments
kubectl get deployments
kubectl apply -f deployment.yaml
kubectl delete -f deployment.yaml
kubectl scale deployment <name> --replicas=3
kubectl rollout status deployment/<name>
kubectl rollout history deployment/<name>
kubectl rollout undo deployment/<name>

# Services
kubectl get svc
kubectl get svc -o wide
kubectl describe svc <name>

# All resources
kubectl get all
kubectl get all -n <namespace>

# Helm
helm list
helm install <release> ./<chart>
helm upgrade <release> ./<chart>
helm rollback <release> <revision>
helm uninstall <release>
```

---

## 📖 Important Terminology (With Analogies)

### Cluster
A set of machines (nodes) that run containerized applications, managed by Kubernetes.

> **Analogy**: A cluster is like an apartment building. Each apartment (node) can house multiple tenants (pods), and the building manager (Kubernetes control plane) decides who lives where.

---

### Node
A single worker machine in a Kubernetes cluster — can be a physical server or a virtual machine.

> **Analogy**: A node is like an individual apartment in the building. It has CPU, memory, and disk resources for the tenants living there.

---

### Pod
The smallest deployable unit in Kubernetes. A Pod can contain one or more containers that share networking and storage.

> **Analogy**: A pod is like a shared apartment for roommates. They share the same address (IP) and fridge (storage), but each has their own bedroom (container).

---

### Container
A lightweight, standalone package that includes everything needed to run an application.

> **Analogy**: A container is like a moving box. You pack your entire room (app + dependencies) inside, and it fits anywhere without worrying about the house layout.

---

### Deployment
A Kubernetes controller that manages the desired state of your application — how many replicas should run, which image to use, and how to update them.

> **Analogy**: A Deployment is like a factory manager. You say "I want 3 workers on the floor," and the manager hires, fires, and shifts workers to keep exactly 3 active at all times.

---

### ReplicaSet
Ensures a specified number of pod replicas are running at any given time.

> **Analogy**: A ReplicaSet is like a thermostat. You set it to 3 pods. If one dies, it automatically turns on another to maintain the temperature (replica count).

---

### Service
Provides a stable network endpoint to access a group of pods, even as individual pods come and go.

> **Analogy**: A Service is like the front desk of a hotel. Guests (traffic) call the front desk number, and the desk routes the call to whichever room (pod) is available. They never dial the room directly.

---

### Label
Key-value pairs attached to Kubernetes objects (like pods) for identification and grouping.

> **Analogy**: Labels are like colored stickers on moving boxes. The Service looks for all boxes with the sticker `app: fastapi-infra` and delivers mail to only those boxes.

---

### Selector
A filter used by controllers and Services to find objects with matching labels.

> **Analogy**: A selector is like a search filter on a shopping website. The Deployment searches for pods with the label `app=fastapi-infra` to know which ones it owns.

---

### Namespace
A virtual cluster inside a physical cluster, used to isolate resources between teams or environments.

> **Analogy**: Namespaces are like separate floors in the same office building. The "dev" floor and "prod" floor don't share printers or meeting rooms, even though they're in the same building.

---

### ConfigMap
An object used to store non-confidential configuration data in key-value pairs.

> **Analogy**: A ConfigMap is like a bulletin board in the office. It holds public notices like office hours, WiFi names, or logo colors — nothing secret.

---

### Secret
An object used to store sensitive data such as passwords, tokens, or API keys.

> **Analogy**: A Secret is like a locked filing cabinet. It stores passwords and keys, but remember — the default lock is just Base64 encoding, not encryption. You need additional tools for a real safe.

---

### Ingress
An API object that manages external access to services inside the cluster, typically via HTTP/HTTPS routing rules.

> **Analogy**: Ingress is like the building's main reception and directory. Visitors arrive at one front door (IP address), and the receptionist routes them: "Floor 3 for API, Floor 5 for blog."

---

### Ingress Controller
The actual software (like NGINX or Traefik) that reads Ingress rules and enforces routing.

> **Analogy**: The Ingress resource is the map. The Ingress Controller is the security guard who actually reads the map and directs people where to go. Without the guard, the map is useless.

---

### PersistentVolume (PV)
A piece of storage in the cluster that has been provisioned by an administrator or dynamic provisioner.

> **Analogy**: A PV is like a dedicated storage locker in the basement. It physically exists and has a specific size.

---

### PersistentVolumeClaim (PVC)
A request for storage by a user or pod. Kubernetes binds the claim to an available PersistentVolume.

> **Analogy**: A PVC is like filling out a storage request form: "I need a 10GB locker." The building manager finds an empty locker (PV) and assigns it to you.

---

### StatefulSet
A controller for managing stateful applications that require stable identity and persistent storage (like databases).

> **Analogy**: A StatefulSet is like assigning numbered parking spots. Even if a tenant moves out and a new one moves in, parking spot #0 always belongs to the same role.

---

### DaemonSet
Ensures that a copy of a specific pod runs on every node in the cluster.

> **Analogy**: A DaemonSet is like installing a smoke detector in every apartment. No matter how many apartments exist, each gets exactly one.

---

### Job
A controller that runs a pod to completion — perfect for one-off tasks like backups or batch processing.

> **Analogy**: A Job is like hiring a plumber for a one-time repair. They come, fix the leak, and leave. You don't keep them on staff forever.

---

### CronJob
A controller that runs Jobs on a repeating schedule.

> **Analogy**: A CronJob is like a weekly cleaning service. Every Sunday at 9 AM, a cleaner arrives, does the job, and leaves until next week.

---

### Liveness Probe
A health check that determines if a container is still alive. If it fails, Kubernetes restarts the container.

> **Analogy**: A liveness probe is like a pulse check. If the patient has no pulse, the doctor performs CPR (restarts the container).

---

### Readiness Probe
A health check that determines if a container is ready to receive traffic.

> **Analogy**: A readiness probe is like a "Do Not Disturb" sign. If the room is not ready, the hotel stops sending guests there, but the room still exists.

---

### Resource Limits
CPU and memory boundaries set for a container to prevent it from consuming all node resources.

> **Analogy**: Resource limits are like data caps on a family phone plan. One teenager can't use all the data and leave nothing for everyone else.

---

### Horizontal Pod Autoscaler (HPA)
Automatically scales the number of pods up or down based on observed metrics like CPU usage.

> **Analogy**: HPA is like an Uber surge system. When demand spikes, more drivers (pods) are added automatically. When demand drops, they log off.

---

### Rolling Update
A deployment strategy where old pods are gradually replaced with new ones to ensure zero downtime.

> **Analogy**: A rolling update is like renovating a hotel one room at a time. Guests can still check in while each room is updated, one by one.

---

### Rollback
Reverting a deployment to a previous version after a failed or undesirable update.

> **Analogy**: A rollback is like pressing Ctrl+Z on a document. You made a bad edit, so you undo it and go back to the last good version.

---

### Helm
A package manager for Kubernetes that bundles YAML manifests into reusable "charts."

> **Analogy**: Helm is like IKEA furniture instructions. Instead of buying each screw and plank separately (raw YAML), you get a complete package with adjustable options (values.yaml).

---

### Chart
A collection of files that describe a related set of Kubernetes resources.

> **Analogy**: A Helm chart is like a recipe book for deploying an app. It tells Kubernetes exactly which ingredients (pods, services, configs) to use and in what order.

---

### ImagePullSecret
A Kubernetes Secret that stores credentials for pulling private container images from a registry.

> **Analogy**: An imagePullSecret is like a VIP membership card. Without it, the club (node) can't let you in to get the special drink (private Docker image).

---

### etcd
The distributed key-value store where Kubernetes saves all cluster data and state.

> **Analogy**: etcd is like the building's central ledger. It records who lives where, what the rules are, and what changes have been made. If the ledger is lost, chaos follows.

---

### kube-scheduler
The control plane component that decides which node a newly created pod should run on.

> **Analogy**: The scheduler is like a restaurant host deciding which table to seat you at, based on room size, available chairs, and your party size.

---

### kube-proxy
A network proxy that runs on each node and maintains network rules for Services.

> **Analogy**: kube-proxy is like the building's internal mailroom. It knows how to deliver letters (packets) to the right apartment (pod) even if tenants move around.

---

### kubectl
The command-line tool used to interact with a Kubernetes cluster.

> **Analogy**: kubectl is like a remote control for your TV (the cluster). You can change channels (contexts), adjust volume (scale), or turn it off (delete resources).

---

## 📚 Recommended Next Steps

After completing this guide, consider learning:
- **Namespaces** — isolate environments (dev, staging, prod)
- **RBAC** — control who can access what
- **NetworkPolicies** — firewall rules between pods
- **Horizontal Pod Autoscaler (HPA)** — auto-scale based on CPU/memory
- **Prometheus + Grafana** — monitor your cluster

---

## 📝 Notes for the Learner

This is a **journey**, not a race. Don't copy-paste manifests. Type them out, break them, fix them, and understand every field. When in doubt, draw the architecture on paper first.

Happy learning! 🚀
