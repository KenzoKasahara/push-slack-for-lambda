resource "aws_dynamodb_table" "test_dynamodb_table" {
  billing_mode                = "PROVISIONED"
  hash_key                    = "id"
  name                        = "RateLimitTable"
  range_key                   = "timestamp"
  read_capacity               = 1
  table_class                 = "STANDARD"
  tags                        = {}
  write_capacity              = 1
  attribute {
    name = "id"
    type = "S"
  }
  attribute {
    name = "message_id"
    type = "S"
  }
  attribute {
    name = "timestamp"
    type = "N"
  }
  point_in_time_recovery {
    enabled = false
  }
  ttl {
    attribute_name = "ttl"
    enabled        = true
  }
  global_secondary_index {
    name               = "message_id-index"
    hash_key           = "message_id"
    range_key          = ""
    write_capacity     = 1
    read_capacity      = 1
    projection_type    = "ALL"
  }
}

