resource "aws_iam_role" "sample_lambda_role" {
  assume_role_policy    = file("${path.module}/iam_policy/SampleSqsToLambdaRole/assume_role_policy.json")
  description           = null
  force_detach_policies = false
  managed_policy_arns = [
    "arn:aws:iam::${local.aws_account_id}:policy/service-role/AWSLambdaBasicExecutionRole-a6e9b6c0-dda5-4ca6-be45-6471545c9a7c",
    "arn:aws:iam::${local.aws_account_id}:policy/service-role/AWSLambdaSQSPollerExecutionRole-ea3c1b5d-e082-4d7a-846a-095055bc6c61"
  ]
  max_session_duration = 3600
  name                 = "SampleSqsToLambdaRole"
  path                 = "/service-role/"
  tags                 = {}
  inline_policy {
    name = "PutDynamoDB"
    policy = templatefile("${path.module}/iam_policy/SampleSqsToLambdaRole/inline_policy.json",
      {
        aws_account_id = local.aws_account_id
      }
    )
  }
}
