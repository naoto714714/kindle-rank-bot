import sys
import traceback

from notifier import send_line_message
from scraper import get_amazon_kindle_ranking


def main():
    try:
        print("Kindleランキング取得処理を開始します...")

        # Kindleランキング情報を取得
        ranking_text = get_amazon_kindle_ranking(limit=10)
        print(f"ランキング取得成功: {len(ranking_text)}文字")

        # LINEに送信
        print("LINEへの送信を開始します...")
        send_line_message(ranking_text)
        print("処理が正常に完了しました")

    except Exception as e:
        print(f"\n★ エラーが発生しました ★")
        print(f"エラー種別: {type(e).__name__}")
        print(f"エラーメッセージ: {str(e)}")
        print("\n詳細なエラー情報:")
        traceback.print_exc()

        # GitHub Actionsのワークフローを失敗させる
        sys.exit(1)


if __name__ == "__main__":
    main()
