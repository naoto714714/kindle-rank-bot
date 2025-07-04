"""
Discord WebHook通知機能のテスト
"""

import json
import os
import sys
import unittest
from unittest.mock import Mock, patch

# srcディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))

from notifier import send_discord_message


class TestNotifier(unittest.TestCase):
    """Discord WebHook通知機能のテストクラス"""

    @patch("notifier.requests.post")
    @patch("notifier.config")
    def test_send_discord_message_success_204(self, mock_config, mock_post):
        """Discord WebHookメッセージ送信成功のテスト（ステータスコード204）"""
        # モック設定
        mock_config.discord_webhook_url = "https://discord.com/api/webhooks/test"
        mock_config.request_timeout = 10

        mock_response = Mock()
        mock_response.status_code = 204
        mock_post.return_value = mock_response

        # テスト実行
        test_message = "テストメッセージ"
        send_discord_message(test_message)

        # アサーション
        mock_post.assert_called_once_with(
            "https://discord.com/api/webhooks/test",
            headers={"Content-Type": "application/json"},
            data=json.dumps({"content": test_message}),
            timeout=10,
        )

    @patch("notifier.requests.post")
    @patch("notifier.config")
    def test_send_discord_message_success_200(self, mock_config, mock_post):
        """Discord WebHookメッセージ送信成功のテスト（ステータスコード200）"""
        # モック設定
        mock_config.discord_webhook_url = "https://discord.com/api/webhooks/test"
        mock_config.request_timeout = 10

        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # テスト実行
        test_message = "テストメッセージ"
        send_discord_message(test_message)

        # アサーション
        mock_post.assert_called_once_with(
            "https://discord.com/api/webhooks/test",
            headers={"Content-Type": "application/json"},
            data=json.dumps({"content": test_message}),
            timeout=10,
        )

    @patch("notifier.requests.post")
    @patch("notifier.config")
    def test_send_discord_message_api_error(self, mock_config, mock_post):
        """Discord WebHook APIエラーのテスト"""
        # モック設定
        mock_config.discord_webhook_url = "https://discord.com/api/webhooks/test"
        mock_config.request_timeout = 10

        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response

        # テスト実行とアサーション
        with self.assertRaises(Exception) as context:
            send_discord_message("テストメッセージ")

        self.assertIn("Discord WebHook APIエラー", str(context.exception))
        self.assertIn("ステータスコード=400", str(context.exception))
        self.assertIn("Bad Request", str(context.exception))

    @patch("notifier.requests.post")
    @patch("notifier.config")
    def test_send_discord_message_connection_error(self, mock_config, mock_post):
        """Discord WebHook接続エラーのテスト"""
        # モック設定
        mock_config.discord_webhook_url = "https://discord.com/api/webhooks/test"
        mock_config.request_timeout = 10

        import requests

        mock_post.side_effect = requests.exceptions.ConnectionError("接続失敗")

        # テスト実行とアサーション
        with self.assertRaises(Exception) as context:
            send_discord_message("テストメッセージ")

        self.assertIn("Discord WebHook APIへの接続エラー", str(context.exception))
        self.assertIn("接続失敗", str(context.exception))

    @patch("notifier.requests.post")
    @patch("notifier.config")
    def test_send_discord_message_timeout(self, mock_config, mock_post):
        """Discord WebHookタイムアウトのテスト"""
        # モック設定
        mock_config.discord_webhook_url = "https://discord.com/api/webhooks/test"
        mock_config.request_timeout = 10

        import requests

        mock_post.side_effect = requests.exceptions.Timeout("タイムアウト")

        # テスト実行とアサーション
        with self.assertRaises(Exception) as context:
            send_discord_message("テストメッセージ")

        self.assertIn("Discord WebHook APIへの接続エラー", str(context.exception))
        self.assertIn("タイムアウト", str(context.exception))


if __name__ == "__main__":
    unittest.main()
