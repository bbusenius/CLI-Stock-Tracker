"""
Configuration management module.

This module provides functions to load configuration data, such as the list of stock and ETF tickers
and display settings, from external files like JSON. It is designed to handle file loading robustly,
providing graceful error handling for missing or invalid files, and serves as a foundation for
configuring the Stock and ETF Price Tracker CLI tool.
"""

import json

from rich import print as rprint


def load_tickers(file_path: str) -> list[dict]:
    """
    Load the list of tickers from a JSON file, supporting both string and object formats.

    Args:
        file_path (str): Path to the JSON file containing the list of tickers.

    Returns:
        list[dict]: A list of dictionaries, each with 'ticker' (str) and optionally 'name' (str or None).

    Notes:
        The JSON file can contain either:
        - A list of strings (e.g., ["AAPL", "MSFT"]), converted to {"ticker": str, "name": None}.
        - A list of objects (e.g., [{"ticker": "AAPL", "name": "Apple Inc."}, {"ticker": "MSFT"}]),
          where "ticker" is required and "name" is optional.
        Invalid entries (e.g., missing "ticker" or non-string types) are skipped with a warning.
        If the file is missing, unreadable, or contains invalid JSON, an error is printed, and an empty list is returned.
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError("Tickers must be a list")
        tickers = []
        for item in data:
            if isinstance(item, str):
                tickers.append({"ticker": item, "name": None})
            elif isinstance(item, dict):
                if "ticker" in item and isinstance(item["ticker"], str):
                    name = item.get("name")
                    if name is not None and not isinstance(name, str):
                        rprint(
                            f"[yellow]Warning: Invalid 'name' for ticker {item['ticker']}, must be a string. Ignoring name.[/yellow]"
                        )
                        name = None
                    tickers.append({"ticker": item["ticker"], "name": name})
                else:
                    rprint(
                        f"[yellow]Warning: Invalid ticker entry {item}, missing 'ticker' key or invalid type. Skipping.[/yellow]"
                    )
            else:
                rprint(
                    f"[yellow]Warning: Invalid ticker entry {item}, must be a string or dictionary. Skipping.[/yellow]"
                )
        return tickers
    except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
        rprint(f"[red]Error loading tickers from {file_path}: {e}[/red]")
        return []


def load_settings(file_path: str) -> dict:
    """
    Load display settings and cache settings from a JSON file.

    Args:
        file_path (str): Path to the JSON file containing settings.

    Returns:
        dict: Settings dictionary with 'columns' and 'cache' sections.

    Notes:
        Expected format:
        {
            "columns": {
                "eps": bool,
                "pe_ratio": bool,
                "dividend": bool,
                "ytd_change": bool,
                "ten_year_change": bool
            },
            "cache": {
                "enabled": bool,
                "interval": int  # minutes
            }
        }
        If the file is missing, unreadable, or invalid, a warning is printed, and default settings are returned.
        Defaults:
        - columns: all False
        - cache: {"enabled": False, "interval": 60}
        Missing sections or keys in the JSON file are filled with defaults to ensure consistent output.
    """
    default_settings = {
        "columns": {
            "eps": False,
            "pe_ratio": False,
            "dividend": False,
            "ytd_change": False,
            "ten_year_change": False,
        },
        "cache": {"enabled": False, "interval": 60},
    }
    try:
        with open(file_path, 'r') as f:
            settings = json.load(f)
        # Handle columns section
        if "columns" not in settings:
            settings["columns"] = default_settings["columns"]
        else:
            for col in default_settings["columns"]:
                if col not in settings["columns"]:
                    settings["columns"][col] = default_settings["columns"][col]
        # Handle cache section
        if "cache" not in settings:
            settings["cache"] = default_settings["cache"]
        else:
            for key in default_settings["cache"]:
                if key not in settings["cache"]:
                    settings["cache"][key] = default_settings["cache"][key]
        return settings
    except (FileNotFoundError, json.JSONDecodeError) as e:
        rprint(
            f"[yellow]Warning: Could not load settings from {file_path}: {e}. Using default settings.[/yellow]"
        )
        return default_settings
