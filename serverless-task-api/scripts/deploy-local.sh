#!/bin/bash
# Deploy to LocalStack (local development)
# Usage: ./deploy-local.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$SCRIPT_DIR/../terraform/environments/local"

echo "========================================="
echo "Deploying to LocalStack"
echo "========================================="

# Check if LocalStack is running
if ! curl -s http://localhost:4566/_localstack/health > /dev/null 2>&1; then
    echo "LocalStack is not running!"
    echo "Start it with: docker run -d --name localstack -p 4566:4566 -v /var/run/docker.sock:/var/run/docker.sock localstack/localstack"
    exit 1
fi

echo "LocalStack is running ✓"

cd "$TERRAFORM_DIR"

# Initialize Terraform
echo "Initializing Terraform..."
terraform init

# Apply (no confirmation needed for local)
echo "Applying changes..."
terraform apply -auto-approve

echo ""
echo "========================================="
echo "LocalStack deployment complete!"
echo "========================================="
terraform output api_url
