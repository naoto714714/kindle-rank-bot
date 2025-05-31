"""
ランキング履歴を管理するモジュール
直近3回分のランキングデータをJSONファイルに保存
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

HISTORY_FILE = "ranking_history.json"
MAX_HISTORY_COUNT = 3


def load_history() -> list[dict]:
    """
    履歴ファイルからランキング履歴を読み込む

    Returns:
        履歴データのリスト（新しい順）
    """
    history_path = Path(HISTORY_FILE)

    if not history_path.exists():
        logger.info("履歴ファイルが存在しません。新規作成します。")
        return []

    try:
        with open(history_path, encoding="utf-8") as f:
            data = json.load(f)
            return data.get("history", [])
    except Exception as e:
        logger.error(f"履歴ファイルの読み込みでエラー: {e}")
        return []


def save_history(history: list[dict]) -> None:
    """
    履歴データをファイルに保存

    Args:
        history: 保存する履歴データ
    """
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump({"history": history}, f, ensure_ascii=False, indent=2)
        logger.info(f"履歴ファイルを保存しました: {len(history)}件")
    except Exception as e:
        logger.error(f"履歴ファイルの保存でエラー: {e}")
        raise


def add_ranking_to_history(ranking_data: list[dict]) -> None:
    """
    新しいランキングデータを履歴に追加

    Args:
        ranking_data: スクレイピングで取得したランキングデータ
    """
    history = load_history()

    # 新しいエントリを作成
    new_entry = {"timestamp": datetime.now().isoformat(), "rankings": ranking_data}

    # 履歴の先頭に追加
    history.insert(0, new_entry)

    # 最大保存数を超えた分を削除
    if len(history) > MAX_HISTORY_COUNT:
        history = history[:MAX_HISTORY_COUNT]

    save_history(history)


def get_previous_rankings() -> Optional[list[dict]]:
    """
    直前のランキングデータを取得

    Returns:
        直前のランキングデータ（存在しない場合はNone）
    """
    history = load_history()

    if len(history) >= 2:
        # 最新のものは今回のデータなので、2番目を返す
        return history[1]["rankings"]
    elif len(history) == 1:
        # 初回実行後の2回目の場合
        return history[0]["rankings"]
    else:
        return None


def analyze_ranking_changes(current: list[dict], previous: list[dict]) -> dict:
    """
    現在と過去のランキングを比較して変化を分析

    Args:
        current: 現在のランキングデータ
        previous: 過去のランキングデータ

    Returns:
        分析結果を含む辞書
    """
    analysis = {"new_entries": [], "rank_changes": [], "dropped_out": []}

    # タイトルをキーにした辞書を作成
    current_dict = {item["title"]: item for item in current}
    previous_dict = {item["title"]: item for item in previous}

    # 新規エントリーを検出
    for title in current_dict:
        if title not in previous_dict:
            analysis["new_entries"].append({"title": title, "rank": current_dict[title]["rank"]})

    # ランク変動を検出
    for title in current_dict:
        if title in previous_dict:
            current_rank = current_dict[title]["rank"]
            previous_rank = previous_dict[title]["rank"]
            if current_rank != previous_rank:
                analysis["rank_changes"].append(
                    {
                        "title": title,
                        "current_rank": current_rank,
                        "previous_rank": previous_rank,
                        "change": previous_rank - current_rank,  # 正の値は上昇
                    }
                )

    # ランキング外に落ちた作品を検出
    for title in previous_dict:
        if title not in current_dict:
            analysis["dropped_out"].append({"title": title, "previous_rank": previous_dict[title]["rank"]})

    return analysis
