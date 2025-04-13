"""
Configuration management module.

This module provides functions to load configuration data, such as the list of stock and ETF tickers
and display settings, from external files like JSON. It is designed to handle file loading robustly,
providing graceful error handling for missing or invalid files, and serves as a foundation for
configuring the Stock and ETF Price Tracker CLI tool.
"""

import json
from typing import Dict, List

from rich import print as rprint


def load_tickers(file_path: str) -> List[Dict[str, str | None]]:
    """
    Load the list of tickers from a JSON file, supporting both string and object formats.

    Args:
        file_path: Path to the JSON file containing the list of tickers.

    Returns:
        A list of dictionaries, each with 'ticker' (str) and optionally 'name' (str or None).

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


def load_settings(file_path: str) -> Dict[str, dict | float]:
    """
    Load display settings, cache settings, and watch interval from a JSON file.

    Args:
        file_path: Path to the JSON file containing settings.

    Returns:
        Settings dictionary with 'columns', 'cache', and 'watch_interval' keys.

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
            },
            "watch_interval": float  # seconds
        }
        If the file is missing, unreadable, or invalid, a warning is printed, and default settings are returned.
        Defaults:
        - columns: all False
        - cache: {"enabled": False, "interval": 60}
        - watch_interval: 5
        Missing sections or keys are filled with defaults.
        watch_interval must be a positive number; invalid values revert to default with a warning.
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
        "watch_interval": 5,
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
        # Handle watch_interval
        watch_interval = settings.get(
            "watch_interval", default_settings["watch_interval"]
        )
        try:
            watch_interval = float(watch_interval)
            if watch_interval <= 0:
                rprint(
                    "[yellow]Warning: watch_interval must be positive. Using default 5 seconds.[/yellow]"
                )
                watch_interval = 5
        except (ValueError, TypeError):
            rprint(
                "[yellow]Warning: Invalid watch_interval in settings. Using default 5 seconds.[/yellow]"
            )
            watch_interval = 5
        settings["watch_interval"] = watch_interval
        return settings
    except (FileNotFoundError, json.JSONDecodeError) as e:
        rprint(
            f"[yellow]Warning: Could not load settings from {file_path}: {e}. Using default settings.[/yellow]"
        )
        return default_settings
