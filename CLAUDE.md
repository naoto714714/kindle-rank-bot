# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
Kindle売れ筋ランキング通知Bot - A Python bot that scrapes Amazon's Kindle bestseller rankings and sends daily notifications via LINE. The bot runs automatically every day at 12:00 JST using GitHub Actions.

## Common Commands

### Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the bot locally (requires environment variables)
cd src
python main.py
```

### Environment Variables
Required for local development:
- `LINE_CHANNEL_ACCESS_TOKEN`
- `LINE_USER_ID`

## Architecture

### Core Components
1. **src/main.py**: Entry point that orchestrates the scraping and notification
2. **src/scraper.py**: Scrapes Amazon Kindle rankings using BeautifulSoup
   - Fetches top 10 books from https://www.amazon.co.jp/gp/bestsellers/digital-text/2275256051/
   - Extracts title, rating, review count, price, and product URL
3. **src/notifier.py**: Sends messages via LINE Messaging API

### GitHub Actions
- **Workflow**: `.github/workflows/daily-ranking.yml`
- Runs daily at 12:00 JST (UTC 03:00)
- Can be manually triggered via workflow_dispatch

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
   - Write PR description to `pr-description.md` first
   - Use `gh pr create --title "[Prefix]<title>" --body-file pr-description.md`

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
- The bot is scheduled to run at 12:00 JST (not 6:00 as mentioned in some docs)