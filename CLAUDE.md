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

### Testing
```bash
# Run all unit tests
python run_tests.py

# Quick test (fetch 1 item)
python run_tests.py --quick

# Stress test (run multiple times)
python run_tests.py --stress 5

# Run all test types
python run_tests.py --all
```

### Environment Variables
Required for local development:
- `LINE_CHANNEL_ACCESS_TOKEN`
- `LINE_USER_ID`

## Architecture

### Core Components
1. **src/main.py**: Entry point that orchestrates the scraping and notification
   - Error handling with detailed logging
   - System exit on failure for GitHub Actions integration
2. **src/scraper.py**: Scrapes Amazon Kindle rankings using BeautifulSoup
   - Fetches top 10 books from https://www.amazon.co.jp/gp/bestsellers/digital-text/2275256051/
   - Extracts title, rating, review count, price, and product URL
   - Retry mechanism with exponential backoff (max 3 attempts)
   - Handles missing data gracefully (ratings, prices, URLs)
3. **src/notifier.py**: Sends messages via LINE Messaging API
   - Environment variable validation
   - Detailed error messages for API failures

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
