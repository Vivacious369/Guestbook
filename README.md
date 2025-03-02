# 🚀 Guestbook Infrastructure Setup

This repository contains the infrastructure setup for deploying the **Guestbook application** on a local Kubernetes cluster using `kind`. It includes **monitoring, observability, and alerting**, ensuring seamless deployment and operational insight.

---

## 📌 Prerequisites

Ensure you have the following installed:

- **[Docker](https://www.docker.com/get-started)** - Container runtime  
- **[Kubernetes CLI (`kubectl`)](https://kubernetes.io/docs/tasks/tools/)** - Kubernetes command-line tool  
- **[Kind](https://kind.sigs.k8s.io/docs/user/quick-start/)** - Local Kubernetes cluster  
- **[Helm](https://helm.sh/docs/intro/install/)** - Package manager for Kubernetes  

---

## 📂 Repository Structure

```
.
├── k8s/                 # Kubernetes manifests for application deployment
├── monitoring/          # Monitoring stack (Prometheus, Grafana, Alertmanager)
├── scripts/             # Automation scripts for setup and deployment
│   ├── start-local.sh   # Starts the local Kubernetes cluster and registry
│   ├── deploy.sh        # Builds and deploys the services
│   ├── cleanup.sh       # Stops and cleans up the cluster
├── README.md            # Setup and usage instructions
```

---

## 🔥 Step 1: Set Up Kubernetes Cluster  

Run the script to create a **Kind** cluster along with a local container registry.

```sh
chmod +x scripts/start-local.sh
./scripts/start-local.sh
```

### ✅ Verify Cluster Status
```sh
kubectl cluster-info --context kind-guestbook-cluster
kubectl get nodes
```

---

## 📊 Step 2: Deploy Monitoring Stack  

### 🚀 Install Prometheus, Grafana & Alertmanager

We use a **Helm chart** to install **five key monitoring components**:

1. **Prometheus Server** – Collects and stores metrics  
2. **Node Exporter** – Captures system metrics  
3. **Kube State Metrics** – Provides cluster health insights  
4. **Grafana** – Visualizes monitoring data  
5. **Alertmanager** – Handles alerting  

Run the following commands:

```sh
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm install prometheus prometheus-community/kube-prometheus-stack --namespace monitoring --create-namespace
```

### ✅ Verify Deployment

```sh
kubectl get pods -n monitoring
kubectl get svc -n monitoring
```

---

## 🛠 Step 3: Deploy Guestbook Application

### 🚀 Build & Push Docker Images

```sh
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

### ✅ Apply Kubernetes Manifests

```sh
kubectl apply -f k8s/
```

### 🎯 Verify Deployment

```sh
kubectl get pods
kubectl get svc
```

---

## 🌍 Step 4: Accessing Services  

### 🚀 Port Forwarding

```sh
kubectl port-forward svc/frontend 8080:80
```
Access Guestbook at: **[http://localhost:8080](http://localhost:8080)**  

### 📈 Grafana Dashboard

```sh
kubectl port-forward svc/prometheus-grafana -n monitoring 3000:80
```
Grafana: **[http://localhost:3000](http://localhost:3000)**  
Login: `admin` / `prom-operator`  

### 📇 Prometheus UI

```sh
kubectl port-forward -n monitoring svc/prometheus-operated 9090:9090
```
Prometheus: **[http://localhost:9090](http://localhost:9090)**  

### 🚨 Alertmanager UI

```sh
kubectl port-forward -n monitoring svc/alertmanager-operated 9093:9093
```
Alertmanager: **[http://localhost:9093](http://localhost:9093)**  

---

## 🔔 Step 5: Configure PagerDuty Alerting

### 🚀 Integrate Alertmanager with PagerDuty  

Edit `monitoring/alertmanager-config.yaml` and replace `<PAGERDUTY_KEY>`:

```yaml
route:
  receiver: 'pagerduty'
receivers:
  - name: 'pagerduty'
    pagerduty_configs:
      - service_key: '<PAGERDUTY_KEY>'
```

Apply configuration:

```sh
kubectl apply -f monitoring/alertmanager-config.yaml
```

Restart Alertmanager:

```sh
kubectl rollout restart statefulset alertmanager-kube-prometheus-stack-alertmanager -n monitoring
```

### ✅ Test Alerts  

```sh
kubectl apply -f monitoring/test-alert.yaml
```

---

## 🪟 Step 6: Cleanup  

To delete the cluster and all resources:

```sh
chmod +x scripts/cleanup.sh
./scripts/cleanup.sh
```

---

## 🔥 Important Commands  

### ✅ Check Running Pods  
```sh
kubectl get pods -A
```

### ✅ Check Services  
```sh
kubectl get svc -A
```

### ✅ View Logs  
```sh
kubectl logs -f <pod-name>
```

### ✅ Delete All Resources  
```sh
kubectl delete -f k8s/
kubectl delete -f monitoring/
```

---

## 🎯 Summary  

- ✅ **Set up Kind cluster** using `start-local.sh`  
- ✅ **Installed monitoring stack** using **Helm**  
- ✅ **Deployed Guestbook application**  
- ✅ **Configured observability with Prometheus & Grafana**  
- ✅ **Integrated PagerDuty alerting**  
- ✅ **Port forwarding for accessing services**  
- ✅ **Cleaned up resources after deployment**  

🎉 **Congratulations! Your infrastructure is fully operational and observable!** 🚀

