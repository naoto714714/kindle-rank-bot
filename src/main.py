import logging
import sys

from config import config
from history_manager import (
    add_ranking_to_history,
    analyze_ranking_changes,
    get_previous_rankings,
)
from notifier import NotifierError, send_main_message, send_thread_message
from scraper import get_amazon_kindle_ranking_with_data
from summarizer import (
    format_summary_only_message,
    generate_first_ranking_summary,
    generate_ranking_changes_summary,
)

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

        # Kindleランキング情報を取得（構造化データも含む）
        ranking_text, ranking_data = get_amazon_kindle_ranking_with_data(limit=config.kindle_ranking_limit)
        logger.info(f"ランキング取得成功: {len(ranking_text)}文字")

        # 履歴から前回のランキングを取得
        previous_rankings = get_previous_rankings()

        # Gemini APIで要約を生成（設定が有効な場合）
        summary = None
        if config.enable_gemini_summary:
            logger.info("Gemini要約機能が有効です...")

            if previous_rankings:
                # 前回のデータがある場合は変化を分析
                logger.info("前回のランキングデータが存在します。変化を分析中...")
                changes_analysis = analyze_ranking_changes(ranking_data, previous_rankings)
                summary = generate_ranking_changes_summary(changes_analysis, ranking_text)
            else:
                # 初回実行の場合は通常の要約
                logger.info("初回実行のため、通常の要約を生成します...")
                summary = generate_first_ranking_summary(ranking_text)

            if summary:
                logger.info(f"要約生成成功: {len(summary)}文字")
            else:
                logger.warning("要約生成に失敗しました（従来のランキングのみ送信）")

        # ランキングデータを履歴に保存
        add_ranking_to_history(ranking_data)
        logger.info("ランキングデータを履歴に保存しました")

        # メインメッセージ（要約のみ）を作成
        main_message = format_summary_only_message(summary)
        logger.info(f"メインメッセージ作成完了: {len(main_message)}文字")

        # Discordに送信
        logger.info("Discordへの送信を開始します...")

        # メインチャンネルに要約を送信
        send_main_message(main_message)
        logger.info("メインチャンネルへの要約送信完了")

        # スレッドにランキング詳細を送信
        try:
            send_thread_message(ranking_text)
            logger.info("スレッドへのランキング送信完了")
        except NotifierError as e:
            logger.warning(f"スレッドへの送信に失敗しました: {e}")
            logger.info("フォールバック: メインチャンネルにランキング詳細も送信します")
            fallback_message = f"⚠️ **スレッド送信失敗のため、ここにランキング詳細を表示します**\n\n{ranking_text}"
            send_main_message(fallback_message)

        logger.info("処理が正常に完了しました")

    except Exception as e:
        logger.error(f"エラーが発生しました - {type(e).__name__}: {str(e)}")
        logger.exception("詳細なエラー情報:")

        # GitHub Actionsのワークフローを失敗させる
        sys.exit(1)


if __name__ == "__main__":
    main()
