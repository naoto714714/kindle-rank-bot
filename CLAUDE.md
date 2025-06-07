# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## タスクを進めるとき、厳守するルール

### 🚨 最重要: Gitコミットルール（必ず守ること）
1. **必ず細かい単位でgit commitしながらタスクを進めること**
   - 1つの論理的な変更 = 1コミット
   - 複数のファイルを編集しても、同じ目的なら1コミットでOK
   - 異なる目的の変更は必ず別コミットに分ける

2. **異なる種類の作業を1つのコミットに混ぜない**
   - ❌ 機能追加(feat)とリファクタリング(refactor)を同時にコミット
   - ❌ バグ修正(fix)とテスト追加(test)を同時にコミット
   - ✅ 各作業を別々にコミット

3. **コミットメッセージの形式を厳守**
   - 形式: `prefix: 日本語で説明`
   - prefixの種類:
     - `feat`: 新機能追加
     - `fix`: バグ修正
     - `refactor`: リファクタリング
     - `test`: テストの追加・修正
     - `docs`: ドキュメントの変更
     - `style`: コードフォーマットなど
     - `chore`: その他の変更

4. **コミット前の確認事項**
   - 関連するテストを実行して動作確認
   - 1つの論理的な変更単位になっているか確認
   - コミットメッセージが適切か確認

### その他の開発ルール
- 待機状態に戻る前に `afplay /Users/kimuranaoto/Music/notice.mp3` を必ず実行しなさい
- コードに変更を加えた場合は、毎回ruffでフォーマットしなさい
- テストを実行するときは、uvを使い、仮想環境で実行しなさい
- CLAUDE.mdを適宜修正して、最新の情報を常に取得できるようにしなさい
- mainブランチでは作業せず、別のブランチで作業しなさい
- 特別な指示がない場合、リモートにgit pushする直前(一通りgit commitし終える)まで作業しなさい

## プルリクエストにレビューするときの情報
- 現在出ているプルリクエストの内容を確認してください
- 以下のファイルを熟読し、則りながらレビューしてください
  - レビューするときのガイドライン: `prompt/code_review_guide.md`
  - レビューするときの人格: `prompt/reviewer_personality.md`
- レビューが完了したら、プルリクエストに日本語でコメントとして投稿してください

## Project Overview
Kindle売れ筋ランキング通知Bot - A Python bot that scrapes Amazon's Kindle bestseller rankings and sends daily notifications via LINE. The bot runs automatically every day at 12:00 JST using GitHub Actions.

## Common Commands

### Development (using uv)
```bash
# Install uv (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies and create virtual environment
uv sync

# Run the bot locally (requires environment variables)
uv run python src/main.py

# Format code with ruff
uv run ruff format .

# Add new dependencies
uv add package-name

# Add development dependencies
uv add --dev package-name
```

### Testing
```bash
# Run all unit tests
uv run python run_tests.py

# Quick test (fetch 1 item)
uv run python run_tests.py --quick

# Stress test (run multiple times)
uv run python run_tests.py --stress 5

# Run all test types
uv run python run_tests.py --all
```

### Legacy Commands (pip)
For compatibility, you can still use pip with pyproject.toml:
```bash
# Install dependencies with pip
pip install -e .

# Run tests with pip environment
python run_tests.py --quick
```

### Environment Variables
Required for local development:
- `LINE_CHANNEL_ACCESS_TOKEN`: LINE Messaging APIのアクセストークン
- `LINE_USER_ID`: 送信先のLINEユーザーID

Optional:
- `KINDLE_RANKING_LIMIT`: 取得するランキング件数（デフォルト: 10）
- `GEMINI_API_KEY`: Gemini APIキー（要約機能を有効にする場合）
- `ENABLE_GEMINI_SUMMARY`: Gemini要約機能の有効/無効（デフォルト: true）
- `LOG_LEVEL`: ログレベル（デフォルト: INFO）

## Architecture

### Core Components
1. **src/main.py**: Entry point that orchestrates the scraping and notification
   - Error handling with detailed logging
   - System exit on failure for GitHub Actions integration
   - Gemini API integration for ranking summaries
2. **src/scraper.py**: Scrapes Amazon Kindle rankings using BeautifulSoup
   - Fetches top 10 books from https://www.amazon.co.jp/gp/bestsellers/digital-text/2275256051/
   - Extracts title, rating, review count, price, and product URL
   - Retry mechanism with exponential backoff (max 3 attempts)
   - Handles missing data gracefully (ratings, prices, URLs)
3. **src/notifier.py**: Sends messages via LINE Messaging API
   - Environment variable validation
   - Detailed error messages for API failures
4. **src/summarizer.py**: Gemini API integration for AI-powered summaries
   - Generates ranking analysis and insights
   - Graceful fallback when API fails
   - Configurable via environment variables
5. **src/config.py**: Centralized configuration management
   - Environment variable handling
   - Validation and defaults

### Testing
- **tests/test_scraper.py**: Comprehensive unit tests for scraping functionality
- **run_tests.py**: Test runner with multiple modes (quick, stress, all)

### GitHub Actions
- **daily-ranking.yml**: Daily scraping and notification at 12:00 JST
- **test.yml**: Automated testing on push and pull requests

## Git Workflow Requirements
This project follows strict Git workflow practices defined in `rules/git.mdc`:

1. **Always create a new branch from main** for any work:
   ```bash
   git checkout main
   git pull origin main
   git checkout -b Prefix/<branch-name>
   ```

2. **Commit with proper prefix**:
   ```bash
   git commit -m "Prefix: <change summary>"
   ```

3. **Pull request creation**:
   ```bash
   git push -u origin <branch-name>
   gh pr create --title "[Prefix]<title>" --body "<description>"
   ```

### Prefix Convention
- `feature`: New features
- `update`: Improvements to existing features
- `bugfix`: Minor bug fixes
- `hotfix`: Critical fixes
- `refactor`: Code refactoring
- `test`: Test additions/modifications
- `docs`: Documentation changes
- `chore`: Maintenance tasks

## Important Notes
- Never edit files directly on the main branch
- Always check `rules/requirements-definition.mdc` for system requirements
- The bot is scheduled to run at 12:00 JST
- Always run `ruff format .` after making code changes to ensure consistent formatting
