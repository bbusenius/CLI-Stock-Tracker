"""
Table display module for the Stock and ETF Price Tracker.

This module provides functionality to display financial data in a formatted table using the rich library.
It is responsible for rendering a table with key financial metrics for stocks and ETFs, handling both
valid data and error cases such as invalid tickers or missing values, and dynamically including columns
based on user-defined settings.
"""

from typing import Dict, List

from rich.console import Console
from rich.table import Table


def format_percentage(value: float | None) -> str:
    """
    Formats a percentage value with color styling.

    Args:
        value: The percentage change value.

    Returns:
        The formatted string with color tags if applicable.

    Notes:
        - If the value is None, returns "N/A" without styling.
        - Positive values (> 0) are styled in green, indicating gains.
        - Negative values (< 0) are styled in red, indicating losses.
        - Zero values are formatted without color styling, treated as neutral.
    """
    if value is None:
        return "N/A"
    if value > 0:
        return f"[green]{value:.2f}%[/]"
    elif value < 0:
        return f"[red]{value:.2f}%[/]"
    else:
        return f"{value:.2f}%"


def display_table(
    data: List[Dict[str, str | float | None]],
    settings: Dict[str, dict],
    console: Console = None,
    debug: bool = False,
) -> None:
    """
    Displays the financial data in a formatted table based on the provided settings.

    Args:
        data: A list of dictionaries, each containing financial data for a ticker.
            Valid ticker keys: 'ticker', 'company_name', 'current_price', 'eps', 'pe_ratio',
            'dividend', 'daily_change', 'ytd_change', 'ten_year_change'.
            Invalid ticker keys: 'ticker', 'message'.
        settings: Display settings indicating which optional columns to include.
        console: An optional existing Console instance; if None, a new one is created.
        debug: If True, prints additional plain text output for test detection.

    Notes:
        - Base columns: Ticker, Company Name, Current Price, Daily % Change.
        - Optional columns: EPS, PE Ratio, Dividend, YTD % Change, 10-Year % Change, included if enabled.
        - Missing values (None) are displayed as 'N/A'.
        - Numbers are formatted to two decimal places; percentages are colored (green for gains, red for losses).
        - Invalid tickers show ticker and message spanning remaining columns.
        - Columns are aligned: text left, numbers right.
        - In watch mode, reusing a console improves performance by avoiding recreation.
    """
    if console is None:
        console = Console(highlight=False, markup=True)
    table = Table(show_header=True)

    # Define base columns that are always included
    base_columns = [
        ("Ticker", "left"),
        ("Company Name", "left"),
        ("Current Price", "right"),
        ("Daily % Change", "right"),
    ]

    # Define optional columns based on settings
    optional_columns = []
    if settings['columns'].get('eps', False):
        optional_columns.append(("EPS", "right"))
    if settings['columns'].get('pe_ratio', False):
        optional_columns.append(("PE Ratio", "right"))
    if settings['columns'].get('dividend', False):
        optional_columns.append(("Dividend", "right"))
    if settings['columns'].get('ytd_change', False):
        optional_columns.append(("YTD % Change", "right"))
    if settings['columns'].get('ten_year_change', False):
        optional_columns.append(("10-Year % Change", "right"))

    # Combine all columns to determine table structure
    all_columns = base_columns + optional_columns
    for col_name, justify in all_columns:
        table.add_column(col_name, justify=justify)

    if debug:
        print("Headers: " + ", ".join(col_name for col_name, _ in all_columns))

    # Define formatters for each column
    column_formatters = {
        "Ticker": lambda item: item["ticker"],
        "Company Name": lambda item: (
            item["company_name"] if item["company_name"] is not None else "N/A"
        ),
        "Current Price": lambda item: (
            f"{item['current_price']:.2f}"
            if item["current_price"] is not None
            else "N/A"
        ),
        "EPS": lambda item: f"{item['eps']:.2f}" if item["eps"] is not None else "N/A",
        "PE Ratio": lambda item: (
            f"{item['pe_ratio']:.2f}" if item["pe_ratio"] is not None else "N/A"
        ),
        "Dividend": lambda item: (
            f"{item['dividend']:.2f}" if item["dividend"] is not None else "N/A"
        ),
        "Daily % Change": lambda item: format_percentage(item["daily_change"]),
        "YTD % Change": lambda item: format_percentage(item["ytd_change"]),
        "10-Year % Change": lambda item: format_percentage(item["ten_year_change"]),
    }

    for item in data:
        if "message" in item:
            # Handle invalid ticker: display ticker and message spanning remaining columns
            ticker = item["ticker"]
            message = item["message"]
            if debug:
                print(f"Invalid ticker: {ticker}, Message: {message}")
            table.add_row(ticker, message, *[""] * (len(all_columns) - 2))
        else:
            # Handle valid ticker: format each field based on included columns
            row = [column_formatters[col](item) for col in [c[0] for c in all_columns]]
            if debug:
                print("Valid ticker: " + ", ".join(row))
            table.add_row(*row)

    console.print(table)
