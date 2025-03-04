"""
Unit tests for the finnhub_client module.

This module contains tests for the API interaction functions in finnhub_client.py,
including get_quote, get_profile, get_financials, get_ytd_price, and get_ten_year_price.
The tests use mocking to simulate Finnhub API responses and verify the behavior of these
functions under various conditions, including successful data retrieval, error scenarios,
and edge cases with missing or invalid data.
"""

from unittest.mock import MagicMock

import finnhub
from finnhub_client import (
    get_financials,
    get_profile,
    get_quote,
    get_ten_year_price,
    get_ytd_price,
)


# Existing tests for get_quote
def test_get_quote_success():
    """
    Test that get_quote returns the quote data when the API call is successful.

    Args:
        None

    Returns:
        None: Asserts the expected behavior of get_quote with a successful API response.
    """
    mock_client = MagicMock()
    mock_client.quote.return_value = {'c': 100.0, 'pc': 99.0}
    result = get_quote(mock_client, 'AAPL')
    assert result == {'c': 100.0, 'pc': 99.0}
    mock_client.quote.assert_called_once_with('AAPL')


def test_get_quote_failure():
    """
    Test that get_quote returns None when the API call raises a FinnhubAPIException.

    Args:
        None

    Returns:
        None: Asserts that get_quote handles API errors by returning None.
    """
    mock_response = MagicMock()
    mock_response.json.return_value = {'error': 'API Error'}
    mock_client = MagicMock()
    mock_client.quote.side_effect = finnhub.FinnhubAPIException(mock_response)
    result = get_quote(mock_client, 'INVALID')
    assert result is None
    mock_client.quote.assert_called_once_with('INVALID')


# Existing tests for get_profile
def test_get_profile_success():
    """
    Test that get_profile returns the company name when the API call is successful.

    Args:
        None

    Returns:
        None: Asserts that get_profile extracts and returns the company name correctly.
    """
    mock_client = MagicMock()
    mock_client.company_profile2.return_value = {'name': 'Apple Inc.'}
    result = get_profile(mock_client, 'AAPL')
    assert result == 'Apple Inc.'
    mock_client.company_profile2.assert_called_once_with(symbol='AAPL')


def test_get_profile_failure():
    """
    Test that get_profile returns None when the API call raises a FinnhubAPIException.

    Args:
        None

    Returns:
        None: Asserts that get_profile handles API errors by returning None.
    """
    mock_response = MagicMock()
    mock_response.json.return_value = {'error': 'API Error'}
    mock_client = MagicMock()
    mock_client.company_profile2.side_effect = finnhub.FinnhubAPIException(
        mock_response
    )
    result = get_profile(mock_client, 'INVALID')
    assert result is None
    mock_client.company_profile2.assert_called_once_with(symbol='INVALID')


def test_get_profile_missing_name():
    """
    Test that get_profile returns None when the profile data does not contain a 'name' key.

    Args:
        None

    Returns:
        None: Asserts that get_profile handles missing 'name' keys gracefully.
    """
    mock_client = MagicMock()
    mock_client.company_profile2.return_value = {'other': 'data'}
    result = get_profile(mock_client, 'AAPL')
    assert result is None
    mock_client.company_profile2.assert_called_once_with(symbol='AAPL')


# Tests for get_financials
def test_get_financials_success():
    """
    Test that get_financials returns financial metrics when the API call is successful.

    Args:
        None

    Returns:
        None: Asserts that get_financials extracts EPS, PE, and dividend correctly.
    """
    mock_client = MagicMock()
    mock_client.company_basic_financials.return_value = {
        'metric': {'epsTTM': 5.89, 'peTTM': 24.70, 'dividendYieldTTM': 0.85}
    }
    result = get_financials(mock_client, 'AAPL')
    assert result == {'eps': 5.89, 'pe': 24.70, 'dividend': 0.85}
    mock_client.company_basic_financials.assert_called_once_with('AAPL', 'all')


def test_get_financials_failure():
    """
    Test that get_financials returns None when the API call raises a FinnhubAPIException.

    Args:
        None

    Returns:
        None: Asserts that get_financials handles API errors by returning None.
    """
    mock_response = MagicMock()
    mock_response.json.return_value = {'error': 'API Error'}
    mock_client = MagicMock()
    mock_client.company_basic_financials.side_effect = finnhub.FinnhubAPIException(
        mock_response
    )
    result = get_financials(mock_client, 'INVALID')
    assert result is None
    mock_client.company_basic_financials.assert_called_once_with('INVALID', 'all')


