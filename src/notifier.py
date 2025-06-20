import json
import logging
from typing import Optional

import requests

from config import config

logger = logging.getLogger(__name__)


class NotifierError(Exception):
    """Notifier関連のエラーの基底クラス"""

    pass


class DiscordWebHookError(NotifierError):
    """Discord WebHook送信エラー"""

    pass


class ThreadConfigurationError(NotifierError):
    """スレッド設定エラー"""

    pass


def send_discord_message(message: str, thread_id: Optional[str] = None) -> None:
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
            destination_type = "スレッド" if thread_id else "チャンネル"
            logger.info(f"Discord{destination_type}メッセージが正常に送信されました")
        else:
            error_msg = f"Discord WebHook APIエラー: ステータスコード={response.status_code}"
            if response.text:
                error_msg += f", レスポンス={response.text}"
            raise DiscordWebHookError(error_msg)

    except requests.exceptions.RequestException as e:
        raise DiscordWebHookError(f"Discord WebHook APIへの接続エラー: {str(e)}")


def send_main_message(message: str) -> None:
    """メインチャンネルにメッセージを送信"""
    send_discord_message(message)


def send_thread_message(message: str) -> None:
    """指定されたスレッドにメッセージを送信"""
    if not config.discord_thread_id:
        raise ThreadConfigurationError("DISCORD_THREAD_IDが設定されていません")
    send_discord_message(message, config.discord_thread_id)
