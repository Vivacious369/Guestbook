
# Guestbook Infrastructure Setup

## Overview
This repository provides the infrastructure setup for deploying the Guestbook application in a local Kubernetes cluster using **kind**. It includes a comprehensive observability stack powered by **Prometheus** for monitoring and **Grafana** for visualizing metrics. The setup is seamlessly integrated with **PagerDuty** to deliver real-time alerts for critical events, ensuring proactive response and system reliability.

## Prerequisites
Before proceeding, ensure you have the following installed:

- Docker
- Kubernetes CLI (kubectl)
- Kind
- Helm
- jq

## Repository Structure

```bash
├── helm/                  # Automation of deployment and monitoring setup via Helm
│   ├── charts/             # Directory for chart dependencies (if any)
│   ├── templates/          # Kubernetes manifests (YAML files with Helm templates)
│   ├── values.yaml         # Default configuration values for deployment
│   ├── Chart.yaml          # Metadata about the Helm chart
│   ├── monitoring-values.yaml # Default configuration values for monitoring
├── kubernetes-manifests/ # Kubernetes manifests for application deployment
├── monitoring/
│   ├── alertmanager.yaml  # For manual installation, it acts as template for integrating PagerDuty
│   ├── service-monitor.yaml # For manual installation, it acts as template for service monitoring
├── scripts/               # Automation scripts for setup and deployment
│   ├── start-local.sh     # Starts the local Kubernetes cluster and registry
│   ├── deploy.sh          # Builds and deploys the services
│   ├── cleanup.sh         # Stops and cleans up the cluster
├── README.md              # Setup and usage instructions
```

## Step 1: Start the Local Kubernetes Cluster
Run the following script to create a kind cluster with a local container registry:

```bash
chmod +x scripts/start-local.sh
./scripts/start-local.sh
```

Verify the cluster is running:

```bash
kubectl cluster-info --context kind-guestbook-cluster
kubectl get nodes
```

## Step 2: Deploy Guestbook Application
### Build and Push Docker Images and Apply Kubernetes Manifests
Run the following script to build and push the frontend and backend images to the local registry:

```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

### Verify the Deployment
```bash
kubectl get pods
kubectl get svc
```

### Access the Guestbook Application
```bash
kubectl port-forward svc/frontend 8080:80
```

Go to: [http://localhost:8080](http://localhost:8080)

## Step 3: Make Service Observable
### Deploy Using Helm
Run the following commands to install Prometheus from `kube-prometheus-stack`:

```bash
helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack --namespace monitoring --create-namespace
helm repo update
```

### What’s Included with `kube-prometheus-stack`
The `kube-prometheus-stack` Helm chart installs the following components for observability and alerting:

- **Prometheus**: A monitoring system and time-series database that collects and stores metrics.
- **Alertmanager**: A service for handling alerts sent by Prometheus, including integration with external alerting systems like PagerDuty.
- **Grafana**: A visualization tool that integrates with Prometheus to display metrics on dashboards.
- **Node Exporter**: A Prometheus exporter that exposes hardware and OS metrics for nodes.
- **Kube-State-Metrics**: An exporter that exposes Kubernetes cluster state metrics.
- **Prometheus Operator**: Manages the deployment and configuration of Prometheus and Alertmanager.
- **ServiceMonitors**: Custom resources that define how Prometheus scrapes metrics from services.
- **Grafana Dashboards**: Pre-configured dashboards to monitor various aspects of the Kubernetes cluster.

### Verify the Deployment
```bash
kubectl get pods -n monitoring
kubectl get svc -n monitoring
```

### Access Grafana Dashboard
```bash
kubectl port-forward svc/prometheus-grafana -n monitoring 3000:80
```

Access Grafana at: [http://localhost:3000](http://localhost:3000)

Default credentials: `admin / prom-operator`

## Step 4: Set Up Alerting
### Configure Alertmanager with PagerDuty (or another service)
Edit the `alertmanager-config.yaml` file and replace `<PAGERDUTY_KEY>` with your API key.

```yaml
route:
  receiver: 'pagerduty'
receivers:
  - name: 'pagerduty'
    pagerduty_configs:
      - service_key: '<PAGERDUTY_KEY>'
```

Apply the configuration:

```bash
kubectl apply -f monitoring/alertmanager-config.yaml
```

### Test Alerts
To test the PagerDuty integration, run the following command:

```bash
curl -X POST "http://localhost:9093/api/v2/alerts" -H "Content-Type: application/json" -d '[
    {
      "labels": {
        "alertname": "TestAlert",
        "severity": "critical",
        "source": "Kubernetes Cluster",
        "component": "Alertmanager",
        "group": "Test Group",
        "class": "Test Class"
      },
      "annotations": {
        "summary": "Test alert from Alertmanager"
      }
    }
  ]'
```

If you receive alerts on PagerDuty, the integration is successful.

## Step 5: Clean Up (Optional)
To delete the cluster and remove all resources:

```bash
chmod +x scripts/cleanup.sh
./scripts/cleanup.sh
```

## Automation Options for Deployment and Monitoring
There are two ways to automate the deployment of the Guestbook application and enable monitoring and alerting.

### 1. Install Guestbook and Make It Observable via Helm
You can deploy the Guestbook application and set up monitoring using Helm charts by following these steps:

1. Navigate to the `helm/` directory.
2. Use the provided `values.yaml` (for application deployment) and `monitoring-values.yaml` (for monitoring setup) configuration files.
3. Run the following commands to deploy both the application and monitoring stack:

```bash
helm install guestbook ./helm --values ./helm/values.yaml
helm install monitoring ./helm --values ./helm/monitoring-values.yaml
```

This will install the Guestbook application along with Prometheus, Grafana, and alerting configured as per the provided `values.yaml` files.

### 2. Use the Full `deploy.sh` Script
Alternatively, you can automate the entire setup by using the `deploy.sh` script. This script will do the following for you:

- Build and push the necessary Docker images.
- Deploy the Guestbook application.
- Set up monitoring using Helm.
- Set up PagerDuty for alerting.

Simply run the following command from the `scripts/` directory:

```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

Sit back, relax, and let the script take care of the deployment, monitoring setup, and alert configuration.

## Important Commands

### Check Running Pods
```bash
kubectl get pods -A
```

### Check Service Endpoints
```bash
kubectl get svc -A
```

### Get Logs
```bash
kubectl logs -f <pod-name>
```

### Delete All Resources
```bash
kubectl delete -f k8s/
kubectl delete -f monitoring/
```
```
