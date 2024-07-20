# SQS Lambda DynamoDB

import json
import time
import urllib.request
import urllib.error
import boto3
import logging
from botocore.exceptions import ClientError
from datetime import datetime, timedelta

SLACK_WEBHOOK_URL = "<Slack Webhook URL>"
MAX_REQUESTS_PER_SECOND = 1  # 1秒あたりの最大リクエスト数

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('RateLimitTable')

# Loggerを設定する
_logger = logging.getLogger()
_logger.setLevel(logging.INFO)  # ログレベルをINFOに設定


# ステータスコードのログを取る
def log_status_code(status_code, result, message_id, retry_delay=0):

    _logger.info(f"datetime: {datetime.now()}, \
                    Status Code: {status_code}, \
                    message_id: {message_id}, \
                    retry_delay: {retry_delay}, \
                    result: {result}\n")


# レートリミットをチェックする
def check_rate_limit(rate_limit_delay):
    current_time = int(time.time())
    one_second_ago = current_time - 1

    # DynamoDBのレコード内にtimestampが1秒前以上であるレコードが存在するかの判定
    try:
        response = table.query(
            KeyConditionExpression='id = :id AND #ts >= :ts',
            ExpressionAttributeNames={'#ts': 'timestamp'},
            ExpressionAttributeValues={
                ':id': 'rate_limit',
                ':ts': one_second_ago
            }
        )

        if not len(response['Items']) < MAX_REQUESTS_PER_SECOND:
            rate_limit_delay *= 2
        else:
            rate_limit_delay = 0

        return rate_limit_delay

    except ClientError as e:
        print(f"DynamoDB のクエリ中にエラーが発生: {e}")
        return False


# slackにメッセージを送信する
def send_to_slack(message_id, message, rate_limit_delay=0):
    headers = {
        'Content-Type': 'application/json',
    }
    data = json.dumps({'text': message}).encode('utf-8')
    req = urllib.request.Request(SLACK_WEBHOOK_URL, data=data, headers=headers)

    with urllib.request.urlopen(req) as response:
        if response.status == 200:
            log_status_code(response.status, "OK", message_id, rate_limit_delay)
            return response.status
        else:
            log_status_code(response.status, "NG", message_id, rate_limit_delay)
            return response.status


# メッセージの重複チェック
def is_unique_message_id(message_id):
    response = table.query(
        IndexName='message_id-index',
        KeyConditionExpression='message_id = :message_id',
        ExpressionAttributeValues={':message_id': message_id}
    )

    for item in response['Items']:
        if message_id in item['message_id']:
            return False

    return True


# リクエストを記録する
def record_request(message_id):
    current_time = int(time.time())
    ttl_time = int((datetime.now() + timedelta(days=7)).timestamp())

    try:
        table.put_item(
            Item={
                'id': 'rate_limit',
                'message_id': message_id,
                'timestamp': current_time,
                'ttl': ttl_time
            }
        )
    except ClientError as e:
        print(f"DynamoDB への書き込みエラー: {e}")


# Lambdaハンドラ
def lambda_handler(event, context):
    rate_limit_delay = 2
    max_retries = 5

    for record in event['Records']:
        message_id = record['messageId']
        message = record['body']

        # 最大5回リトライ
        for cnt in range(max_retries):
            try:
                # メッセージIDの重複チェック
                if not is_unique_message_id(message_id):
                    print(f"重複メッセージ有 id: {message_id}")
                    break

                cnt += 1
                rate_limit_delay = check_rate_limit(rate_limit_delay)
                respose_code = send_to_slack(message_id, message, rate_limit_delay)
                print(str(cnt) + '個目')
                print('rate_limit_delay: ', rate_limit_delay)
                print('respose_code: ', respose_code)

                record_request(message_id)  # DynamoDBへのレコード書き込み

                if respose_code == 200:
                    break
                if respose_code == 429:
                    time.sleep(rate_limit_delay)
            except Exception as e:
                print(f"例外発生: {e}")
                # 必要に応じてリトライやエラーハンドリングを追加
