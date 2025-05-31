#!/usr/bin/env python3
"""HTMLの構造を確認するためのデバッグスクリプト"""

import requests
from bs4 import BeautifulSoup

def debug_amazon_structure():
    url = "https://www.amazon.co.jp/gp/bestsellers/digital-text/2275256051/"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "ja-JP,ja;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    
    print(f"URL: {url}")
    print("ヘッダー:", headers)
    print("\n")
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"ステータスコード: {response.status_code}")
        print(f"レスポンスの長さ: {len(response.content)} bytes")
        
        soup = BeautifulSoup(response.content, "html.parser")
        
        # 商品ブロックを探す
        print("\n=== 商品ブロックの検索 ===")
        items = soup.find_all("div", {"class": "_cDEzb_grid-cell_1uMOS"})
        print(f"_cDEzb_grid-cell_1uMOS クラスの要素数: {len(items)}")
        
        if not items:
            # 他の可能性のあるクラスを探す
            print("\n他のクラスを探しています...")
            
            # id="gridItemRoot"を持つ要素を探す
            grid_items = soup.find_all("div", {"id": lambda x: x and x.startswith("gridItemRoot")})
            print(f"gridItemRoot IDを持つ要素数: {len(grid_items)}")
            
            # data-asin属性を持つ要素を探す
            asin_items = soup.find_all("div", {"data-asin": True})
            print(f"data-asin属性を持つ要素数: {len(asin_items)}")
            
            # classにp13nを含む要素を探す
            p13n_items = soup.find_all("div", class_=lambda x: x and "p13n" in str(x))
            print(f"p13nを含むクラスの要素数: {len(p13n_items)}")
            
            if p13n_items:
                print("\np13nクラスのサンプル:")
                for item in p13n_items[:3]:
                    print(f"  - {item.get('class')}")
        
        # 最初の商品の詳細を表示
        if items and len(items) > 0:
            print("\n=== 最初の商品の構造 ===")
            first_item = items[0]
            
            # タイトル
            title_div = first_item.find("div", {"class": "_cDEzb_p13n-sc-css-line-clamp-1_1Fn1y"})
            if title_div:
                print(f"タイトル: {title_div.get_text(strip=True)}")
            else:
                print("タイトルが見つかりません")
                # 他の可能性のあるタイトル要素を探す
                h2_tags = first_item.find_all("h2")
                if h2_tags:
                    print(f"h2タグ数: {len(h2_tags)}")
                    for h2 in h2_tags:
                        print(f"  - {h2.get_text(strip=True)[:50]}...")
            
            # 評価
            rating_row = first_item.find("div", {"class": "a-icon-row"})
            if rating_row:
                print("\n評価行が見つかりました")
                a_tag = rating_row.find("a")
                if a_tag:
                    title_attr = a_tag.get("title")
                    print(f"評価のtitle属性: {title_attr}")
                    # aria-labelも確認
                    aria_label = a_tag.get("aria-label")
                    print(f"aria-label属性: {aria_label}")
                    # spanタグも確認
                    span_tag = a_tag.find("span")
                    if span_tag:
                        print(f"spanのテキスト: {span_tag.get_text(strip=True)}")
                        print(f"spanのclass: {span_tag.get('class')}")
                else:
                    print("評価のaタグが見つかりません")
                    # 他の評価要素を探す
                    span_stars = first_item.find("span", class_=lambda x: x and "a-icon-star" in str(x))
                    if span_stars:
                        print(f"スター要素: {span_stars.get('class')}")
                        print(f"スター要素のテキスト: {span_stars.get_text(strip=True)}")
                
                # 評価数を含む要素を探す
                all_spans = rating_row.find_all("span")
                print(f"\n評価行内のspan要素数: {len(all_spans)}")
                for i, span in enumerate(all_spans):
                    print(f"  span[{i}]: class={span.get('class')}, text={span.get_text(strip=True)}")
            else:
                print("評価行が見つかりません")
            
            # 価格
            price_span = first_item.find("span", {"class": "_cDEzb_p13n-sc-price_3mJ9Z"})
            if price_span:
                print(f"\n価格: {price_span.get_text(strip=True)}")
            else:
                print("\n価格が見つかりません")
                # 他の価格要素を探す
                price_spans = first_item.find_all("span", class_=lambda x: x and "price" in str(x).lower())
                if price_spans:
                    print(f"priceを含むspan要素数: {len(price_spans)}")
                    for span in price_spans[:3]:
                        print(f"  - {span.get('class')}: {span.get_text(strip=True)}")
        
        # HTMLの一部を保存（デバッグ用）
        with open("debug_output.html", "w", encoding="utf-8") as f:
            f.write(soup.prettify()[:10000])  # 最初の10000文字のみ
        print("\n\nHTMLの一部をdebug_output.htmlに保存しました")
        
    except Exception as e:
        print(f"エラーが発生しました: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_amazon_structure()