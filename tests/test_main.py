"""
Unit tests for the main workflow in main.py.

This module tests the integration of loading tickers, initializing the Finnhub API client,
fetching financial data, caching, and displaying results. It uses mocking to simulate
dependencies and verify behavior under various scenarios, including caching and the --refresh option.
"""

from unittest.mock import MagicMock, patch

import pytest
from main import main

# Sample data for consistent test inputs
SAMPLE_AAPL = {
    'ticker': 'AAPL',
    'company_name': 'Apple Inc.',
    'current_price': 145.67,
    'eps': 5.89,
    'pe_ratio': 24.70,
    'dividend': 0.85,
    'daily_change': 1.23,
    'ytd_change': -2.34,
    'ten_year_change': 245.67,
}

SAMPLE_MSFT = {
    'ticker': 'MSFT',
    'company_name': 'Microsoft Corporation',
    'current_price': 280.50,
    'eps': 8.05,
    'pe_ratio': 34.80,
    'dividend': 1.00,
    'daily_change': 0.56,
    'ytd_change': 5.67,
    'ten_year_change': 300.00,
}

INVALID_XYZ = {'ticker': 'XYZ', 'message': 'Data unavailable'}


def test_main_with_cache(capsys):
    """Tests main workflow using cached data when available and fresh.

    Args:
        capsys: Pytest fixture to capture console output.

    Returns:
        None: Asserts display_table uses cached data and no updates occur.
    """
    with patch(
        "main.load_settings",
        return_value={"columns": {}, "cache": {"enabled": True, "interval": 60}},
    ), patch(
        "main.load_tickers", return_value=[{"ticker": "AAPL", "name": None}]
    ), patch(
        "main.initialize_client", return_value=MagicMock()
    ), patch(
        "main.get_cached_data", return_value=SAMPLE_AAPL
    ), patch(
        "main.fetch_ticker_data", side_effect=[SAMPLE_AAPL]
    ), patch(
        "main.update_cache"
    ) as mock_update, patch(
        "main.display_table"
    ) as mock_display:
        main()
        mock_display.assert_called_once_with(
            [SAMPLE_AAPL], {"columns": {}, "cache": {"enabled": True, "interval": 60}}
        )
        mock_update.assert_not_called()
    captured = capsys.readouterr()
    assert captured.out == ""


def test_main_with_stale_cache(capsys):
    """Tests main workflow fetching fresh data when cache is stale.

    Args:
        capsys: Pytest fixture to capture console output.

    Returns:
        None: Asserts fresh data is fetched and cache is updated.
    """
    with patch(
        "main.load_settings",
        return_value={"columns": {}, "cache": {"enabled": True, "interval": 60}},
    ), patch(
        "main.load_tickers", return_value=[{"ticker": "AAPL", "name": None}]
    ), patch(
        "main.initialize_client", return_value=MagicMock()
    ), patch(
        "main.get_cached_data", return_value=None
    ), patch(
        "main.fetch_ticker_data", return_value=SAMPLE_AAPL
    ), patch(
        "main.update_cache"
    ) as mock_update, patch(
        "main.display_table"
    ) as mock_display:
        main()
        mock_display.assert_called_once_with(
            [SAMPLE_AAPL], {"columns": {}, "cache": {"enabled": True, "interval": 60}}
        )
        mock_update.assert_called_once_with("AAPL", SAMPLE_AAPL)
    captured = capsys.readouterr()
    assert captured.out == ""


def test_main_with_refresh(capsys):
    """Tests main workflow with --refresh option bypassing cache.

    Args:
        capsys: Pytest fixture to capture console output.

    Returns:
        None: Asserts fresh data is fetched despite cache.
    """
    with patch(
        "main.load_settings",
        return_value={"columns": {}, "cache": {"enabled": True, "interval": 60}},
    ), patch(
        "main.load_tickers", return_value=[{"ticker": "AAPL", "name": None}]
    ), patch(
        "main.initialize_client", return_value=MagicMock()
    ), patch(
        "main.get_cached_data", return_value=SAMPLE_AAPL
    ), patch(
        "main.fetch_ticker_data", return_value=SAMPLE_AAPL
    ), patch(
        "main.update_cache"
    ) as mock_update, patch(
        "main.display_table"
    ) as mock_display, patch(
        "sys.argv", ["main.py", "--refresh"]
    ):
        main()
        mock_display.assert_called_once_with(
            [SAMPLE_AAPL], {"columns": {}, "cache": {"enabled": True, "interval": 60}}
        )
        mock_update.assert_called_once_with("AAPL", SAMPLE_AAPL)
    captured = capsys.readouterr()
    assert captured.out == ""


def test_main_no_tickers(capsys):
    """Tests main workflow when no tickers are provided.

    Args:
        capsys: Pytest fixture to capture console output.

    Returns:
        None: Asserts error message and no further processing.
    """
    with patch("main.load_settings"), patch(
        "main.load_tickers", return_value=[]
    ), patch("main.initialize_client") as mock_init, patch(
        "main.fetch_ticker_data"
    ) as mock_fetch, patch(
        "main.display_table"
    ) as mock_display:
        main()
        captured = capsys.readouterr()
        assert "No tickers to process" in captured.out
        mock_init.assert_not_called()
        mock_fetch.assert_not_called()
        mock_display.assert_not_called()


def test_main_partial_data(capsys):
    """Tests main workflow with mixed valid and invalid tickers.

    Args:
        capsys: Pytest fixture to capture console output.

    Returns:
        None: Asserts all data is displayed without errors.
    """
    with patch(
        "main.load_settings",
        return_value={"columns": {}, "cache": {"enabled": False, "interval": 60}},
    ), patch(
        "main.load_tickers",
        return_value=[
            {"ticker": "AAPL", "name": None},
            {"ticker": "XYZ", "name": None},
            {"ticker": "MSFT", "name": None},
        ],
    ), patch(
        "main.initialize_client", return_value=MagicMock()
    ), patch(
        "main.fetch_ticker_data", side_effect=[SAMPLE_AAPL, INVALID_XYZ, SAMPLE_MSFT]
    ), patch(
        "main.display_table"
    ) as mock_display:
        main()
        mock_display.assert_called_once_with(
            [SAMPLE_AAPL, INVALID_XYZ, SAMPLE_MSFT],
            {"columns": {}, "cache": {"enabled": False, "interval": 60}},
        )
    captured = capsys.readouterr()
    assert captured.out == ""
