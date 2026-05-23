"""
Momentum Crossover Factor
10-day EMA crossed above 50-day EMA in last 5 days?
Score based on gap size + 3-month return magnitude.
"""
import pandas as pd
from datetime import datetime, timedelta


def calculate_momentum_score(ticker: str, data: pd.DataFrame) -> dict:
    """
    Calculate momentum crossover score for a ticker.

    Args:
        ticker: Stock ticker symbol
        data: DataFrame with OHLCV data (minimum 90 days)

    Returns:
        dict: {
            'ticker': str,
            'score': float (0-100),
            'ema_10': float,
            'ema_50': float,
            'crossover': bool,
            'return_3m': float (percentage),
            'factor_name': str
        }
    """
    if len(data) < 90:
        return {
            'ticker': ticker,
            'score': 0.0,
            'error': 'Insufficient data',
            'factor_name': 'Momentum Crossover'
        }

    # Calculate EMAs
    ema_10 = data['Close'].ewm(span=10, adjust=False).mean()
    ema_50 = data['Close'].ewm(span=50, adjust=False).mean()

    current_ema_10 = float(ema_10.iloc[-1])
    current_ema_50 = float(ema_50.iloc[-1])

    # Check for crossover in last 5 days
    crossover = False
    for i in range(-5, 0):
        if ema_10.iloc[i-1] <= ema_50.iloc[i-1] and ema_10.iloc[i] > ema_50.iloc[i]:
            crossover = True
            break

    # Calculate 3-month return
    if len(data) >= 63:  # ~3 months of trading days
        return_3m = ((data['Close'].iloc[-1] / data['Close'].iloc[-63]) - 1) * 100
    else:
        return_3m = ((data['Close'].iloc[-1] / data['Close'].iloc[0]) - 1) * 100

    # Scoring logic
    if not crossover:
        score = 0.0
    else:
        # Base score from gap size
        gap_pct = ((current_ema_10 - current_ema_50) / current_ema_50) * 100
        gap_score = min(50, gap_pct * 100)  # Max 50 points

        # Bonus from 3-month return
        return_score = min(50, max(0, return_3m * 2))  # Max 50 points

        score = gap_score + return_score

    score = max(0, min(100, score))

    return {
        'ticker': ticker,
        'score': round(score, 2),
        'ema_10': round(current_ema_10, 2),
        'ema_50': round(current_ema_50, 2),
        'crossover': bool(crossover),
        'return_3m': round(return_3m, 2),
        'factor_name': 'Momentum Crossover'
    }
