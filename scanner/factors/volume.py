"""
Volume Surge Factor
5-day avg volume / 20-day avg volume.
Expanding volume = institutions accumulating.
Map: 0.7 -> 0, 2.0 -> 100.
"""
import pandas as pd


def calculate_volume_score(ticker: str, data: pd.DataFrame) -> dict:
    """
    Calculate volume surge score for a ticker.

    Args:
        ticker: Stock ticker symbol
        data: DataFrame with OHLCV data (minimum 25 days)

    Returns:
        dict: {
            'ticker': str,
            'score': float (0-100),
            'vol_5d': float,
            'vol_20d': float,
            'vol_ratio': float,
            'factor_name': str
        }
    """
    if len(data) < 25:
        return {
            'ticker': ticker,
            'score': 0.0,
            'error': 'Insufficient data',
            'factor_name': 'Volume Surge'
        }

    # Calculate average volumes
    vol_5d = float(data['Volume'].iloc[-5:].mean())
    vol_20d = float(data['Volume'].iloc[-20:].mean())

    # Avoid division by zero
    if vol_20d == 0:
        return {
            'ticker': ticker,
            'score': 0.0,
            'error': 'Zero volume',
            'factor_name': 'Volume Surge'
        }

    vol_ratio = vol_5d / vol_20d

    # Map ratio to score: 0.7 -> 0, 2.0 -> 100
    if vol_ratio <= 0.7:
        score = 0.0
    elif vol_ratio >= 2.0:
        score = 100.0
    else:
        # Linear interpolation
        score = ((vol_ratio - 0.7) / (2.0 - 0.7)) * 100

    return {
        'ticker': ticker,
        'score': round(score, 2),
        'vol_5d': round(vol_5d, 0),
        'vol_20d': round(vol_20d, 0),
        'vol_ratio': round(vol_ratio, 2),
        'factor_name': 'Volume Surge'
    }
