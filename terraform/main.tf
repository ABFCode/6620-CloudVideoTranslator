terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1" # Or your preferred region
}

resource "aws_s3_bucket" "results" {
  bucket = "video-translator-results-${random_id.id.hex}" # Unique bucket name
}

resource "random_id" "id" {
  byte_length = 8
}

# This gives our Lambda permission to do things
resource "aws_iam_role" "poc_lambda_role" {
  name = "poc-lambda-execution-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

# Allows writing logs, putting objects in S3, and using Translate
resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.poc_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "lambda_permissions" {
  name = "poc-lambda-s3-translate-policy"
  role = aws_iam_role.poc_lambda_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action   = ["s3:PutObject"]
        Effect   = "Allow"
        Resource = "${aws_s3_bucket.results.arn}/*"
      },
      {
        Action   = ["translate:TranslateText"]
        Effect   = "Allow"
        Resource = "*"
      }
    ]
  })
}

data "archive_file" "poc_lambda_zip" {
  type        = "zip"
  source_dir  = "../poc_lambda"
  output_path = "/tmp/poc_lambda.zip"
}

resource "aws_lambda_function" "poc_lambda" {
  function_name = "poc-video-translator"
  filename      = data.archive_file.poc_lambda_zip.output_path
  source_code_hash = data.archive_file.poc_lambda_zip.output_base64sha256
  role          = aws_iam_role.poc_lambda_role.arn
  handler       = "main.handler"
  runtime       = "python3.9"
  timeout       = 30

  environment {
    variables = {
      RESULT_BUCKET = aws_s3_bucket.results.bucket
    }
  }
}

resource "aws_apigatewayv2_api" "http_api" {
  name          = "poc-translator-api"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "lambda_integration" {
  api_id           = aws_apigatewayv2_api.http_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.poc_lambda.invoke_arn
}

resource "aws_apigatewayv2_route" "post_translate" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "POST /translate"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.http_api.id
  name        = "$default"
  auto_deploy = true
}

resource "aws_lambda_permission" "api_gw_permission" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.poc_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*"
}

# Output the URL so we know where to send requests
output "api_endpoint" {
  value = aws_apigatewayv2_stage.default.invoke_url
}