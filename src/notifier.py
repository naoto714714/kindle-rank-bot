import json
import logging

import requests

from config import config

logger = logging.getLogger(__name__)


def send_discord_message(message: str, thread_id: str = None) -> None:
    # ヘッダーを設定
    headers = {
        "Content-Type": "application/json",
    }

    # 送信するデータ（メッセージ内容）
    payload = {"content": message}

    # WebHook URLを設定（thread_idがある場合はクエリパラメータとして追加）
    webhook_url = config.discord_webhook_url
    if thread_id:
        webhook_url += f"?thread_id={thread_id}"

    try:
        # POSTリクエストを送信
        response = requests.post(webhook_url, headers=headers, data=json.dumps(payload), timeout=config.request_timeout)

        # 結果を表示
        if response.status_code in (200, 204):
            target = "スレッド" if thread_id else "チャンネル"
            logger.info(f"Discord{target}メッセージが正常に送信されました")
        else:
            error_msg = f"Discord WebHook APIエラー: ステータスコード={response.status_code}"
            if response.text:
                error_msg += f", レスポンス={response.text}"
            raise Exception(error_msg)

    except requests.exceptions.RequestException as e:
        raise Exception(f"Discord WebHook APIへの接続エラー: {str(e)}")


def send_main_message(message: str) -> None:
    """メインチャンネルにメッセージを送信"""
    send_discord_message(message)


def send_thread_message(message: str) -> None:
    """指定されたスレッドにメッセージを送信"""
    send_discord_message(message, config.discord_thread_id)
