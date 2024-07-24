# SQS SQS(FIFO) Lambda

import json
import time
import urllib.request
import urllib.error
import boto3

# Slack接続情報
SLACK_WEBHOOK_URL = "<Slack Webhook URL>"
rete_limit_delay = 1  # レートリミットのための遅延時間（秒）
max_retries = 5  # リトライ回数

sqs = boto3.client('sqs')


# キュー名をARNから抽出
def get_queue_url_from_arn(queue_arn):
    queue_name = queue_arn.split(':')[-1]
    response = sqs.get_queue_url(QueueName=queue_name)
    print(f'queue_name: {queue_name}')
    print(f'response: {response}')
    return response['QueueUrl']


# slackにメッセージを送信する
def send_to_slack(message):
    headers = {
        'Content-Type': 'application/json',
    }
    data = json.dumps({'text': message}).encode('utf-8')
    req = urllib.request.Request(SLACK_WEBHOOK_URL, data=data, headers=headers)

    try:
        with urllib.request.urlopen(req) as response:
            return response.status
    except urllib.error.HTTPError as e:
        print(f"Slack へのメッセージ送信中にエラーが発生: {e}")
        return response.status


# Lambdaハンドラ
def lambda_handler(event, context):
    for record in event['Records']:
        post_message = record['body']
        queue_arn = record['eventSourceARN']
        queue_url = get_queue_url_from_arn(queue_arn)

        try:
            for attempt in range(max_retries):
                response_status = send_to_slack(post_message)

                # slackへ送信成功時のみキューを削除
                if response_status == 200:
                    sqs.delete_message(
                        QueueUrl=queue_url,
                        ReceiptHandle=record['receiptHandle']
                    )
                    break
                else:
                    print(f"Slack へのメッセージ送信に失敗: {response_status}")
                    rete_limit_delay = rete_limit_delay * 2  # バックオフ時間を倍増
                    print(f'rete_limit_delay: {rete_limit_delay}')
                    time.sleep(rete_limit_delay)

        except Exception as e:
            print(f"例外発生: {e}")
            # 必要に応じてリトライやエラーハンドリングを追加
