"""
L2: Quantitative Scanner
Scans S&P 500 universe and ranks by 5-factor composite score.
Only activates when macro gate is green.
"""
import json
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

import yfinance as yf
import pandas as pd
import numpy as np

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from scanner.factors.momentum import calculate_momentum_score
from scanner.factors.volume import calculate_volume_score
from scanner.factors.relative_strength import calculate_relative_strength_score
from scanner.factors.high_proximity import calculate_high_proximity_score
from scanner.factors.short_interest import calculate_short_interest_score


# S&P 500 sample (use full list in production)
SP500_TICKERS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK-B', 'V', 'JNJ',
    'WMT', 'JPM', 'MA', 'PG', 'UNH', 'HD', 'CVX', 'MRK', 'ABBV', 'KO',
    'PEP', 'COST', 'AVGO', 'ADBE', 'TMO', 'MCD', 'CSCO', 'ACN', 'LLY', 'NKE',
    'DHR', 'ABT', 'VZ', 'TXN', 'NEE', 'PM', 'CMCSA', 'DIS', 'CRM', 'BMY',
    'INTC', 'WFC', 'AMD', 'NFLX', 'QCOM', 'UPS', 'HON', 'LOW', 'RTX', 'ORCL',
    'INTU', 'BA', 'SPGI', 'CAT', 'GS', 'AXP', 'DE', 'ISRG', 'NOW', 'BKNG',
    'TJX', 'GILD', 'MMM', 'SYK', 'AMT', 'BLK', 'MDLZ', 'PLD', 'VRTX', 'CB',
    'C', 'MO', 'ADI', 'REGN', 'SBUX', 'SO', 'ZTS', 'CI', 'DUK', 'PNC',
    'CCI', 'TGT', 'BSX', 'USB', 'EOG', 'CL', 'ITW', 'HUM', 'NSC', 'APD',
    'SLB', 'ETN', 'AON', 'GE', 'D', 'FCX', 'MMC', 'EL', 'FIS', 'GM'
]


def check_macro_gate() -> dict:
    """
    Check if macro gate is green (allows scanner activation).

    Returns:
        dict: Macro gate results
    """
    macro_file = Path(__file__).parent.parent / 'data' / 'results' / 'macro_gate.json'

    if not macro_file.exists():
        print("⚠️  Macro gate results not found. Run signals/run_signals.py first.")
        return {'green_light': False, 'composite_score': 0}

    with open(macro_file) as f:
        macro_data = json.load(f)

    return macro_data


def download_stock_data(ticker: str, lookback_days: int = 300) -> pd.DataFrame:
    """
    Download historical data for a ticker.

    Args:
        ticker: Stock ticker symbol
        lookback_days: Days of history to download

    Returns:
        pd.DataFrame: OHLCV data
    """
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_days)

        data = yf.download(ticker, start=start_date, end=end_date, progress=False)

        if data.empty:
            return pd.DataFrame()

        # Handle multi-index columns
        if hasattr(data.columns, 'levels'):
            data.columns = data.columns.get_level_values(0)

        return data

    except Exception as e:
        print(f"Error downloading {ticker}: {e}")
        return pd.DataFrame()


def scan_ticker(ticker: str, spy_data: pd.DataFrame) -> dict:
    """
    Scan a single ticker and calculate composite score.

    Args:
        ticker: Stock ticker symbol
        spy_data: SPY data for relative strength calculation

    Returns:
        dict: Scan results with composite score
    """
    data = download_stock_data(ticker)

    if data.empty or len(data) < 90:
        return {
            'ticker': ticker,
            'composite_score': 0.0,
            'error': 'Insufficient data',
            'factors': []
        }

    # Calculate all factor scores
    factors = []

    try:
        momentum = calculate_momentum_score(ticker, data)
        factors.append(momentum)
    except Exception as e:
        factors.append({'factor_name': 'Momentum Crossover', 'score': 0.0, 'error': str(e)})

    try:
        volume = calculate_volume_score(ticker, data)
        factors.append(volume)
    except Exception as e:
        factors.append({'factor_name': 'Volume Surge', 'score': 0.0, 'error': str(e)})

    try:
        rel_strength = calculate_relative_strength_score(ticker, data, spy_data)
        factors.append(rel_strength)
    except Exception as e:
        factors.append({'factor_name': 'Relative Strength', 'score': 0.0, 'error': str(e)})

    try:
        high_prox = calculate_high_proximity_score(ticker, data)
        factors.append(high_prox)
    except Exception as e:
        factors.append({'factor_name': '52-Week High Proximity', 'score': 0.0, 'error': str(e)})

    try:
        short_int = calculate_short_interest_score(ticker, data)
        factors.append(short_int)
    except Exception as e:
        factors.append({'factor_name': 'Short Interest Decline', 'score': 0.0, 'error': str(e)})

    # Calculate composite score (equal weight)
    scores = [f.get('score', 0.0) for f in factors]
    composite_score = sum(scores) / len(scores) if scores else 0.0

    return {
        'ticker': ticker,
        'composite_score': round(composite_score, 2),
        'factors': factors,
        'timestamp': datetime.now().isoformat()
    }


