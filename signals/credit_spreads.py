"""
Credit Spreads Signal - HYG vs TLT spread proxy.
Uses z-score against 1-year history.
Tight spreads (z = -2) -> 100 (risk-on).
Wide spreads (z = +2) -> 0 (risk-off).
"""
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta


def calculate_credit_spreads_score() -> dict:
    """
    Calculate credit spreads score (0-100) using HYG/TLT ratio.

    Returns:
        dict: {
            'score': float (0-100),
            'current_spread': float,
            'z_score': float,
            'hyg_price': float,
            'tlt_price': float,
            'signal_name': str,
            'timestamp': str
        }
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)

    # Download HYG (high yield bonds) and TLT (long-term treasuries)
    hyg = yf.download('HYG', start=start_date, end=end_date, progress=False)
    tlt = yf.download('TLT', start=start_date, end=end_date, progress=False)

    if hyg.empty or tlt.empty:
        raise ValueError("Failed to download credit spreads data")

    # Handle multi-index columns
    if hasattr(hyg.columns, 'levels'):
        hyg.columns = hyg.columns.get_level_values(0)
    if hasattr(tlt.columns, 'levels'):
        tlt.columns = tlt.columns.get_level_values(0)

    # Calculate spread proxy: HYG/TLT ratio
    # Higher ratio = tighter spreads = risk-on
    spread_ratio = hyg['Close'] / tlt['Close']

    current_spread = float(spread_ratio.iloc[-1])
    mean_spread = float(spread_ratio.mean())
    std_spread = float(spread_ratio.std())

    # Calculate z-score
    z_score = (current_spread - mean_spread) / std_spread

    # Map z-score to score: -2 -> 100, +2 -> 0
    # Inverted because low z-score (below mean) = wider spreads = risk-off
    if z_score <= -2:
        score = 100.0
    elif z_score >= 2:
        score = 0.0
    else:
        # Linear map from [-2, 2] to [100, 0]
        score = 100 - ((z_score + 2) / 4) * 100

    return {
        'score': round(score, 2),
        'current_spread': round(current_spread, 4),
        'z_score': round(z_score, 2),
        'hyg_price': round(hyg['Close'].iloc[-1], 2),
        'tlt_price': round(tlt['Close'].iloc[-1], 2),
        'signal_name': 'Credit Spreads',
        'timestamp': datetime.now().isoformat()
    }


if __name__ == '__main__':
    result = calculate_credit_spreads_score()
    print(f"Credit Spreads Signal: {result['score']}/100")
    print(f"HYG/TLT Ratio: {result['current_spread']} (z-score: {result['z_score']})")
    print(f"HYG: ${result['hyg_price']}, TLT: ${result['tlt_price']}")
