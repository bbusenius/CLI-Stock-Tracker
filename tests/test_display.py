"""
Unit tests for the display module.

This module contains tests for the display.py module, specifically the format_percentage and
display_table functions, ensuring that financial data is correctly formatted and displayed in a
table using the rich library. The tests cover various scenarios including valid data, invalid
tickers, missing values, multiple items, and empty input, verifying both the formatting logic
and the presence of expected output in the console.
"""

from display import display_table, format_percentage

SAMPLE_SETTINGS = {
    "columns": {
        "eps": True,
        "pe_ratio": True,
        "dividend": True,
        "ytd_change": True,
        "ten_year_change": True,
    }
}


def test_format_percentage_positive():
    """
    Test that format_percentage returns a green styled string for positive values.
    """
    assert format_percentage(1.23) == "[green]1.23%[/]"


def test_format_percentage_negative():
    """
    Test that format_percentage returns a red styled string for negative values.
    """
    assert format_percentage(-2.34) == "[red]-2.34%[/]"


def test_format_percentage_zero():
    """
    Test that format_percentage returns an unstyled string for zero.
    """
    assert format_percentage(0.0) == "0.00%"


def test_format_percentage_none():
    """
    Test that format_percentage returns 'N/A' for None.
    """
    assert format_percentage(None) == "N/A"


def test_display_table_valid_data(capsys):
    """
    Test that display_table prints a correctly formatted row for valid ticker data.

    Args:
        capsys: Pytest fixture to capture console output.
    """
    data = [
        {
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
    ]
    display_table(data, SAMPLE_SETTINGS, debug=True)
    captured = capsys.readouterr()
    assert "AAPL" in captured.out  # Ticker is unique and unlikely to split
    assert "Apple" in captured.out  # First part of company name
    assert "Inc." in captured.out  # Second part of company name
    assert "145.67" in captured.out  # Current price
    assert "5.89" in captured.out  # EPS
    assert "24.70" in captured.out  # PE Ratio
    assert "0.85" in captured.out  # Dividend
    assert "1.23%" in captured.out  # Daily change
    assert "-2.34%" in captured.out  # YTD change
    # Part of 10-year change (avoid ellipsis)
    assert "245.6" in captured.out


def test_display_table_invalid_ticker(capsys):
    """
    Test that display_table prints a row with 'Data unavailable' for invalid tickers.

    Args:
        capsys: Pytest fixture to capture console output.
    """
    data = [{'ticker': 'XYZ', 'message': 'Data unavailable'}]
    display_table(data, SAMPLE_SETTINGS, debug=True)
    captured = capsys.readouterr()
    assert "XYZ" in captured.out  # Ticker is unique
    assert "Data" in captured.out  # First part of message
    assert "unavailable" in captured.out  # Second part of message


def test_display_table_missing_values(capsys):
    """
    Test that display_table handles missing values by displaying 'N/A'.

    Args:
        capsys: Pytest fixture to capture console output.
    """
    data = [
        {
            'ticker': 'MSFT',
            'company_name': 'Microsoft Corporation',
            'current_price': None,
            'eps': 8.05,
            'pe_ratio': None,
            'dividend': 1.00,
            'daily_change': None,
            'ytd_change': 5.67,
            'ten_year_change': None,
        }
    ]
    display_table(data, SAMPLE_SETTINGS, debug=True)
    captured = capsys.readouterr()
    assert "MSFT" in captured.out  # Ticker
    assert "Microsoft" in captured.out  # First part of company name
    assert "Corporation" in captured.out  # Second part of company name
    assert "N/A" in captured.out  # Missing value indicator
    assert "8.05" in captured.out  # EPS
    assert "1.00" in captured.out  # Dividend
    assert "5.67%" in captured.out  # YTD change


def test_display_table_multiple_items(capsys):
    """
    Test that display_table handles multiple data items, including valid and invalid tickers.

    Args:
        capsys: Pytest fixture to capture console output.
    """
    data = [
        {
            'ticker': 'AAPL',
            'company_name': 'Apple Inc.',
            'current_price': 145.67,
            'eps': 5.89,
            'pe_ratio': 24.70,
            'dividend': 0.85,
            'daily_change': 1.23,
            'ytd_change': -2.34,
            'ten_year_change': 245.67,
        },
        {'ticker': 'XYZ', 'message': 'Data unavailable'},
        {
            'ticker': 'MSFT',
            'company_name': 'Microsoft Corporation',
            'current_price': None,
            'eps': 8.05,
            'pe_ratio': None,
            'dividend': 1.00,
            'daily_change': None,
            'ytd_change': 5.67,
            'ten_year_change': None,
        },
    ]
    display_table(data, SAMPLE_SETTINGS, debug=True)
    captured = capsys.readouterr()
    # Check AAPL row
    assert "AAPL" in captured.out
    assert "Apple" in captured.out
    assert "Inc." in captured.out
    assert "145.67" in captured.out
    assert "1.23%" in captured.out
    # Check XYZ row
    assert "XYZ" in captured.out
    assert "Data" in captured.out
    assert "unavailable" in captured.out
    # Check MSFT row
    assert "MSFT" in captured.out
    assert "Microsoft" in captured.out
    assert "Corporation" in captured.out
    assert "N/A" in captured.out
    assert "5.67%" in captured.out


def test_display_table_empty_list(capsys):
    """
    Test that display_table prints only headers for an empty data list.

    Args:
        capsys: Pytest fixture to capture console output.
    """
    data = []
    display_table(data, SAMPLE_SETTINGS, debug=True)
    captured = capsys.readouterr()
    assert "Ticker" in captured.out  # Check part of header
    assert "Company" in captured.out  # Abbreviated or split header
    assert "Price" in captured.out  # Abbreviated or split header
    assert "AAPL" not in captured.out  # No data rows
    assert "Data" not in captured.out  # No invalid ticker messages


def test_display_table_no_eps_pe(capsys):
    """
    Test that display_table does not include EPS and PE Ratio when they are disabled in settings.

    Args:
        capsys: Pytest fixture to capture console output.
    """
    settings = {
        "columns": {
            "eps": False,
            "pe_ratio": False,
            "dividend": True,
            "ytd_change": True,
            "ten_year_change": True,
        }
    }
    data = [
        {
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
    ]
    display_table(data, settings, debug=True)
    captured = capsys.readouterr()
    assert "AAPL" in captured.out
    assert "Apple" in captured.out
    assert "145.67" in captured.out
    assert "1.23%" in captured.out
    assert "0.85" in captured.out  # Dividend
    assert "-2.34%" in captured.out  # YTD
    assert "245.67%" in captured.out  # 10-Year
    assert "5.89" not in captured.out  # EPS should not be present
    assert "24.70" not in captured.out  # PE Ratio should not be present
