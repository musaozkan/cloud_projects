# Lambda Function Configuration

# Package the Lambda function code
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../lambda/src"
  output_path = "${path.module}/../lambda/function.zip"
}

# Lambda function
resource "aws_lambda_function" "task_handler" {
  function_name = "${local.name_prefix}-handler"
  description   = "Task Manager API Handler"

  # Code configuration
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  handler          = "handler.lambda_handler"
  runtime          = "python3.9"

  # Resource configuration (free tier friendly)
  memory_size = 128
  timeout     = 30

  # IAM role
  role = aws_iam_role.lambda_role.arn

  # Environment variables
  environment {
    variables = {
      TABLE_NAME  = aws_dynamodb_table.tasks.name
      ENVIRONMENT = var.environment
    }
  }

  tags = {
    Name = "${local.name_prefix}-handler"
  }

  depends_on = [
    aws_iam_role_policy_attachment.lambda_dynamodb,
    aws_iam_role_policy_attachment.lambda_logging,
  ]
}

# CloudWatch Log Group for Lambda logs
resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${aws_lambda_function.task_handler.function_name}"
  retention_in_days = 7 # Keep logs for 7 days to minimize costs
}

# Outputs
output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = aws_lambda_function.task_handler.function_name
}

output "lambda_function_arn" {
  description = "ARN of the Lambda function"
  value       = aws_lambda_function.task_handler.arn
}
