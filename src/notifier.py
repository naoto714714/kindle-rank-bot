import json
import os

import requests


def send_line_message(message):
    line_channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
    line_user_id = os.getenv("LINE_USER_ID")

    # 環境変数のチェック
    if not line_channel_access_token:
        raise ValueError("環境変数 LINE_CHANNEL_ACCESS_TOKEN が設定されていません")
    if not line_user_id:
        raise ValueError("環境変数 LINE_USER_ID が設定されていません")

    url = "https://api.line.me/v2/bot/message/push"

    # ヘッダーにアクセストークンを設定
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {line_channel_access_token}",
    }

    # 送信するデータ（メッセージ内容と送信先ID）
    payload = {"to": line_user_id, "messages": [{"type": "text", "text": message}]}

    try:
        # POSTリクエストを送信
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=10)

        # 結果を表示
        if response.status_code == 200:
            print("メッセージが正常に送信されました。")
        else:
            error_msg = f"LINE APIエラー: ステータスコード={response.status_code}"
            if response.text:
                try:
                    error_detail = json.loads(response.text)
                    error_msg += f", エラー詳細={error_detail}"
                except:
                    error_msg += f", レスポンス={response.text}"
            raise Exception(error_msg)

    except requests.exceptions.RequestException as e:
        raise Exception(f"LINE APIへの接続エラー: {str(e)}")
