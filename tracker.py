"""Track prices on a web page and report price changes.

Each run downloads the page, saves every product price with a timestamp
into price_history.csv, and compares it with the previous run. Run it
daily (manually or with a scheduler) to build a price history.

Works with books.toscrape.com, a practice site made for scraping.

Usage:
    python tracker.py                    # check the first catalogue page
    python tracker.py --history my.csv   # use a different history file
"""

import argparse
import csv
import os
import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup

URL = "https://books.toscrape.com/catalogue/page-1.html"
HEADERS = {"User-Agent": "Mozilla/5.0 (portfolio price tracker project)"}
FIELDS = ["timestamp", "title", "price_gbp"]


def fetch_html(url):
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    response.encoding = "utf-8"
    return response.text


def parse_prices(html):
    """Return {title: price} for every product on the page."""
    soup = BeautifulSoup(html, "html.parser")
    prices = {}
    for article in soup.select("article.product_pod"):
        title = article.h3.a["title"]
        text = article.select_one("p.price_color").text
        prices[title] = float(re.search(r"[\d.]+", text).group())
    return prices


def load_last_prices(history_path):
    """Read the history file and keep the most recent price of each title."""
    last = {}
    if not os.path.exists(history_path):
        return last
    with open(history_path, newline="", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            last[row["title"]] = float(row["price_gbp"])  # later rows overwrite earlier ones
    return last


def find_changes(old, new):
    """Compare two price dictionaries. Returns a list of (title, old, new)."""
    return [(t, old[t], p) for t, p in new.items() if t in old and old[t] != p]


def save_prices(history_path, prices):
    is_new_file = not os.path.exists(history_path)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(history_path, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if is_new_file:
            writer.writerow(FIELDS)
        for title, price in prices.items():
            writer.writerow([now, title, price])


def run(html, history_path):
    new_prices = parse_prices(html)
    old_prices = load_last_prices(history_path)
    changes = find_changes(old_prices, new_prices)
    save_prices(history_path, new_prices)

    print(f"Checked {len(new_prices)} products.")
    if not old_prices:
        print("First run: history created, nothing to compare yet.")
    elif not changes:
        print("No price changes since the last run.")
    for title, old, new in changes:
        direction = "DROPPED" if new < old else "ROSE"
        print(f"{direction}: {title}  £{old:.2f} -> £{new:.2f}")
    return changes


def main():
    parser = argparse.ArgumentParser(description="Price tracker")
    parser.add_argument("--url", default=URL, help="page to check")
    parser.add_argument("--history", default="price_history.csv", help="history CSV file")
    args = parser.parse_args()

    try:
        html = fetch_html(args.url)
    except requests.RequestException as error:
        print(f"Could not load the page: {error}")
        return
    run(html, args.history)


if __name__ == "__main__":
    main()
