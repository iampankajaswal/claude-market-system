"""
Quick test of scanner with just a few tickers.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from scanner.run_scanner import run_scanner

if __name__ == '__main__':
    # Test with just 5 tickers
    result = run_scanner(max_workers=5, universe_size=5)
    print(f"\n✓ Test completed. Status: {result['status']}")
