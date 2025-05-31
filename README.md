# Kindle売れ筋ランキング通知Bot

## 概要
Amazonの「Kindle電子書籍売れ筋ランキング」の上位10タイトルを毎日スクレイピングし、LINEで通知するbotです。
GitHub Actionsを使用して、毎日正午12時（日本時間）に自動実行されます。

## 機能
- Amazonの「Kindle本の売れ筋ランキング」から上位10タイトルをスクレイピング
  - https://www.amazon.co.jp/gp/bestsellers/digital-text/2275256051
- スクレイピングしたデータをLINE Messaging APIを使ってLINEに通知
- GitHub Actionsによる定期実行（毎日正午12時）
- **Gemini APIによるランキング変化の要約機能**
  - 前回のランキングと比較して変化を分析
  - 新規ランクイン、順位変動、ランク外などを2-3文で簡潔にレポート
  - 履歴は直近3回分を保存

### 通知例

#### Gemini要約付きの場合
```
📊 注目の変化：「〇〇」が初ランクイン2位！「△△」は5位から1位に急上昇。ビジネス書が好調です。

---

1位|タイトル
⭐️4.5(123件)
¥1,000
https://www.amazon.co.jp/dp/XXXXXXXXXX

（以下、ランキング続く）
```

#### 通常の場合（Gemini無効時）
```
1位|タイトル
⭐️4.5(123件)
¥1,000
https://www.amazon.co.jp/dp/XXXXXXXXXX

（以下、ランキング続く）
```

## 技術スタック
- Python 3.13+
- [uv](https://github.com/astral-sh/uv) (Fast Python package manager)
- BeautifulSoup4（スクレイピング）
- LINE Messaging API（通知）
- GitHub Actions（定期実行）

## 環境変数
GitHub Secretsまたはローカルの.envファイルに以下の環境変数を設定してください：

### 必須
- `LINE_CHANNEL_ACCESS_TOKEN`: LINE Messaging APIのアクセストークン
- `LINE_USER_ID`: 送信先のLINEユーザーID

### オプション
- `KINDLE_RANKING_LIMIT`: 取得するランキング件数（デフォルト: 10）
- `GEMINI_API_KEY`: Gemini APIキー（ランキング変化の要約機能を有効にする場合）
- `ENABLE_GEMINI_SUMMARY`: Gemini要約機能の有効/無効（デフォルト: true）
- `LOG_LEVEL`: ログレベル（デフォルト: INFO）

## 開発環境のセットアップ

### 推奨方法（uv使用）

#### 1. uvのインストール
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### 2. 依存関係のインストールと仮想環境作成
```bash
uv sync
```

#### 3. テストの実行方法

**ユニットテストを実行:**
```bash
uv run python run_tests.py
```

**クイックテスト（1件のみ取得）:**
```bash
uv run python run_tests.py --quick
# または
uv run python run_tests.py -q
```

**ストレステスト（複数回実行）:**
```bash
uv run python run_tests.py --stress 5  # 5回実行
# または
uv run python run_tests.py -s 10      # 10回実行
```

**すべてのテストを実行:**
```bash
uv run python run_tests.py --all
# または
uv run python run_tests.py -a
```

### 本番環境での実行

```bash
# 環境変数を設定してから実行
export LINE_CHANNEL_ACCESS_TOKEN="your_token"
export LINE_USER_ID="your_user_id"
export GEMINI_API_KEY="your_api_key"  # オプション

uv run python src/main.py
```

### GitHub Actionsでのテスト

プッシュまたはプルリクエスト時に自動的にテストが実行されます。
手動でテストを実行したい場合は、GitHubのActionsタブから「スクレイピングテスト」ワークフローを手動実行できます。

#### テスト内容

1. **基本的なスクレイピングテスト**: 実際にAmazonから3件のデータを取得
2. **limitパラメータテスト**: 指定した件数が正しく取得できるか確認
3. **データ形式テスト**: 取得したデータの形式が正しいか確認
4. **リトライ機能テスト**: エラー時のリトライが正しく動作するか確認
5. **エラーハンドリングテスト**: エラー時に適切なメッセージが表示されるか確認
6. **パフォーマンステスト**: 処理時間が適切な範囲内か確認
7. **履歴管理機能テスト**: ランキング履歴の保存・読み込み・変化分析のテスト

## プロジェクト構成

```
kindle-rank-bot/
├── src/
│   ├── main.py              # メインエントリーポイント
│   ├── scraper.py           # Amazonスクレイピング機能
│   ├── notifier.py          # LINE通知機能
│   ├── summarizer.py        # Gemini要約機能
│   ├── history_manager.py   # ランキング履歴管理
│   └── config.py            # 設定管理
├── tests/
│   ├── test_scraper.py      # スクレイピングのテスト
│   └── test_history_manager.py # 履歴管理のテスト
├── .github/workflows/
│   ├── daily-ranking.yml    # 毎日12時の定期実行
│   └── test.yml             # テスト自動実行
├── pyproject.toml           # プロジェクト設定
├── uv.lock                  # 依存関係ロックファイル
└── ranking_history.json     # ランキング履歴（自動生成）
```
