# Terraform Outputs
# Display important information after deployment

output "api_endpoint" {
  description = "API Gateway endpoint URL"
  value       = "${aws_api_gateway_stage.stage.invoke_url}/tasks"
}

output "api_id" {
  description = "API Gateway ID"
  value       = aws_api_gateway_rest_api.api.id
}

output "aws_region" {
  description = "AWS Region"
  value       = var.aws_region
}

output "environment" {
  description = "Deployment environment"
  value       = var.environment
}

# Quick test commands
output "test_commands" {
  description = "Commands to test the API"
  value       = <<-EOT
    
    # Test your API with these commands:
    
    # List all tasks
    curl ${aws_api_gateway_stage.stage.invoke_url}/tasks
    
    # Create a task
    curl -X POST ${aws_api_gateway_stage.stage.invoke_url}/tasks \
      -H "Content-Type: application/json" \
      -d '{"title": "My Task", "status": "pending"}'
    
    # Get a task (replace TASK_ID)
    curl ${aws_api_gateway_stage.stage.invoke_url}/tasks/TASK_ID
    
    # Update a task
    curl -X PUT ${aws_api_gateway_stage.stage.invoke_url}/tasks/TASK_ID \
      -H "Content-Type: application/json" \
      -d '{"status": "completed"}'
    
    # Delete a task
    curl -X DELETE ${aws_api_gateway_stage.stage.invoke_url}/tasks/TASK_ID
    
  EOT
}
