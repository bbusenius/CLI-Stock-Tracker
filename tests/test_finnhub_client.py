"""
Unit tests for the finnhub_client module.

This module contains tests for the API interaction functions in finnhub_client.py,
specifically focusing on the get_quote and get_profile functions. The tests use
mocking to simulate Finnhub API responses and verify the behavior of these functions
under various conditions, including successful data retrieval and error scenarios.
"""

from unittest.mock import MagicMock

import finnhub
from finnhub_client import get_profile, get_quote


def test_get_quote_success():
    """
    Test that get_quote returns the quote data when the API call is successful.

    Args:
        None

    Returns:
        None: Asserts the expected behavior of get_quote with a successful API response.
    """
    # Create a mock client
    mock_client = MagicMock()
    mock_client.quote.return_value = {'c': 100.0, 'pc': 99.0}

    # Call the function
    result = get_quote(mock_client, 'AAPL')

    # Assertions
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
    # Create a mock response with a json method
    mock_response = MagicMock()
    mock_response.json.return_value = {'error': 'API Error'}

    # Create a mock client
    mock_client = MagicMock()
    # Set side effect to raise FinnhubAPIException with the mock response
    mock_client.quote.side_effect = finnhub.FinnhubAPIException(mock_response)

    # Call the function
    result = get_quote(mock_client, 'INVALID')

    # Assertions
    assert result is None
    mock_client.quote.assert_called_once_with('INVALID')


def test_get_profile_success():
    """
    Test that get_profile returns the company name when the API call is successful.

    Args:
        None

    Returns:
        None: Asserts that get_profile extracts and returns the company name correctly.
    """
    # Create a mock client
    mock_client = MagicMock()
    mock_client.company_profile2.return_value = {'name': 'Apple Inc.'}

    # Call the function
    result = get_profile(mock_client, 'AAPL')

    # Assertions
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
    # Create a mock response with a json method
    mock_response = MagicMock()
    mock_response.json.return_value = {'error': 'API Error'}

    # Create a mock client
    mock_client = MagicMock()
    # Set side effect to raise FinnhubAPIException with the mock response
    mock_client.company_profile2.side_effect = finnhub.FinnhubAPIException(
        mock_response
    )

    # Call the function
    result = get_profile(mock_client, 'INVALID')

    # Assertions
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
    # Create a mock client
    mock_client = MagicMock()
    mock_client.company_profile2.return_value = {'other': 'data'}

    # Call the function
    result = get_profile(mock_client, 'AAPL')

    # Assertions
    assert result is None
    mock_client.company_profile2.assert_called_once_with(symbol='AAPL')
