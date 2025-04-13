"""
Unit tests for the configuration module.

This module contains tests for the `config.py` module, specifically the `load_tickers` and `load_settings`
functions, which load a list of stock and ETF tickers and settings from JSON files. The tests verify that
the functions correctly handle various formats and edge cases, ensuring robust configuration management
for the Stock and ETF Price Tracker CLI tool.
"""

from unittest.mock import patch

from config import load_settings, load_tickers


@patch('config.rprint')
def test_load_tickers_strings(mock_rprint, tmp_path):
    """Tests loading a JSON file with a list of ticker strings (backward compatibility).

    Args:
        mock_rprint: Mocked rich.print function to verify no warnings/errors are printed.
        tmp_path: Pytest fixture providing a temporary directory.

    Returns:
        None: Asserts the expected ticker list is returned without warnings.
    """
    file_path = tmp_path / "tickers.json"
    file_path.write_text('["AAPL", "MSFT"]')
    tickers = load_tickers(str(file_path))
    assert tickers == [
        {"ticker": "AAPL", "name": None},
        {"ticker": "MSFT", "name": None},
    ]
    mock_rprint.assert_not_called()


@patch('config.rprint')
def test_load_tickers_objects(mock_rprint, tmp_path):
    """Tests loading a JSON file with a list of ticker objects including optional names.

    Args:
        mock_rprint: Mocked rich.print function to verify no warnings/errors are printed.
        tmp_path: Pytest fixture providing a temporary directory.

    Returns:
        None: Asserts the expected ticker list with names is returned without warnings.
    """
    file_path = tmp_path / "tickers.json"
    file_path.write_text(
        '[{"ticker": "AAPL", "name": "Apple Inc."}, {"ticker": "MSFT"}]'
    )
    tickers = load_tickers(str(file_path))
    assert tickers == [
        {"ticker": "AAPL", "name": "Apple Inc."},
        {"ticker": "MSFT", "name": None},
    ]
    mock_rprint.assert_not_called()


@patch('config.rprint')
def test_load_tickers_mixed(mock_rprint, tmp_path):
    """Tests loading a JSON file with a mix of ticker strings and objects.

    Args:
        mock_rprint: Mocked rich.print function to verify no warnings/errors are printed.
        tmp_path: Pytest fixture providing a temporary directory.

    Returns:
        None: Asserts the expected ticker list is returned without warnings.
    """
    file_path = tmp_path / "tickers.json"
    file_path.write_text('["AAPL", {"ticker": "MSFT", "name": "Microsoft Corp."}]')
    tickers = load_tickers(str(file_path))
    assert tickers == [
        {"ticker": "AAPL", "name": None},
        {"ticker": "MSFT", "name": "Microsoft Corp."},
    ]
    mock_rprint.assert_not_called()


@patch('config.rprint')
def test_load_tickers_invalid_entries(mock_rprint, tmp_path):
    """Tests handling of invalid entries in the ticker list, ensuring they are skipped.

    Args:
        mock_rprint: Mocked rich.print function to verify warning messages.
        tmp_path: Pytest fixture providing a temporary directory.

    Returns:
        None: Asserts valid tickers are returned and warnings are printed for invalid entries.
    """
    file_path = tmp_path / "tickers.json"
    file_path.write_text('["AAPL", {"name": "No Ticker"}, 123, {"ticker": "MSFT"}]')
    tickers = load_tickers(str(file_path))
    assert tickers == [
        {"ticker": "AAPL", "name": None},
        {"ticker": "MSFT", "name": None},
    ]
    assert mock_rprint.call_count == 2
    calls = mock_rprint.call_args_list
    assert "Warning: Invalid ticker entry {'name': 'No Ticker'}" in calls[0][0][0]
    assert "Warning: Invalid ticker entry 123" in calls[1][0][0]


@patch('config.rprint')
def test_load_tickers_missing_file(mock_rprint, tmp_path):
    """Tests handling of a missing JSON file.

    Args:
        mock_rprint: Mocked rich.print function to verify error message.
        tmp_path: Pytest fixture providing a temporary directory.

    Returns:
        None: Asserts an empty list is returned with an error message.
    """
    missing_file = tmp_path / "missing.json"
    tickers = load_tickers(str(missing_file))
    assert tickers == []
    mock_rprint.assert_called_once()
    args, _ = mock_rprint.call_args
    assert f"[red]Error loading tickers from {missing_file}:" in args[0]
    assert "No such file or directory" in args[0]


@patch('config.rprint')
def test_load_tickers_invalid_json(mock_rprint, tmp_path):
    """Tests handling of a file with invalid JSON content.

    Args:
        mock_rprint: Mocked rich.print function to verify error message.
        tmp_path: Pytest fixture providing a temporary directory.

    Returns:
        None: Asserts an empty list is returned with an error message.
    """
    file_path = tmp_path / "invalid.json"
    file_path.write_text('{ "key": value }')
    tickers = load_tickers(str(file_path))
    assert tickers == []
    mock_rprint.assert_called_once()
    args, _ = mock_rprint.call_args
    assert f"[red]Error loading tickers from {file_path}:" in args[0]
    assert "Expecting value" in args[0]


@patch('config.rprint')
def test_load_tickers_non_list(mock_rprint, tmp_path):
    """Tests handling of a JSON file that does not contain a list.

    Args:
        mock_rprint: Mocked rich.print function to verify error message.
        tmp_path: Pytest fixture providing a temporary directory.

    Returns:
        None: Asserts an empty list is returned with an error message.
    """
    file_path = tmp_path / "non_list.json"
    file_path.write_text('{"tickers": ["AAPL", "MSFT"]}')
    tickers = load_tickers(str(file_path))
    assert tickers == []
    mock_rprint.assert_called_once()
    args, _ = mock_rprint.call_args
    assert f"[red]Error loading tickers from {file_path}:" in args[0]
    assert "Tickers must be a list" in args[0]


def test_load_settings_watch_interval(tmp_path):
    """Test loading watch_interval from settings.json.

    Args:
        tmp_path: Pytest fixture providing a temporary directory.

    Returns:
        None: Asserts watch_interval is loaded correctly when valid.
    """
    file_path = tmp_path / "settings.json"
    file_path.write_text('{"watch_interval": 10}')
    settings = load_settings(str(file_path))
    assert settings["watch_interval"] == 10


def test_load_settings_watch_interval_invalid(tmp_path):
    """Test handling invalid watch_interval in settings.json.

    Args:
        tmp_path: Pytest fixture providing a temporary directory.

    Returns:
        None: Asserts default value is used with a warning for invalid input.
    """
    file_path = tmp_path / "settings.json"
    file_path.write_text('{"watch_interval": "invalid"}')
    with patch('config.rprint') as mock_rprint:
        settings = load_settings(str(file_path))
        assert settings["watch_interval"] == 5
        mock_rprint.assert_called_with(
            "[yellow]Warning: Invalid watch_interval in settings. Using default 5 seconds.[/yellow]"
        )


def test_load_settings_watch_interval_negative(tmp_path):
    """Test handling negative watch_interval in settings.json.

    Args:
        tmp_path: Pytest fixture providing a temporary directory.

    Returns:
        None: Asserts default value is used with a warning for negative input.
    """
    file_path = tmp_path / "settings.json"
    file_path.write_text('{"watch_interval": -5}')
    with patch('config.rprint') as mock_rprint:
        settings = load_settings(str(file_path))
        assert settings["watch_interval"] == 5
        mock_rprint.assert_called_with(
            "[yellow]Warning: watch_interval must be positive. Using default 5 seconds.[/yellow]"
        )
