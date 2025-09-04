# Reddit scraper for domain-specific intelligence gathering

This repository provides a light-weight Reddit scraper built on PRAW. It searches a fixed list of subreddits for domain keywords, summarizes post bodies and discussion threads, and streams the results to CSV.

## Features

1. Fixed subreddit list under version control
2. Naïve word-count summarization of posts and discussions
3. CSV export with streaming writes
4. Rate-limit friendly delays between queries

## Quick start

### 1. Python environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure credentials

Create a Reddit app at https://www.reddit.com/prefs/apps and set the following environment variables. Copy `.env.example` to `.env` and fill in your values.

```bash
cp .env.example .env
# edit .env with your credentials
# then load them for this shell
set -a; source .env; set +a
```

Required variables:
- `REDDIT_CLIENT_ID`
- `REDDIT_CLIENT_SECRET`
- `REDDIT_USER_AGENT` (any descriptive string)

### 3. Run

```bash
python reddit-scraper.py
```

The script writes `reddit_scrapped.csv` in the project root.

## Configuration

Edit the constants near the top of `reddit-scraper.py` to adjust:

- `SUBREDDITS`: the subreddits to scan
- `SEARCH_KEYWORDS`: the domain keywords to query in each subreddit
- `SEARCH_LIMIT`: number of posts per (subreddit, keyword) pair
- `REQUEST_DELAY`: seconds to sleep between keyword batches
- `CSV_FILE`: output path

## CSV schema

- `subreddit`
- `search_query`
- `title`
- `post_summary`
- `discussion_summary`
- `score`
- `url`
- `created_utc`

## Notes

- The script fetches and flattens all comments for each post in order to summarize discussion. This is network intensive for very popular threads.
- Respect Reddit's API terms and community rules. Add larger delays if you encounter rate-limit errors.

**Author:** Adeel Ahsan

**Website:** www.aeronautyy.com
