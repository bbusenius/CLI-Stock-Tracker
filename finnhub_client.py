"""
Finnhub API interaction module.

This module provides functions to interact with the Finnhub API, including initializing the API client
and fetching data for stocks and ETFs. It handles API key management, error handling for API calls,
and data extraction for the Stock and ETF Price Tracker CLI tool.
"""

import os
import sys

import finnhub
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
