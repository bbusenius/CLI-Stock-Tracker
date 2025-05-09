#!/usr/bin/env python3
"""
Main script for the Stock and ETF Price Tracker CLI tool.

Supports normal mode for displaying data, daemon mode for background cache updates,
and watch mode for real-time updates via websockets. Coordinates configuration loading,
API interactions, caching, and display rendering. Logs key operations and errors to 'tracker.log'
for monitoring and debugging purposes.
"""

import argparse
import logging
import os
import time
from typing import Dict, List

import finnhub
from rich import print as rprint
from rich.console import Console

from cache import get_cached_data, get_cached_data_unchecked, update_cache
from config import load_settings, load_tickers
from display import display_table
from finnhub_client import (
    calculate_changes,
    fetch_static_data,
    fetch_ticker_data,
    initialize_client,
)
from websocket_client import get_latest_price, start_websocket

# Configure logging at module level
logging.basicConfig(
    level=logging.INFO,
    filename='tracker.log',
    format='%(asctime)s - %(levelname)s - %(message)s',
)


def daemon_mode(
    client: finnhub.Client,
    tickers: List[Dict[str, str | None]],
    settings: Dict[str, dict | float],
) -> None:
    """Run in daemon mode to periodically update the cache.

    Args:
        client: Initialized Finnhub client.
        tickers: List of ticker dictionaries with 'ticker' and optional 'name'.
        settings: Configuration settings containing cache interval.

    Notes:
        Runs indefinitely, updating the cache every interval minutes.
        Logs key operations (start, updates, errors) to 'tracker.log'.
        Respects API rate limits with a 1-second delay between ticker updates.
    """
    interval = settings["cache"]["interval"] * 60  # Convert minutes to seconds
    logging.info("Daemon mode started.")
    while True:
        logging.info("Starting cache update cycle.")
        for ticker_obj in tickers:
            ticker = ticker_obj["ticker"]
            logging.info(f"Updating cache for {ticker}")
            try:
                data = fetch_ticker_data(client, ticker_obj, settings)
                if "message" in data:
                    logging.error(
                        f"Failed to fetch data for {ticker}: {data['message']}"
                    )
                else:
                    update_cache(ticker, data)
                    logging.info(f"Cache updated for {ticker}")
            except Exception as e:
                logging.error(f"Error updating cache for {ticker}: {str(e)}")
            time.sleep(1)  # Respect API rate limits
        logging.info(f"Cache update cycle complete. Sleeping for {interval} seconds.")
        time.sleep(interval)  # Wait before next cycle


