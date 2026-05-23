"""
52-Week High Proximity Factor
Current price / 52-week high.
Above 0.95 scores highest (George & Hwang 2004).
"""
import pandas as pd


def calculate_high_proximity_score(ticker: str, data: pd.DataFrame) -> dict:
    """
    Calculate 52-week high proximity score.

    Args:
        ticker: Stock ticker symbol
        data: DataFrame with OHLCV data (minimum 252 days for 52 weeks)

    Returns:
        dict: {
            'ticker': str,
            'score': float (0-100),
            'current_price': float,
            'high_52w': float,
            'proximity': float (ratio),
            'factor_name': str
        }
    """
    if len(data) < 200:  # At least ~40 weeks
        return {
            'ticker': ticker,
            'score': 0.0,
            'error': 'Insufficient data',
            'factor_name': '52-Week High Proximity'
        }

    current_price = float(data['Close'].iloc[-1])

    # Use available data (up to 252 days)
    lookback = min(252, len(data))
    high_52w = float(data['High'].iloc[-lookback:].max())

    proximity = current_price / high_52w

    # Scoring: exponential increase above 0.95
    if proximity >= 0.95:
        score = 100.0
    elif proximity >= 0.90:
        # 90-95% range: 70-100 score
        score = 70 + ((proximity - 0.90) / 0.05) * 30
    elif proximity >= 0.80:
        # 80-90% range: 40-70 score
        score = 40 + ((proximity - 0.80) / 0.10) * 30
    else:
        # Below 80%: 0-40 score
        score = (proximity / 0.80) * 40

    score = max(0, min(100, score))

    return {
        'ticker': ticker,
        'score': round(score, 2),
        'current_price': round(current_price, 2),
        'high_52w': round(high_52w, 2),
        'proximity': round(proximity, 4),
        'factor_name': '52-Week High Proximity'
    }
