#!/bin/bash

# Exit on any error
set -e

# Step 1: Delete Prometheus and Grafana deployments
echo "Deleting Prometheus and Grafana Helm releases..."
helm uninstall kube-prometheus-stack -n monitoring

# Step 2: Delete the 'monitoring' namespace if it exists (optional)
echo "Deleting the 'monitoring' namespace..."
kubectl delete namespace monitoring --ignore-not-found=true

# Step 3: Delete Kind Cluster
echo "Deleting the Kind Kubernetes cluster..."
kind delete cluster --name kind-guestbook-cluster

# Step 4: Clean up local Docker images and containers (if needed)
echo "Cleaning up local Docker images and containers..."
docker system prune -f

# Step 5: Delete local registry (if using local registry setup)
echo "Cleaning up local Docker registry..."
docker volume rm kind-registry || true
docker container rm kind-registry || true

# Step 6: Remove any remaining resources
echo "Cleaning up any remaining resources..."
kubectl delete all --all -n monitoring
kubectl delete all --all -n default 

# Step 7: Clean up Helm repositories (optional)
echo "Cleaning up Helm repositories..."
helm repo remove prometheus-community
helm repo remove grafana


echo "Cleanup complete!"
