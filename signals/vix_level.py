"""
VIX Level Signal - scores current VIX against historical percentiles.
Low VIX = complacency = high score. High VIX = fear = low score.
Bonus: +5 if VIX < 15. Penalty: -10 if VIX > 30.
"""
import yfinance as yf
import numpy as np
import pandas as pd
from datetime import datetime, timedelta


def calculate_vix_level_score() -> dict:
    """
    Calculate VIX level score (0-100).

    Returns:
        dict: {
            'score': float (0-100),
            'current_vix': float,
            'percentile': float,
            'signal_name': str,
            'timestamp': str
        }
    """
    # Download 1 year of VIX data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)

    vix = yf.download('^VIX', start=start_date, end=end_date, progress=False)

    if vix.empty:
        raise ValueError("Failed to download VIX data")

    # Handle multi-index columns from yfinance
    if isinstance(vix.columns, pd.MultiIndex):
        vix.columns = vix.columns.get_level_values(0)

    current_vix = float(vix['Close'].iloc[-1])

    # Calculate percentile (lower VIX = higher percentile = higher score)
    percentile = 100 - (np.searchsorted(np.sort(vix['Close']), current_vix) / len(vix) * 100)

    # Base score from percentile
    score = percentile

    # Bonus: VIX < 15 (extreme complacency)
    if current_vix < 15:
        score = min(100, score + 5)

    # Penalty: VIX > 30 (extreme fear)
    if current_vix > 30:
        score = max(0, score - 10)

    return {
        'score': round(score, 2),
        'current_vix': round(current_vix, 2),
        'percentile': round(percentile, 2),
        'signal_name': 'VIX Level',
        'timestamp': datetime.now().isoformat()
    }


if __name__ == '__main__':
    result = calculate_vix_level_score()
    print(f"VIX Level Signal: {result['score']}/100")
    print(f"Current VIX: {result['current_vix']}")
    print(f"Percentile: {result['percentile']}")
