import logging
import sys

from config import config
from notifier import send_line_message
from scraper import get_amazon_kindle_ranking

# ロガーの設定
logging.basicConfig(
    level=getattr(logging, config.log_level),
    format=config.log_format,
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def main():
    try:
        # 設定の妥当性を検証
        config.validate()

        logger.info("Kindleランキング取得処理を開始します...")
        logger.info(f"ランキング取得件数: {config.kindle_ranking_limit}")

        # Kindleランキング情報を取得
        ranking_text = get_amazon_kindle_ranking(limit=config.kindle_ranking_limit)
        logger.info(f"ランキング取得成功: {len(ranking_text)}文字")

        # LINEに送信
        logger.info("LINEへの送信を開始します...")
        send_line_message(ranking_text)
        logger.info("処理が正常に完了しました")

    except Exception as e:
        logger.error(f"エラーが発生しました - {type(e).__name__}: {str(e)}")
        logger.exception("詳細なエラー情報:")

        # GitHub Actionsのワークフローを失敗させる
        sys.exit(1)


if __name__ == "__main__":
    main()
