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
- Aggregating data into a structured format for display, considering display settings.
- Fetching static data for use in real-time update modes.

All functions include error handling for API failures, invalid tickers, or missing data, ensuring
robustness in real-world usage.
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Dict, Tuple

import finnhub


def initialize_client() -> finnhub.Client:
    """Initializes the Finnhub API client using the API key from the environment variable.

    Returns:
        Initialized Finnhub client.

    Raises:
        ValueError: If the FINNHUB_API_KEY environment variable is not set.
    """
    api_key = os.getenv("FINNHUB_API_KEY")
    if not api_key:
        raise ValueError("FINNHUB_API_KEY environment variable is not set.")
    return finnhub.Client(api_key)


def get_quote(client: finnhub.Client, ticker: str) -> Dict[str, float] | None:
    """Fetches the current quote data for the given ticker.

    Args:
        client: Initialized Finnhub client.
        ticker: Stock or ETF ticker symbol.

    Returns:
        Quote data if successful, None otherwise.
    """
    try:
        return client.quote(ticker)
    except finnhub.FinnhubAPIException:
        return None


def get_profile(client: finnhub.Client, ticker: str) -> str | None:
    """Fetches the company name from the company profile for the given ticker.

    Args:
        client: Initialized Finnhub client.
        ticker: Stock or ETF ticker symbol.

    Returns:
        Company name if successful, None otherwise.
    """
    try:
        profile = client.company_profile2(symbol=ticker)
        return profile.get('name')
    except finnhub.FinnhubAPIException:
        return None


def get_financials(
    client: finnhub.Client, ticker: str
) -> Dict[str, float | None] | None:
    """Fetches basic financial metrics (EPS, PE ratio, dividend) for the given ticker.

    Args:
        client: Initialized Finnhub client.
        ticker: Stock or ETF ticker symbol.

    Returns:
        Dictionary with EPS, PE, and dividend if successful, None otherwise.
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
    """Fetches the closing price from the start of the year for the given ticker.

    Args:
        client: Initialized Finnhub client.
        ticker: Stock or ETF ticker symbol.

    Returns:
        YTD closing price if available, None otherwise.

    Notes:
        - Uses a 10-day range from January 1st to account for non-trading days.
        - Returns None if the API call fails (e.g., due to free plan limitations with a 403 error).
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
    """Fetches the closing price from 10 years ago for the given ticker.

    Args:
        client: Initialized Finnhub client.
        ticker: Stock or ETF ticker symbol.

    Returns:
        The closing price from 10 years ago, or None if unavailable.

    Notes:
        - Uses a 5-day range from 10 years ago to ensure a trading day is captured.
        - Returns None if the API call fails (e.g., due to free plan limitations with a 403 error).
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
    quote: Dict[str, float] | None,
    ytd_price: float | None,
    ten_year_price: float | None,
) -> Tuple[float | None, float | None, float | None]:
    """Calculates the percentage changes for daily, YTD, and 10-year periods.

    Args:
        quote: The quote data containing 'c' (current price) and 'pc' (previous close).
        ytd_price: The closing price at the start of the year.
        ten_year_price: The closing price from 10 years ago.

    Returns:
        A tuple containing daily_change, ytd_change, and ten_year_change. Each change is a float
        representing the percentage change, or None if the calculation cannot be performed.

    Notes:
        - Returns (None, None, None) if quote is None.
        - Individual changes are None if required prices are missing or zero to prevent division errors.
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


