import json
import logging

import requests

from config import config

logger = logging.getLogger(__name__)


def send_discord_message(message: str) -> None:
    # ヘッダーを設定
    headers = {
        "Content-Type": "application/json",
    }

    # 送信するデータ（メッセージ内容）
    payload = {"content": message}

    try:
        # POSTリクエストを送信
        response = requests.post(
            config.discord_webhook_url, headers=headers, data=json.dumps(payload), timeout=config.request_timeout
        )

        # 結果を表示
        if response.status_code in (200, 204):
            logger.info("Discordメッセージが正常に送信されました")
        else:
            error_msg = f"Discord WebHook APIエラー: ステータスコード={response.status_code}"
            if response.text:
                error_msg += f", レスポンス={response.text}"
            raise Exception(error_msg)

    except requests.exceptions.RequestException as e:
        raise Exception(f"Discord WebHook APIへの接続エラー: {str(e)}")
