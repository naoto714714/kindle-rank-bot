import json
import logging
from typing import Optional

import requests

from config import config

logger = logging.getLogger(__name__)


def send_discord_message_with_thread(summary: Optional[str], ranking_text: str) -> None:
    """
    Discordに要約をメインメッセージとして送信し、ランキングをスレッドとして送信
    
    Args:
        summary: Gemini生成の要約（Noneの場合は代替メッセージ）
        ranking_text: ランキングテキスト
    """
    # ヘッダーを設定
    headers = {
        "Content-Type": "application/json",
    }
    
    try:
        # 1. メインメッセージ（要約）を送信
        main_message = summary if summary else "📊 本日のKindle売れ筋ランキングを取得しました"
        main_payload = {
            "content": main_message,
            "wait": True  # レスポンスでメッセージ情報を取得するため
        }
        
        logger.info("Discordにメインメッセージ（要約）を送信中...")
        main_response = requests.post(
            config.discord_webhook_url, 
            headers=headers, 
            data=json.dumps(main_payload), 
            timeout=config.request_timeout
        )
        
        if main_response.status_code not in (200, 204):
            error_msg = f"Discord WebHook APIエラー（メインメッセージ）: ステータスコード={main_response.status_code}"
            if main_response.text:
                error_msg += f", レスポンス={main_response.text}"
            raise Exception(error_msg)
        
        # メッセージIDを取得
        try:
            main_message_data = main_response.json()
            message_id = main_message_data.get("id")
        except (ValueError, KeyError) as e:
            raise Exception(f"メインメッセージのレスポンス解析エラー: {str(e)}, レスポンス: {main_response.text}")
        
        if not message_id:
            raise Exception("メインメッセージのIDを取得できませんでした")
        
        logger.info(f"メインメッセージ送信成功（ID: {message_id}）")
        
        # 2. スレッドとしてランキングを送信
        # Discord WebHookではthread_idパラメータを使ってスレッド返信を作成
        thread_payload = {
            "content": f"```\n{ranking_text}\n```"
        }
        
        # スレッド作成のためのURL（メッセージIDをパスに含める）
        thread_url = f"{config.discord_webhook_url}?thread_id={message_id}"
        
        logger.info("Discordにランキング詳細をスレッドとして送信中...")
        thread_response = requests.post(
            thread_url,
            headers=headers,
            data=json.dumps(thread_payload),
            timeout=config.request_timeout
        )
        
        if thread_response.status_code not in (200, 204):
            error_msg = f"Discord WebHook APIエラー（スレッド）: ステータスコード={thread_response.status_code}"
            if thread_response.text:
                error_msg += f", レスポンス={thread_response.text}"
            raise Exception(error_msg)
        
        logger.info("スレッドメッセージ送信成功")
        logger.info("Discordメッセージが正常に送信されました（メイン + スレッド）")
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Discord WebHook APIへの接続エラー: {str(e)}")


def send_discord_message(message: str) -> None:
    """
    後方互換性のため残しておく単純なメッセージ送信関数
    """
    headers = {
        "Content-Type": "application/json",
    }

    payload = {"content": message}

    try:
        response = requests.post(
            config.discord_webhook_url, headers=headers, data=json.dumps(payload), timeout=config.request_timeout
        )

        if response.status_code in (200, 204):
            logger.info("Discordメッセージが正常に送信されました")
        else:
            error_msg = f"Discord WebHook APIエラー: ステータスコード={response.status_code}"
            if response.text:
                error_msg += f", レスポンス={response.text}"
            raise Exception(error_msg)

    except requests.exceptions.RequestException as e:
        raise Exception(f"Discord WebHook APIへの接続エラー: {str(e)}")
