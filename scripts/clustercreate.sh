#!/bin/bash

# Exit on any error
set -e

## Step 1: Set Up Kubernetes Cluster with Kind and Local Registry

echo "Starting the Kubernetes cluster with Kind and setting up local registry..."

# Check if the Kind cluster already exists
if kind get clusters | grep -q "kind"; then
  echo "Kind cluster already exists. Skipping creation."
else
  # Make the start-local.sh script executable and run it to create the cluster
  chmod +x scripts/start-local.sh
  ./scripts/start-local.sh
fi

echo "Kubernetes cluster and local registry setup complete!"

# Continue with other steps...
