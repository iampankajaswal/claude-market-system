"""
Market Momentum Signal - SPY price vs moving averages.
Strong uptrend = high score. Downtrend = low score.
Checks: price vs 20/50/200 SMA, slope of 50-day SMA.
"""
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta


def calculate_market_momentum_score() -> dict:
    """
    Calculate market momentum score (0-100) using SPY trend analysis.

    Returns:
        dict: {
            'score': float (0-100),
            'spy_price': float,
            'sma_20': float,
            'sma_50': float,
            'sma_200': float,
            'above_20': bool,
            'above_50': bool,
            'above_200': bool,
            'sma_50_slope': float,
            'signal_name': str,
            'timestamp': str
        }
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=300)  # Extended to ensure 200 trading days

    # Download SPY data
    spy = yf.download('SPY', start=start_date, end=end_date, progress=False)

    if spy.empty or len(spy) < 200:
        raise ValueError(f"Failed to download sufficient SPY data (got {len(spy)} rows, need 200)")

    # Handle multi-index columns
    if hasattr(spy.columns, 'levels'):
        spy.columns = spy.columns.get_level_values(0)

    current_price = float(spy['Close'].iloc[-1])

    # Calculate SMAs
    sma_20 = float(spy['Close'].rolling(window=20).mean().iloc[-1])
    sma_50 = float(spy['Close'].rolling(window=50).mean().iloc[-1])
    sma_200 = float(spy['Close'].rolling(window=200).mean().iloc[-1])

    # Check if price is above each SMA
    above_20 = current_price > sma_20
    above_50 = current_price > sma_50
    above_200 = current_price > sma_200

    # Calculate 50-day SMA slope (change over last 10 days)
    sma_50_series = spy['Close'].rolling(window=50).mean()
    sma_50_slope = (sma_50_series.iloc[-1] - sma_50_series.iloc[-10]) / sma_50_series.iloc[-10] * 100

    # Scoring logic
    score = 0.0

    # +40 points if above 200-day SMA (long-term uptrend)
    if above_200:
        score += 40

    # +30 points if above 50-day SMA (intermediate uptrend)
    if above_50:
        score += 30

    # +20 points if above 20-day SMA (short-term uptrend)
    if above_20:
        score += 20

    # +10 points if 50-day SMA is rising (positive momentum)
    if sma_50_slope > 0:
        score += 10

    # Ensure score is within 0-100
    score = max(0, min(100, score))

    return {
        'score': round(score, 2),
        'spy_price': round(current_price, 2),
        'sma_20': round(sma_20, 2),
        'sma_50': round(sma_50, 2),
        'sma_200': round(sma_200, 2),
        'above_20': bool(above_20),
        'above_50': bool(above_50),
        'above_200': bool(above_200),
        'sma_50_slope': round(sma_50_slope, 2),
        'signal_name': 'Market Momentum',
        'timestamp': datetime.now().isoformat()
    }


if __name__ == '__main__':
    result = calculate_market_momentum_score()
    print(f"Market Momentum Signal: {result['score']}/100")
    print(f"SPY: ${result['spy_price']}")
    print(f"Above 20/50/200 SMA: {result['above_20']}/{result['above_50']}/{result['above_200']}")
    print(f"50-day SMA slope: {result['sma_50_slope']:+.2f}%")
