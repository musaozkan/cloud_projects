#!/bin/bash
# Deploy to AWS
# Usage: ./deploy-aws.sh [environment]

set -e

ENVIRONMENT=${1:-dev}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$SCRIPT_DIR/../terraform"

echo "========================================="
echo "Deploying to AWS ($ENVIRONMENT)"
echo "========================================="

cd "$TERRAFORM_DIR"

# Initialize Terraform
echo "Initializing Terraform..."
terraform init

# Plan the deployment
echo "Planning deployment..."
terraform plan -var="environment=$ENVIRONMENT"

# Prompt for confirmation
read -p "Do you want to apply these changes? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo "Deployment cancelled."
    exit 0
fi

# Apply
echo "Applying changes..."
terraform apply -var="environment=$ENVIRONMENT" -auto-approve

echo ""
echo "========================================="
echo "Deployment complete!"
echo "========================================="
terraform output api_endpoint
