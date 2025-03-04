"""
Unit tests for the main workflow in main.py.

This module tests the integration of loading tickers, initializing the Finnhub API client,
fetching financial data, and displaying the results in a table. It uses mocking to simulate
dependencies and verify behavior under various scenarios, including successful execution,
no tickers, missing API key, and partial data fetching, ensuring the Stock and ETF Price
Tracker CLI tool functions as intended.
"""

from unittest.mock import patch, MagicMock

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


@patch('main.display_table')
@patch('main.fetch_ticker_data')
@patch('main.initialize_client')
@patch('main.load_tickers')
def test_main_success(mock_load, mock_init, mock_fetch, mock_display, capsys):
    """Test successful execution of the main workflow with valid tickers.

    Args:
        mock_load (MagicMock): Mock for config.load_tickers function.
        mock_init (MagicMock): Mock for finnhub_client.initialize_client function.
        mock_fetch (MagicMock): Mock for finnhub_client.fetch_ticker_data function.
        mock_display (MagicMock): Mock for display.display_table function.
        capsys: Pytest fixture to capture console output.

    Returns:
        None: Asserts that display_table is called with correct data and no errors are printed.
    """
    # Setup mocks: Simulate two valid tickers with sample data
    mock_load.return_value = ["AAPL", "MSFT"]
    mock_init.return_value = MagicMock()  # Mock client object
    # Return data for each ticker
    mock_fetch.side_effect = [SAMPLE_AAPL, SAMPLE_MSFT]
    main()
    # Verify display_table is called with the aggregated data
    mock_display.assert_called_once_with([SAMPLE_AAPL, SAMPLE_MSFT])
    captured = capsys.readouterr()
    # No error messages should be printed in success case
    assert captured.out == ""


@patch('main.display_table')
@patch('main.fetch_ticker_data')
@patch('main.initialize_client')
@patch('main.load_tickers')
def test_main_no_tickers(mock_load, mock_init, mock_fetch, mock_display, capsys):
    """Test main workflow when no tickers are provided.

    Args:
        mock_load (MagicMock): Mock for config.load_tickers function.
        mock_init (MagicMock): Mock for finnhub_client.initialize_client function.
        mock_fetch (MagicMock): Mock for finnhub_client.fetch_ticker_data function.
        mock_display (MagicMock): Mock for display.display_table function.
        capsys: Pytest fixture to capture console output.

    Returns:
        None: Asserts error message is printed and no further functions are called.
    """
    # Setup mock: Empty ticker list
    mock_load.return_value = []
    main()
    captured = capsys.readouterr()
    # Check for error message from main.py
    assert "No tickers to process" in captured.out
    # Ensure subsequent functions are not called
    mock_init.assert_not_called()
    mock_fetch.assert_not_called()
    mock_display.assert_not_called()


@patch('main.display_table')
@patch('main.fetch_ticker_data')
@patch('main.initialize_client')
@patch('main.load_tickers')
def test_main_missing_api_key(mock_load, mock_init, mock_fetch, mock_display, capsys):
    """Test main workflow when the API key is missing.

    Args:
        mock_load (MagicMock): Mock for config.load_tickers function.
        mock_init (MagicMock): Mock for finnhub_client.initialize_client function.
        mock_fetch (MagicMock): Mock for finnhub_client.fetch_ticker_data function.
        mock_display (MagicMock): Mock for display.display_table function.
        capsys: Pytest fixture to capture console output.

    Returns:
        None: Asserts error message is printed and no further functions are called.
    """
    # Setup mocks: Valid tickers, but client initialization fails
    mock_load.return_value = ["AAPL"]
    mock_init.side_effect = ValueError(
        "FINNHUB_API_KEY environment variable is not set."
    )
    main()
    captured = capsys.readouterr()
    # Check for specific error message from initialize_client via main.py
    assert "Error: FINNHUB_API_KEY environment variable is not set." in captured.out
    # Ensure data fetching and display are not called
    mock_fetch.assert_not_called()
    mock_display.assert_not_called()


@patch('main.display_table')
@patch('main.fetch_ticker_data')
@patch('main.initialize_client')
@patch('main.load_tickers')
def test_main_partial_data(mock_load, mock_init, mock_fetch, mock_display, capsys):
    """Test main workflow with a mix of valid and invalid tickers.

    Args:
        mock_load (MagicMock): Mock for config.load_tickers function.
        mock_init (MagicMock): Mock for finnhub_client.initialize_client function.
        mock_fetch (MagicMock): Mock for finnhub_client.fetch_ticker_data function.
        mock_display (MagicMock): Mock for display.display_table function.
        capsys: Pytest fixture to capture console output.

    Returns:
        None: Asserts display_table is called with mixed data and no errors are printed.
    """
    # Setup mocks: Mix of valid and invalid tickers
    mock_load.return_value = ["AAPL", "XYZ", "MSFT"]
    mock_init.return_value = MagicMock()  # Mock client object
    mock_fetch.side_effect = [
        SAMPLE_AAPL,
        INVALID_XYZ,
        SAMPLE_MSFT,
    ]  # Simulate partial success
    main()
    # Verify display_table is called with all data, including invalid ticker
    mock_display.assert_called_once_with([SAMPLE_AAPL, INVALID_XYZ, SAMPLE_MSFT])
    captured = capsys.readouterr()
    # No error messages should be printed; invalid ticker is handled in data
    assert captured.out == ""
