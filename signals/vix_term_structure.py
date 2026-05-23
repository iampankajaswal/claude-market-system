"""
VIX Term Structure Signal - measures contango vs backwardation.
Ratio = VIX / VIX3M. Below 1.0 = contango = calm = high score.
Above 1.0 = backwardation = stress = low score.
Map: 0.85 -> 100, 1.15 -> 0 (linear interpolation).
"""
import yfinance as yf
from datetime import datetime, timedelta


def calculate_vix_term_structure_score() -> dict:
    """
    Calculate VIX term structure score (0-100).

    Returns:
        dict: {
            'score': float (0-100),
            'vix': float,
            'vix3m': float,
            'ratio': float,
            'structure': str ('contango' or 'backwardation'),
            'signal_name': str,
            'timestamp': str
        }
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=5)

    # Download VIX and VIX3M
    vix = yf.download('^VIX', start=start_date, end=end_date, progress=False)
    vix3m = yf.download('^VIX3M', start=start_date, end=end_date, progress=False)

    if vix.empty or vix3m.empty:
        raise ValueError("Failed to download VIX term structure data")

    # Handle multi-index columns
    if hasattr(vix.columns, 'levels'):
        vix.columns = vix.columns.get_level_values(0)
    if hasattr(vix3m.columns, 'levels'):
        vix3m.columns = vix3m.columns.get_level_values(0)

    current_vix = float(vix['Close'].iloc[-1])
    current_vix3m = float(vix3m['Close'].iloc[-1])

    # Calculate ratio
    ratio = current_vix / current_vix3m

    # Determine structure
    if ratio < 1.0:
        structure = 'contango'
    else:
        structure = 'backwardation'

    # Map ratio to score: 0.85 -> 100, 1.15 -> 0
    # Linear interpolation
    if ratio <= 0.85:
        score = 100.0
    elif ratio >= 1.15:
        score = 0.0
    else:
        # Linear map from [0.85, 1.15] to [100, 0]
        score = 100 - ((ratio - 0.85) / (1.15 - 0.85)) * 100

    return {
        'score': round(score, 2),
        'vix': round(current_vix, 2),
        'vix3m': round(current_vix3m, 2),
        'ratio': round(ratio, 4),
        'structure': structure,
        'signal_name': 'VIX Term Structure',
        'timestamp': datetime.now().isoformat()
    }


if __name__ == '__main__':
    result = calculate_vix_term_structure_score()
    print(f"VIX Term Structure Signal: {result['score']}/100")
    print(f"VIX: {result['vix']}, VIX3M: {result['vix3m']}")
    print(f"Ratio: {result['ratio']} ({result['structure']})")
