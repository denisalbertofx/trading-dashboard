# Main application file for the trading dashboard
# This file will contain the core Flask application logic

import pandas as pd
from flask import Flask, render_template
from data_retrieval.data_fetcher import get_stock_data
from analysis.technical_analyzer import calculate_sma
from models.predictor import generate_recommendation

app = Flask(__name__)

@app.route('/')
def index():
    """
    Renders the main dashboard page, fetching, analyzing, and displaying stock data and recommendation.
    """
    ticker = "AAPL"  # Sample ticker
    sma_window = 20
    # Fetch more data for SMA; yfinance often returns Date as index
    stock_data_original = get_stock_data(ticker, period="3mo", interval="1d")

    recommendation_text = "N/A"
    data_for_template = []

    if stock_data_original is not None and not stock_data_original.empty:
        # Calculate SMA
        stock_data_analyzed = calculate_sma(stock_data_original.copy(), window=sma_window)

        # Generate recommendation
        # Use .copy() if generate_recommendation modifies the df, though current one doesn't seem to.
        recommendation_text = generate_recommendation(stock_data_analyzed, sma_window=sma_window)

        # Prepare data for template table
        # Use a consistent variable name like table_data
        if stock_data_analyzed.index.name == 'Date':
            table_data = stock_data_analyzed.reset_index().to_dict(orient='records')
        else:
            table_data = stock_data_analyzed.to_dict(orient='records')

        # Prepare data for chart
        # Create a DataFrame for charting, ensuring 'Date' is a column.
        # If 'Date' was the index, reset_index() makes it a column.
        # If 'Date' was already a column, this is fine.
        chart_df = stock_data_analyzed.reset_index() if stock_data_analyzed.index.name == 'Date' else stock_data_analyzed.copy()

        # Ensure 'Date' column exists for charting after potential reset_index or if it was already a column
        if 'Date' not in chart_df.columns:
             # This case should ideally not happen if yfinance data is consistent
             # or if data loading ensures a 'Date' column.
             # For now, creating empty lists or handling error.
            chart_dates, chart_closes, chart_smas = [], [], []
            print("Warning: 'Date' column not found in chart_df.")
        else:
            chart_dates = [d.strftime('%Y-%m-%d') for d in chart_df['Date']]
            chart_closes = [c for c in chart_df['Close']] # Assuming 'Close' column exists

            sma_col_name = f'SMA_{sma_window}'
            # Convert pd.NA or numpy.nan to None for JSON serialization (null in JS)
            chart_smas = [None if pd.isna(s) else s for s in chart_df.get(sma_col_name, [])]

        return render_template(
            'index.html',
            data=table_data,
            ticker=ticker,
            sma_window=sma_window,
            recommendation=recommendation_text,
            chart_dates=chart_dates,
            chart_closes=chart_closes,
            chart_smas=chart_smas
        )
    else:
        error_message = f"Could not retrieve sufficient data for {ticker}."
        if stock_data_original is None:
            error_message = f"Could not retrieve any data for {ticker} (data is None)."
        elif stock_data_original.empty:
            error_message = f"Retrieved data for {ticker}, but it is empty."

        # Pass empty lists for chart data in case of error to prevent template errors
        return render_template('index.html', error=error_message, ticker=ticker, recommendation=recommendation_text, chart_dates=[], chart_closes=[], chart_smas=[])

if __name__ == '__main__':
    app.run(debug=True)
