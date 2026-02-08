# Main Terraform Configuration
# This file sets up the AWS provider and basic configuration

terraform {
  required_version = ">= 1.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Configure the AWS Provider
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = var.tags
  }
}

# Get current AWS account information
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# Local variables for consistent naming
locals {
  name_prefix = "${var.project_name}-${var.environment}"
  account_id  = data.aws_caller_identity.current.account_id
  region      = data.aws_region.current.name
}
