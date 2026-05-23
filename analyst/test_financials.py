"""
Test financial data gathering without requiring Claude API key.
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from analyst.financials import get_financial_data, format_financial_summary

if __name__ == '__main__':
    print("Testing financial data gathering...\n")

    test_ticker = 'AAPL'
    print(f"Fetching financial data for {test_ticker}...")

    data = get_financial_data(test_ticker)

    if data.get('error'):
        print(f"❌ Error: {data['error']}")
    else:
        print(f"✓ Retrieved {len(data['quarters'])} quarters of data\n")

        # Show formatted summary
        summary = format_financial_summary(data)
        print(summary)

        print(f"\n✓ Financial data gathering works!")
        print(f"  (Claude API integration ready but requires ANTHROPIC_API_KEY)")
