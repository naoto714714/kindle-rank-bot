import re
import time
from typing import Optional

import requests
from bs4 import BeautifulSoup


def get_amazon_kindle_ranking(limit=10, max_retries=3) -> str:
    # AmazonランキングページURL
    url = "https://www.amazon.co.jp/gp/bestsellers/digital-text/2275256051/"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "ja-JP,ja;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

    # リトライ機能付きのリクエスト
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()  # エラーチェック
            soup = BeautifulSoup(response.content, "html.parser")
            break
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                # 最後の試行で失敗した場合
                raise Exception(f"スクレイピングに失敗しました（{max_retries}回試行）: {str(e)}")
            
            # 指数バックオフ（1秒、2秒、4秒...）
            wait_time = 2 ** attempt
            print(f"リトライ {attempt + 1}/{max_retries} - {wait_time}秒待機中... (エラー: {str(e)})")
            time.sleep(wait_time)

    # ランキングの商品ブロックを全て取得
    items = soup.find_all("div", {"class": "_cDEzb_grid-cell_1uMOS"}, limit=limit)

    if not items:
        raise Exception("商品情報が見つかりませんでした。Amazonのページ構造が変更された可能性があります。")

    result_text = ""

    for i, item in enumerate(items, 1):
        try:
            # タイトルとリンクを含むaタグ
            a_tag = item.find("a", {"class": "a-link-normal aok-block"})
            if not a_tag:
                continue

            # タイトルのdivを探す
            title_div = item.find("div", {"class": "_cDEzb_p13n-sc-css-line-clamp-1_1Fn1y"})
            title = title_div.get_text(strip=True) if title_div else "タイトル不明"

            # 評価と評価数を取得
            rating_row = item.find("div", {"class": "a-icon-row"})
            if not rating_row:
                print(f"警告: {i}位の商品で評価情報が見つかりません")
                continue
            
            rating_link = rating_row.find("a")
            if not rating_link:
                print(f"警告: {i}位の商品で評価リンクが見つかりません")
                continue
            
            # aria-label属性から評価情報を取得
            aria_label = rating_link.get("aria-label")
            if not aria_label:
                print(f"警告: {i}位の商品でaria-label属性が見つかりません")
                continue
            
            rating = re.search(r"5つ星のうち([0-9.]+)、([0-9,]+)件", aria_label)
            
            value = item.find("span", {"class": "_cDEzb_p13n-sc-price_3mJ9Z"})
            value = value.get_text(strip=True) if value else "価格不明"

            # 商品IDを取得（URLを構築するため）
            url_div = item.find("div", class_="p13n-sc-uncoverable-faceout")
            product_id = url_div.get("id") if url_div else None
            
            # IDが取得できない場合は、data-asin属性も試す
            if not product_id:
                parent_div = item.find("div", {"data-asin": True})
                if parent_div:
                    product_id = parent_div.get("data-asin")
            
            # URL構築
            product_url = f"https://www.amazon.co.jp/dp/{product_id}" if product_id else "URLなし"

            # 順位とタイトル、評価、URLを追加
            if rating:
                result_text += (
                    f"{i}位|{title}\n"
                    f"⭐️{rating.group(1)}({rating.group(2)}件)\n"
                    f"{value}\n"
                    f"{product_url}\n\n"
                )
            else:
                # 評価がない場合
                result_text += (
                    f"{i}位|{title}\n"
                    f"評価なし\n"
                    f"{value}\n"
                    f"{product_url}\n\n"
                )
        except Exception as e:
            print(f"エラー: {i}位の商品の処理中にエラーが発生しました: {str(e)}")
            continue

    if not result_text.strip():
        raise Exception("商品情報の取得に失敗しました。一つも商品を取得できませんでした。")
    
    return result_text.strip()
