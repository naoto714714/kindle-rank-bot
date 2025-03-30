# Kindle売れ筋ランキング通知Bot

## 概要
Amazonの「Kindle電子書籍売れ筋ランキング」の上位10タイトルを毎日スクレイピングし、LINEで通知するbotです。
GitHub Actionsを使用して、毎日朝6時に自動実行されます。

## 機能
- Amazonの「Kindle本の売れ筋ランキング」から上位10タイトルをスクレイピング
  - https://www.amazon.co.jp/gp/bestsellers/digital-text/2275256051
- スクレイピングしたデータをLINE Messaging APIを使ってLINEに通知
- GitHub Actionsによる定期実行（毎日午前6時）

### 通知例
1位|タイトル
⭐️4.5(123件)
¥1,000
https://www.amazon.co.jp/dp/XXXXXXXXXX

## 技術スタック
- Python 3.12
- BeautifulSoup4（スクレイピング）
- LINE Messaging API（通知）
- GitHub Actions（定期実行）

## 環境変数
GitHub Secretsに以下の環境変数を設定してください：
- `LINE_CHANNEL_ACCESS_TOKEN`
- `LINE_USER_ID`
