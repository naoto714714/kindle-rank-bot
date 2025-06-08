"""
Gemini APIを使用してKindleランキングデータの要約を生成するモジュール
"""

import logging
from typing import Optional

from google import genai
from google.genai import errors as genai_errors
from google.genai import types

from config import config

logger = logging.getLogger(__name__)

# Gemini API用のシステム指示（変化分析用）
SYSTEM_INSTRUCTION_CHANGES = """
Kindleランキングの変化を3-4行以内で簡潔に報告してください。新作、順位変動、トレンドに注目し、絵文字を使って分かりやすく。
"""

# Gemini API用のシステム指示（初回分析用）
SYSTEM_INSTRUCTION_FIRST = """
Kindleランキングの特徴を3-4行以内で簡潔に報告してください。ジャンル、傾向、注目作品に注目し、絵文字を使って分かりやすく。
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
Kindleランキング上位5位までの傾向を分析:
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
            system_instruction=system_instruction, temperature=0.7, max_output_tokens=2000
        ),
        contents=prompt,
    )

    # テキスト取得の試行
    text_content = None
    if response.text:
        text_content = response.text.strip()
    elif hasattr(response, "candidates") and response.candidates:
        candidate = response.candidates[0]
        if candidate.content and candidate.content.parts:
            # パーツからテキストを直接取得
            text_parts = []
            for part in candidate.content.parts:
                if hasattr(part, "text") and part.text:
                    text_parts.append(part.text)
            if text_parts:
                text_content = "".join(text_parts).strip()

    if not text_content:
        logger.error("Gemini APIからテキストを取得できませんでした")
        if hasattr(response, "candidates") and response.candidates:
            candidate = response.candidates[0]
            logger.error(f"finish_reason: {candidate.finish_reason}")
            logger.error(f"content: {candidate.content}")
            if candidate.content and candidate.content.parts:
                logger.error(f"parts: {candidate.content.parts}")
        raise ValueError("Gemini APIからの応答が空です")

    return text_content


def generate_ranking_changes_summary(changes_analysis: dict, current_ranking_text: str) -> Optional[str]:
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
        prompt = PROMPT_TEMPLATE_CHANGES.format(changes_text=changes_text, current_ranking=current_ranking_text)

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

        # ランキングテキストを上位5位に制限
        lines = ranking_text.split("\n")
        top5_lines = []
        count = 0
        for line in lines:
            if line.strip() and ("位|" in line):
                count += 1
                if count > 5:
                    break
            top5_lines.append(line)
        top5_text = "\n".join(top5_lines)

        # プロンプトを作成
        prompt = PROMPT_TEMPLATE_FIRST.format(ranking_text=top5_text)

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


def _format_changes_for_prompt(analysis: dict) -> str:
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
                    lines.append(
                        f"- {change['title']}: {change['previous_rank']}位→{change['current_rank']}位（↑{change['change']}）"
                    )
                else:
                    lines.append(
                        f"- {change['title']}: {change['previous_rank']}位→{change['current_rank']}位（↓{abs(change['change'])}）"
                    )

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


def format_summary_only_message(summary: Optional[str] = None) -> str:
    """
    要約のみのメッセージを作成

    Args:
        summary: Gemini生成の要約（Noneの場合はデフォルトメッセージ）

    Returns:
        要約メッセージテキスト
    """
    if summary:
        return f"📚 **今日のKindleランキング分析**\n\n{summary}"
    else:
        return "📚 **今日のKindleランキング**"
