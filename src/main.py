from notifier import send_line_message
from scraper import get_amazon_kindle_ranking


def main():
    # Kindleランキング情報を取得
    ranking_text = get_amazon_kindle_ranking(limit=10)

    # LINEに送信
    send_line_message(ranking_text)


if __name__ == "__main__":
    main()
