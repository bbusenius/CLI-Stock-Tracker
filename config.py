"""
Configuration management module.

This module provides functions to load configuration data, such as the list of stock and ETF tickers
and display settings, from external files like JSON. It is designed to handle file loading robustly,
providing graceful error handling for missing or invalid files, and serves as a foundation for
configuring the Stock and ETF Price Tracker CLI tool.
"""

import json

from rich import print as rprint


def load_tickers(file_path: str) -> list[str]:
    """
    Load the list of tickers from a JSON file.

    Args:
        file_path (str): The path to the JSON file containing the list of tickers.

    Returns:
        list[str]: A list of ticker symbols if successfully loaded, otherwise an empty list.

    Notes:
        If the file is missing, cannot be read, or contains invalid JSON (e.g., not a list), an error
        message is printed to the console using `rich`, and an empty list is returned. This allows
        the program to continue execution without crashing, deferring further handling to the
        caller (e.g., the main script).

    Examples:
        >>> load_tickers("tickers.json")  # With a valid file ["AAPL", "MSFT"]
        ['AAPL', 'MSFT']
        >>> load_tickers("missing.json")  # With a missing file
        [red]Error loading tickers from missing.json: [Errno 2] No such file or directory[/red]
        []
    """
    try:
        with open(file_path, 'r') as f:
            tickers = json.load(f)
        # Validate that the loaded data is a list
        if not isinstance(tickers, list):
            raise ValueError("Tickers must be a list")
        return tickers
    except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
        # Print error message in red using rich and return empty list
        rprint(f"[red]Error loading tickers from {file_path}: {e}[/red]")
        return []


def load_settings(file_path: str) -> dict:
    """
    Load display settings from a JSON file.

    Args:
        file_path (str): The path to the JSON file containing display settings.

    Returns:
        dict: A dictionary of settings if successfully loaded, otherwise default settings.

    Notes:
        The settings file should contain a JSON object with a "columns" key, which is a dictionary
        indicating which optional columns to include in the display table. For example:
        {
            "columns": {
                "eps": true,
                "pe_ratio": true,
                "dividend": true,
                "ytd_change": false,
                "ten_year_change": true
            }
        }
        If the file is missing, cannot be read, or contains invalid JSON, a warning is printed,
        and default settings are returned with all optional columns disabled. This ensures that
        optional columns (EPS, PE Ratio, Dividend, YTD % Change, 10-Year % Change) are excluded
        by default, avoiding errors or missing data due to API limitations.

    Examples:
        >>> load_settings("settings.json")  # With a valid file
        {'columns': {'eps': True, 'pe_ratio': True, 'dividend': True, 'ytd_change': False, 'ten_year_change': True}}
        >>> load_settings("missing.json")  # With a missing file
        [yellow]Warning: Could not load settings from missing.json: [Errno 2] No such file or directory. Using default settings.[/yellow]
        {'columns': {'eps': False, 'pe_ratio': False, 'dividend': False, 'ytd_change': False, 'ten_year_change': False}}
    """
    default_settings = {
        "columns": {
            "eps": False,
            "pe_ratio": False,
            "dividend": False,
            "ytd_change": False,
            "ten_year_change": False,
        }
    }
    try:
        with open(file_path, 'r') as f:
            settings = json.load(f)
        # Ensure "columns" key exists
        if "columns" not in settings:
            settings["columns"] = default_settings["columns"]
        else:
            # Fill in missing column settings with defaults
            for col in default_settings["columns"]:
                if col not in settings["columns"]:
                    settings["columns"][col] = default_settings["columns"][col]
        return settings
    except (FileNotFoundError, json.JSONDecodeError) as e:
        rprint(
            f"[yellow]Warning: Could not load settings from {file_path}: {e}. Using default settings.[/yellow]"
        )
        return default_settings
