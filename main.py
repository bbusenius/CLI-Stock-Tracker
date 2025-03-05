#!/usr/bin/env python3
"""
Main script for the Stock and ETF Price Tracker CLI tool.

This script orchestrates the workflow by loading the list of tickers and display settings,
fetching financial data for each ticker using the Finnhub API, and displaying the results
in a formatted table. It serves as the entry point for the command-line interface, integrating
the configuration, API client, and display modules to provide a seamless user experience.
"""

from rich import print as rprint

from config import load_settings, load_tickers
from display import display_table
from finnhub_client import fetch_ticker_data, initialize_client


def main():
    """
    Main function to run the Stock and ETF Price Tracker.

    This function performs the following steps:
    1. Loads the display settings from 'settings.json'.
    2. Loads the list of tickers from 'tickers.json'.
    3. Initializes the Finnhub API client using the API key from the environment variable.
    4. Fetches financial data for each ticker, considering the display settings.
    5. Displays the collected data in a formatted table using the rich library, based on the settings.

    Args:
        None

    Returns:
        None: The function executes the workflow and prints output to the console.

    Notes:
        - If the ticker list is empty (e.g., due to a missing or invalid 'tickers.json' file),
          it prints a red error message using rich and exits.
        - If the API key is not set, it catches the ValueError from initialize_client(),
          prints a red error message, and exits.
        - The function fetches data sequentially for each ticker, respecting the Finnhub API's
          rate limit of 60 calls per minute (up to 12 tickers without delays when all columns
          are enabled, fewer calls if optional columns are disabled).
        - Display settings determine which optional columns (Dividend, YTD % Change, 10-Year % Change)
          are fetched and displayed, with defaults excluding them to avoid API errors or missing data.
        - Edge cases like invalid tickers or unavailable data are handled by fetch_ticker_data(),
          which returns a dict with a 'message' key, displayed appropriately by display_table().
    """
    # Load display settings
    settings = load_settings('settings.json')

    # Load tickers from configuration file
    tickers = load_tickers('tickers.json')
    if not tickers:
        rprint("[red]No tickers to process. Please check your tickers.json file.[/red]")
        return

    # Initialize Finnhub API client
    try:
        client = initialize_client()
    except ValueError as e:
        rprint(f"[red]Error: {e}[/red]")
        return

    # Fetch data for each ticker, passing settings
    data = []
    for ticker in tickers:
        ticker_data = fetch_ticker_data(client, ticker, settings)
        data.append(ticker_data)

    # Display the data in a table, passing settings
    display_table(data, settings)


if __name__ == "__main__":
    main()
