"""
Short Interest Decline Factor
Change in short interest vs prior period.
Note: yfinance doesn't provide short interest data reliably.
This is a placeholder that assigns a neutral score.
In production, integrate with a data provider that has short interest.
"""
import pandas as pd


def calculate_short_interest_score(ticker: str, data: pd.DataFrame) -> dict:
    """
    Calculate short interest decline score.

    Note: This is a placeholder implementation.
    Real implementation would require short interest data from:
    - FINRA data feeds
    - Quandl
    - Market data provider APIs

    Args:
        ticker: Stock ticker symbol
        data: DataFrame with OHLCV data

    Returns:
        dict: {
            'ticker': str,
            'score': float (0-100),
            'note': str,
            'factor_name': str
        }
    """
    # Placeholder: assign neutral score
    # In production, this would calculate:
    # (short_interest_current - short_interest_prior) / short_interest_prior
    # Declining short interest (negative change) = higher score

    return {
        'ticker': ticker,
        'score': 50.0,  # Neutral score
        'note': 'Short interest data not available via yfinance. Assign neutral score.',
        'factor_name': 'Short Interest Decline'
    }
