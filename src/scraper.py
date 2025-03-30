import requests
from bs4 import BeautifulSoup

# AmazonランキングページURL
url = "https://www.amazon.co.jp/gp/bestsellers/digital-text/2275256051/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, "html.parser")

# ランキングの商品ブロックを全て取得（上位10つ）
items = soup.find_all("div", {"class": "_cDEzb_grid-cell_1uMOS"}, limit=10)

print("Kindle 売れ筋ランキング Top 10:\n")

for item in items:
    # タイトルとリンクを含むaタグ
    a_tag = item.find("a", {"class": "a-link-normal aok-block"})
    if not a_tag:
        continue

    # タイトルのdivを探す
    title_div = item.find("div", {"class": "_cDEzb_p13n-sc-css-line-clamp-1_1Fn1y"})
    title = title_div.get_text(strip=True) if title_div else "タイトル不明"

    url_div = item.find("div", class_="p13n-sc-uncoverable-faceout")
    id = url_div["id"] if url_div else None

    print(f"タイトル: {title}")
    print(f"URL: https://www.amazon.co.jp/dp/{id}")
