"""
Unit tests for the finnhub_client module.

This module tests the API interaction and data processing functions in finnhub_client.py,
including get_quote, get_profile, get_financials, get_ytd_price, get_ten_year_price,
calculate_changes, and fetch_ticker_data. The tests use mocking to simulate Finnhub API responses
and verify behavior under various conditions, including successful data retrieval and edge cases.
"""

from unittest.mock import MagicMock, patch

import finnhub
import pytest
from finnhub_client import (
    calculate_changes,
    fetch_ticker_data,
    get_financials,
    get_profile,
    get_quote,
    get_ten_year_price,
    get_ytd_price,
)

SAMPLE_SETTINGS = {
    "columns": {
        "eps": True,
        "pe_ratio": True,
        "dividend": True,
        "ytd_change": True,
        "ten_year_change": True,
    }
}


def test_get_quote_success():
    """Tests successful retrieval of quote data.

    Returns:
        None: Asserts quote data is returned correctly.
    """
    mock_client = MagicMock()
    mock_client.quote.return_value = {'c': 100.0, 'pc': 99.0}
    result = get_quote(mock_client, 'AAPL')
    assert result == {'c': 100.0, 'pc': 99.0}
    mock_client.quote.assert_called_once_with('AAPL')


def test_get_quote_failure():
    """Tests quote retrieval failure handling.

    Returns:
        None: Asserts None is returned on API exception.
    """
    mock_response = MagicMock()
    mock_response.json.return_value = {'error': 'API Error'}
    mock_client = MagicMock()
    mock_client.quote.side_effect = finnhub.FinnhubAPIException(mock_response)
    result = get_quote(mock_client, 'INVALID')
    assert result is None
    mock_client.quote.assert_called_once_with('INVALID')


def test_get_profile_success():
    """Tests successful retrieval of company profile name.

    Returns:
        None: Asserts company name is returned correctly.
    """
    mock_client = MagicMock()
    mock_client.company_profile2.return_value = {'name': 'Apple Inc.'}
    result = get_profile(mock_client, 'AAPL')
    assert result == 'Apple Inc.'
    mock_client.company_profile2.assert_called_once_with(symbol='AAPL')


def test_get_profile_failure():
    """Tests profile retrieval failure handling.

    Returns:
        None: Asserts None is returned on API exception.
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
    """Tests handling of profile data missing the name key.

    Returns:
        None: Asserts None is returned when name is absent.
    """
    mock_client = MagicMock()
    mock_client.company_profile2.return_value = {'other': 'data'}
    result = get_profile(mock_client, 'AAPL')
    assert result is None
    mock_client.company_profile2.assert_called_once_with(symbol='AAPL')


def test_get_financials_success():
    """Tests successful retrieval of financial metrics.

    Returns:
        None: Asserts financial data is returned correctly.
    """
    mock_client = MagicMock()
    mock_client.company_basic_financials.return_value = {
        'metric': {'epsTTM': 5.89, 'peTTM': 24.70, 'currentDividendYieldTTM': 0.85}
    }
    result = get_financials(mock_client, 'AAPL')
    assert result == {'eps': 5.89, 'pe': 24.70, 'dividend': 0.85}
    mock_client.company_basic_financials.assert_called_once_with('AAPL', 'all')


def test_get_financials_failure():
    """Tests financials retrieval failure handling.

    Returns:
        None: Asserts None is returned on API exception.
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
    """Tests handling of partial financial metrics.

    Returns:
        None: Asserts missing metrics are None.
    """
    mock_client = MagicMock()
    mock_client.company_basic_financials.return_value = {
        'metric': {'epsTTM': 5.89, 'currentDividendYieldTTM': 0.85}
    }
    result = get_financials(mock_client, 'AAPL')
    assert result == {'eps': 5.89, 'pe': None, 'dividend': 0.85}
    mock_client.company_basic_financials.assert_called_once_with('AAPL', 'all')


def test_get_financials_no_metric():
    """Tests handling of missing metric key in financials.

    Returns:
        None: Asserts all metrics are None.
    """
    mock_client = MagicMock()
    mock_client.company_basic_financials.return_value = {}
    result = get_financials(mock_client, 'AAPL')
    assert result == {'eps': None, 'pe': None, 'dividend': None}
    mock_client.company_basic_financials.assert_called_once_with('AAPL', 'all')


