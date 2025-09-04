#!/usr/bin/env python3
"""
Reddit scraper for domain-specific intelligence gathering.

Author: Adeel Ahsan
Website: www.aeronautyy.com
License: MIT

Overview
--------
This script searches a fixed list of subreddits for a set of domain keywords,
summarizes post bodies and flattened comment discussions with a naïve
word-count truncation, and streams results to a CSV file. Requests are spaced
to be friendlier to Reddit API rate limits.

Configuration
-------------
- Credentials are embedded below at your request.
- Subreddits are fixed in SUBREDDITS.
- Keywords are fixed in SEARCH_KEYWORDS.
- SEARCH_LIMIT controls results per (subreddit, keyword).

Requirements
------------
pip install praw
"""

from __future__ import annotations

import csv
import time
from typing import List

import praw


# ============================================================================
# 0. Credentials and static configuration
# ============================================================================
PRAW_CFG = {
    "client_id": "-----",           # Replace
    "client_secret": "-------------",  # Replace
    "user_agent": "RedditScraper/0.1 (by u/YourRedditUsername)",
}

# Fixed list of subreddits to scan
SUBREDDITS: List[str] = [
    "ROV",
    "UnderwaterRobotics",
    "OceanEngineering",
    "MarineScience",
    "Aquaculture",
    "robotics",
    "engineering",
]

# Domain keywords to query
SEARCH_KEYWORDS: List[str] = [
    "underwater ROV inspection",
    "aquaculture net damage",
    "marine hull biofouling",
    "subsea infrastructure corrosion",
    "diver safety underwater inspection",
    "ocean environmental monitoring",
    "cost effective underwater inspection",
    "autonomous underwater vehicle",
    "underwater robot",
    "modular underwater drone",
    "marine robotics",
    "automated underwater monitoring",
    "underwater inspection technology",
    "ROV innovation",
    "diver risks",
]

SEARCH_LIMIT = 50          # Posts per (subreddit, keyword) pair
REQUEST_DELAY = 2.0        # Seconds between keyword batches

CSV_FILE = "reddit_scrapped.csv"
CSV_FIELDS = [
    "subreddit",
    "search_query",
    "title",
    "post_summary",
    "discussion_summary",
    "score",
    "url",
    "created_utc",
]


# ============================================================================
# 1. Summarization helper
# ============================================================================
def naive_summarizer(text: str, max_words: int = 50) -> str:
    """Truncate text to max_words tokens; append ' ...' if truncated."""
    words = text.split()
    return text if len(words) <= max_words else " ".join(words[:max_words]) + " ..."


# ============================================================================
# 2. Main crawler logic (fixed subreddits)
# ============================================================================
def main() -> None:
    reddit = praw.Reddit(**PRAW_CFG)

    subreddits_to_scrape = sorted({s.strip() for s in SUBREDDITS if s.strip()})
    if not subreddits_to_scrape:
        print("[WARN] No subreddits configured.")
        return

    print(f"[INFO] {len(subreddits_to_scrape)} subreddits will be scanned:")
    print("       " + ", ".join(subreddits_to_scrape))

    with open(CSV_FILE, "w", encoding="utf-8", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=CSV_FIELDS)
        writer.writeheader()

        for sub_name in subreddits_to_scrape:
            subreddit = reddit.subreddit(sub_name)
            print(f"\n[INFO] Scraping r/{sub_name}")

            for kw in SEARCH_KEYWORDS:
                print(f"    Query: «{kw}»")
                try:
                    for submission in subreddit.search(query=kw, limit=SEARCH_LIMIT):
                        _handle_submission(writer, submission, sub_name, kw)
                    time.sleep(REQUEST_DELAY)
                except Exception as exc:
                    print(f"    [ERROR] during search: {exc}")
                    time.sleep(5)

    print(f"\n[INFO] Scraping complete – data saved to «{CSV_FILE}».")


def _handle_submission(
    writer: csv.DictWriter,
    submission: praw.models.Submission,
    sub_name: str,
    kw: str,
) -> None:
    """Summarize a submission and write a CSV row. Exceptions are suppressed."""
    try:
        # Post summary
        title = submission.title.strip()
        body = getattr(submission, "selftext", "") or ""
        post_summary = naive_summarizer(f"{title} {body}", max_words=50)

        # Discussion summary
        try:
            submission.comments.replace_more(limit=None)
            comments = [c.body for c in submission.comments.list() if hasattr(c, "body")]
            discussion_summary = naive_summarizer(" ".join(comments), max_words=80)
        except Exception:
            discussion_summary = ""

        writer.writerow(
            {
                "subreddit": sub_name,
                "search_query": kw,
                "title": title,
                "post_summary": post_summary,
                "discussion_summary": discussion_summary,
                "score": submission.score,
                "url": submission.url,
                "created_utc": submission.created_utc,
            }
        )
    except Exception as exc:
        print(f"        [WARN] skipping submission: {exc}")


# ============================================================================
# Entry point
# ============================================================================
if __name__ == "__main__":
    main()
