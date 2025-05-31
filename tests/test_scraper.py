#!/usr/bin/env python3
"""
スクレイピング機能のテスト
開発中やpush時に実行して、スクレイピングが正常に動作することを確認する
"""

import sys
import os
import time
import unittest
from unittest.mock import patch, MagicMock

# srcディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))

from scraper import get_amazon_kindle_ranking


class TestScraper(unittest.TestCase):
    """スクレイピング機能のテストクラス"""

    def test_basic_scraping(self):
        """基本的なスクレイピング機能のテスト（実際のWebサイトにアクセス）"""
        print("\n=== 基本的なスクレイピングテスト ===")
        try:
            result = get_amazon_kindle_ranking(limit=3)

            # 結果が文字列であることを確認
            self.assertIsInstance(result, str)

            # 結果が空でないことを確認
            self.assertTrue(len(result) > 0)

            # 3件のデータが含まれていることを確認（1件あたり4行 + 空行）
            lines = result.strip().split("\n")
            self.assertGreaterEqual(len(lines), 11)  # 3件 × 4行 - 1（最後の空行なし）

            # 各商品の基本形式を確認
            for i in range(3):
                base_idx = i * 5
                if base_idx < len(lines):
                    # タイトル行の確認
                    self.assertIn(f"{i + 1}位|", lines[base_idx])

                    # 評価行の確認（⭐️または「評価なし」）
                    if base_idx + 1 < len(lines):
                        rating_line = lines[base_idx + 1]
                        self.assertTrue(
                            "⭐️" in rating_line or "評価なし" in rating_line, f"評価行が正しくありません: {rating_line}"
                        )

            print(f"✓ 成功: {len(result)}文字のデータを取得")
            print(f"  1行目: {lines[0][:50]}...")

        except Exception as e:
            self.fail(f"スクレイピングが失敗しました: {str(e)}")

    def test_limit_parameter(self):
        """limit パラメータのテスト"""
        print("\n=== limitパラメータのテスト ===")
        for limit in [1, 5, 10]:
            with self.subTest(limit=limit):
                try:
                    result = get_amazon_kindle_ranking(limit=limit)
                    lines = result.strip().split("\n")

                    # 商品数を数える（1位|、2位|...の形式）
                    product_count = 0
                    for line in lines:
                        if "位|" in line:
                            product_count += 1

                    self.assertEqual(
                        product_count, limit, f"期待した商品数({limit})と実際の商品数({product_count})が一致しません"
                    )

                    print(f"✓ limit={limit}: {product_count}件の商品を取得")

                except Exception as e:
                    self.fail(f"limit={limit}でのスクレイピングが失敗: {str(e)}")

    def test_data_format(self):
        """取得したデータの形式をテスト"""
        print("\n=== データ形式のテスト ===")
        try:
            result = get_amazon_kindle_ranking(limit=2)
            lines = result.strip().split("\n")

            # 1つ目の商品のデータを確認
            if len(lines) >= 4:
                # タイトル行
                title_line = lines[0]
                self.assertRegex(title_line, r"^\d+位\|.+")

                # 評価行
                rating_line = lines[1]
                self.assertTrue(
                    "⭐️" in rating_line or "評価なし" in rating_line, f"評価行の形式が正しくありません: {rating_line}"
                )

                # 価格行
                price_line = lines[2]
                self.assertTrue(
                    "￥" in price_line or "¥" in price_line or "価格不明" in price_line,
                    f"価格行の形式が正しくありません: {price_line}",
                )

                # URL行
                url_line = lines[3]
                self.assertTrue(
                    url_line.startswith("https://www.amazon.co.jp/dp/") or url_line == "URLなし",
                    f"URL行の形式が正しくありません: {url_line}",
                )

                print("✓ データ形式が正しいことを確認")

        except Exception as e:
            self.fail(f"データ形式のテストが失敗: {str(e)}")

    @patch("scraper.requests.get")
    def test_retry_mechanism(self, mock_get):
        """リトライ機能のテスト"""
        print("\n=== リトライ機能のテスト ===")

        # 2回失敗して3回目で成功するように設定
        call_count = 0

        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                import requests

                raise requests.exceptions.RequestException(f"エラー {call_count}")

            # 3回目は成功レスポンスを返す
            response = MagicMock()
            response.status_code = 200
            response.content = """
                <html>
                <div class="_cDEzb_grid-cell_1uMOS">
                    <a class="a-link-normal aok-block"></a>
                    <div class="_cDEzb_p13n-sc-css-line-clamp-1_1Fn1y">テスト商品</div>
                    <div class="a-icon-row">
                        <a aria-label="5つ星のうち4.5、100件のレーティング"></a>
                    </div>
                    <span class="_cDEzb_p13n-sc-price_3mJ9Z">¥1,000</span>
                    <div class="p13n-sc-uncoverable-faceout" id="TEST123"></div>
                </div>
                </html>
            """.encode("utf-8")
            response.raise_for_status = MagicMock()
            return response

        mock_get.side_effect = side_effect

        # リトライが成功することを確認
        try:
            result = get_amazon_kindle_ranking(limit=1)
            self.assertEqual(call_count, 3)
            self.assertIn("テスト商品", result)
            print(f"✓ {call_count}回目の試行で成功")
        except Exception as e:
            self.fail(f"リトライ機能のテストが失敗: {str(e)}")

    @patch("scraper.requests.get")
    def test_error_handling(self, mock_get):
        """エラーハンドリングのテスト"""
        print("\n=== エラーハンドリングのテスト ===")

        # 常に失敗するように設定
        import requests

        mock_get.side_effect = requests.exceptions.RequestException("永続的なエラー")

        # 適切なエラーメッセージが出ることを確認
        with self.assertRaises(Exception) as context:
            get_amazon_kindle_ranking(limit=1, max_retries=2)

        error_msg = str(context.exception)
        self.assertIn("スクレイピングに失敗しました", error_msg)
        self.assertIn("2回試行", error_msg)
        print(f"✓ 期待通りのエラーメッセージ: {error_msg}")

    def test_performance(self):
        """パフォーマンステスト"""
        print("\n=== パフォーマンステスト ===")

        start_time = time.time()
        try:
            result = get_amazon_kindle_ranking(limit=5)
            elapsed_time = time.time() - start_time

            # 通常は3秒以内に完了するはず
            self.assertLess(elapsed_time, 3.0, f"処理時間が長すぎます: {elapsed_time:.2f}秒")

            print(f"✓ 処理時間: {elapsed_time:.2f}秒")

        except Exception as e:
            self.fail(f"パフォーマンステストが失敗: {str(e)}")


if __name__ == "__main__":
    # テスト実行
    unittest.main(verbosity=2)
