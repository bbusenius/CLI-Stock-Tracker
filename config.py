"""
Configuration management module.

This module provides functions to load configuration data, such as the list of stock and ETF tickers,
from external files like JSON. It is designed to handle file loading robustly, providing graceful
error handling for missing or invalid files, and serves as a foundation for configuring the
Stock and ETF Price Tracker CLI tool.
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
