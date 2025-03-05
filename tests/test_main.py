"""
Unit tests for the main workflow in main.py.

This module tests the integration of loading tickers, initializing the Finnhub API client,
fetching financial data, and displaying the results in a table. It uses mocking to simulate
dependencies and verify behavior under various scenarios, including successful execution,
no tickers, missing API key, and partial data fetching, ensuring the Stock and ETF Price
Tracker CLI tool functions as intended.
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


def test_main_success(capsys):
    """Test successful execution of the main workflow with valid tickers.

    Args:
        capsys: Pytest fixture to capture console output.

    Returns:
        None: Asserts that display_table is called with correct data and no errors are printed.
    """
    # Create a settings dictionary for the test
    test_settings = {
        "columns": {
            "eps": True,  # These values don't matter for the test assertion
            "pe_ratio": True,
            "dividend": False,
            "ytd_change": False,
            "ten_year_change": False,
        }
    }

    # Use patch as a context manager
    with patch(
        'main.load_settings', return_value=test_settings
    ) as mock_settings, patch(
        'main.load_tickers', return_value=["AAPL", "MSFT"]
    ) as mock_load, patch(
        'main.initialize_client', return_value=MagicMock()
    ) as mock_init, patch(
        'main.fetch_ticker_data', side_effect=[SAMPLE_AAPL, SAMPLE_MSFT]
    ) as mock_fetch, patch(
        'main.display_table'
    ) as mock_display:

        # Run the main function
        main()

        # Verify display_table is called with the aggregated data and the mocked settings
        mock_display.assert_called_once_with([SAMPLE_AAPL, SAMPLE_MSFT], test_settings)
    captured = capsys.readouterr()
    # No error messages should be printed in success case
    assert captured.out == ""


def test_main_no_tickers(capsys):
    """Test main workflow when no tickers are provided.

    Args:
        capsys: Pytest fixture to capture console output.

    Returns:
        None: Asserts error message is printed and no further functions are called.
    """
    # Use patch as a context manager
    with patch('main.load_settings') as mock_settings, patch(
        'main.load_tickers', return_value=[]
    ) as mock_load, patch('main.initialize_client') as mock_init, patch(
        'main.fetch_ticker_data'
    ) as mock_fetch, patch(
        'main.display_table'
    ) as mock_display:

        # Run the main function
        main()

        captured = capsys.readouterr()
        # Check for error message from main.py
        assert "No tickers to process" in captured.out
        # Ensure subsequent functions are not called
        mock_init.assert_not_called()
        mock_fetch.assert_not_called()
        mock_display.assert_not_called()


def test_main_missing_api_key(capsys):
    """Test main workflow when the API key is missing.

    Args:
        capsys: Pytest fixture to capture console output.

    Returns:
        None: Asserts error message is printed and no further functions are called.
    """
    # Use patch as a context manager
    with patch('main.load_settings') as mock_settings, patch(
        'main.load_tickers', return_value=["AAPL"]
    ) as mock_load, patch(
        'main.initialize_client',
        side_effect=ValueError("FINNHUB_API_KEY environment variable is not set."),
    ) as mock_init, patch(
        'main.fetch_ticker_data'
    ) as mock_fetch, patch(
        'main.display_table'
    ) as mock_display:

        # Run the main function
        main()

        captured = capsys.readouterr()
        # Check for specific error message from initialize_client via main.py
        assert "Error: FINNHUB_API_KEY environment variable is not set." in captured.out
        # Ensure data fetching and display are not called
        mock_fetch.assert_not_called()
        mock_display.assert_not_called()


def test_main_partial_data(capsys):
    """Test main workflow with a mix of valid and invalid tickers.

    Args:
        capsys: Pytest fixture to capture console output.

    Returns:
        None: Asserts display_table is called with mixed data and no errors are printed.
    """
    # Create a settings dictionary for the test
    test_settings = {
        "columns": {
            "eps": True,  # These values don't matter for the test assertion
            "pe_ratio": True,
            "dividend": False,
            "ytd_change": False,
            "ten_year_change": False,
        }
    }

    # Use patch as a context manager
    with patch(
        'main.load_settings', return_value=test_settings
    ) as mock_settings, patch(
        'main.load_tickers', return_value=["AAPL", "XYZ", "MSFT"]
    ) as mock_load, patch(
        'main.initialize_client', return_value=MagicMock()
    ) as mock_init, patch(
        'main.fetch_ticker_data',
        side_effect=[
            SAMPLE_AAPL,
            INVALID_XYZ,
            SAMPLE_MSFT,
        ],
    ) as mock_fetch, patch(
        'main.display_table'
    ) as mock_display:

        # Run the main function
        main()

        # Verify display_table is called with all data, including invalid ticker and the mocked settings
        mock_display.assert_called_once_with(
            [SAMPLE_AAPL, INVALID_XYZ, SAMPLE_MSFT], test_settings
        )
    captured = capsys.readouterr()
    # No error messages should be printed; invalid ticker is handled in data
    assert captured.out == ""
