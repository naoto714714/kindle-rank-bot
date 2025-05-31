"""
Gemini APIを使用してKindleランキングデータの要約を生成するモジュール
"""

import logging
from typing import Dict, Optional

from google import genai
from google.genai import errors as genai_errors
from google.genai import types

from config import config

logger = logging.getLogger(__name__)

# Gemini API用のシステム指示（変化分析用）
SYSTEM_INSTRUCTION_CHANGES = """
あなたはKindle電子書籍の売れ筋ランキング分析の専門家です。
前回と今回のランキングを比較して、重要な変化を2-3文で簡潔に報告してください。

以下の点に注目してください：
- 新たにランクインした注目作品
- 大きく順位が変動した作品
- ランキングのトレンドの変化

絵文字を使って分かりやすく、重要な変化のみを報告してください。
"""

# Gemini API用のシステム指示（初回分析用）
SYSTEM_INSTRUCTION_FIRST = """
あなたはKindle電子書籍の売れ筋ランキング分析の専門家です。
今回のランキングの特徴を2-3文で簡潔に報告してください。

以下の点に注目してください：
- 上位作品の傾向
- 人気ジャンル
- 高評価作品

絵文字を使って分かりやすく報告してください。
"""

# プロンプトテンプレート（変化分析用）
PROMPT_TEMPLATE_CHANGES = """
前回と今回のKindleランキングの変化を分析してください。

【変化の内容】
{changes_text}

【今回のランキング】
{current_ranking}
"""

# プロンプトテンプレート（初回分析用）
PROMPT_TEMPLATE_FIRST = """
今回のKindleランキングを分析してください。

【ランキング】
{ranking_text}
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
        genai_errors.APIError: API呼び出しエラー
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


def generate_ranking_changes_summary(changes_analysis: Dict, current_ranking_text: str) -> Optional[str]:
    """
    Gemini APIを使ってランキングの変化を要約

    Args:
        changes_analysis: 変化分析の結果
        current_ranking_text: 現在のランキングテキスト

    Returns:
        要約テキスト（失敗時はNone）
    """
    if not config.enable_gemini_summary or not config.gemini_api_key:
        logger.info("Gemini要約が無効または、APIキーが設定されていません")
        return None

    try:
        logger.info("Gemini APIを使用して変化の要約を生成中...")

        # 変化の内容をテキスト化
        changes_text = _format_changes_for_prompt(changes_analysis)
        
        # プロンプトを作成
        prompt = PROMPT_TEMPLATE_CHANGES.format(
            changes_text=changes_text,
            current_ranking=current_ranking_text
        )

        # API呼び出し
        summary = _call_gemini_api(prompt, SYSTEM_INSTRUCTION_CHANGES)

        logger.info(f"Gemini変化要約生成成功: {len(summary)}文字")
        return summary

    except genai_errors.APIError as e:
        logger.error(f"Gemini API呼び出しでエラーが発生しました: {str(e)}")
        return None
    except ValueError as e:
        logger.error(f"Gemini APIレスポンスの処理でエラーが発生しました: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"予期しないエラーが発生しました: {type(e).__name__}: {str(e)}")
        return None


def generate_first_ranking_summary(ranking_text: str) -> Optional[str]:
    """
    Gemini APIを使って初回のランキング要約を生成

    Args:
        ranking_text: スクレイピングで取得したランキングデータ

    Returns:
        要約テキスト（失敗時はNone）
    """
    if not config.enable_gemini_summary or not config.gemini_api_key:
        logger.info("Gemini要約が無効または、APIキーが設定されていません")
        return None

    try:
        logger.info("Gemini APIを使用して初回要約を生成中...")

        # プロンプトを作成
        prompt = PROMPT_TEMPLATE_FIRST.format(ranking_text=ranking_text)

        # API呼び出し
        summary = _call_gemini_api(prompt, SYSTEM_INSTRUCTION_FIRST)

        logger.info(f"Gemini初回要約生成成功: {len(summary)}文字")
        return summary

    except genai_errors.APIError as e:
        logger.error(f"Gemini API呼び出しでエラーが発生しました: {str(e)}")
        return None
    except ValueError as e:
        logger.error(f"Gemini APIレスポンスの処理でエラーが発生しました: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"予期しないエラーが発生しました: {type(e).__name__}: {str(e)}")
        return None


def _format_changes_for_prompt(analysis: Dict) -> str:
    """
    変化分析結果をプロンプト用のテキストに整形
    """
    lines = []
    
    if analysis["new_entries"]:
        lines.append("【新規ランクイン】")
        for entry in analysis["new_entries"][:3]:  # 上位3つまで
            lines.append(f"- {entry['rank']}位: {entry['title']}")
    
    if analysis["rank_changes"]:
        # 大きな変動のみ抽出（3位以上の変動）
        big_changes = [c for c in analysis["rank_changes"] if abs(c["change"]) >= 3]
        if big_changes:
            lines.append("\n【大きな順位変動】")
            for change in sorted(big_changes, key=lambda x: abs(x["change"]), reverse=True)[:3]:
                if change["change"] > 0:
                    lines.append(f"- {change['title']}: {change['previous_rank']}位→{change['current_rank']}位（↑{change['change']}）")
                else:
                    lines.append(f"- {change['title']}: {change['previous_rank']}位→{change['current_rank']}位（↓{abs(change['change'])}）")
    
    if analysis["dropped_out"]:
        lines.append("\n【ランク外】")
        for entry in analysis["dropped_out"][:2]:  # 上位2つまで
            lines.append(f"- {entry['title']}（前回{entry['previous_rank']}位）")
    
    return "\n".join(lines)


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
