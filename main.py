#!/usr/bin/env python3
"""
Main script for the Stock and ETF Price Tracker CLI tool.
Supports normal mode for displaying data and daemon mode for background cache updates.
"""

import argparse
import time

from rich import print as rprint

from cache import get_cached_data, get_cached_data_unchecked, update_cache
from config import load_settings, load_tickers
from display import display_table
from finnhub_client import fetch_ticker_data, initialize_client


def daemon_mode(client, tickers, settings):
    """Run in daemon mode to periodically update the cache."""
    interval = settings["cache"]["interval"] * 60  # Convert minutes to seconds
    while True:
        for ticker_obj in tickers:
            data = fetch_ticker_data(client, ticker_obj, settings)
            if "message" not in data:
                update_cache(ticker_obj["ticker"], data)
            time.sleep(1)  # Respect API rate limits
        time.sleep(interval)  # Wait before next cycle


def main():
    parser = argparse.ArgumentParser(description="CLI Stock and ETF Price Tracker")
    parser.add_argument("--refresh", action="store_true", help="Force fetch fresh data")
    parser.add_argument("--daemon", action="store_true", help="Run in daemon mode")
    args = parser.parse_args()

    if args.daemon:
        settings = load_settings("settings.json")
        tickers = load_tickers("tickers.json")
        if not tickers:
            rprint("[red]No tickers to process in daemon mode.[/red]")
            return
        client = initialize_client()
        daemon_mode(client, tickers, settings)
    else:
        settings = load_settings("settings.json")
        tickers = load_tickers("tickers.json")
        if not tickers:
            rprint("[red]No tickers to process.[/red]")
            return
        client = initialize_client()
        data = []
        failed_refreshes = []
        for ticker_obj in tickers:
            ticker = ticker_obj["ticker"]
            cache_enabled = settings["cache"]["enabled"]
            interval = settings["cache"]["interval"]
            if cache_enabled and not args.refresh:
                cached_data = get_cached_data(ticker, interval)
                if cached_data is not None:
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
                        data.append(cached_data)
                        failed_refreshes.append(ticker)
                    else:
                        data.append(fresh_data)
                else:
                    data.append(fresh_data)
        display_table(data, settings)
        if failed_refreshes:
            rprint(
                "[yellow]Warning: Used cached data for some tickers due to refresh failures:[/yellow]"
            )
            for ticker in failed_refreshes:
                rprint(f"[yellow]- {ticker}[/yellow]")


if __name__ == "__main__":
    main()
