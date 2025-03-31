"""
Cache management module for the Stock and ETF Price Tracker.

This module provides functions to manage a persistent cache of API results stored in a JSON file.
The cache reduces the need for repeated API calls by storing financial data for tickers across
application runs. It includes functions to load the cache, save the cache, retrieve cached data
if it is fresh based on a specified interval, retrieve cached data unconditionally for fallback,
and update the cache with new data. Thread safety is ensured using a lock during save operations
to prevent race conditions.

The cache is stored in 'cache.json' as a dictionary where each key is a ticker symbol, and each
value is a dictionary containing the data and a timestamp (e.g., {"AAPL": {"data": {...}, "timestamp": 1633024800}}).
"""

import json
import os
from datetime import datetime, timezone
from threading import Lock
from typing import Dict, Optional

# Constants
CACHE_FILE = "cache.json"
cache_lock = Lock()


def load_cache() -> Dict[str, dict]:
    """Load the cache from 'cache.json'.

    Returns:
        Dict[str, dict]: The cache dictionary with tickers as keys and data/timestamp dictionaries as values.
            Returns an empty dictionary if the file does not exist or is invalid.

    Notes:
        - Handles file not found or invalid JSON by returning an empty dictionary.
        - No error messages are printed here; higher-level modules handle user notifications.
    """
    if not os.path.exists(CACHE_FILE):
        return {}
    try:
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_cache(cache_dict: Dict[str, dict]) -> None:
    """Save the cache dictionary to 'cache.json'.

    Args:
        cache_dict (Dict[str, dict]): The cache dictionary to save, with tickers as keys and
            data/timestamp dictionaries as values.

    Notes:
        - Uses a threading lock to ensure thread safety during write operations.
        - Formats JSON with indentation for readability.
        - Assumes the directory is writable; IOError handling is left to the OS.
    """
    with cache_lock:
        with open(CACHE_FILE, "w") as f:
            json.dump(cache_dict, f, indent=2)


def get_cached_data(ticker: str, interval: int) -> Optional[dict]:
    """Retrieve cached data for the given ticker if it is fresh.

    Args:
        ticker (str): The ticker symbol to retrieve data for.
        interval (int): The cache freshness interval in minutes.

    Returns:
        Optional[dict]: The cached data dictionary if it exists and is fresh, None otherwise.

    Notes:
        - Freshness is determined by comparing the current UTC timestamp to the cached timestamp.
        - Returns None if the ticker is not in the cache or if the data is stale (older than interval minutes).
    """
    cache = load_cache()
    entry = cache.get(ticker)
    if not entry:
        return None
    now = datetime.now(timezone.utc).timestamp()
    if now - entry["timestamp"] <= interval * 60:
        return entry["data"]
    return None


def get_cached_data_unchecked(ticker: str) -> Optional[dict]:
    """Retrieve cached data for the given ticker without checking freshness.

    Args:
        ticker (str): The ticker symbol to retrieve data for.

    Returns:
        Optional[dict]: The cached data dictionary if it exists, None otherwise.

    Notes:
        - Used as a fallback when fetching fresh data fails and cached data is available, even if stale.
        - Does not consider the timestamp, only whether data exists for the ticker.
    """
    cache = load_cache()
    entry = cache.get(ticker)
    if entry:
        return entry["data"]
    return None


def update_cache(ticker: str, data: dict) -> None:
    """Update the cache with new data for the given ticker.

    Args:
        ticker (str): The ticker symbol to update.
        data (dict): The financial data dictionary to cache.

    Notes:
        - Stores the data with the current UTC timestamp as an integer.
        - Overwrites existing cache entry for the ticker if it exists.
    """
    cache = load_cache()
    cache[ticker] = {
        "data": data,
        "timestamp": int(datetime.now(timezone.utc).timestamp()),
    }
    save_cache(cache)