def main() -> None:
    """Main entry point for the CLI Stock and ETF Price Tracker.

    Parses command-line arguments and executes the appropriate mode:
    - Normal mode: Displays data once, using cache if enabled.
    - Daemon mode: Continuously updates the cache in the background.
    - Watch mode: Continuously updates the display with real-time prices.

    Notes:
        Exits on critical errors like missing API key or tickers, logged as errors.
        Handles Ctrl+C in watch mode for graceful shutdown.
        Logs initialization and mode selection for debugging.
    """
    logging.info("Application starting.")
    parser = argparse.ArgumentParser(description="CLI Stock and ETF Price Tracker")
    parser.add_argument(
        "--refresh", action="store_true", help="Force fetch fresh data in normal mode"
    )
    parser.add_argument(
        "--daemon", action="store_true", help="Run in daemon mode for cache updates"
    )
    parser.add_argument(
        "--watch", action="store_true", help="Run in watch mode with real-time updates"
    )
    parser.add_argument(
        "--interval", type=float, help="Refresh interval in seconds for watch mode"
    )
    # In test environments, pytest may pass additional arguments
    # Use parse_known_args to ignore unknown arguments during testing
    args, _ = parser.parse_known_args()

    settings = load_settings("settings.json")
    tickers = load_tickers("tickers.json")
    if not tickers:
        logging.error("No tickers to process.")
        rprint("[red]No tickers to process.[/red]")
        return

    try:
        client = initialize_client()
        logging.info("Finnhub client initialized successfully.")
    except ValueError as e:
        logging.error(f"Failed to initialize Finnhub client: {str(e)}")
        rprint(f"[red]Error: {e}[/red]")
        return

    if args.daemon:
        logging.info("Entering daemon mode.")
        daemon_mode(client, tickers, settings)
    elif args.watch:
        logging.info("Entering watch mode.")
        # Determine refresh interval
        if args.interval is not None:
            if args.interval > 0:
                interval = args.interval
                logging.info(f"Using custom watch interval: {interval} seconds.")
            else:
                logging.warning("Interval must be positive. Using settings value.")
                rprint(
                    "\n[yellow]Warning: Interval must be positive. Using settings value.[/yellow]"
                )
                interval = settings["watch_interval"]
        else:
            interval = settings["watch_interval"]
            logging.info(
                f"Using default watch interval from settings: {interval} seconds."
            )

        # Start websocket
        api_key = os.getenv("FINNHUB_API_KEY")
        if not api_key:
            logging.error("FINNHUB_API_KEY is not set.")
            rprint("[red]Error: FINNHUB_API_KEY is not set.[/red]")
            return
        start_websocket([ticker_obj["ticker"] for ticker_obj in tickers], api_key)
        logging.info("Websocket started for real-time updates.")

        # Fetch static data once
        static_data = {
            ticker_obj["ticker"]: fetch_static_data(client, ticker_obj, settings)
            for ticker_obj in tickers
        }
        logging.info("Static data fetched for watch mode.")

        # Create console for watch mode
        console = Console(highlight=False, markup=True)

        # Continuous update loop
        while True:
            try:
                console.clear()
                data = []
                for ticker_obj in tickers:
                    ticker = ticker_obj["ticker"]
                    static = static_data[ticker]
                    if "message" in static:
                        data.append(static)
                        continue
                    latest_price = get_latest_price(ticker)
                    initial_current_price = static.get("initial_current_price")
                    current_price = (
                        latest_price
                        if latest_price is not None
                        else initial_current_price
                    )
                    quote = {"c": current_price, "pc": static["pc"]}
                    ytd_price = static["ytd_price"]
                    ten_year_price = static["ten_year_price"]
                    daily_change, ytd_change, ten_year_change = calculate_changes(
                        quote, ytd_price, ten_year_price
                    )
                    data.append(
                        {
                            "ticker": ticker,
                            "company_name": static["company_name"],
                            "current_price": current_price,
                            "eps": static["eps"],
                            "pe_ratio": static["pe_ratio"],
                            "dividend": static["dividend"],
                            "daily_change": daily_change,
                            "ytd_change": ytd_change,
                            "ten_year_change": ten_year_change,
                        }
                    )
                display_table(data, settings, console=console)
                time.sleep(interval)
            except KeyboardInterrupt:
                logging.info("Watch mode stopped by user.")
                rprint("\n[yellow]Stopping watch mode.[/yellow]")
                break
    else:
        # Normal mode
        logging.info("Entering normal mode.")
        data = []
        failed_refreshes = []
        cache_enabled = settings["cache"]["enabled"]
        for ticker_obj in tickers:
            ticker = ticker_obj["ticker"]
            if cache_enabled and not args.refresh:
                cached_data = get_cached_data(ticker, settings["cache"]["interval"])
                if cached_data is not None:
                    logging.info(f"Using cached data for {ticker}")
                    data.append(cached_data)
                    continue
            fresh_data = fetch_ticker_data(client, ticker_obj, settings)
            if "message" not in fresh_data:
                if cache_enabled:
                    update_cache(ticker, fresh_data)
                data.append(fresh_data)
            else:
                if cache_enabled:
                    cached_data = get_cached_data_unchecked(ticker)
                    if cached_data is not None:
                        logging.info(
                            f"Fallback to cached data for {ticker} due to fetch failure"
                        )
                        data.append(cached_data)
                        failed_refreshes.append(ticker)
                    else:
                        logging.error(
                            f"No cached data available for {ticker}, using failure message"
                        )
                        data.append(fresh_data)
                else:
                    data.append(fresh_data)
        display_table(data, settings)
        if failed_refreshes:
            logging.warning("Used cached data for some tickers due to refresh failures")
            rprint(
                "[yellow]Warning: Used cached data for some tickers due to refresh failures:[/yellow]"
            )
            for ticker in failed_refreshes:
                rprint(f"[yellow]- {ticker}[/yellow]")


if __name__ == "__main__":
    main()
