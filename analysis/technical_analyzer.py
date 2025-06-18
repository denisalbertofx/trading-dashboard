import pandas as pd

def calculate_sma(data_df: pd.DataFrame | None, window: int) -> pd.DataFrame | None:
    """
    Calculates the Simple Moving Average (SMA) for the 'Close' column of a DataFrame.

    Args:
        data_df (pd.DataFrame | None): DataFrame with stock data, expected to have a 'Close' column.
        window (int): The window size for the SMA calculation.

    Returns:
        pd.DataFrame | None: The DataFrame with an added SMA column (e.g., 'SMA_20'),
                             or the original DataFrame if calculation is not possible,
                             or None if input is None.
    """
    if data_df is None:
        print("Warning: Input DataFrame is None. Cannot calculate SMA.")
        return None

    if not isinstance(data_df, pd.DataFrame):
        print("Warning: Input is not a pandas DataFrame. Cannot calculate SMA.")
        return data_df # Or raise TypeError

    if 'Close' not in data_df.columns:
        print("Warning: 'Close' column not found in DataFrame. Cannot calculate SMA.")
        return data_df

    if len(data_df) < window:
        print(f"Warning: DataFrame length ({len(data_df)}) is less than SMA window ({window}). SMA will not be calculated.")
        # Optionally add an empty column or return as is
        # data_df[f'SMA_{window}'] = pd.NA
        return data_df

    sma_column_name = f'SMA_{window}'
    data_df[sma_column_name] = data_df['Close'].rolling(window=window).mean()

    return data_df

if __name__ == '__main__':
    # Example Usage
    data = {
        'Date': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05',
                 '2023-01-06', '2023-01-07', '2023-01-08', '2023-01-09', '2023-01-10']),
        'Close': [10, 12, 11, 13, 14, 15, 16, 17, 18, 19]
    }
    sample_df = pd.DataFrame(data)
    sample_df.set_index('Date', inplace=True)

    print("Original DataFrame:")
    print(sample_df)

    # Test with sufficient data
    df_with_sma = calculate_sma(sample_df.copy(), window=5)
    if df_with_sma is not None:
        print("\nDataFrame with SMA_5:")
        print(df_with_sma)

    # Test with data too short for window
    df_short = sample_df.head(3).copy()
    print("\nShort DataFrame (3 rows):")
    print(df_short)
    df_short_sma = calculate_sma(df_short, window=5)
    if df_short_sma is not None:
        print("\nShort DataFrame with SMA_5 attempt:")
        print(df_short_sma)
        # Check if SMA column was added (it shouldn't be, or should be all NA)
        if f'SMA_5' not in df_short_sma.columns or df_short_sma[f'SMA_5'].isna().all():
            print("SMA column correctly not calculated or all NA for short dataframe.")


    # Test with missing 'Close' column
    df_no_close = pd.DataFrame({'Open': [1, 2, 3]})
    print("\nDataFrame without 'Close' column:")
    df_no_close_sma = calculate_sma(df_no_close.copy(), window=2)
    if df_no_close_sma is not None:
        print(df_no_close_sma)

    # Test with None input
    print("\nTesting with None input:")
    none_df_sma = calculate_sma(None, window=5)
    if none_df_sma is None:
        print("Correctly returned None for None input.")
