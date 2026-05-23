"""
Put/Call Sentiment Signal - VIX 20-day rate of change as proxy.
Rapidly rising VIX = fear = low score.
Stable or declining VIX = complacency = high score.
ROC -30% -> 100, ROC +50% -> 0.
"""
import yfinance as yf
from datetime import datetime, timedelta


def calculate_put_call_score() -> dict:
    """
    Calculate put/call sentiment score (0-100) using VIX rate of change.

    Returns:
        dict: {
            'score': float (0-100),
            'vix_current': float,
            'vix_20d_ago': float,
            'roc_pct': float,
            'signal_name': str,
            'timestamp': str
        }
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    # Download VIX data
    vix = yf.download('^VIX', start=start_date, end=end_date, progress=False)

    if vix.empty or len(vix) < 20:
        raise ValueError("Failed to download sufficient VIX data for ROC calculation")

    # Handle multi-index columns
    if hasattr(vix.columns, 'levels'):
        vix.columns = vix.columns.get_level_values(0)

    current_vix = float(vix['Close'].iloc[-1])
    vix_20d_ago = float(vix['Close'].iloc[-20] if len(vix) >= 20 else vix['Close'].iloc[0])

    # Calculate 20-day rate of change
    roc_pct = ((current_vix - vix_20d_ago) / vix_20d_ago) * 100

    # Map ROC to score: -30% -> 100, +50% -> 0
    if roc_pct <= -30:
        score = 100.0
    elif roc_pct >= 50:
        score = 0.0
    else:
        # Linear map from [-30, 50] to [100, 0]
        score = 100 - ((roc_pct + 30) / 80) * 100

    return {
        'score': round(score, 2),
        'vix_current': round(current_vix, 2),
        'vix_20d_ago': round(vix_20d_ago, 2),
        'roc_pct': round(roc_pct, 2),
        'signal_name': 'Put/Call Sentiment',
        'timestamp': datetime.now().isoformat()
    }


if __name__ == '__main__':
    result = calculate_put_call_score()
    print(f"Put/Call Sentiment Signal: {result['score']}/100")
    print(f"VIX ROC (20d): {result['roc_pct']:+.2f}%")
    print(f"Current VIX: {result['vix_current']}, 20d ago: {result['vix_20d_ago']}")
