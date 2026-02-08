#!/bin/bash
# Destroy all resources
# Usage: ./destroy.sh [aws|local]

set -e

TARGET=${1:-aws}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ "$TARGET" == "local" ]; then
    TERRAFORM_DIR="$SCRIPT_DIR/../terraform/environments/local"
    echo "Destroying LocalStack resources..."
else
    TERRAFORM_DIR="$SCRIPT_DIR/../terraform"
    echo "Destroying AWS resources..."
    read -p "Are you sure you want to destroy AWS resources? (yes/no): " CONFIRM
    if [ "$CONFIRM" != "yes" ]; then
        echo "Destroy cancelled."
        exit 0
    fi
fi

cd "$TERRAFORM_DIR"
terraform destroy -auto-approve

echo "Resources destroyed successfully!"
