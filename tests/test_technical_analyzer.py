import pytest
import pandas as pd
import numpy as np
from analysis.technical_analyzer import calculate_sma

# Fixture for a sample DataFrame
@pytest.fixture
def sample_stock_data():
    data = {
        'Date': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05',
                                '2023-01-06', '2023-01-07', '2023-01-08', '2023-01-09', '2023-01-10']),
        'Open': [10, 11, 12, 13, 14, 15, 16, 17, 18, 19],
        'High': [11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
        'Low': [9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
        'Close': [10.0, 12.0, 11.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0], # Made floats for precision
        'Volume': [100, 110, 120, 130, 140, 150, 160, 170, 180, 190]
    }
    df = pd.DataFrame(data)
    # df.set_index('Date', inplace=True) # calculate_sma doesn't assume Date is index
    return df

def test_calculate_sma_valid_data_window(sample_stock_data):
    window = 5
    df = sample_stock_data.copy()
    result_df = calculate_sma(df, window)

    assert f'SMA_{window}' in result_df.columns
    assert result_df[f'SMA_{window}'].isnull().sum() == window - 1 # First window-1 values are NaN

    # Manual calculation for a few points
    # Close prices: [10, 12, 11, 13, 14, 15, 16, 17, 18, 19]
    # SMA_5 for index 4 (5th item): (10+12+11+13+14)/5 = 60/5 = 12.0
    assert result_df[f'SMA_{window}'].iloc[4] == pytest.approx(12.0)
    # SMA_5 for index 5: (12+11+13+14+15)/5 = 65/5 = 13.0
    assert result_df[f'SMA_{window}'].iloc[5] == pytest.approx(13.0)
    # SMA_5 for index 9: (15+16+17+18+19)/5 = 85/5 = 17.0
    assert result_df[f'SMA_{window}'].iloc[9] == pytest.approx(17.0)

def test_calculate_sma_window_greater_than_data_length(sample_stock_data):
    window = 20 # Larger than sample_stock_data length (10)
    df = sample_stock_data.copy()
    result_df = calculate_sma(df, window)

    # The function should return the original df (or df with all-NaN SMA col) and print a warning
    # Current implementation returns original df without SMA column
    assert f'SMA_{window}' not in result_df.columns
    # Or, if it adds an all-NaN column:
    # assert f'SMA_{window}' in result_df.columns
    # assert result_df[f'SMA_{window}'].isnull().all()
    pd.testing.assert_frame_equal(result_df, df) # Check if it's the original

def test_calculate_sma_empty_dataframe():
    window = 5
    df = pd.DataFrame(columns=['Date', 'Close', 'Open', 'High', 'Low', 'Volume'])
    result_df = calculate_sma(df.copy(), window) # Pass copy

    assert result_df.empty
    pd.testing.assert_frame_equal(result_df, df) # Should return the same empty df

def test_calculate_sma_missing_close_column():
    window = 5
    df = pd.DataFrame({'Open': [1, 2, 3], 'High': [2,3,4]})
    result_df = calculate_sma(df.copy(), window) # Pass copy

    assert 'SMA_5' not in result_df.columns
    pd.testing.assert_frame_equal(result_df, df) # Should return the original df

def test_calculate_sma_with_nan_in_close(sample_stock_data):
    window = 3
    df = sample_stock_data.copy()
    df.loc[2, 'Close'] = np.nan # Introduce a NaN: [10, 12, NaN, 13, 14, ...]

    result_df = calculate_sma(df, window)
    sma_col = f'SMA_{window}'
    assert sma_col in result_df.columns

    # Close prices: [10, 12, NaN, 13, 14, 15, ...]
    # SMA_3:
    # iloc[0]: NaN (window)
    # iloc[1]: NaN (window)
    # iloc[2]: (10+12+NaN)/3 = NaN
    # iloc[3]: (12+NaN+13)/3 = NaN
    # iloc[4]: (NaN+13+14)/3 = NaN
    # iloc[5]: (13+14+15)/3 = 14.0
    assert result_df[sma_col].isnull().sum() == (window - 1) + 3 # initial (w-1) NaNs + 3 NaNs due to propagation
    assert pd.isna(result_df[sma_col].iloc[0]) # Window related
    assert pd.isna(result_df[sma_col].iloc[1]) # Window related
    assert pd.isna(result_df[sma_col].iloc[2]) # Calculation with NaN
    assert pd.isna(result_df[sma_col].iloc[3]) # Calculation with NaN
    assert pd.isna(result_df[sma_col].iloc[4]) # Calculation with NaN
    assert result_df[sma_col].iloc[5] == pytest.approx(14.0) # First valid calculation after NaN

def test_calculate_sma_none_input():
    result_df = calculate_sma(None, 5)
    assert result_df is None

def test_calculate_sma_not_dataframe_input():
    # Test with a list instead of a DataFrame
    not_a_df = [1, 2, 3]
    result_df = calculate_sma(not_a_df, 5) # type: ignore
    assert result_df == not_a_df # Returns original input

# Test with a very small DataFrame, less than window
def test_calculate_sma_very_short_data(sample_stock_data):
    window = 5
    df_short = sample_stock_data.head(2).copy() # Only 2 rows
    result_df = calculate_sma(df_short, window)

    # Should return original df as len < window
    assert f'SMA_{window}' not in result_df.columns
    pd.testing.assert_frame_equal(result_df, df_short)

# Test that the original DataFrame is not modified if a copy is not passed explicitly by caller
# (though calculate_sma itself should ideally work on a copy or not modify in place if not returning new df)
# The current implementation of calculate_sma modifies the DataFrame in-place by adding a column.
# This test will check that behavior. If it's desired that it should not modify, the function needs to change.
def test_calculate_sma_modifies_input_dataframe_in_place(sample_stock_data):
    window = 3
    df_copy_for_test = sample_stock_data.copy() # Keep original sample_stock_data clean for other tests

    # If calculate_sma is expected to not modify, then:
    # calculate_sma(df_copy_for_test.copy(), window) # Pass a copy to the function
    # assert f'SMA_{window}' not in df_copy_for_test.columns # Original df_copy_for_test is unchanged

    # Current behavior: it modifies in place
    calculate_sma(df_copy_for_test, window)
    assert f'SMA_{window}' in df_copy_for_test.columns

# Test with window = 1
def test_calculate_sma_window_one(sample_stock_data):
    window = 1
    df = sample_stock_data.copy()
    result_df = calculate_sma(df, window)
    sma_col = f'SMA_{window}'

    assert sma_col in result_df.columns
    # SMA with window 1 should be the 'Close' price itself
    pd.testing.assert_series_equal(result_df[sma_col], result_df['Close'], check_dtype=False, check_names=False)
    assert result_df[sma_col].isnull().sum() == 0 # No NaNs for window 1

# The warning messages in `calculate_sma` are side effects (print statements).
# Similar to data_fetcher, testing these would require mocking `print` or using proper logging.
# These tests focus on the returned DataFrame and its contents.
