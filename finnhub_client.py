"""
Finnhub API client module for the Stock and ETF Price Tracker.

This module provides functionality to interact with the Finnhub API, fetching real-time and historical
financial data for stocks and ETFs. It is responsible for initializing the API client using an
environment variable, retrieving data such as quotes, company profiles, financial metrics, and
historical prices, and processing this data to calculate percentage changes (daily, year-to-date,
and 10-year). The module is designed to handle errors gracefully, returning None or partial data
when API calls fail, and serves as the core data-fetching component of the CLI tool.

Key features include:
- Initializing the Finnhub client with an API key from the environment.
- Fetching current quotes, company names, financial metrics, and historical prices.
- Calculating percentage changes based on fetched data.
- Aggregating data into a structured format for display.

All functions include error handling for API failures, invalid tickers, or missing data, ensuring
robustness in real-world usage.
"""

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
            'dividend': metrics.get('currentDividendYieldTTM'),
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


def calculate_changes(
    quote: dict | None, ytd_price: float | None, ten_year_price: float | None
) -> tuple[float | None, float | None, float | None]:
    """
    Calculates the percentage changes for daily, YTD, and 10-year periods.

    Args:
        quote (dict | None): The quote data containing 'c' (current price) and 'pc' (previous close).
        ytd_price (float | None): The closing price at the start of the year.
        ten_year_price (float | None): The closing price from 10 years ago.

    Returns:
        tuple[float | None, float | None, float | None]: A tuple containing daily_change,
        ytd_change, and ten_year_change. Each change is a float representing the percentage
        change, or None if the calculation cannot be performed.
    """
    if quote is None:
        return None, None, None

    current_price = quote.get('c')
    previous_close = quote.get('pc')

    # Calculate daily percentage change: ((current - previous) / previous) * 100
    daily_change = (
        ((current_price - previous_close) / previous_close) * 100
        if current_price is not None
        and previous_close is not None
        and previous_close != 0
        else None
    )

    # Calculate YTD percentage change: ((current - ytd) / ytd) * 100
    ytd_change = (
        ((current_price - ytd_price) / ytd_price) * 100
        if current_price is not None and ytd_price is not None and ytd_price != 0
        else None
    )

    # Calculate 10-year percentage change: ((current - ten_year) / ten_year) * 100
    ten_year_change = (
        ((current_price - ten_year_price) / ten_year_price) * 100
        if current_price is not None
        and ten_year_price is not None
        and ten_year_price != 0
        else None
    )

    return daily_change, ytd_change, ten_year_change


def fetch_ticker_data(client: finnhub.Client, ticker: str) -> dict:
    """
    Fetches and aggregates financial data for the given ticker.

    This function retrieves the quote, company profile, basic financials, and historical
    closing prices (YTD and 10 years ago) for the specified ticker. It then calculates
    the daily, YTD, and 10-year percentage changes. If the ticker is invalid (i.e., quote
    data is unavailable), it returns a dictionary with a 'message' key indicating the
    data is unavailable. Otherwise, it returns a dictionary with all the fetched and
    calculated data, where missing values are represented as None.

    Args:
        client (finnhub.Client): The initialized Finnhub API client.
        ticker (str): The stock or ETF ticker symbol.

    Returns:
        dict: A dictionary containing the aggregated data. If the ticker is invalid,
              it contains {'ticker': str, 'message': 'Data unavailable'}. Otherwise,
              it contains keys for 'ticker', 'company_name', 'current_price', 'eps',
              'pe_ratio', 'dividend', 'daily_change', 'ytd_change', and 'ten_year_change',
              with values that may be None if the data is unavailable.

    Notes:
        - The function assumes that all prior fetch functions (`get_quote`, etc.) return
          None on failure (e.g., API errors, invalid tickers), which is handled here.
        - Missing values are kept as None to allow the display module to format them as 'N/A'.
        - Edge cases like API rate limits or partial data are implicitly handled via None returns
          from the fetch functions.
    """
    quote = get_quote(client, ticker)
    if quote is None:
        return {'ticker': ticker, 'message': 'Data unavailable'}

    profile = get_profile(client, ticker)
    financials = get_financials(client, ticker)
    ytd_price = get_ytd_price(client, ticker)
    ten_year_price = get_ten_year_price(client, ticker)

    daily_change, ytd_change, ten_year_change = calculate_changes(
        quote, ytd_price, ten_year_price
    )

    return {
        'ticker': ticker,
        'company_name': profile,
        'current_price': quote.get('c'),
        'eps': financials.get('eps') if financials else None,
        'pe_ratio': financials.get('pe') if financials else None,
        'dividend': financials.get('dividend') if financials else None,
        'daily_change': daily_change,
        'ytd_change': ytd_change,
        'ten_year_change': ten_year_change,
    }
