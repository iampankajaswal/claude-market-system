"""
Relative Strength vs SPY Factor
20-day stock return minus 20-day SPY return.
Outperforming market = higher score.
Percentile rank the spread.
"""
import pandas as pd


def calculate_relative_strength_score(ticker: str, data: pd.DataFrame, spy_data: pd.DataFrame) -> dict:
    """
    Calculate relative strength score vs SPY.

    Args:
        ticker: Stock ticker symbol
        data: DataFrame with stock OHLCV data (minimum 20 days)
        spy_data: DataFrame with SPY OHLCV data (minimum 20 days)

    Returns:
        dict: {
            'ticker': str,
            'score': float (0-100),
            'stock_return': float (percentage),
            'spy_return': float (percentage),
            'spread': float (percentage points),
            'factor_name': str
        }
    """
    if len(data) < 20 or len(spy_data) < 20:
        return {
            'ticker': ticker,
            'score': 0.0,
            'error': 'Insufficient data',
            'factor_name': 'Relative Strength'
        }

    # Calculate 20-day returns
    stock_return = ((data['Close'].iloc[-1] / data['Close'].iloc[-20]) - 1) * 100
    spy_return = ((spy_data['Close'].iloc[-1] / spy_data['Close'].iloc[-20]) - 1) * 100

    spread = stock_return - spy_return

    # Simple mapping: outperformance > 10% = 100, underperformance < -10% = 0
    if spread >= 10:
        score = 100.0
    elif spread <= -10:
        score = 0.0
    else:
        # Linear map from [-10, 10] to [0, 100]
        score = ((spread + 10) / 20) * 100

    return {
        'ticker': ticker,
        'score': round(score, 2),
        'stock_return': round(stock_return, 2),
        'spy_return': round(spy_return, 2),
        'spread': round(spread, 2),
        'factor_name': 'Relative Strength'
    }
