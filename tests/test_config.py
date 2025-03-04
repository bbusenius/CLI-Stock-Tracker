"""
Unit tests for the configuration module.

This module contains tests for the `config.py` module, specifically the `load_tickers` function,
which is responsible for loading a list of stock and ETF tickers from a JSON file. The tests verify
that the function correctly handles various scenarios, including valid input, missing files, and
invalid JSON, ensuring robust configuration management for the Stock and ETF Price Tracker CLI
tool.
"""

from unittest.mock import patch
from config import load_tickers


@patch('config.rprint')
def test_load_tickers_valid(mock_rprint, tmp_path):
    """
    Test loading a valid JSON file with a list of tickers.

    Args:
        mock_rprint (MagicMock): Mocked rich.print function to verify no error messages are printed.
        tmp_path (Path): Pytest fixture providing a temporary directory unique to this test.

    Returns:
        None: The test asserts the expected behavior and raises an AssertionError if it fails.

    Notes:
        - Creates a temporary JSON file with a valid list of tickers.
        - Verifies that `load_tickers` returns the correct list and does not print any error messages.
        - Ensures the function handles standard input as expected in normal operation.
    """
    file_path = tmp_path / "tickers.json"
    file_path.write_text('["AAPL", "MSFT"]')
    tickers = load_tickers(str(file_path))
    assert tickers == ["AAPL", "MSFT"]
    mock_rprint.assert_not_called()


@patch('config.rprint')
def test_load_tickers_missing_file(mock_rprint, tmp_path):
    """
    Test handling of a missing JSON file.

    Args:
        mock_rprint (MagicMock): Mocked rich.print function to verify error message content.
        tmp_path (Path): Pytest fixture providing a temporary directory unique to this test.

    Returns:
        None: The test asserts the expected behavior and raises an AssertionError if it fails.

    Notes:
        - Uses a non-existent file path within the temporary directory.
        - Checks that `load_tickers` returns an empty list and prints an error message with the
          expected file path and "No such file or directory" substring.
        - Validates the error handling for a common failure case (missing config file).
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
    """
    Test handling of a file with invalid JSON content.

    Args:
        mock_rprint (MagicMock): Mocked rich.print function to verify error message content.
        tmp_path (Path): Pytest fixture providing a temporary directory unique to this test.

    Returns:
        None: The test asserts the expected behavior and raises an AssertionError if it fails.

    Notes:
        - Creates a temporary file with malformed JSON (unquoted value).
        - Verifies that `load_tickers` returns an empty list and prints an error message indicating
          a JSON decoding issue (e.g., "Expecting value").
        - Tests robustness against corrupted or improperly formatted configuration files.
    """
    file_path = tmp_path / "invalid.json"
    # Invalid JSON due to unquoted 'value'
    file_path.write_text('{ "key": value }')
    tickers = load_tickers(str(file_path))
    assert tickers == []
    mock_rprint.assert_called_once()
    args, _ = mock_rprint.call_args
    assert f"[red]Error loading tickers from {file_path}:" in args[0]
    assert "Expecting value" in args[0]  # Common JSONDecodeError message


@patch('config.rprint')
def test_load_tickers_non_list(mock_rprint, tmp_path):
    """
    Test handling of a JSON file that does not contain a list.

    Args:
        mock_rprint (MagicMock): Mocked rich.print function to verify error message content.
        tmp_path (Path): Pytest fixture providing a temporary directory unique to this test.

    Returns:
        None: The test asserts the expected behavior and raises an AssertionError if it fails.

    Notes:
        - Creates a temporary JSON file with a dictionary instead of a list.
        - Ensures `load_tickers` returns an empty list and prints an error message stating that
          tickers must be a list, per the function's validation logic.
        - Addresses an edge case where the JSON structure is valid but semantically incorrect.
    """
    file_path = tmp_path / "non_list.json"
    file_path.write_text('{"tickers": ["AAPL", "MSFT"]}')
    tickers = load_tickers(str(file_path))
    assert tickers == []
    mock_rprint.assert_called_once()
    args, _ = mock_rprint.call_args
    assert f"[red]Error loading tickers from {file_path}:" in args[0]
    assert "Tickers must be a list" in args[0]


@patch('config.rprint')
def test_load_tickers_empty_list(mock_rprint, tmp_path):
    """
    Test loading a JSON file with an empty list.

    Args:
        mock_rprint (MagicMock): Mocked rich.print function to verify no error messages are printed.
        tmp_path (Path): Pytest fixture providing a temporary directory unique to this test.

    Returns:
        None: The test asserts the expected behavior and raises an AssertionError if it fails.

    Notes:
        - Creates a temporary JSON file with an empty list (`[]`).
        - Confirms that `load_tickers` returns an empty list without printing any error messages,
          as an empty list is a valid input per the specification.
        - Tests the edge case of a user intentionally providing no tickers.
    """
    file_path = tmp_path / "empty_list.json"
    file_path.write_text('[]')
    tickers = load_tickers(str(file_path))
    assert tickers == []
    mock_rprint.assert_not_called()


@patch('config.rprint')
def test_load_tickers_empty_file(mock_rprint, tmp_path):
    """
    Test handling of an empty JSON file.

    Args:
        mock_rprint (MagicMock): Mocked rich.print function to verify error message content.
        tmp_path (Path): Pytest fixture providing a temporary directory unique to this test.

    Returns:
        None: The test asserts the expected behavior and raises an AssertionError if it fails.

    Notes:
        - Creates a temporary empty file.
        - Verifies that `load_tickers` returns an empty list and prints an error message due to
          invalid JSON (empty string cannot be parsed), with "Expecting value" in the message.
        - Ensures the function handles the edge case of an accidentally empty configuration file.
    """
    file_path = tmp_path / "empty.json"
    file_path.write_text('')
    tickers = load_tickers(str(file_path))
    assert tickers == []
    mock_rprint.assert_called_once()
    args, _ = mock_rprint.call_args
    assert f"[red]Error loading tickers from {file_path}:" in args[0]
    # JSONDecodeError message for empty input
    assert "Expecting value" in args[0]
