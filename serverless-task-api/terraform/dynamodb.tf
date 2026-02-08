# DynamoDB Table for Task Storage
# Using on-demand billing mode for cost optimization (pay per request)

resource "aws_dynamodb_table" "tasks" {
  name         = "${local.name_prefix}-tasks"
  billing_mode = "PAY_PER_REQUEST" # Free tier: 25 read/write units

  # Primary key - unique identifier for each task
  hash_key = "id"

  attribute {
    name = "id"
    type = "S" # String type
  }

  tags = {
    Name = "${local.name_prefix}-tasks"
  }
}

# Outputs for the DynamoDB table
output "dynamodb_table_name" {
  description = "Name of the DynamoDB table"
  value       = aws_dynamodb_table.tasks.name
}

output "dynamodb_table_arn" {
  description = "ARN of the DynamoDB table"
  value       = aws_dynamodb_table.tasks.arn
}