def test_get_ytd_price_success():
    """Tests successful retrieval of YTD price.

    Returns:
        None: Asserts first closing price is returned.
    """
    mock_client = MagicMock()
    mock_client.stock_candles.return_value = {'s': 'ok', 'c': [100.0, 101.0, 102.0]}
    result = get_ytd_price(mock_client, 'AAPL')
    assert result == 100.0
    mock_client.stock_candles.assert_called_once()


def test_get_ytd_price_failure():
    """Tests YTD price retrieval failure handling.

    Returns:
        None: Asserts None is returned on API exception.
    """
    mock_response = MagicMock()
    mock_response.json.return_value = {'error': 'API Error'}
    mock_client = MagicMock()
    mock_client.stock_candles.side_effect = finnhub.FinnhubAPIException(mock_response)
    result = get_ytd_price(mock_client, 'INVALID')
    assert result is None
    mock_client.stock_candles.assert_called_once()


def test_get_ytd_price_no_data():
    """Tests handling of no YTD price data.

    Returns:
        None: Asserts None is returned for no_data or empty list.
    """
    mock_client = MagicMock()
    mock_client.stock_candles.return_value = {'s': 'no_data'}
    result = get_ytd_price(mock_client, 'AAPL')
    assert result is None
    mock_client.stock_candles.assert_called_once()

    mock_client.stock_candles.reset_mock()
    mock_client.stock_candles.return_value = {'s': 'ok', 'c': []}
    result = get_ytd_price(mock_client, 'AAPL')
    assert result is None
    mock_client.stock_candles.assert_called_once()


def test_get_ten_year_price_success():
    """Tests successful retrieval of 10-year price.

    Returns:
        None: Asserts first closing price is returned.
    """
    mock_client = MagicMock()
    mock_client.stock_candles.return_value = {'s': 'ok', 'c': [50.0, 51.0, 52.0]}
    result = get_ten_year_price(mock_client, 'AAPL')
    assert result == 50.0
    mock_client.stock_candles.assert_called_once()


def test_get_ten_year_price_failure():
    """Tests 10-year price retrieval failure handling.

    Returns:
        None: Asserts None is returned on API exception.
    """
    mock_response = MagicMock()
    mock_response.json.return_value = {'error': 'API Error'}
    mock_client = MagicMock()
    mock_client.stock_candles.side_effect = finnhub.FinnhubAPIException(mock_response)
    result = get_ten_year_price(mock_client, 'INVALID')
    assert result is None
    mock_client.stock_candles.assert_called_once()


def test_get_ten_year_price_no_data():
    """Tests handling of no 10-year price data.

    Returns:
        None: Asserts None is returned for no_data or empty list.
    """
    mock_client = MagicMock()
    mock_client.stock_candles.return_value = {'s': 'no_data'}
    result = get_ten_year_price(mock_client, 'AAPL')
    assert result is None
    mock_client.stock_candles.assert_called_once()

    mock_client.stock_candles.reset_mock()
    mock_client.stock_candles.return_value = {'s': 'ok', 'c': []}
    result = get_ten_year_price(mock_client, 'AAPL')
    assert result is None
    mock_client.stock_candles.assert_called_once()


def test_calculate_changes_success():
    """Tests successful calculation of all percentage changes.

    Returns:
        None: Asserts changes are calculated correctly.
    """
    quote = {'c': 100.0, 'pc': 99.0}
    ytd_price = 90.0
    ten_year_price = 50.0
    daily, ytd, ten_year = calculate_changes(quote, ytd_price, ten_year_price)
    assert daily == pytest.approx(1.010101, abs=0.0001)
    assert ytd == pytest.approx(11.111111, abs=0.0001)
    assert ten_year == pytest.approx(100.0, abs=0.0001)


def test_calculate_changes_missing_quote():
    """Tests handling of missing quote data.

    Returns:
        None: Asserts all changes are None.
    """
    daily, ytd, ten_year = calculate_changes(None, 90.0, 50.0)
    assert daily is None
    assert ytd is None
    assert ten_year is None


def test_calculate_changes_missing_ytd():
    """Tests handling of missing YTD price.

    Returns:
        None: Asserts YTD change is None, others calculated.
    """
    quote = {'c': 100.0, 'pc': 99.0}
    daily, ytd, ten_year = calculate_changes(quote, None, 50.0)
    assert daily == pytest.approx(1.010101, abs=0.0001)
    assert ytd is None
    assert ten_year == pytest.approx(100.0, abs=0.0001)


