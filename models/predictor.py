import pandas as pd

def generate_recommendation(data_df: pd.DataFrame | None, sma_window: int) -> str:
    """
    Generates a simple trading recommendation based on the latest Close price
    and its Simple Moving Average (SMA).

    Args:
        data_df (pd.DataFrame | None): DataFrame with stock data, expected to have
                                     'Close' and 'SMA_{sma_window}' columns.
        sma_window (int): The window size used for the SMA calculation.

    Returns:
        str: A recommendation string: "Buy", "Sell", "Hold", or "N/A" / "Error".
    """
    sma_column_name = f'SMA_{sma_window}'

    if data_df is None:
        print("Error: Input DataFrame is None. Cannot generate recommendation.")
        return "Error: No data provided"

    if not isinstance(data_df, pd.DataFrame):
        print("Error: Input is not a pandas DataFrame.")
        return "Error: Invalid data type"

    if data_df.empty:
        return "N/A: Data is empty"

    if 'Close' not in data_df.columns:
        return f"Error: 'Close' column not found"

    if sma_column_name not in data_df.columns:
        return f"Error: '{sma_column_name}' column not found"

    # Get the latest valid data point (ignoring trailing NaNs if any)
    latest_data = data_df.dropna(subset=['Close', sma_column_name]).iloc[-1:]

    if latest_data.empty:
        return "N/A: Not enough data or SMA not calculated for recent period"

    latest_close = latest_data['Close'].iloc[0]
    latest_sma = latest_data[sma_column_name].iloc[0]

    if pd.isna(latest_close) or pd.isna(latest_sma):
        return "N/A: Missing Close or SMA value in the latest data point"

    if latest_close > latest_sma:
        return "Buy"
    elif latest_close < latest_sma:
        return "Sell"
    else:
        return "Hold"

if __name__ == '__main__':
    # Example Usage:
    sma_win = 20
    sma_col = f'SMA_{sma_win}'

    # Case 1: Buy
    data_buy = {
        'Date': pd.to_datetime(['2023-01-01', '2023-01-02']),
        'Close': [100, 105],
        sma_col: [98, 100] # SMA is typically calculated on more data
    }
    df_buy = pd.DataFrame(data_buy)
    print(f"Recommendation for Buy case: {generate_recommendation(df_buy.copy(), sma_win)}")

    # Case 2: Sell
    data_sell = {
        'Date': pd.to_datetime(['2023-01-01', '2023-01-02']),
        'Close': [100, 95],
        sma_col: [102, 100]
    }
    df_sell = pd.DataFrame(data_sell)
    print(f"Recommendation for Sell case: {generate_recommendation(df_sell.copy(), sma_win)}")

    # Case 3: Hold
    data_hold = {
        'Date': pd.to_datetime(['2023-01-01', '2023-01-02']),
        'Close': [100, 100],
        sma_col: [100, 100]
    }
    df_hold = pd.DataFrame(data_hold)
    print(f"Recommendation for Hold case: {generate_recommendation(df_hold.copy(), sma_win)}")

    # Case 4: SMA is NaN for latest
    data_sma_nan = {
        'Date': pd.to_datetime(['2023-01-01', '2023-01-02']),
        'Close': [100, 100],
        sma_col: [98, pd.NA] # Last SMA is NA
    }
    df_sma_nan = pd.DataFrame(data_sma_nan)
    print(f"Recommendation for SMA NaN case: {generate_recommendation(df_sma_nan.copy(), sma_win)}")

    # Case 5: Empty DataFrame
    df_empty = pd.DataFrame(columns=['Date', 'Close', sma_col])
    print(f"Recommendation for Empty DataFrame: {generate_recommendation(df_empty.copy(), sma_win)}")

    # Case 6: None DataFrame
    print(f"Recommendation for None DataFrame: {generate_recommendation(None, sma_win)}")

    # Case 7: Missing 'Close'
    df_no_close = pd.DataFrame({sma_col: [10,11]})
    print(f"Recommendation for no 'Close': {generate_recommendation(df_no_close.copy(), sma_win)}")

    # Case 8: Missing SMA column
    df_no_sma = pd.DataFrame({'Close': [10,11]})
    print(f"Recommendation for no SMA col: {generate_recommendation(df_no_sma.copy(), sma_win)}")

    # Case 9: DataFrame with all NaNs in SMA or Close for latest relevant rows
    data_all_nan_relevant = {
        'Date': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03']),
        'Close': [100, 101, pd.NA],
        sma_col: [98, pd.NA, pd.NA]
    }
    df_all_nan_relevant = pd.DataFrame(data_all_nan_relevant)
    print(f"Recommendation for all NaN relevant: {generate_recommendation(df_all_nan_relevant.copy(), sma_win)}")

    data_some_nan_relevant = {
        'Date': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03']),
        'Close': [100, 101, 102],
        sma_col: [98, 99, pd.NA] # Last SMA is NA
    }
    df_some_nan_relevant = pd.DataFrame(data_some_nan_relevant)
    print(f"Recommendation for some NaN relevant (SMA NA at end): {generate_recommendation(df_some_nan_relevant.copy(), sma_win)}")
