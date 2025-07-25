import logging
import re
import time
from dataclasses import dataclass
from typing import Optional

import requests
from bs4 import BeautifulSoup

from config import config

logger = logging.getLogger(__name__)

# HTTP リクエスト用ヘッダー
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "ja-JP,ja;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}


@dataclass
class KindleBook:
    """Kindle書籍の情報を保持するデータクラス"""

    rank: int
    title: str
    rating: Optional[float] = None
    review_count: Optional[int] = None
    price: str = "価格不明"
    url: str = "URLなし"

    def to_string(self) -> str:
        """LINEメッセージ用の文字列に変換"""
        lines = [f"{self.rank}位|{self.title}"]

        if self.rating and self.review_count:
            lines.append(f"⭐️{self.rating}({self.review_count:,}件)")
        else:
            lines.append("評価なし")

        lines.append(self.price)
        lines.append(self.url)

        return "\n".join(lines)


def _fetch_amazon_page(max_retries: int = None) -> BeautifulSoup:
    """AmazonランキングページをHTTPリクエストで取得"""
    if max_retries is None:
        max_retries = config.max_retries

    for attempt in range(max_retries):
        try:
            response = requests.get(config.kindle_ranking_url, headers=REQUEST_HEADERS, timeout=config.request_timeout)
            response.raise_for_status()
            return BeautifulSoup(response.content, "html.parser")
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise Exception(f"スクレイピングに失敗しました（{max_retries}回試行）: {str(e)}") from e

            # 指数バックオフ（1秒、2秒、4秒...）
            wait_time = 2**attempt
            logger.warning(f"リトライ {attempt + 1}/{max_retries} - {wait_time}秒待機中... (エラー: {str(e)})")
            time.sleep(wait_time)


def _extract_product_id(item) -> Optional[str]:
    """商品IDを抽出"""
    url_div = item.find("div", class_="p13n-sc-uncoverable-faceout")
    product_id = url_div.get("id") if url_div else None

    # IDが取得できない場合は、data-asin属性も試す
    if not product_id:
        parent_div = item.find("div", {"data-asin": True})
        if parent_div:
            product_id = parent_div.get("data-asin")

    return product_id


def _parse_book_item(item, rank: int) -> Optional[KindleBook]:
    """HTML要素から書籍情報を抽出してKindleBookオブジェクトを作成"""
    try:
        # タイトルとリンクを含むaタグ
        a_tag = item.find("a", {"class": "a-link-normal aok-block"})
        if not a_tag:
            return None

        # タイトルの取得
        title_div = item.find("div", {"class": "_cDEzb_p13n-sc-css-line-clamp-1_1Fn1y"})
        title = title_div.get_text(strip=True) if title_div else "タイトル不明"

        # 評価と評価数を取得
        rating = None
        review_count = None
        rating_row = item.find("div", {"class": "a-icon-row"})
        if rating_row:
            rating_link = rating_row.find("a")
            if rating_link:
                aria_label = rating_link.get("aria-label")
                if aria_label:
                    rating_match = re.search(r"5つ星のうち([0-9.]+)、([0-9,]+)件", aria_label)
                    if rating_match:
                        rating = float(rating_match.group(1))
                        review_count = int(rating_match.group(2).replace(",", ""))

        # 価格の取得
        price_span = item.find("span", {"class": "_cDEzb_p13n-sc-price_3mJ9Z"})
        price = price_span.get_text(strip=True) if price_span else "価格不明"

        # 商品URLの構築
        product_id = _extract_product_id(item)
        url = f"https://www.amazon.co.jp/dp/{product_id}" if product_id else "URLなし"

        return KindleBook(rank=rank, title=title, rating=rating, review_count=review_count, price=price, url=url)

    except Exception as e:
        logger.error(f"エラー: {rank}位の商品の処理中にエラーが発生しました: {str(e)}")
        return None


def _parse_books_from_soup(soup: BeautifulSoup, limit: int) -> list[KindleBook]:
    """BeautifulSoupオブジェクトから書籍リストを抽出"""
    items = soup.find_all("div", {"class": "_cDEzb_grid-cell_1uMOS"}, limit=limit)

    if not items:
        raise Exception("商品情報が見つかりませんでした。Amazonのページ構造が変更された可能性があります。")

    books = []
    for i, item in enumerate(items, 1):
        book = _parse_book_item(item, i)
        if book:
            books.append(book)

    if not books:
        raise Exception("商品情報の取得に失敗しました。一つも商品を取得できませんでした。")

    return books


def get_amazon_kindle_ranking(limit=10, max_retries=3) -> str:
    """Amazonの Kindle ランキングを取得して文字列として返す"""
    soup = _fetch_amazon_page(max_retries)
    books = _parse_books_from_soup(soup, limit)

    # 書籍リストを文字列に変換
    result_lines = []
    for book in books:
        result_lines.append(book.to_string())

    return "\n\n".join(result_lines)


def get_amazon_kindle_ranking_with_data(limit=10, max_retries=3) -> tuple[str, list[dict]]:
    """
    Amazonの Kindle ランキングを取得して文字列と構造化データの両方を返す

    Returns:
        tuple: (表示用文字列, 構造化データのリスト)
    """
    soup = _fetch_amazon_page(max_retries)
    books = _parse_books_from_soup(soup, limit)

    # 書籍リストを文字列に変換
    result_lines = []
    structured_data = []

    for book in books:
        result_lines.append(book.to_string())
        # 構造化データとして保存
        structured_data.append(
            {
                "rank": book.rank,
                "title": book.title,
                "rating": book.rating,
                "review_count": book.review_count,
                "price": book.price,
                "url": book.url,
            }
        )

    return "\n\n".join(result_lines), structured_data