def test_calculate_changes_missing_ten_year():
    """Tests handling of missing 10-year price.

    Returns:
        None: Asserts 10-year change is None, others calculated.
    """
    quote = {'c': 100.0, 'pc': 99.0}
    daily, ytd, ten_year = calculate_changes(quote, 90.0, None)
    assert daily == pytest.approx(1.010101, abs=0.0001)
    assert ytd == pytest.approx(11.111111, abs=0.0001)
    assert ten_year is None


def test_calculate_changes_zero_previous_close():
    """Tests handling of zero previous close price.

    Returns:
        None: Asserts daily change is None, others calculated.
    """
    quote = {'c': 100.0, 'pc': 0.0}
    daily, ytd, ten_year = calculate_changes(quote, 90.0, 50.0)
    assert daily is None
    assert ytd == pytest.approx(11.111111, abs=0.0001)
    assert ten_year == pytest.approx(100.0, abs=0.0001)


def test_calculate_changes_zero_ytd_price():
    """Tests handling of zero YTD price.

    Returns:
        None: Asserts YTD change is None, others calculated.
    """
    quote = {'c': 100.0, 'pc': 99.0}
    daily, ytd, ten_year = calculate_changes(quote, 0.0, 50.0)
    assert daily == pytest.approx(1.010101, abs=0.0001)
    assert ytd is None
    assert ten_year == pytest.approx(100.0, abs=0.0001)


def test_calculate_changes_zero_ten_year_price():
    """Tests handling of zero 10-year price.

    Returns:
        None: Asserts 10-year change is None, others calculated.
    """
    quote = {'c': 100.0, 'pc': 99.0}
    daily, ytd, ten_year = calculate_changes(quote, 90.0, 0.0)
    assert daily == pytest.approx(1.010101, abs=0.0001)
    assert ytd == pytest.approx(11.111111, abs=0.0001)
    assert ten_year is None


def test_calculate_changes_missing_current_price():
    """Tests handling of missing current price.

    Returns:
        None: Asserts all changes are None.
    """
    quote = {'pc': 99.0}
    daily, ytd, ten_year = calculate_changes(quote, 90.0, 50.0)
    assert daily is None
    assert ytd is None
    assert ten_year is None


def test_calculate_changes_missing_previous_close():
    """Tests handling of missing previous close.

    Returns:
        None: Asserts daily change is None, others calculated.
    """
    quote = {'c': 100.0}
    daily, ytd, ten_year = calculate_changes(quote, 90.0, 50.0)
    assert daily is None
    assert ytd == pytest.approx(11.111111, abs=0.0001)
    assert ten_year == pytest.approx(100.0, abs=0.0001)


def test_fetch_ticker_data_with_user_name():
    """Tests fetch_ticker_data with a user-provided name.

    Returns:
        None: Asserts user-provided name is used.
    """
    with patch("finnhub_client.get_quote", return_value={"c": 100.0, "pc": 99.0}):
        result = fetch_ticker_data(
            MagicMock(), {"ticker": "AAPL", "name": "Apple Inc."}, SAMPLE_SETTINGS
        )
        assert result["company_name"] == "Apple Inc."


def test_fetch_ticker_data_without_user_name():
    """Tests fetch_ticker_data falling back to API name when user name is None.

    Returns:
        None: Asserts API-provided name is used.
    """
    with patch(
        "finnhub_client.get_quote", return_value={"c": 100.0, "pc": 99.0}
    ), patch("finnhub_client.get_profile", return_value="Apple Inc."):
        result = fetch_ticker_data(
            MagicMock(), {"ticker": "AAPL", "name": None}, SAMPLE_SETTINGS
        )
        assert result["company_name"] == "Apple Inc."


def test_fetch_ticker_data_no_name():
    """Tests fetch_ticker_data when no name is available.

    Returns:
        None: Asserts company_name is None when both user and API names are unavailable.
    """
    with patch(
        "finnhub_client.get_quote", return_value={"c": 100.0, "pc": 99.0}
    ), patch("finnhub_client.get_profile", return_value=None):
        result = fetch_ticker_data(
            MagicMock(), {"ticker": "AAPL", "name": None}, SAMPLE_SETTINGS
        )
        assert result["company_name"] is None


def test_fetch_ticker_data_invalid_ticker():
    """Tests fetch_ticker_data with an invalid ticker.

    Returns:
        None: Asserts error message is returned.
    """
    with patch("finnhub_client.get_quote", return_value=None):
        result = fetch_ticker_data(
            MagicMock(), {"ticker": "INVALID", "name": None}, SAMPLE_SETTINGS
        )
        assert result == {"ticker": "INVALID", "message": "Data unavailable"}
