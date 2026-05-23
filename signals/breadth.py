"""
Market Breadth Signal - % of S&P 500 stocks above 200-day SMA.
80%+ -> 100 score (healthy broad rally).
30%- -> 0 score (narrow market, few leaders).
"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed


# S&P 500 tickers (representative sample for performance - use full list in production)
SP500_SAMPLE = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK-B', 'V', 'JNJ',
    'WMT', 'JPM', 'MA', 'PG', 'UNH', 'HD', 'CVX', 'MRK', 'ABBV', 'KO',
    'PEP', 'COST', 'AVGO', 'ADBE', 'TMO', 'MCD', 'CSCO', 'ACN', 'LLY', 'NKE',
    'DHR', 'ABT', 'VZ', 'TXN', 'NEE', 'PM', 'CMCSA', 'DIS', 'CRM', 'BMY',
    'INTC', 'WFC', 'AMD', 'NFLX', 'QCOM', 'UPS', 'HON', 'LOW', 'RTX', 'ORCL'
]


def check_stock_above_sma(ticker: str, lookback_days: int = 250) -> bool:
    """
    Check if a stock is trading above its 200-day SMA.

    Args:
        ticker: Stock ticker symbol
        lookback_days: Days of history to download (default 250 for 200-day SMA)

    Returns:
        bool: True if current price > 200-day SMA, False otherwise
    """
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_days)

        data = yf.download(ticker, start=start_date, end=end_date, progress=False)

        if data.empty or len(data) < 200:
            return False

        # Handle multi-index columns
        if hasattr(data.columns, 'levels'):
            data.columns = data.columns.get_level_values(0)

        current_price = float(data['Close'].iloc[-1])
        sma_200 = float(data['Close'].rolling(window=200).mean().iloc[-1])

        return current_price > sma_200

    except Exception:
        return False


def calculate_breadth_score(sample_size: int = 50) -> dict:
    """
    Calculate market breadth score (0-100).

    Args:
        sample_size: Number of stocks to sample from S&P 500

    Returns:
        dict: {
            'score': float (0-100),
            'pct_above_sma': float,
            'stocks_above': int,
            'stocks_checked': int,
            'signal_name': str,
            'timestamp': str
        }
    """
    tickers = SP500_SAMPLE[:sample_size]

    # Check stocks in parallel
    stocks_above = 0
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(check_stock_above_sma, ticker): ticker
                   for ticker in tickers}

        for future in as_completed(futures):
            if future.result():
                stocks_above += 1

    pct_above = (stocks_above / len(tickers)) * 100

    # Map percentage to score: 80%+ -> 100, 30%- -> 0
    if pct_above >= 80:
        score = 100.0
    elif pct_above <= 30:
        score = 0.0
    else:
        # Linear map from [30, 80] to [0, 100]
        score = ((pct_above - 30) / (80 - 30)) * 100

    return {
        'score': round(score, 2),
        'pct_above_sma': round(pct_above, 2),
        'stocks_above': stocks_above,
        'stocks_checked': len(tickers),
        'signal_name': 'Market Breadth',
        'timestamp': datetime.now().isoformat()
    }


if __name__ == '__main__':
    result = calculate_breadth_score()
    print(f"Market Breadth Signal: {result['score']}/100")
    print(f"{result['pct_above_sma']}% above 200-day SMA ({result['stocks_above']}/{result['stocks_checked']})")