def test_get_financials_missing_metrics():
    """
    Test that get_financials returns None for missing metrics in the API response.

    Args:
        None

    Returns:
        None: Asserts that get_financials handles partial metric data gracefully.
    """
    mock_client = MagicMock()
    mock_client.company_basic_financials.return_value = {
        'metric': {
            'epsTTM': 5.89,
            # 'peTTM' is missing
            'dividendYieldTTM': 0.85,
        }
    }
    result = get_financials(mock_client, 'AAPL')
    assert result == {'eps': 5.89, 'pe': None, 'dividend': 0.85}
    mock_client.company_basic_financials.assert_called_once_with('AAPL', 'all')


def test_get_financials_no_metric():
    """
    Test that get_financials returns None for all metrics when 'metric' key is missing.

    Args:
        None

    Returns:
        None: Asserts that get_financials handles an empty or missing 'metric' dictionary.
    """
    mock_client = MagicMock()
    mock_client.company_basic_financials.return_value = {}
    result = get_financials(mock_client, 'AAPL')
    assert result == {'eps': None, 'pe': None, 'dividend': None}
    mock_client.company_basic_financials.assert_called_once_with('AAPL', 'all')


# Tests for get_ytd_price
def test_get_ytd_price_success():
    """
    Test that get_ytd_price returns the first closing price when the API call is successful.

    Args:
        None

    Returns:
        None: Asserts that get_ytd_price extracts the YTD price correctly.
    """
    mock_client = MagicMock()
    mock_client.stock_candles.return_value = {'s': 'ok', 'c': [100.0, 101.0, 102.0]}
    result = get_ytd_price(mock_client, 'AAPL')
    assert result == 100.0
    mock_client.stock_candles.assert_called_once()


def test_get_ytd_price_failure():
    """
    Test that get_ytd_price returns None when the API call raises a FinnhubAPIException.

    Args:
        None

    Returns:
        None: Asserts that get_ytd_price handles API errors by returning None.
    """
    mock_response = MagicMock()
    mock_response.json.return_value = {'error': 'API Error'}
    mock_client = MagicMock()
    mock_client.stock_candles.side_effect = finnhub.FinnhubAPIException(mock_response)
    result = get_ytd_price(mock_client, 'INVALID')
    assert result is None
    mock_client.stock_candles.assert_called_once()


def test_get_ytd_price_no_data():
    """
    Test that get_ytd_price returns None when no data is available.

    Args:
        None

    Returns:
        None: Asserts that get_ytd_price handles 'no_data' status or empty price list.
    """
    mock_client = MagicMock()
    # Test with 'no_data' status
    mock_client.stock_candles.return_value = {'s': 'no_data'}
    result = get_ytd_price(mock_client, 'AAPL')
    assert result is None
    mock_client.stock_candles.assert_called_once()

    # Reset mock to clear previous call state
    mock_client.stock_candles.reset_mock()

    # Test with empty price list
    mock_client.stock_candles.return_value = {'s': 'ok', 'c': []}
    result = get_ytd_price(mock_client, 'AAPL')
    assert result is None
    mock_client.stock_candles.assert_called_once()


# Tests for get_ten_year_price
def test_get_ten_year_price_success():
    """
    Test that get_ten_year_price returns the first closing price when the API call is successful.

    Args:
        None

    Returns:
        None: Asserts that get_ten_year_price extracts the 10-year price correctly.
    """
    mock_client = MagicMock()
    mock_client.stock_candles.return_value = {'s': 'ok', 'c': [50.0, 51.0, 52.0]}
    result = get_ten_year_price(mock_client, 'AAPL')
    assert result == 50.0
    mock_client.stock_candles.assert_called_once()


def test_get_ten_year_price_failure():
    """
    Test that get_ten_year_price returns None when the API call raises a FinnhubAPIException.

    Args:
        None

    Returns:
        None: Asserts that get_ten_year_price handles API errors by returning None.
    """
    mock_response = MagicMock()
    mock_response.json.return_value = {'error': 'API Error'}
    mock_client = MagicMock()
    mock_client.stock_candles.side_effect = finnhub.FinnhubAPIException(mock_response)
    result = get_ten_year_price(mock_client, 'INVALID')
    assert result is None
    mock_client.stock_candles.assert_called_once()


def test_get_ten_year_price_no_data():
    """
    Test that get_ten_year_price returns None when no data is available.

    Args:
        None

    Returns:
        None: Asserts that get_ten_year_price handles 'no_data' status or empty price list.
    """
    mock_client = MagicMock()
    # Test with 'no_data' status
    mock_client.stock_candles.return_value = {'s': 'no_data'}
    result = get_ten_year_price(mock_client, 'AAPL')
    assert result is None
    mock_client.stock_candles.assert_called_once()

    # Reset mock to clear previous call state
    mock_client.stock_candles.reset_mock()

    # Test with empty price list
    mock_client.stock_candles.return_value = {'s': 'ok', 'c': []}
    result = get_ten_year_price(mock_client, 'AAPL')
    assert result is None
    mock_client.stock_candles.assert_called_once()
