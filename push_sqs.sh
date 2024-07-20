#!/bin/bash

# 送信するメッセージの件数
cnt=50

# SQSキューのURLを設定
QUEUE_URL="<SQSのURL>"

# メッセージの内容を設定
MESSAGE_BODY="SQSに{$cnt}件 非同期送信 1回目"

# メッセージを非同期で送信
for i in {1..50}
do
  aws sqs send-message \
    --profile inspector_admin_switch_role_non_mfa \
    --queue-url "$QUEUE_URL" \
    --message-body "$MESSAGE_BODY $i" &
done

# 全てのバックグラウンドプロセスの終了を待機
wait

echo "{$cnt}件のメッセージを非同期で送信しました。"
