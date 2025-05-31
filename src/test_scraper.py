#!/usr/bin/env python3
"""スクレイピング機能のテストスクリプト"""

from scraper import get_amazon_kindle_ranking

if __name__ == "__main__":
    try:
        print("Kindleランキングの取得を開始します...")
        result = get_amazon_kindle_ranking(limit=3)  # まず3件でテスト
        print("取得結果:")
        print(result)
    except Exception as e:
        print(f"エラーが発生しました: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()