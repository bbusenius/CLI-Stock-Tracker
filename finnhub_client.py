import os
from datetime import datetime, timedelta, timezone

import finnhub


def initialize_client() -> finnhub.Client:
    """
    Initializes the Finnhub API client using the API key from the environment variable.

    Returns:
        finnhub.Client: Initialized Finnhub client.

    Raises:
        ValueError: If the FINNHUB_API_KEY environment variable is not set.
    """
    api_key = os.getenv("FINNHUB_API_KEY")
    if not api_key:
        raise ValueError("FINNHUB_API_KEY environment variable is not set.")
    return finnhub.Client(api_key)


def get_quote(client: finnhub.Client, ticker: str) -> dict | None:
    """
    Fetches the current quote data for the given ticker.

    Args:
        client (finnhub.Client): Initialized Finnhub client.
        ticker (str): Stock or ETF ticker symbol.

    Returns:
        dict | None: Quote data if successful, None otherwise.
    """
    try:
        return client.quote(ticker)
    except finnhub.FinnhubAPIException:
        return None


def get_profile(client: finnhub.Client, ticker: str) -> str | None:
    """
    Fetches the company name from the company profile for the given ticker.

    Args:
        client (finnhub.Client): Initialized Finnhub client.
        ticker (str): Stock or ETF ticker symbol.

    Returns:
        str | None: Company name if successful, None otherwise.
    """
    try:
        profile = client.company_profile2(symbol=ticker)
        return profile.get('name')
    except finnhub.FinnhubAPIException:
        return None


def get_financials(client: finnhub.Client, ticker: str) -> dict | None:
    """
    Fetches basic financial metrics (EPS, PE ratio, dividend) for the given ticker.

    Args:
        client (finnhub.Client): Initialized Finnhub client.
        ticker (str): Stock or ETF ticker symbol.

    Returns:
        dict | None: Dictionary with EPS, PE, and dividend if successful, None otherwise.
    """
    try:
        financials = client.company_basic_financials(ticker, 'all')
        metrics = financials.get('metric', {})
        return {
            'eps': metrics.get('epsTTM'),
            'pe': metrics.get('peTTM'),
            'dividend': metrics.get('dividendYieldTTM'),
        }
    except finnhub.FinnhubAPIException:
        return None


def get_ytd_price(client: finnhub.Client, ticker: str) -> float | None:
    """
    Fetches the closing price from the start of the year for the given ticker.

    Args:
        client (finnhub.Client): Initialized Finnhub client.
        ticker (str): Stock or ETF ticker symbol.

    Returns:
        float | None: YTD closing price if available, None otherwise.
    """
    try:
        today = datetime.now(timezone.utc)
        ytd_start = datetime(today.year, 1, 1, tzinfo=timezone.utc)
        ytd_end = ytd_start + timedelta(days=10)
        start_timestamp = int(ytd_start.timestamp())
        end_timestamp = int(ytd_end.timestamp())
        data = client.stock_candles(ticker, 'D', start_timestamp, end_timestamp)
        if data['s'] == 'ok' and data['c']:
            return data['c'][0]
        return None
    except finnhub.FinnhubAPIException:
        return None


def get_ten_year_price(client: finnhub.Client, ticker: str) -> float | None:
    """
    Fetches the closing price from 10 years ago for the given ticker.

    Args:
        client (finnhub.Client): Initialized Finnhub client.
        ticker (str): Stock or ETF ticker symbol.

    Returns:
        float | None: The closing price from 10 years ago, or None if unavailable.
    """
    try:
        # Calculate date 10 years ago from today (approximate, ignoring leap years)
        today = datetime.now(timezone.utc).date()
        start_date = today - timedelta(days=365 * 10)
        # Set start to midnight UTC
        start_datetime = datetime.combine(
            start_date, datetime.min.time(), tzinfo=timezone.utc
        )
        # End date is 5 days later to ensure a trading day is captured
        end_datetime = start_datetime + timedelta(days=5)
        start_timestamp = int(start_datetime.timestamp())
        end_timestamp = int(end_datetime.timestamp())

        # Fetch daily candles for the 5-day range
        data = client.stock_candles(ticker, 'D', start_timestamp, end_timestamp)
        if data['s'] == 'ok' and data['c']:
            # Return the earliest closing price in the range
            return data['c'][0]
        # No data available (e.g., new stock or non-trading period)
        return None
    except finnhub.FinnhubAPIException:
        # Handle API errors (e.g., rate limits, network issues, invalid ticker)
        return None
