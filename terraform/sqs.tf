resource "aws_sqs_queue" "sample_standard_queue" {
  kms_data_key_reuse_period_seconds = 300
  max_message_size                  = 262144
  message_retention_seconds         = 345600
  name                              = "sample-sqs-to-lambda"
  policy = templatefile("${path.module}/sqs_policy/sample-sqs-to-lambda.json",
    {
      aws_account_id = local.aws_account_id
      sqs_name       = "sample-sqs-to-lambda"
    }
  )
  receive_wait_time_seconds = 0
  redrive_allow_policy      = null
  tags                       = {}
  visibility_timeout_seconds = 30
}