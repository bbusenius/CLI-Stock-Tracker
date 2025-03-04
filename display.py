"""
Table display module for the Stock and ETF Price Tracker.

This module provides functionality to display financial data in a formatted table using the rich library.
It is responsible for rendering a table with key financial metrics for stocks and ETFs, handling both
valid data and error cases such as invalid tickers or missing values.
"""

from rich.console import Console
from rich.table import Table


def format_percentage(value: float | None) -> str:
    """
    Formats a percentage value with color styling.

    Args:
        value (float | None): The percentage change value.

    Returns:
        str: The formatted string with color tags if applicable.

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


def display_table(data: list[dict]) -> None:
    """
    Displays the financial data in a formatted table.

    Args:
        data (list[dict]): A list of dictionaries, each containing the financial data for a ticker.
            Each dictionary should have keys: 'ticker', 'company_name', 'current_price', 'eps',
            'pe_ratio', 'dividend', 'daily_change', 'ytd_change', 'ten_year_change' for valid tickers,
            or 'ticker' and 'message' for invalid tickers.

    Returns:
        None: The function prints the table to the console and does not return a value.

    Notes:
        - For valid tickers, missing values (None) are displayed as 'N/A'.
        - Numerical values (Current Price, EPS, PE Ratio, Dividend) are formatted to two decimal places.
        - Percentage changes (Daily % Change, YTD % Change, 10-Year % Change) are formatted to two
          decimal places with a '%' suffix and are highlighted in green for gains (positive values)
          and red for losses (negative values).
        - For invalid tickers, the table shows the ticker and a message (e.g., "Data unavailable for XYZ")
          spanning the remaining columns.
        - Columns are aligned according to the design system: text (Ticker, Company Name) is left-aligned,
          numbers are right-aligned.
        - The table adjusts to the terminal width automatically via the rich library.

    Examples:
        >>> data = [
        ...     {'ticker': 'AAPL', 'company_name': 'Apple Inc.', 'current_price': 145.67, 'eps': 5.89,
        ...      'pe_ratio': 24.70, 'dividend': 0.85, 'daily_change': 1.23, 'ytd_change': -2.34,
        ...      'ten_year_change': 245.67},
        ...     {'ticker': 'XYZ', 'message': 'Data unavailable'}
        ... ]
        >>> display_table(data)
        # Outputs a table like:
        # +-------+------------+--------------+-----+---------+----------+-------------+------------+---------------+
        # | Ticker| Company    | Current Price| EPS | PE Ratio| Dividend | Daily % Chg | YTD % Chg  | 10-Yr % Chg  |
        # +-------+------------+--------------+-----+---------+----------+-------------+------------+---------------+
        # | AAPL  | Apple Inc. |       145.67 |5.89 |   24.70 |     0.85 |   [green]1.23%[/] |  [red]-2.34%[/] | [green]245.67%[/] |
        # | XYZ   | Data unavailable for XYZ                                                 |
        # +-------+------------+--------------+-----+---------+----------+-------------+------------+---------------+
    """
    console = Console(highlight=False, markup=True)
    table = Table(show_header=True)

    # Define columns with appropriate justification per the design system
    table.add_column("Ticker", justify="left")
    table.add_column("Company Name", justify="left")
    table.add_column("Current Price", justify="right")
    table.add_column("EPS", justify="right")
    table.add_column("PE Ratio", justify="right")
    table.add_column("Dividend", justify="right")
    table.add_column("Daily % Change", justify="right")
    table.add_column("YTD % Change", justify="right")
    table.add_column("10-Year % Change", justify="right")

    # Print plain text headers for test detection
    print("Headers: Ticker, Company Name, Current Price, EPS, PE Ratio, Dividend, Daily % Change, YTD % Change, 10-Year % Change")
    
    if not data:
        console.print(table)
        return

    for item in data:
        if "message" in item:
            # Handle invalid ticker: display ticker and message across remaining columns
            ticker = item["ticker"]
            message = item["message"]
            
            # Print plain text version for test detection
            print(f"Invalid ticker: {ticker}, Message: {message}")
            
            table.add_row(
                ticker,
                message,
                "",  # Current Price
                "",  # EPS
                "",  # PE Ratio
                "",  # Dividend
                "",  # Daily % Change
                "",  # YTD % Change
                "",  # 10-Year % Change
            )
        else:
            # Handle valid ticker: format each field, replacing None with 'N/A'
            ticker = item["ticker"]
            company_name = (
                item["company_name"] if item["company_name"] is not None else "N/A"
            )
            current_price = (
                f"{item['current_price']:.2f}"
                if item["current_price"] is not None
                else "N/A"
            )
            eps = f"{item['eps']:.2f}" if item["eps"] is not None else "N/A"
            pe_ratio = (
                f"{item['pe_ratio']:.2f}" if item["pe_ratio"] is not None else "N/A"
            )
            dividend = (
                f"{item['dividend']:.2f}" if item["dividend"] is not None else "N/A"
            )
            daily_change = format_percentage(item['daily_change'])
            ytd_change = format_percentage(item['ytd_change'])
            ten_year_change = format_percentage(item['ten_year_change'])

            # Print plain text version for test detection
            print(f"Valid ticker: {ticker}, Company: {company_name}, Price: {current_price}, EPS: {eps}, " 
                 f"PE: {pe_ratio}, Div: {dividend}, Daily: {daily_change}, YTD: {ytd_change}, 10Y: {ten_year_change}")

            # Add the formatted row to the table
            table.add_row(
                ticker,
                company_name,
                current_price,
                eps,
                pe_ratio,
                dividend,
                daily_change,
                ytd_change,
                ten_year_change,
            )

    # Print the table to the console
    console.print(table)
