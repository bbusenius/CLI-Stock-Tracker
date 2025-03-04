# Stock and ETF Price Tracker
Stock and ETF Price Tracker is a command-line tool that fetches and displays key financial metrics for a configurable list of stock and ETF tickers using the [Finnhub API](https://finnhub.io/). It provides real-time data on stock prices, earnings, dividends, and more, formatted in a readable table using the rich library.

## Prerequisites
- Python 3.12: Ensure you have Python 3.12 installed on your system.
- Finnhub API Key: Sign up at [Finnhub](https://finnhub.io/) to obtain a free API key.

## Installation

### 1.  Clone the repository:
```
git clone https://github.com/bbusenius/Stock-Tracker.git
cd Stock-Tracker
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
```
python main.py
```
This will fetch the financial data for the specified tickers and display it in a formatted table.

## Configuration
- The tool reads the list of tickers from tickers.json. This file should contain a JSON array of ticker symbols, e.g., ["AAPL", "MSFT"].
- Ensure that tickers.json is present in the project root directory.

## API Rate Limits
- The Finnhub API has a rate limit of 60 calls per minute on the free tier.
- Each ticker requires up to 5 API calls (quote, profile, financials, YTD historical, and 10-year historical).
- Therefore, you can track up to 12 tickers without exceeding the rate limit in a single run.
- If you have more than 12 tickers, you may need to add delays between requests or consider upgrading to a paid Finnhub plan.
- The current implementation does not include delays, so please be mindful of the rate limits to avoid API errors.

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
