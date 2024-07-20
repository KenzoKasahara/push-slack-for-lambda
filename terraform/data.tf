# AWSのアカウントIDを取得するためのデータソースを定義
data "aws_caller_identity" "current" {}

locals {
  aws_account_id = data.aws_caller_identity.current.account_id
}