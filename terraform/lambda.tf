resource "aws_lambda_function" "sample_lambda" {
  architectures                  = ["x86_64"]
  function_name                  = "sample-lambda-push-slack"
  filename                       = "${path.module}/lambda_function/sample-lambda-push-slack.zip"
  handler                        = "push_slack_message.lambda_handler"
  layers                         = []
  memory_size                    = 128
  package_type                   = "Zip"
  publish                        = false
  reserved_concurrent_executions = -1
  role                           = aws_iam_role.sample_lambda_role.arn
  runtime                        = "python3.9"
  skip_destroy                   = false
  tags                           = {}
  timeout                        = 10
  ephemeral_storage {
    size = 512
  }
  logging_config {
    application_log_level = null
    log_format            = "Text"
    log_group             = "/aws/lambda/sample-lambda-push-slack"
    system_log_level      = null
  }
  tracing_config {
    mode = "PassThrough"
  }
}
