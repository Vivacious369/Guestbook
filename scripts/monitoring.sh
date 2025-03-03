#!/bin/bash

# Exit on any error
set -e

# Check if Prometheus is already installed
if helm list -n monitoring | grep -q "kube-prometheus-stack"; then
  echo "Prometheus is already installed. Skipping installation."
  exit 0
else
  echo "Installing Prometheus using Helm..."
  helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack --namespace monitoring --create-namespace
fi

# Step 2: Check if Prometheus, Grafana, and related services are deployed
echo "Checking deployed pods and services in 'monitoring' namespace..."

kubectl get pods -n monitoring
kubectl get svc -n monitoring

# Step 3: Set up port-forwarding to access Prometheus and Grafana UIs
echo "Setting up port-forwarding for Prometheus and Grafana..."

# Forwarding Prometheus UI
kubectl port-forward -n monitoring svc/prometheus-operated 9090:9090 &

# Forwarding Grafana UI
kubectl port-forward -n monitoring svc/grafana 3000:80 &

echo "Prometheus UI is available at http://localhost:9090"
echo "Grafana UI is available at http://localhost:3000"

# Step 4: Configure Prometheus as DataSource in Grafana
# Grafana URL is localhost:3000, login with default username/password: admin/admin
echo "Please log in to Grafana at http://localhost:3000"
echo "Use the following steps to configure Prometheus as a DataSource in Grafana:"
echo "1. Go to Configuration > Data Sources."
echo "2. Click 'Add data source' and choose 'Prometheus'."
echo "3. In the URL field, enter 'http://prometheus-operated:9090'."
echo "4. Click 'Save & Test'."

# Step 5: Set up Alertmanager with PagerDuty
echo "Setting up Alertmanager with PagerDuty..."

# Create the secret from the alertmanager.yaml file
kubectl create secret generic alertmanager-kube-prometheus-stack-alertmanager -n monitoring \
  --from-file=alertmanager.yaml=monitoring/alertmanager.yaml \
  --dry-run=client -o yaml | kubectl apply -f -

# Step 6: Restart the Alertmanager StatefulSet to apply the new configuration
echo "Restarting Alertmanager StatefulSet..."

kubectl rollout restart statefulset alertmanager-kube-prometheus-stack-alertmanager -n monitoring

echo "PagerDuty alerting is now configured with Alertmanager!"

# Forwarding Alertmanager UI
kubectl port-forward -n monitoring pod/alertmanager-kube-prometheus-stack-alertmanager-0 9093:9093 &
echo " Alertmanager can be accessed at http://localhost:9093"


# Final Output
echo "Setup complete! Prometheus and Grafana are now running."
echo "You can access Prometheus UI at: http://localhost:9090"
echo "You can access Grafana UI at: http://localhost:3000"
echo "Please configure Prometheus as a data source in Grafana."
echo "Alertmanager is now configured with PagerDuty."
