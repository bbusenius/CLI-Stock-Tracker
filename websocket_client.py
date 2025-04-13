"""Websocket client module for real-time trade updates from Finnhub.

This module provides functionality to connect to Finnhub's websocket, subscribe to specified tickers,
and maintain a thread-safe dictionary of the latest trade prices. It includes functions to start the
websocket listener in a background thread and to retrieve the latest price for a given ticker.

The websocket connection is managed with automatic reconnection attempts in case of errors.

Usage:
    - Call `start_websocket(tickers, api_key)` to start the websocket listener in a background thread.
    - Use `get_latest_price(ticker)` to retrieve the latest price for a ticker.

Note:
    - Requires the `websockets` library. Install via `pip install websockets`.
    - The websocket listener runs indefinitely until the application exits.
"""

import asyncio
import json
import threading
import time
from typing import Dict, List, Optional

import websockets

# Global dictionary to store the latest prices, protected by a lock for thread safety
latest_prices: Dict[str, float] = {}
lock = threading.Lock()


async def websocket_listener(api_key: str, tickers: List[str]) -> None:
    """Asynchronous function to listen to websocket messages and update latest prices.

    Args:
        api_key: Finnhub API key for authentication.
        tickers: List of ticker symbols to subscribe to.

    Notes:
        Runs an infinite loop to maintain the connection, subscribing to tickers on each reconnect.
        Updates `latest_prices` with trade data from received messages.
        Handles connection errors by waiting 5 seconds before retrying.
    """
    uri = f"wss://ws.finnhub.io?token={api_key}"
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                # Subscribe to all specified tickers
                for ticker in tickers:
                    await websocket.send(
                        json.dumps({"type": "subscribe", "symbol": ticker})
                    )
                # Continuously receive messages
                while True:
                    message = await websocket.recv()
                    data = json.loads(message)
                    if data["type"] == "trade":
                        for trade in data["data"]:
                            ticker = trade["s"]
                            price = trade["p"]
                            with lock:
                                latest_prices[ticker] = price
        except Exception as e:
            print(f"Websocket error: {e}")
            time.sleep(5)  # Wait before reconnecting


def start_websocket(tickers: List[str], api_key: str) -> None:
    """Start the websocket listener in a background thread.

    Args:
        tickers: List of ticker symbols to subscribe to.
        api_key: Finnhub API key.

    Notes:
        - Launches the websocket listener in a daemon thread, which terminates when the main
          application exits.
        - Uses asyncio.run to manage the async websocket_listener within the thread.
        - Assumes tickers are valid strings; invalid tickers may result in no data from Finnhub.
    """
    threading.Thread(
        target=asyncio.run, args=(websocket_listener(api_key, tickers),), daemon=True
    ).start()


def get_latest_price(ticker: str) -> Optional[float]:
    """Retrieve the latest price for the given ticker.

    Args:
        ticker: The ticker symbol.

    Returns:
        The latest price if available, None otherwise.

    Notes:
        - Thread-safe access to `latest_prices` using a lock.
        - Returns None if no price has been received for the ticker yet.
    """
    with lock:
        return latest_prices.get(ticker)
