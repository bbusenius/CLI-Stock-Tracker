"""
Finnhub API interaction module.

This module provides functions to interact with the Finnhub API, including initializing the API client
and fetching data for stocks and ETFs. It handles API key management, error handling for API calls,
and data extraction for the Stock and ETF Price Tracker CLI tool.
"""

import os
import sys

import finnhub
from finnhub.exceptions import FinnhubAPIException
from rich import print as rprint


def initialize_client() -> finnhub.Client:
    """
    Initialize the Finnhub API client.

    Retrieves the API key from the FINNHUB_API_KEY environment variable and creates a Finnhub client
    instance. If the environment variable is not set, prints an error message and exits the program.

    Returns:
        finnhub.Client: An instance of the Finnhub API client configured with the provided API key.

    Raises:
        SystemExit: If the FINNHUB_API_KEY environment variable is not set, exits with status code 1.

    Notes:
        - The error message includes instructions for setting the environment variable, enhancing
          user experience by guiding them to resolve the issue.
        - This function assumes the API key is valid; validation of the key's correctness (e.g.,
          via API calls) will be handled in subsequent steps.
    """
    api_key = os.getenv("FINNHUB_API_KEY")
    if api_key is None:
        rprint(
            "[red]Error: FINNHUB_API_KEY environment variable is not set. "
            "Please set it using 'export FINNHUB_API_KEY=your_api_key' and try again.[/red]"
        )
        sys.exit(1)
    return finnhub.Client(api_key=api_key)


def get_quote(client: finnhub.Client, ticker: str) -> dict | None:
    """
    Fetch the quote data for a given ticker.

    Args:
        client (finnhub.Client): The Finnhub API client instance.
        ticker (str): The stock or ETF ticker symbol (e.g., "AAPL").

    Returns:
        dict | None: A dictionary containing quote data (e.g., {'c': current_price, 'pc': previous_close})
                     if the fetch is successful and the ticker is valid, otherwise None.

    Notes:
        - Quote data includes 'c' (current price), 'pc' (previous close), and other fields as provided
          by the Finnhub API (e.g., 'h' for high, 'l' for low, 'o' for open, 't' for timestamp).
        - Returns None if the API call raises FinnhubAPIException (e.g., network errors, rate limits,
          or invalid API key) or if the current price ('c') is 0, indicating an invalid or non-existent
          ticker.
        - The assumption that a current price of 0 denotes an invalid ticker is a simplification for
          this tool, as stocks or ETFs with a legitimate price of 0 are rare and typically delisted.
        - Error messages are not printed here; the caller (e.g., main workflow) will handle user feedback
          based on the None return value (e.g., displaying "Data unavailable for [TICKER]").
    """
    try:
        quote = client.quote(ticker)
        # Check if the current price is 0, suggesting an invalid ticker
        if quote.get('c', 0) == 0:
            return None
        return quote
    except FinnhubAPIException:
        # Covers API errors (e.g., invalid key, rate limit) and network issues
        return None


def get_profile(client: finnhub.Client, ticker: str) -> str | None:
    """
    Fetch the company name for a given ticker from the Finnhub API.

    Args:
        client (finnhub.Client): The Finnhub API client instance.
        ticker (str): The stock or ETF ticker symbol (e.g., "AAPL").

    Returns:
        str | None: The company name if successfully fetched and available, otherwise None.

    Notes:
        - Returns None if the API call raises FinnhubAPIException (e.g., network errors, rate limits,
          or invalid API key) or if the company name is missing or empty in the API response.
        - The caller is responsible for handling the None return value appropriately (e.g., displaying
          "Data unavailable for [TICKER]").
    """
    try:
        profile = client.company_profile2(symbol=ticker)
        if isinstance(profile, dict) and 'name' in profile and profile['name']:
            return profile['name']
        else:
            return None
    except FinnhubAPIException:
        return None
