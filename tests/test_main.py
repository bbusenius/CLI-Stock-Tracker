"""
Unit tests for the main workflow in main.py.

This module tests the integration of loading tickers, initializing the Finnhub API client,
fetching financial data, caching, and displaying results. It uses mocking to simulate
dependencies and verify behavior under various scenarios, including caching, the --refresh option,
and watch mode with real-time updates.
"""

from unittest.mock import MagicMock, patch

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

# Additional sample static data for watch mode tests
SAMPLE_STATIC_AAPL = {
    "ticker": "AAPL",
    "company_name": "Apple Inc.",
    "pc": 145.0,
    "initial_current_price": 150.0,
    "eps": 5.89,
    "pe_ratio": 24.70,
    "dividend": 0.85,
    "ytd_price": 130.0,
    "ten_year_price": 50.0,
}

SAMPLE_STATIC_MSFT = {
    "ticker": "MSFT",
    "company_name": "Microsoft",
    "pc": 280.0,
    "initial_current_price": 285.0,
    "eps": 8.05,
    "pe_ratio": 34.80,
    "dividend": 1.00,
    "ytd_price": 250.0,
    "ten_year_price": 100.0,
}


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
        None: Asserts fresh data is fetched despite cache and cache is updated.
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


def test_watch_mode():
    """Test watch mode with real-time updates.

    Verifies that watch mode starts the websocket, fetches static data once, and updates the display
    with real-time prices at the default interval.
    """
    with patch(
        "main.load_settings",
        return_value={
            "columns": {},
            "cache": {"enabled": False, "interval": 60},
            "watch_interval": 5,
        },
    ), patch(
        "main.load_tickers",
        return_value=[
            {"ticker": "AAPL", "name": None},
            {"ticker": "MSFT", "name": None},
        ],
    ), patch(
        "main.initialize_client", return_value=MagicMock()
    ), patch(
        "main.start_websocket"
    ) as mock_start_ws, patch(
        "main.fetch_static_data", side_effect=[SAMPLE_STATIC_AAPL, SAMPLE_STATIC_MSFT]
    ) as mock_fetch_static, patch(
        "main.get_latest_price", side_effect=[151.0, 286.0, 152.0, 287.0]
    ), patch(
        "main.display_table"
    ) as mock_display, patch(
        "time.sleep"
    ) as mock_sleep, patch(
        "sys.argv", ["main.py", "--watch"]
    ), patch(
        "os.getenv", return_value="dummy_key"
    ):

        def display_side_effect(*args, **kwargs):
            display_side_effect.call_count += 1
            if display_side_effect.call_count >= 2:
                raise KeyboardInterrupt

        display_side_effect.call_count = 0
        mock_display.side_effect = display_side_effect
        main()
        mock_start_ws.assert_called_once_with(["AAPL", "MSFT"], "dummy_key")
        assert mock_fetch_static.call_count == 2
        assert mock_display.call_count == 2
        call1 = mock_display.call_args_list[0]
        data1 = call1[0][0]
        assert data1[0]["current_price"] == 151.0
        assert data1[1]["current_price"] == 286.0
        call2 = mock_display.call_args_list[1]
        data2 = call2[0][0]
        assert data2[0]["current_price"] == 152.0
        assert data2[1]["current_price"] == 287.0
        mock_sleep.assert_called_with(5)


def test_watch_mode_with_interval():
    """Test watch mode with a custom interval.

    Verifies that the --interval argument overrides the settings interval.
    """
    with patch(
        "main.load_settings",
        return_value={
            "columns": {},
            "cache": {"enabled": False, "interval": 60},
            "watch_interval": 5,
        },
    ), patch(
        "main.load_tickers", return_value=[{"ticker": "AAPL", "name": None}]
    ), patch(
        "main.initialize_client", return_value=MagicMock()
    ), patch(
        "main.start_websocket"
    ), patch(
        "main.fetch_static_data", return_value=SAMPLE_STATIC_AAPL
    ), patch(
        "main.get_latest_price", return_value=151.0
    ), patch(
        "main.display_table"
    ) as mock_display, patch(
        "time.sleep"
    ) as mock_sleep, patch(
        "sys.argv", ["main.py", "--watch", "--interval", "10"]
    ), patch(
        "os.getenv", return_value="dummy_key"
    ):
        mock_display.side_effect = [None, KeyboardInterrupt]
        main()
        mock_sleep.assert_called_with(10)


# File: tests/test_main.py (only showing the changed test)
def test_watch_mode_invalid_interval():
    """Test watch mode with an invalid interval, falling back to settings.

    Verifies that an invalid --interval triggers a warning and uses the settings value.
    """
    with patch(
        "main.load_settings",
        return_value={
            "columns": {},
            "cache": {"enabled": False, "interval": 60},
            "watch_interval": 5,
        },
    ), patch(
        "main.load_tickers", return_value=[{"ticker": "AAPL", "name": None}]
    ), patch(
        "main.initialize_client", return_value=MagicMock()
    ), patch(
        "main.start_websocket"
    ), patch(
        "main.fetch_static_data", return_value=SAMPLE_STATIC_AAPL
    ), patch(
        "main.get_latest_price", return_value=151.0
    ), patch(
        "main.display_table"
    ) as mock_display, patch(
        "time.sleep"
    ) as mock_sleep, patch(
        "sys.argv", ["main.py", "--watch", "--interval", "0"]
    ), patch(
        "main.rprint"
    ) as mock_rprint, patch(
        "os.getenv", return_value="dummy_key"
    ):
        # Allow one display call before interrupting
        mock_display.side_effect = [None, KeyboardInterrupt]
        main()
        mock_rprint.assert_any_call(
            "\n[yellow]Warning: Interval must be positive. Using settings value.[/yellow]"
        )
        mock_sleep.assert_called_with(5)
