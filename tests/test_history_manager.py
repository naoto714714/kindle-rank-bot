"""
履歴管理機能のテスト
"""

import json
import os
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from src.history_manager import (
    add_ranking_to_history,
    analyze_ranking_changes,
    get_previous_rankings,
    load_history,
    save_history,
)


class TestHistoryManager(unittest.TestCase):
    """履歴管理機能のテストクラス"""

    def setUp(self):
        """各テストの前に実行される"""
        # 一時ファイルを作成
        self.temp_fd, self.temp_path = tempfile.mkstemp(suffix=".json")
        os.close(self.temp_fd)

        # パッチを適用
        self.patcher = patch("src.history_manager.HISTORY_FILE", self.temp_path)
        self.patcher.start()

        # サンプルデータ
        self.sample_ranking_data = [
            {
                "rank": 1,
                "title": "テスト書籍1",
                "rating": 4.5,
                "review_count": 100,
                "price": "¥500",
                "url": "https://example.com/1",
            },
            {
                "rank": 2,
                "title": "テスト書籍2",
                "rating": 4.0,
                "review_count": 50,
                "price": "¥1000",
                "url": "https://example.com/2",
            },
        ]

    def tearDown(self):
        """各テストの後に実行される"""
        # パッチを解除
        self.patcher.stop()

        # 一時ファイルを削除
        if os.path.exists(self.temp_path):
            os.unlink(self.temp_path)

    def test_load_empty_history(self):
        """空の履歴を読み込むテスト"""
        history = load_history()
        self.assertEqual(history, [])

    def test_save_and_load_history(self):
        """履歴の保存と読み込みテスト"""
        history_data = [{"timestamp": datetime.now().isoformat(), "rankings": self.sample_ranking_data}]

        save_history(history_data)
        loaded = load_history()

        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0]["rankings"], self.sample_ranking_data)

    def test_add_ranking_to_history(self):
        """ランキングを履歴に追加するテスト"""
        # 初回追加
        add_ranking_to_history(self.sample_ranking_data)
        history = load_history()

        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["rankings"], self.sample_ranking_data)

        # 2回目追加
        new_data = self.sample_ranking_data.copy()
        new_data[0] = new_data[0].copy()
        new_data[0]["title"] = "新しい書籍"
        add_ranking_to_history(new_data)
        history = load_history()

        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["rankings"][0]["title"], "新しい書籍")  # 最新が先頭
        self.assertEqual(history[1]["rankings"], self.sample_ranking_data)  # 古いデータが後ろ

    def test_max_history_limit(self):
        """履歴の最大保存数テスト"""
        # 4回追加（最大3回分なので、最後の3つが残る）
        for i in range(4):
            data = self.sample_ranking_data.copy()
            data[0] = data[0].copy()
            data[0]["title"] = f"書籍{i}"
            add_ranking_to_history(data)

        history = load_history()
        self.assertEqual(len(history), 3)
        self.assertEqual(history[0]["rankings"][0]["title"], "書籍3")  # 最新
        self.assertEqual(history[2]["rankings"][0]["title"], "書籍1")  # 最古（書籍0は削除済み）

    def test_get_previous_rankings_empty(self):
        """履歴が空の場合の前回ランキング取得テスト"""
        self.assertIsNone(get_previous_rankings())

    def test_get_previous_rankings_single(self):
        """履歴が1つの場合の前回ランキング取得テスト"""
        add_ranking_to_history(self.sample_ranking_data)
        # 初回実行後なので、その履歴を返す
        self.assertEqual(get_previous_rankings(), self.sample_ranking_data)

    def test_get_previous_rankings_multiple(self):
        """履歴が複数の場合の前回ランキング取得テスト"""
        # 1回目
        add_ranking_to_history(self.sample_ranking_data)

        # 2回目
        new_data = self.sample_ranking_data.copy()
        new_data[0] = new_data[0].copy()
        new_data[0]["title"] = "新しい書籍"
        add_ranking_to_history(new_data)

        # 2番目（前回）のデータが返される
        previous = get_previous_rankings()
        self.assertEqual(previous, self.sample_ranking_data)

    def test_analyze_ranking_changes(self):
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
        self.assertEqual(len(analysis["new_entries"]), 1)
        self.assertEqual(analysis["new_entries"][0]["title"], "書籍D")
        self.assertEqual(analysis["new_entries"][0]["rank"], 2)

        # ランク変動
        self.assertEqual(len(analysis["rank_changes"]), 2)

        # 書籍Aの上昇を確認
        book_a_change = next(c for c in analysis["rank_changes"] if c["title"] == "書籍A")
        self.assertEqual(book_a_change["current_rank"], 1)
        self.assertEqual(book_a_change["previous_rank"], 2)
        self.assertEqual(book_a_change["change"], 1)  # 上昇

        # 書籍Bの下降を確認
        book_b_change = next(c for c in analysis["rank_changes"] if c["title"] == "書籍B")
        self.assertEqual(book_b_change["current_rank"], 3)
        self.assertEqual(book_b_change["previous_rank"], 1)
        self.assertEqual(book_b_change["change"], -2)  # 下降

        # ランク外
        self.assertEqual(len(analysis["dropped_out"]), 1)
        self.assertEqual(analysis["dropped_out"][0]["title"], "書籍C")
        self.assertEqual(analysis["dropped_out"][0]["previous_rank"], 3)


if __name__ == "__main__":
    unittest.main()