def run_scanner(max_workers: int = 10, universe_size: int = 100) -> dict:
    """
    Run the quantitative scanner on S&P 500 universe.

    Args:
        max_workers: Number of parallel download threads
        universe_size: Number of stocks to scan

    Returns:
        dict: Scanner results with ranked candidates
    """
    print("Running L2: Quantitative Scanner...\n")

    # Check macro gate
    macro_gate = check_macro_gate()
    print(f"Macro Gate Status: {'🟢 GREEN' if macro_gate.get('green_light') else '🔴 RED'}")
    print(f"Composite Score: {macro_gate.get('composite_score', 0):.2f}/100\n")

    # Get scanner mode from environment
    scanner_mode = os.getenv('SCANNER_MODE', 'REDUCED').upper()
    print(f"Scanner Mode: {scanner_mode}")

    if scanner_mode == 'DEFENSIVE' or not macro_gate.get('green_light'):
        print("❌ Scanner disabled (macro gate RED or DEFENSIVE mode)\n")
        return {
            'status': 'disabled',
            'reason': 'Macro gate red or defensive mode',
            'macro_gate': macro_gate,
            'candidates': [],
            'timestamp': datetime.now().isoformat()
        }

    print(f"✓ Scanner activated. Scanning {min(universe_size, len(SP500_TICKERS))} stocks...\n")

    # Download SPY data for relative strength calculation
    print("Downloading SPY data...")
    spy_data = download_stock_data('SPY')

    if spy_data.empty:
        print("❌ Failed to download SPY data\n")
        return {
            'status': 'error',
            'reason': 'Failed to download SPY data',
            'candidates': [],
            'timestamp': datetime.now().isoformat()
        }

    # Scan tickers in parallel
    tickers = SP500_TICKERS[:universe_size]
    scan_results = []

    print(f"Scanning {len(tickers)} tickers (parallel: {max_workers} workers)...")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(scan_ticker, ticker, spy_data): ticker
                   for ticker in tickers}

        for i, future in enumerate(as_completed(futures), 1):
            result = future.result()
            scan_results.append(result)
            if i % 10 == 0:
                print(f"  Scanned {i}/{len(tickers)} tickers...")

    print(f"✓ Scanned {len(scan_results)} tickers\n")

    # Filter and rank results
    valid_results = [r for r in scan_results if r.get('composite_score', 0) > 0]
    valid_results.sort(key=lambda x: x['composite_score'], reverse=True)

    # Apply REDUCED mode filter (only surface > 75)
    if scanner_mode == 'REDUCED':
        filtered_results = [r for r in valid_results if r['composite_score'] > 75]
        print(f"REDUCED mode: {len(filtered_results)} candidates above 75 threshold")
    else:
        filtered_results = valid_results
        print(f"NORMAL mode: {len(filtered_results)} candidates")

    # Display top candidates
    print(f"\n{'='*80}")
    print(f"TOP CANDIDATES (showing top 10):")
    print(f"{'='*80}")

    for i, result in enumerate(filtered_results[:10], 1):
        print(f"{i}. {result['ticker']:6} - Score: {result['composite_score']:.2f}/100")
        for factor in result.get('factors', []):
            fname = factor.get('factor_name', 'Unknown')
            fscore = factor.get('score', 0)
            print(f"     {fname:30} {fscore:6.2f}")
        print()

    print(f"{'='*80}\n")

    result = {
        'status': 'success',
        'macro_gate': macro_gate,
        'scanner_mode': scanner_mode,
        'tickers_scanned': len(scan_results),
        'candidates': filtered_results,
        'timestamp': datetime.now().isoformat()
    }

    # Save results
    save_results(result)

    return result


def save_results(result: dict):
    """Save scanner results to JSON file."""
    output_dir = Path(__file__).parent.parent / 'data' / 'results'
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / 'scanner_results.json'

    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"Results saved to: {output_file}")


if __name__ == '__main__':
    result = run_scanner(max_workers=10, universe_size=100)

    if result['status'] == 'success':
        print(f"\nScanner Summary:")
        print(f"  Tickers Scanned: {result['tickers_scanned']}")
        print(f"  Candidates Found: {len(result['candidates'])}")
        print(f"  Mode: {result['scanner_mode']}")
