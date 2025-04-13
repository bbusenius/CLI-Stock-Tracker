"""
Cache management module for the Stock and ETF Price Tracker.

This module provides functions to manage a persistent cache of API results stored in a JSON file.
The cache reduces the need for repeated API calls by storing financial data for tickers across
application runs. It includes functions to load the cache, save the cache, retrieve cached data
if it is fresh based on a specified interval, retrieve cached data unconditionally for fallback,
and update the cache with new data. Thread safety is ensured using a lock during save operations,
and operations are logged to 'tracker.log' for monitoring.
"""

import json
import logging
import os
from datetime import datetime, timezone
from threading import Lock
from typing import Dict, Optional

# Constants
CACHE_FILE = "cache.json"
cache_lock = Lock()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    filename='tracker.log',
    format='%(asctime)s - %(levelname)s - %(message)s',
)


def load_cache() -> Dict[str, dict]:
    """Load the cache from 'cache.json'.

    Returns:
        Dict[str, dict]: The cache dictionary with tickers as keys and data/timestamp dictionaries as values.
            Returns an empty dictionary if the file does not exist or is invalid.

    Notes:
        Handles file not found or invalid JSON by returning an empty dictionary and logging errors.
        No error messages are printed here; higher-level modules handle user notifications.
    """
    logging.info("Loading cache")
    if not os.path.exists(CACHE_FILE):
        logging.info("Cache file not found")
        return {}
    try:
        with open(CACHE_FILE, "r") as f:
            cache = json.load(f)
        logging.info("Cache loaded successfully")
        return cache
    except (json.JSONDecodeError, IOError) as e:
        logging.error(f"Error loading cache: {str(e)}")
        return {}


def save_cache(cache_dict: Dict[str, dict]) -> None:
    """Save the cache dictionary to 'cache.json'.

    Args:
        cache_dict (Dict[str, dict]): The cache dictionary to save, with tickers as keys and
            data/timestamp dictionaries as values.

    Notes:
        Uses a threading lock to ensure thread safety during write operations.
        Formats JSON with indentation for readability.
        Logs the save operation and any errors.
        Assumes the directory is writable; IOError handling is logged.
    """
    logging.info("Saving cache")
    with cache_lock:
        try:
            with open(CACHE_FILE, "w") as f:
                json.dump(cache_dict, f, indent=2)
            logging.info("Cache saved successfully")
        except IOError as e:
            logging.error(f"Error saving cache: {str(e)}")


def get_cached_data(ticker: str, interval: int) -> Optional[dict]:
    """Retrieve cached data for the given ticker if it is fresh.

    Args:
        ticker (str): The ticker symbol to retrieve data for.
        interval (int): The cache freshness interval in minutes.

    Returns:
        Optional[dict]: The cached data dictionary if it exists and is fresh, None otherwise.

    Notes:
        Freshness is determined by comparing the current UTC timestamp to the cached timestamp.
        Returns None if the ticker is not in the cache or if the data is stale.
        Logs retrieval attempts and outcomes.
    """
    logging.info(f"Getting cached data for {ticker} with interval {interval} minutes")
    cache = load_cache()
    entry = cache.get(ticker)
    if not entry:
        logging.info(f"No cache entry for {ticker}")
        return None
    now = datetime.now(timezone.utc).timestamp()
    age = now - entry["timestamp"]
    if age <= interval * 60:
        logging.info(f"Cache for {ticker} is fresh (age: {age} seconds)")
        return entry["data"]
    logging.info(f"Cache for {ticker} is stale (age: {age} seconds)")
    return None


def get_cached_data_unchecked(ticker: str) -> Optional[dict]:
    """Retrieve cached data for the given ticker without checking freshness.

    Args:
        ticker (str): The ticker symbol to retrieve data for.

    Returns:
        Optional[dict]: The cached data dictionary if it exists, None otherwise.

    Notes:
        Used as a fallback when fetching fresh data fails.
        Does not consider the timestamp, only whether data exists.
        Logs retrieval attempts and outcomes.
    """
    logging.info(f"Getting unchecked cached data for {ticker}")
    cache = load_cache()
    entry = cache.get(ticker)
    if entry:
        logging.info(f"Cache entry found for {ticker}")
        return entry["data"]
    logging.info(f"No cache entry for {ticker}")
    return None


def update_cache(ticker: str, data: dict) -> None:
    """Update the cache with new data for the given ticker.

    Args:
        ticker (str): The ticker symbol to update.
        data (dict): The financial data dictionary to cache.

    Notes:
        Stores the data with the current UTC timestamp as an integer.
        Overwrites existing cache entry for the ticker if it exists.
        Logs the update operation.
    """
    logging.info(f"Updating cache for {ticker}")
    cache = load_cache()
    cache[ticker] = {
        "data": data,
        "timestamp": int(datetime.now(timezone.utc).timestamp()),
    }
    save_cache(cache)
    logging.info(f"Cache updated for {ticker}")
