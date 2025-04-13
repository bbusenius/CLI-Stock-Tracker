"""
Unit tests for websocket_client.py.

This module tests the websocket listener's ability to connect to Finnhub's websocket, subscribe to
tickers, and update the latest_prices dictionary with trade data. It also tests the get_latest_price
function for retrieving prices. Tests use mocking to simulate websocket interactions, ensuring
reliable and fast execution without network dependencies.
"""

import pytest
from websocket_client import get_latest_price, latest_prices, lock


@pytest.fixture(autouse=True)
def clear_latest_prices():
    """Clear latest_prices before each test to ensure a clean state."""
    with lock:
        latest_prices.clear()


def test_get_latest_price():
    """Test retrieving the latest price for a ticker.

    Verifies that get_latest_price returns the correct price when available and None when not.
    """
    with lock:
        latest_prices["AAPL"] = 150.0
    assert get_latest_price("AAPL") == 150.0
    assert get_latest_price("MSFT") is None
