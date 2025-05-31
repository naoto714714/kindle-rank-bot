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

## テスト

### ローカルでのテスト実行

#### 1. 依存関係のインストール
```bash
pip install -r requirements.txt
```

#### 2. テストの実行方法

**ユニットテストを実行:**
```bash
python run_tests.py
```

**クイックテスト（1件のみ取得）:**
```bash
python run_tests.py --quick
# または
python run_tests.py -q
```

**ストレステスト（複数回実行）:**
```bash
python run_tests.py --stress 5  # 5回実行
# または
python run_tests.py -s 10      # 10回実行
```

**すべてのテストを実行:**
```bash
python run_tests.py --all
# または
python run_tests.py -a
```

### GitHub Actionsでのテスト

プッシュまたはプルリクエスト時に自動的にテストが実行されます。
手動でテストを実行したい場合は、GitHubのActionsタブから「スクレイピングテスト」ワークフローを手動実行できます。

### テスト内容

1. **基本的なスクレイピングテスト**: 実際にAmazonから3件のデータを取得
2. **limitパラメータテスト**: 指定した件数が正しく取得できるか確認
3. **データ形式テスト**: 取得したデータの形式が正しいか確認
4. **リトライ機能テスト**: エラー時のリトライが正しく動作するか確認
5. **エラーハンドリングテスト**: エラー時に適切なメッセージが表示されるか確認
6. **パフォーマンステスト**: 処理時間が適切な範囲内か確認
