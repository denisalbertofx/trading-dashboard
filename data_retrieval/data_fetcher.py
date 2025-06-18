import yfinance as yf
import pandas as pd

def get_stock_data(ticker: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame | None:
    """
    Fetches historical stock data for a given ticker.

    Args:
        ticker (str): The stock ticker symbol (e.g., "AAPL").
        period (str): The period for which to fetch data (e.g., "1y", "6mo", "1d").
        interval (str): The interval of data points (e.g., "1d", "1wk", "1mo").

    Returns:
        pd.DataFrame | None: A DataFrame containing the stock data,
                             or None if an error occurs.
    """
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period=period, interval=interval)
        if data.empty:
            print(f"No data found for ticker {ticker} with period {period} and interval {interval}.")
            return None
        return data
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None

if __name__ == '__main__':
    # Example usage:
    aapl_data = get_stock_data("AAPL", period="1mo", interval="1d")
    if aapl_data is not None:
        print("AAPL Data (last 5 days):")
        print(aapl_data.tail())
    else:
        print("Could not retrieve AAPL data.")

    invalid_data = get_stock_data("INVALIDTICKER", period="1d", interval="1d")
    if invalid_data is not None:
        print("\nINVALIDTICKER Data:")
        print(invalid_data)
    else:
        print("\nCould not retrieve INVALIDTICKER data, as expected.")