def fetch_ticker_data(
    client: finnhub.Client, ticker_obj: Dict[str, str | None], settings: Dict[str, dict]
) -> Dict[str, str | float | None]:
    """Fetches and aggregates financial data for the given ticker object based on display settings.

    This function retrieves the quote, company profile (if needed), basic financials, and conditionally
    fetches historical closing prices (YTD and 10 years ago) based on the provided settings. It then
    calculates the daily, YTD, and 10-year percentage changes if the corresponding data is available.
    The ticker object must contain a 'ticker' key and may include an optional 'name' key. If 'name' is
    provided and not None, it overrides the API-fetched name; otherwise, the API is queried. If the
    ticker is invalid (i.e., quote data is unavailable), it returns a dictionary with a 'message' key.
    Otherwise, it returns a dictionary with all fetched and calculated data, where missing values are
    None.

    Args:
        client: The initialized Finnhub API client.
        ticker_obj: A dictionary with 'ticker' (str) and optionally 'name' (str or None).
        settings: Display settings indicating which optional columns to include.

    Returns:
        A dictionary containing the aggregated data. If invalid, contains {'ticker': str, 'message': str}.
        Otherwise, contains keys for 'ticker', 'company_name', 'current_price', 'eps', 'pe_ratio',
        'dividend', 'daily_change', 'ytd_change', and 'ten_year_change'.

    Notes:
        - Assumes 'ticker' key exists in ticker_obj, as validated by load_tickers in config.py.
        - Historical prices are fetched only if their change columns are enabled, minimizing API calls.
        - If both user-provided and API-fetched names are unavailable, company_name is None.
    """
    ticker = ticker_obj["ticker"]
    user_name = ticker_obj.get("name")
    quote = get_quote(client, ticker)
    if quote is None:
        return {"ticker": ticker, "message": "Data unavailable"}

    # Use user-provided name if available, else fetch from API
    if user_name is not None:
        company_name = user_name
    else:
        company_name = get_profile(client, ticker)

    financials = get_financials(client, ticker)
    ytd_price = (
        get_ytd_price(client, ticker) if settings["columns"]["ytd_change"] else None
    )
    ten_year_price = (
        get_ten_year_price(client, ticker)
        if settings["columns"]["ten_year_change"]
        else None
    )
    daily_change, ytd_change, ten_year_change = calculate_changes(
        quote, ytd_price, ten_year_price
    )

    return {
        "ticker": ticker,
        "company_name": company_name,
        "current_price": quote.get("c"),
        "eps": financials.get("eps") if financials else None,
        "pe_ratio": financials.get("pe") if financials else None,
        "dividend": financials.get("dividend") if financials else None,
        "daily_change": daily_change,
        "ytd_change": ytd_change,
        "ten_year_change": ten_year_change,
    }


def fetch_static_data(
    client: finnhub.Client, ticker_obj: Dict[str, str | None], settings: Dict[str, dict]
) -> Dict[str, str | float | None]:
    """Fetches static financial data for the given ticker object.

    This function retrieves data that does not change frequently, such as the previous close price,
    initial current price, company name, financial metrics, and historical prices for YTD and 10-year
    changes, intended for use with real-time price updates via websockets.

    Args:
        client: The initialized Finnhub API client.
        ticker_obj: A dictionary with 'ticker' (str) and optionally 'name' (str or None).
        settings: Display settings indicating which optional columns to include.

    Returns:
        A dictionary containing the static data. If invalid, contains {'ticker': str, 'message': str}.
        Otherwise, includes keys for 'ticker', 'company_name', 'pc', 'initial_current_price', 'eps',
        'pe_ratio', 'dividend', 'ytd_price', and 'ten_year_price'.

    Notes:
        - 'company_name' prioritizes the user-provided name; otherwise, it fetches from the API.
        - 'ytd_price' and 'ten_year_price' are fetched only if their change columns are enabled.
        - 'initial_current_price' is included from the quote to provide a starting value for watch mode.
        - Assumes 'ticker' key exists in ticker_obj, validated by load_tickers in config.py.
    """
    ticker = ticker_obj["ticker"]
    user_name = ticker_obj.get("name")
    quote = get_quote(client, ticker)
    if quote is None:
        return {"ticker": ticker, "message": "Data unavailable"}

    pc = quote.get("pc")
    initial_current_price = quote.get("c")

    # Use user-provided name if available, else fetch from API
    if user_name is not None:
        company_name = user_name
    else:
        company_name = get_profile(client, ticker)

    financials = get_financials(client, ticker)
    ytd_price = (
        get_ytd_price(client, ticker) if settings["columns"]["ytd_change"] else None
    )
    ten_year_price = (
        get_ten_year_price(client, ticker)
        if settings["columns"]["ten_year_change"]
        else None
    )

    return {
        "ticker": ticker,
        "company_name": company_name,
        "pc": pc,
        "initial_current_price": initial_current_price,
        "eps": financials.get("eps") if financials else None,
        "pe_ratio": financials.get("pe") if financials else None,
        "dividend": financials.get("dividend") if financials else None,
        "ytd_price": ytd_price,
        "ten_year_price": ten_year_price,
    }
