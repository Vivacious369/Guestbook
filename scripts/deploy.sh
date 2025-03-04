#!/bin/bash

# Exit on any error
# set -e

# Set variables
REGISTRY="localhost:5000"
FRONTEND_IMAGE="$REGISTRY/guestbook-frontend:latest"
BACKEND_IMAGE="$REGISTRY/guestbook-backend:latest"

echo " Mongo Image"
docker pull mongo:latest
docker tag mongo:latest localhost:5000/the-mongo-image:latest


# Build Docker images
echo "🚀 Building Docker images..."
docker build -t $FRONTEND_IMAGE ./src/frontend
docker build -t $BACKEND_IMAGE ./src/backend

# Push images to local Kind registry
echo "📤 Pushing images to local registry..."
docker push $FRONTEND_IMAGE
docker push $BACKEND_IMAGE
docker push localhost:5000/the-mongo-image:latest



# Apply Kubernetes Manifests to Deploy Services
echo "Deploying ervices to Kubernetes..."

kubectl apply -f kubernetes-manifests/guestbook-frontend.deployment.yaml
kubectl apply -f kubernetes-manifests/guestbook-backend.deployment.yaml
kubectl apply -f kubernetes-manifests/guestbook-mongodb.deployment.yaml

# Verify the Deployments
echo "Verifying deployments..."

kubectl get pods

# Apply K8s services 

kubectl apply -f kubernetes-manifests/guestbook-frontend.service.yaml
kubectl apply -f kubernetes-manifests/guestbook-backend.service.yaml
kubectl apply -f kubernetes-manifests/guestbook-mongodb.service.yaml

#Verify the services

kubectl get svc

# Expose the Frontend Service (e.g., via port-forwarding) to access the application
# kubectl port-forward svc/python-guestbook-frontend 8080:80

# Application is available at http://localhost:80

echo "Deployment complete!"

