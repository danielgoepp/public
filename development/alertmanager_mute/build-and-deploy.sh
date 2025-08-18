#!/bin/bash
set -e

# Configuration
DOCKERHUB_USERNAME="danielgoepp"
IMAGE_NAME="backup-cpu-alert"
IMAGE_TAG="latest"
FULL_IMAGE_NAME="${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${IMAGE_TAG}"

echo "🔨 Building multi-platform Docker image..."
docker buildx build --platform linux/amd64,linux/arm64 -t ${FULL_IMAGE_NAME} --push .

echo "✅ Multi-platform image pushed to Docker Hub"
echo "   Image: ${FULL_IMAGE_NAME}"

echo "🚀 Applying Kubernetes CronJob..."
kubectl apply -f backup-cpu-alert-cronjob.yaml

echo "✅ Deployment complete!"
echo ""
echo "📊 Check CronJob status:"
echo "kubectl get cronjobs -n management"
echo ""
echo "📜 View job history:"
echo "kubectl get jobs --selector=app=backup-cpu-alert -n management"
echo ""
echo "📋 View logs:"
echo "kubectl logs -l app=backup-cpu-alert -n management --tail=50"
echo ""
echo "🧪 Test immediately:"
echo "kubectl create job --from=cronjob/backup-cpu-alert-silence backup-test -n management"