"""
履歴管理機能のテスト
"""

import json
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from src.history_manager import (
    add_ranking_to_history,
    analyze_ranking_changes,
    get_previous_rankings,
    load_history,
    save_history,
)


@pytest.fixture
def sample_ranking_data():
    """テスト用のランキングデータ"""
    return [
        {
            "rank": 1,
            "title": "テスト書籍1",
            "rating": 4.5,
            "review_count": 100,
            "price": "¥500",
            "url": "https://example.com/1"
        },
        {
            "rank": 2,
            "title": "テスト書籍2",
            "rating": 4.0,
            "review_count": 50,
            "price": "¥1000",
            "url": "https://example.com/2"
        }
    ]


@pytest.fixture
def temp_history_file():
    """一時的な履歴ファイルを作成"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = f.name
    
    # history_manager.HISTORY_FILEをパッチ
    with patch('src.history_manager.HISTORY_FILE', temp_path):
        yield temp_path
    
    # クリーンアップ
    Path(temp_path).unlink(missing_ok=True)


def test_load_empty_history(temp_history_file):
    """空の履歴を読み込むテスト"""
    history = load_history()
    assert history == []


def test_save_and_load_history(temp_history_file, sample_ranking_data):
    """履歴の保存と読み込みテスト"""
    history_data = [{
        "timestamp": datetime.now().isoformat(),
        "rankings": sample_ranking_data
    }]
    
    save_history(history_data)
    loaded = load_history()
    
    assert len(loaded) == 1
    assert loaded[0]["rankings"] == sample_ranking_data


def test_add_ranking_to_history(temp_history_file, sample_ranking_data):
    """ランキングを履歴に追加するテスト"""
    # 初回追加
    add_ranking_to_history(sample_ranking_data)
    history = load_history()
    
    assert len(history) == 1
    assert history[0]["rankings"] == sample_ranking_data
    
    # 2回目追加
    new_data = sample_ranking_data.copy()
    new_data[0]["title"] = "新しい書籍"
    add_ranking_to_history(new_data)
    history = load_history()
    
    assert len(history) == 2
    assert history[0]["rankings"][0]["title"] == "新しい書籍"  # 最新が先頭
    assert history[1]["rankings"] == sample_ranking_data  # 古いデータが後ろ


def test_max_history_limit(temp_history_file, sample_ranking_data):
    """履歴の最大保存数テスト"""
    # 4回追加（最大3回分なので、最後の3つが残る）
    for i in range(4):
        data = sample_ranking_data.copy()
        data[0]["title"] = f"書籍{i}"
        add_ranking_to_history(data)
    
    history = load_history()
    assert len(history) == 3
    assert history[0]["rankings"][0]["title"] == "書籍3"  # 最新
    assert history[2]["rankings"][0]["title"] == "書籍1"  # 最古（書籍0は削除済み）


def test_get_previous_rankings_empty(temp_history_file):
    """履歴が空の場合の前回ランキング取得テスト"""
    assert get_previous_rankings() is None


def test_get_previous_rankings_single(temp_history_file, sample_ranking_data):
    """履歴が1つの場合の前回ランキング取得テスト"""
    add_ranking_to_history(sample_ranking_data)
    # 初回実行後なので、その履歴を返す
    assert get_previous_rankings() == sample_ranking_data


def test_get_previous_rankings_multiple(temp_history_file, sample_ranking_data):
    """履歴が複数の場合の前回ランキング取得テスト"""
    # 1回目
    add_ranking_to_history(sample_ranking_data)
    
    # 2回目
    new_data = sample_ranking_data.copy()
    new_data[0]["title"] = "新しい書籍"
    add_ranking_to_history(new_data)
    
    # 2番目（前回）のデータが返される
    previous = get_previous_rankings()
    assert previous == sample_ranking_data


def test_analyze_ranking_changes():
    """ランキング変化分析のテスト"""
    current = [
        {"rank": 1, "title": "書籍A"},  # 前回2位から上昇
        {"rank": 2, "title": "書籍D"},  # 新規エントリー
        {"rank": 3, "title": "書籍B"},  # 前回1位から下降
    ]
    
    previous = [
        {"rank": 1, "title": "書籍B"},
        {"rank": 2, "title": "書籍A"},
        {"rank": 3, "title": "書籍C"},  # ランク外へ
    ]
    
    analysis = analyze_ranking_changes(current, previous)
    
    # 新規エントリー
    assert len(analysis["new_entries"]) == 1
    assert analysis["new_entries"][0]["title"] == "書籍D"
    assert analysis["new_entries"][0]["rank"] == 2
    
    # ランク変動
    assert len(analysis["rank_changes"]) == 2
    
    # 書籍Aの上昇を確認
    book_a_change = next(c for c in analysis["rank_changes"] if c["title"] == "書籍A")
    assert book_a_change["current_rank"] == 1
    assert book_a_change["previous_rank"] == 2
    assert book_a_change["change"] == 1  # 上昇
    
    # 書籍Bの下降を確認
    book_b_change = next(c for c in analysis["rank_changes"] if c["title"] == "書籍B")
    assert book_b_change["current_rank"] == 3
    assert book_b_change["previous_rank"] == 1
    assert book_b_change["change"] == -2  # 下降
    
    # ランク外
    assert len(analysis["dropped_out"]) == 1
    assert analysis["dropped_out"][0]["title"] == "書籍C"
    assert analysis["dropped_out"][0]["previous_rank"] == 3