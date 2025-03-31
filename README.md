# CLI Stock and ETF Price Tracker
CLI Stock and ETF Price Tracker is a command-line tool that fetches and displays key financial metrics for a configurable list of stock and ETF tickers using the [Finnhub API](https://finnhub.io/). It provides real-time data on stock prices, earnings, dividends, and more, formatted in a readable table using the rich library.

![Example terminal output](https://github.com/bbusenius/CLI-Stock-Tracker/raw/master/docs/screenshot.png)

## Prerequisites
- Python 3.12: Ensure you have Python 3.12 installed on your system.
- Finnhub API Key: Sign up at [Finnhub](https://finnhub.io/) to obtain a free API key.

## Installation

### 1.  Clone the repository:
```
git clone https://github.com/bbusenius/CLI-Stock-Tracker.git
cd CLI-Stock-Tracker
```

### 2.  Create and activate a virtual environment:
#### For Linux/Mac:
```
python3.12 -m venv venv
source venv/bin/activate
```
#### For Windows:
```
python3.12 -m venv venv
venv\Scripts\activate
```

### 3.  Install dependencies:
```
pip install -r requirements-dev.txt
```

### 4.  Set the Finnhub API key:
#### For Linux/Mac:
```
export FINNHUB_API_KEY=your_api_key_here
```
#### For Windows:
```
set FINNHUB_API_KEY=your_api_key_here
```

## Usage

### 1.  Configure your tickers:
Copy the example tickers.json.example to tickers.json:
```
cp tickers.json.example tickers.json
```

Edit tickers.json to include the tickers you want to track. For example:
```
["AAPL", "MSFT", "GOOGL"]
```

### 2.  Run the tool:
Run the tool in normal mode to display financial data:
```
python main.py
```
This will fetch the financial data for the specified tickers and display it in a formatted table.

Force a refresh to bypass the cache and fetch fresh data:
```
python main.py --refresh
```

Run in daemon mode for continuous cache updates (requires caching enabled):
```
python main.py --daemon &

```
In daemon mode, the tool updates the cache periodically without displaying the table.

## Caching Mechanism
The tool includes an optional caching system storing API results in `cache.json`:
- When enabled, it checks the cache for fresh data (within the `interval`).
- If data is missing or stale, it fetches fresh data, updates the cache, and uses it.
- If an API call fails, it falls back to cached data (if available) and notifies the user.
- In daemon mode, it continuously updates the cache every `interval` minutes.
- To clear the cache, delete `cache.json`.

## Configuration
- **Tickers**: The tool reads the list of tickers from `tickers.json`. This file can contain either:
  - A list of strings (e.g., `["AAPL", "MSFT"]`), treated as tickers with no user-provided name.
  - A list of objects with `ticker` (required) and optional `name` fields (e.g., `[{"ticker": "AAPL", "name": "Apple Inc."}, {"ticker": "MSFT"}]`). If a `name` is provided, it is used in the display instead of fetching it from the API, which is useful for ETFs or when the API name is inaccurate.
- **Display and Cache Settings**: The tool reads settings from `settings.json`, which contains:
  - `"columns"`: A dictionary specifying optional columns to include in the table:
    - `"eps"`: Include the EPS column.
    - `"pe_ratio"`: Include the PE Ratio column.
    - `"dividend"`: Include the Dividend column.
    - `"ytd_change"`: Include the YTD % Change column.
    - `"ten_year_change"`: Include the 10-Year % Change column.
  - `"cache"`: A dictionary with cache settings:
    - `"enabled"`: Boolean to enable or disable caching (default: `false`).
    - `"interval"`: Integer specifying the cache refresh interval in minutes (default: 60).
- If `settings.json` is missing or invalid, defaults are used: all optional columns are excluded, and caching is disabled.

**Example `settings.json`:**
```json
{
  "columns": {
    "eps": true,
    "pe_ratio": true,
    "dividend": true,
    "ytd_change": false,
    "ten_year_change": true
  },
  "cache": {
    "enabled": true,
    "interval": 60
  }
}

## API Rate Limits
- Free tier limit: 60 API calls per minute.
- Each ticker requires up to 5 calls (quote, profile, financials, YTD, 10-year).
- Caching reduces calls by reusing data when fresh.
- In daemon mode, updates are staggered (1-second delay per ticker). For 12 tickers with a 60-minute interval, it uses ~60 calls/hour, staying within limits. Adjust interval or ticker count to avoid exceeding limits.

## Development
### Run unit tests:
```
pytest
```
### Linting and formatting:
- The project uses Flake8, isort, autopep8, and black for code quality.
- To apply linting and formatting:
```
flake8 . --ignore=D100,D101,D202,D204,D205,D400,D401,E303,E501,W503,N805,N806
isort . --profile black
autopep8 -i -r .
black .
```
