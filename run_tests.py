#!/usr/bin/env python3
"""
ローカルでテストを実行するためのスクリプト
開発中にスクレイピングが正常に動作するか確認する際に使用
"""

import sys
import os
import argparse
import subprocess
from datetime import datetime


def run_unit_tests():
    """ユニットテストを実行"""
    print("=" * 60)
    print("ユニットテストを実行中...")
    print("=" * 60)

    cmd = [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-v"]
    result = subprocess.run(cmd, capture_output=True, text=True)

    print(result.stdout)
    if result.stderr:
        print(result.stderr)

    return result.returncode == 0


def run_quick_test():
    """クイックテスト（1件だけ取得）"""
    print("=" * 60)
    print("クイックテスト（1件のみ取得）を実行中...")
    print("=" * 60)

    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

    try:
        from scraper import get_amazon_kindle_ranking

        start_time = datetime.now()
        result = get_amazon_kindle_ranking(limit=1)
        elapsed = (datetime.now() - start_time).total_seconds()

        print(f"\n実行時間: {elapsed:.2f}秒")
        print("\n取得結果:")
        print("-" * 40)
        print(result)
        print("-" * 40)

        return True

    except Exception as e:
        print(f"\nエラーが発生しました: {type(e).__name__}: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


def run_stress_test(count=5):
    """ストレステスト（複数回実行）"""
    print("=" * 60)
    print(f"ストレステスト（{count}回実行）を開始...")
    print("=" * 60)

    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

    from scraper import get_amazon_kindle_ranking
    import time

    success_count = 0
    failure_count = 0
    times = []

    for i in range(1, count + 1):
        print(f"\n実行 {i}/{count}:")
        start_time = time.time()

        try:
            result = get_amazon_kindle_ranking(limit=3)
            elapsed = time.time() - start_time
            times.append(elapsed)

            lines = result.split("\n")
            first_title = lines[0].split("|")[1] if "|" in lines[0] else "不明"

            print(f"  ✓ 成功 (実行時間: {elapsed:.2f}秒)")
            print(f"    1位: {first_title}")
            success_count += 1

        except Exception as e:
            elapsed = time.time() - start_time
            print(f"  ✗ 失敗 (実行時間: {elapsed:.2f}秒)")
            print(f"    エラー: {str(e)}")
            failure_count += 1

        # 次の実行まで少し待機
        if i < count:
            time.sleep(1)

    # 結果サマリー
    print("\n" + "=" * 60)
    print("テスト結果サマリー")
    print("=" * 60)
    print(f"総実行数: {count}")
    print(f"成功: {success_count} ({success_count / count * 100:.1f}%)")
    print(f"失敗: {failure_count} ({failure_count / count * 100:.1f}%)")

    if times:
        avg_time = sum(times) / len(times)
        print(f"\n平均実行時間: {avg_time:.2f}秒")
        print(f"最速: {min(times):.2f}秒")
        print(f"最遅: {max(times):.2f}秒")

    return failure_count == 0


def main():
    parser = argparse.ArgumentParser(description="Kindleランキングボットのテストを実行")
    parser.add_argument("--quick", "-q", action="store_true", help="クイックテスト（1件のみ取得）を実行")
    parser.add_argument("--stress", "-s", type=int, metavar="N", help="ストレステスト（N回実行）")
    parser.add_argument("--all", "-a", action="store_true", help="すべてのテストを実行")

    args = parser.parse_args()

    # 引数がない場合はユニットテストを実行
    if not any([args.quick, args.stress, args.all]):
        success = run_unit_tests()
        sys.exit(0 if success else 1)

    all_success = True

    if args.quick or args.all:
        success = run_quick_test()
        all_success = all_success and success

    if args.stress:
        success = run_stress_test(args.stress)
        all_success = all_success and success
    elif args.all:
        success = run_stress_test(5)
        all_success = all_success and success

    if args.all:
        success = run_unit_tests()
        all_success = all_success and success

    sys.exit(0 if all_success else 1)


if __name__ == "__main__":
    main()
