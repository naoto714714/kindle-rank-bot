import json
import logging

import requests

from config import config

logger = logging.getLogger(__name__)


def send_line_message(message: str) -> None:
    # ヘッダーにアクセストークンを設定
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config.line_channel_access_token}",
    }

    # 送信するデータ（メッセージ内容と送信先ID）
    payload = {"to": config.line_user_id, "messages": [{"type": "text", "text": message}]}

    try:
        # POSTリクエストを送信
        response = requests.post(
            config.line_api_url, headers=headers, data=json.dumps(payload), timeout=config.request_timeout
        )

        # 結果を表示
        if response.status_code == 200:
            logger.info("LINEメッセージが正常に送信されました")
        else:
            error_msg = f"LINE APIエラー: ステータスコード={response.status_code}"
            if response.text:
                try:
                    error_detail = json.loads(response.text)
                    error_msg += f", エラー詳細={error_detail}"
                except (json.JSONDecodeError, ValueError):
                    error_msg += f", レスポンス={response.text}"
            raise Exception(error_msg)

    except requests.exceptions.RequestException as e:
        raise Exception(f"LINE APIへの接続エラー: {str(e)}")
