"""
プロジェクト全体の設定を管理するモジュール
"""

import os
from dataclasses import dataclass


@dataclass
class Config:
    """アプリケーション設定"""

    # Kindle ランキング設定
    kindle_ranking_limit: int = 10
    kindle_ranking_url: str = "https://www.amazon.co.jp/gp/bestsellers/digital-text/2275256051/"

    # HTTP リクエスト設定
    request_timeout: int = 10
    max_retries: int = 3

    # Discord WebHook 設定
    discord_webhook_url: str = ""
    discord_thread_id: str | None = None

    # Gemini API 設定
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-pro"
    enable_gemini_summary: bool = True
    gemini_summary_ranking_limit: int = 5

    # ログ設定
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    @classmethod
    def from_env(cls) -> "Config":
        """環境変数から設定を読み込む"""
        return cls(
            kindle_ranking_limit=int(os.getenv("KINDLE_RANKING_LIMIT", "10")),
            discord_webhook_url=os.getenv("DISCORD_WEBHOOK_URL", ""),
            discord_thread_id=os.getenv("DISCORD_THREAD_ID"),
            gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
            enable_gemini_summary=os.getenv("ENABLE_GEMINI_SUMMARY", "true").lower() == "true",
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )

    def validate(self) -> None:
        """設定の妥当性を検証"""
        if not self.discord_webhook_url:
            raise ValueError("環境変数 DISCORD_WEBHOOK_URL が設定されていません")
        if self.kindle_ranking_limit <= 0:
            raise ValueError("KINDLE_RANKING_LIMIT は1以上である必要があります")
        if self.enable_gemini_summary and not self.gemini_api_key:
            raise ValueError("Gemini要約が有効ですが、環境変数 GEMINI_API_KEY が設定されていません")


# グローバル設定インスタンス
config = Config.from_env()
