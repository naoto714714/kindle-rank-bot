import re

import requests
from bs4 import BeautifulSoup


def get_amazon_kindle_ranking(limit=10):
    # AmazonランキングページURL
    url = "https://www.amazon.co.jp/gp/bestsellers/digital-text/2275256051/"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()  # エラーチェック
    soup = BeautifulSoup(response.content, "html.parser")

    # ランキングの商品ブロックを全て取得
    items = soup.find_all("div", {"class": "_cDEzb_grid-cell_1uMOS"}, limit=limit)

    result_text = ""

    for i, item in enumerate(items, 1):
        # タイトルとリンクを含むaタグ
        a_tag = item.find("a", {"class": "a-link-normal aok-block"})
        if not a_tag:
            continue

        # タイトルのdivを探す
        title_div = item.find("div", {"class": "_cDEzb_p13n-sc-css-line-clamp-1_1Fn1y"})
        title = title_div.get_text(strip=True) if title_div else "タイトル不明"

        # 評価と評価数を取得
        rating_row = item.find("div", {"class": "a-icon-row"})
        rating_title = rating_row.find("a").get("title")
        rating = re.search(r"5つ星のうち([0-9.]+)、([0-9,]+)件", rating_title)

        value = item.find("span", {"class": "_cDEzb_p13n-sc-price_3mJ9Z"})
        value = value.get_text(strip=True) if value else "価格不明"

        url_div = item.find("div", class_="p13n-sc-uncoverable-faceout")
        id = url_div["id"] if url_div else None

        # 順位とタイトル、評価、URLを追加
        result_text += (
            f"{i}位|{title}\n"
            f"⭐️{rating.group(1)}({rating.group(2)}件)\n"
            f"{value}\n"
            f"https://www.amazon.co.jp/dp/{id}\n\n"
        )

    return result_text.strip()
