import pytest
import pandas as pd
from data_retrieval.data_fetcher import get_stock_data
from unittest.mock import MagicMock, patch

# Sample data for mocking yfinance responses
SAMPLE_COLUMNS = ['Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']
SAMPLE_DATES = pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03'])

def create_sample_df(empty=False, data=None):
    if empty:
        return pd.DataFrame(columns=SAMPLE_COLUMNS)
    if data is None:
        data = {
            'Open': [150.0, 151.0, 152.0],
            'High': [155.0, 156.0, 157.0],
            'Low': [149.0, 150.0, 151.0],
            'Close': [152.0, 153.0, 154.0],
            'Volume': [1000000, 1200000, 1100000],
            'Dividends': [0, 0, 0],
            'Stock Splits': [0, 0, 0]
        }
    return pd.DataFrame(data, index=SAMPLE_DATES)

@pytest.fixture
def mock_yfinance_ticker(mocker):
    """Mocks yfinance.Ticker."""
    mock_ticker_instance = MagicMock()
    mock_ticker_constructor = mocker.patch('yfinance.Ticker', return_value=mock_ticker_instance)
    return mock_ticker_instance, mock_ticker_constructor

def test_get_stock_data_success(mock_yfinance_ticker):
    mock_ticker_instance, _ = mock_yfinance_ticker
    sample_df = create_sample_df()
    mock_ticker_instance.history.return_value = sample_df

    ticker_symbol = "AAPL"
    data = get_stock_data(ticker_symbol, period="1mo", interval="1d")

    assert data is not None
    pd.testing.assert_frame_equal(data, sample_df)
    mock_ticker_instance.history.assert_called_once_with(period="1mo", interval="1d")

def test_get_stock_data_yfinance_exception(mock_yfinance_ticker):
    mock_ticker_instance, _ = mock_yfinance_ticker
    mock_ticker_instance.history.side_effect = Exception("Simulated yfinance error")

    data = get_stock_data("MSFT", period="1y", interval="1d")

    assert data is None

def test_get_stock_data_empty_history(mock_yfinance_ticker):
    mock_ticker_instance, _ = mock_yfinance_ticker
    empty_df = create_sample_df(empty=True)
    mock_ticker_instance.history.return_value = empty_df

    # Current implementation of get_stock_data returns None if data.empty
    data = get_stock_data("GOOG", period="5d", interval="1h")

    assert data is None

def test_get_stock_data_non_existent_ticker(mock_yfinance_ticker):
    # This scenario often results in an empty DataFrame or specific error from yfinance.
    # If yfinance.Ticker("NONEXISTENT").history() returns an empty df:
    mock_ticker_instance, _ = mock_yfinance_ticker
    empty_df = create_sample_df(empty=True) # Or specific error yfinance might return
    mock_ticker_instance.history.return_value = empty_df

    data = get_stock_data("NONEXISTENTTICKER", period="1d", interval="1d")

    # Current implementation of get_stock_data returns None if data.empty
    assert data is None

@patch('yfinance.Ticker') # An alternative way to patch
def test_get_stock_data_specific_columns(mock_yf_ticker_constructor):
    mock_ticker_instance = MagicMock()
    mock_yf_ticker_constructor.return_value = mock_ticker_instance

    sample_df = create_sample_df()
    mock_ticker_instance.history.return_value = sample_df

    data = get_stock_data("TSLA")
    assert data is not None
    assert list(data.columns) == SAMPLE_COLUMNS
    assert len(data) == len(SAMPLE_DATES)

# To run these tests, you would use pytest in your terminal
# Ensure yfinance is NOT actually called by good mocking.
# The data_fetcher.py itself has a check:
# if data.empty:
#     print(f"No data found for ticker {ticker}...")
#     return None
# This means for empty_history and non_existent_ticker (if it returns empty df),
# the function will return None.
# If the actual yfinance behavior for non-existent tickers is to raise an exception
# that Ticker() itself can catch, then the yfinance_exception test covers it.
# If Ticker("NONEXISTENT") itself raises an error before .history() is called,
# the mock_yfinance_ticker fixture's patch on yf.Ticker would need to handle that.
# For now, assuming Ticker() succeeds and history() returns empty or raises.
# The current `get_stock_data` doesn't catch errors on `yf.Ticker()` itself, only on `.history()`
# or if data is empty.

# A test for yf.Ticker() raising an exception:
def test_get_stock_data_ticker_creation_exception(mocker):
    mocker.patch('yfinance.Ticker', side_effect=Exception("Simulated Ticker creation error"))
    data = get_stock_data("ERRORTICKER")
    assert data is None # Because the try-except in get_stock_data should catch this.

# A test for when data is returned, but it's not a dataframe (shouldn't happen with yf but good for robustness)
def test_get_stock_data_unexpected_return_type(mock_yfinance_ticker):
    mock_ticker_instance, _ = mock_yfinance_ticker
    mock_ticker_instance.history.return_value = "not a dataframe"

    # Depending on how robust get_stock_data is, this might raise an error or return None.
    # Current implementation: would raise AttributeError when trying to access .empty or .columns
    # The try-except Exception in get_stock_data should catch this.
    data = get_stock_data("ANYTICKER")
    assert data is None

# Test with different periods and intervals to ensure they are passed to history
@patch('yfinance.Ticker')
def test_get_stock_data_params_passed(mock_yf_ticker_constructor_params):
    mock_ticker_instance = MagicMock()
    mock_yf_ticker_constructor_params.return_value = mock_ticker_instance
    mock_ticker_instance.history.return_value = create_sample_df()

    get_stock_data("AAPL", period="6mo", interval="1wk")
    mock_ticker_instance.history.assert_called_once_with(period="6mo", interval="1wk")

    mock_yf_ticker_constructor_params.assert_called_once_with("AAPL") # Check Ticker was called with symbol

# Note: The print statements in get_stock_data are side effects.
# In a more complex scenario, you might want to mock `print` as well to check output,
# or refactor to use logging. For now, focusing on return values.
