# Guestbook Infrastructure Setup

## Overview
This repository provides the infrastructure setup for deploying the Guestbook application in a local Kubernetes cluster using `kind`. It also includes a comprehensive observability stack powered by **Prometheus** for monitoring and **Grafana** for visualizing metrics, seamlessly integrated with **PagerDuty** to deliver real-time alerts for critical events, ensuring proactive response and system reliability.

## Prerequisites
Before proceeding, ensure you have the following installed:

- [Docker](https://www.docker.com/get-started)
- [Kubernetes CLI (`kubectl`)](https://kubernetes.io/docs/tasks/tools/)
- [Kind](https://kind.sigs.k8s.io/docs/user/quick-start/)
- [Helm](https://helm.sh/docs/intro/install/)
- [jq](https://stedolan.github.io/jq/)

## Repository Structure
```
├── helm/                  # Automation of deployment and monitoring setup via helm
│   ├──charts/             # Directory for chart dependencies (if any)  
│   ├──templates/          # Kubernetes manifests (YAML files with Helm templates)  
│   ├──values.yaml         # Default configuration values  for deployment
│   ├──Chart.yaml          # Metadata about the Helm chart  
│   ├──monitoring-values.yaml # Default configuration values  for monitoring
├── kubernetes-manifests/ # Kubernetes manifests for application deployment
├── monitoring/
│   ├── alertmanager.yaml # For manual installation, it acts as template for integrating pagerduty
│   ├── service-monitor.yaml # For manual installation, it acts as template for service monitor
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
Run the following commands to install Prometheus from kube-prometheus-stack:
```sh
helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack --namespace monitoring --create-namespace
helm repo update

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

### Build and Push Docker Images and apply Kubernetest manifests
Run the following script to build and push the frontend and backend images to the local registry:
```sh
chmod +x scripts/deploy.sh
./scripts/deploy.sh
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
curl -X POST "https://events.pagerduty.com/v2/enqueue" \
  -H "Content-Type: application/json" \
  -d '{
        "payload": {
          "summary": "PagerDuty Test Alert",
          "source": "Alertmanager",
          "severity": "critical",
          "component": "test-component",
          "group": "test-group",
          "class": "test-class"
        },
        "routing_key": "2439d0f35b834908c19743e7449959a5Y",
        "event_action": "trigger"
      }'

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
