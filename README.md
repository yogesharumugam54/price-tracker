# Price Tracker

Downloads a product page, saves every price with a timestamp, and tells you which prices dropped or rose since the last run. Run it daily to build a price history.

Uses [books.toscrape.com](https://books.toscrape.com), a practice site made for learning scraping.

## Setup
```
python -m venv venv
venv\Scripts\activate        # Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
```

## Run
```
python tracker.py
python tracker.py --history my_history.csv
```
First run creates `price_history.csv`. Later runs compare against it:
```
Checked 20 products.
DROPPED: Book A  £10.00 -> £8.50
```

## Output
`price_history.csv` with columns: `timestamp, title, price_gbp`

## Adapting to a client
Change the selectors in `parse_prices()` to match another site (right-click a price, Inspect). Only scrape sites that allow it: check their terms and `robots.txt`.
