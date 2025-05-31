"""
Gemini APIを使用してKindleランキングデータの要約を生成するモジュール
"""

import logging
from typing import Optional

from google import genai
from google.genai import types
from google.api_core import exceptions as google_exceptions

from config import config

logger = logging.getLogger(__name__)

# Gemini API用のシステム指示
SYSTEM_INSTRUCTION = """
あなたはKindle電子書籍の売れ筋ランキング分析の専門家です。
与えられたランキングデータを分析して、読者に興味深い洞察を提供してください。

以下の形式で要約を作成してください：
📊 **今日のKindleランキング分析**

🔥 **注目ポイント**
- ランキング上位の特徴やトレンド
- 人気ジャンルの傾向

⭐ **おすすめ作品**
- 特に評価が高い（★4.0以上）作品を1-2冊

💡 **読書のヒント**
- 今のトレンドに基づく一言コメント

文字数は200文字程度で簡潔にまとめてください。
"""

# プロンプトテンプレート
PROMPT_TEMPLATE = """
以下はAmazon Kindle売れ筋ランキングのデータです：

{ranking_text}

このデータを分析して要約してください。
"""


def _call_gemini_api(prompt: str, system_instruction: str) -> str:
    """
    Gemini APIを呼び出してテキストを生成

    Args:
        prompt: ユーザープロンプト
        system_instruction: システム指示

    Returns:
        生成されたテキスト

    Raises:
        google_exceptions.GoogleAPIError: API呼び出しエラー
        ValueError: レスポンスが空の場合
    """
    client = genai.Client(api_key=config.gemini_api_key)

    response = client.models.generate_content(
        model=config.gemini_model,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction, temperature=0.7, max_output_tokens=500
        ),
        contents=prompt,
    )

    if not response.text:
        raise ValueError("Gemini APIからの応答が空です")

    return response.text.strip()


def generate_ranking_summary(ranking_text: str) -> Optional[str]:
    """
    Gemini APIを使ってKindleランキングの要約を生成

    Args:
        ranking_text: スクレイピングで取得したランキングデータ

    Returns:
        要約テキスト（失敗時はNone）
    """
    if not config.enable_gemini_summary or not config.gemini_api_key:
        logger.info("Gemini要約が無効または、APIキーが設定されていません")
        return None

    try:
        logger.info("Gemini APIを使用して要約を生成中...")

        # プロンプトを作成
        prompt = PROMPT_TEMPLATE.format(ranking_text=ranking_text)

        # API呼び出し
        summary = _call_gemini_api(prompt, SYSTEM_INSTRUCTION)

        logger.info(f"Gemini要約生成成功: {len(summary)}文字")
        return summary

    except google_exceptions.GoogleAPIError as e:
        logger.error(f"Gemini API呼び出しでエラーが発生しました: {str(e)}")
        return None
    except ValueError as e:
        logger.error(f"Gemini APIレスポンスの処理でエラーが発生しました: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"予期しないエラーが発生しました: {type(e).__name__}: {str(e)}")
        return None


def format_message_with_summary(ranking_text: str, summary: Optional[str] = None) -> str:
    """
    ランキングデータと要約を組み合わせて最終メッセージを作成

    Args:
        ranking_text: スクレイピングで取得したランキングデータ
        summary: Gemini生成の要約（Noneの場合は要約なし）

    Returns:
        最終的なメッセージテキスト
    """
    if summary:
        return f"{summary}\n\n---\n\n{ranking_text}"
    else:
        return ranking_text
