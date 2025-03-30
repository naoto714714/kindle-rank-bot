import json
import os

import requests

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_USER_ID = os.getenv("LINE_USER_ID")


def send_line_message(message):
    url = "https://api.line.me/v2/bot/message/push"

    # ヘッダーにアクセストークンを設定
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
    }

    # 送信するデータ（メッセージ内容と送信先ID）
    payload = {"to": LINE_USER_ID, "messages": [{"type": "text", "text": message}]}

    # POSTリクエストを送信
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    # 結果を表示
    if response.status_code == 200:
        print("メッセージが正常に送信されました。")
    else:
        print(
            f"メッセージ送信に失敗しました。ステータスコード: {response.status_code}, 内容: {response.text}"
        )
