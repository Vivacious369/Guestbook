#!/bin/bash

# Exit on any error
set -e

# Step 1: Create the cluster
bash scripts/clustercreate.sh

# Step 2: Deploy Services to Kubernetes
bash scripts/deploy.sh

# Step 3: Set up Monitoring Stack (Prometheus + Grafana)
bash scripts/monitoring.sh

#Step 3: IF we wanna use helm , comment step 2 and step 3 and run below command instead
# helm install guestbook ./helm --values ./helm/values.yaml
# helm install monitoring ./helm --values ./helm/monitoring-values.yaml



echo "Full automation complete!"
