"""
Unit tests for the cache module.

This module tests the caching functions in cache.py, including load_cache, save_cache,
get_cached_data, and update_cache. The tests verify that the cache is correctly loaded,
saved, retrieved based on freshness, and updated, ensuring reliable persistent storage
for the Stock and ETF Price Tracker CLI tool.
"""

import json
import os
import time

from cache import get_cached_data, load_cache, save_cache, update_cache


def test_load_cache_existing(tmp_path):
    """Tests loading an existing cache file."""
    cache_file = tmp_path / "cache.json"
    cache_data = {"AAPL": {"data": {"ticker": "AAPL"}, "timestamp": 1633024800}}
    cache_file.write_text(json.dumps(cache_data))
    os.chdir(tmp_path)
    cache = load_cache()
    assert cache == cache_data


def test_load_cache_missing(tmp_path):
    """Tests loading a non-existent cache file."""
    os.chdir(tmp_path)
    cache = load_cache()
    assert cache == {}


def test_save_cache(tmp_path):
    """Tests saving the cache to a file."""
    cache_file = tmp_path / "cache.json"
    os.chdir(tmp_path)
    cache_data = {"AAPL": {"data": {"ticker": "AAPL"}, "timestamp": 1633024800}}
    save_cache(cache_data)
    with open(cache_file, "r") as f:
        assert json.load(f) == cache_data


def test_get_cached_data_fresh(tmp_path):
    """Tests retrieving fresh cached data."""
    cache_file = tmp_path / "cache.json"
    current_time = int(time.time())
    cache_data = {"AAPL": {"data": {"ticker": "AAPL"}, "timestamp": current_time}}
    cache_file.write_text(json.dumps(cache_data))
    os.chdir(tmp_path)
    data = get_cached_data("AAPL", 60)
    assert data == {"ticker": "AAPL"}


def test_get_cached_data_stale(tmp_path):
    """Tests retrieving stale cached data."""
    cache_file = tmp_path / "cache.json"
    stale_time = int(time.time()) - 3600
    cache_data = {"AAPL": {"data": {"ticker": "AAPL"}, "timestamp": stale_time}}
    cache_file.write_text(json.dumps(cache_data))
    os.chdir(tmp_path)
    data = get_cached_data("AAPL", 30)
    assert data is None


def test_update_cache(tmp_path):
    """Tests updating the cache with new data."""
    os.chdir(tmp_path)
    update_cache("AAPL", {"ticker": "AAPL"})
    cache = load_cache()
    assert "AAPL" in cache
    assert cache["AAPL"]["data"] == {"ticker": "AAPL"}
    assert "timestamp" in cache["AAPL"]
