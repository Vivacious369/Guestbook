# Guestbook Infrastructure Setup

## Overview
This repository contains the infrastructure setup for deploying the Guestbook application in a local Kubernetes cluster using `kind`. It also includes a monitoring and logging stack to observe the system and an alerting mechanism to notify on critical events.

## Prerequisites
Before proceeding, ensure you have the following installed:

- [Docker](https://www.docker.com/get-started)
- [Kubernetes CLI (`kubectl`)](https://kubernetes.io/docs/tasks/tools/)
- [Kind](https://kind.sigs.k8s.io/docs/user/quick-start/)
- [Helm](https://helm.sh/docs/intro/install/)
- [jq](https://stedolan.github.io/jq/)

## Repository Structure
```
.
├── k8s/                 # Kubernetes manifests for application deployment
├── monitoring/          # Monitoring stack (Prometheus, Grafana, Loki, Promtail, Alertmanager)
├── scripts/             # Automation scripts for setup and deployment
│   ├── start-local.sh   # Starts the local Kubernetes cluster and registry
│   ├── deploy.sh        # Builds and deploys the services
│   ├── cleanup.sh       # Stops and cleans up the cluster
├── README.md            # Setup and usage instructions
```

---

## Step 1: Start the Local Kubernetes Cluster

Run the following script to create a `kind` cluster with a local container registry:
```sh
chmod +x scripts/start-local.sh
./scripts/start-local.sh
```

Verify the cluster is running:
```sh
kubectl cluster-info --context kind-guestbook-cluster
kubectl get nodes
```

---

## Step 2: Deploy Monitoring and Logging Stack

### Deploy using Helm
Run the following commands to install Prometheus, Grafana, Loki, and Promtail:
```sh
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

helm install prometheus prometheus-community/kube-prometheus-stack --namespace monitoring --create-namespace
helm install loki grafana/loki-stack --namespace monitoring
```

### Verify the Deployment
```sh
kubectl get pods -n monitoring
kubectl get svc -n monitoring
```

### Access Grafana Dashboard
```sh
kubectl port-forward svc/prometheus-grafana -n monitoring 3000:80
```
Access Grafana at: [http://localhost:3000](http://localhost:3000)  
Default credentials: `admin` / `prom-operator`

---

## Step 3: Deploy Guestbook Application

### Build and Push Docker Images
Run the following script to build and push the frontend and backend images to the local registry:
```sh
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

### Apply Kubernetes Manifests
```sh
kubectl apply -f k8s/
```

### Verify the Deployment
```sh
kubectl get pods
kubectl get svc
```

### Access the Guestbook Application
```sh
kubectl port-forward svc/frontend 8080:80
```
Go to: [http://localhost:8080](http://localhost:8080)

---

## Step 4: Set Up Alerting

### Configure Alertmanager with PagerDuty (or another service)
Edit the `alertmanager-config.yaml` and replace `<PAGERDUTY_KEY>` with your API key.
```yaml
route:
  receiver: 'pagerduty'
receivers:
  - name: 'pagerduty'
    pagerduty_configs:
      - service_key: '<PAGERDUTY_KEY>'
```

Apply the configuration:
```sh
kubectl apply -f monitoring/alertmanager-config.yaml
```

### Test Alerts
```sh
kubectl apply -f monitoring/test-alert.yaml
```

---

## Step 5: Clean Up
To delete the cluster and remove all resources:
```sh
chmod +x scripts/cleanup.sh
./scripts/cleanup.sh
```

---

## Important Commands

### Check Running Pods
```sh
kubectl get pods -A
```

### Check Service Endpoints
```sh
kubectl get svc -A
```

### Get Logs
```sh
kubectl logs -f <pod-name>
```

### Delete All Resources
```sh
kubectl delete -f k8s/
kubectl delete -f monitoring/
```

---
