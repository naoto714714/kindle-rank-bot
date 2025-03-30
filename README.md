# Kindle売れ筋ランキング通知Bot

## 概要
このプロジェクトは、Amazonの「Kindle電子書籍売れ筋ランキング」の上位10タイトルを毎日スクレイピングし、LINEに通知するbotです。GitHub Actionsを使用して、毎日朝6時に自動実行されます。

## 機能
- Amazonの「Kindle電子書籍売れ筋ランキング」から上位10タイトルをスクレイピング
- スクレイピングしたデータをLINE Messaging APIを使ってLINEに通知
- GitHub Actionsによる定期実行（毎日午前6時）

## 技術スタック
- Python 3.12
- BeautifulSoup4（スクレイピング）
- LINE Messaging API（通知）
- GitHub Actions（定期実行）

## セットアップ

### 必要条件
- Python 3.12
- LINE Messaging APIアカウント
- LINE Botのチャンネルアクセストークン
- LINE通知を受け取るユーザーID

### インストール手順
1. リポジトリをクローン
   ```bash
   git clone git@github.com:naoto714714/kindle-rank-bot.git
   cd kindle-rank-bot
   ```

2. 依存パッケージをインストール
   ```bash
   pip install -r requirements.txt
   ```

3. 環境変数ファイルを設定
   ```bash
   cp .env.sample .env
   ```
   `.env`ファイルを編集し、LINE Messaging APIのアクセストークンとユーザーIDを設定してください。

### 手動実行
```bash
cd src
python main.py
```

### GitHub Actionsでの自動実行設定
GitHub Secretsに以下の環境変数を設定してください：
- `LINE_CHANNEL_ACCESS_TOKEN`
- `LINE_USER_ID`

## 免責事項
本プロジェクトはAmazonの公開情報をスクレイピングするものですが、Amazonの利用規約を遵守してご利用ください。個人的な利用を目的としており、商用利用は想定していません。
