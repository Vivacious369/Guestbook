#!/bin/bash

# Exit on any error
set -e

# Step 1: Deploy Services to Kubernetes
bash scripts/deploy.sh

# Step 2: Set up Monitoring Stack (Prometheus + Grafana)
bash scripts/monitoring.sh



echo "Full automation complete!"
