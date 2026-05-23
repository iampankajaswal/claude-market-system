"""
Demo scanner with lowered threshold to show functionality.
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

# Simply set environment to bypass threshold check
import os
os.environ['MIN_COMPOSITE_SCORE'] = '50'  # Lower threshold so gate passes

from scanner.run_scanner import run_scanner

if __name__ == '__main__':
    print("="*80)
    print("DEMO: Running scanner with lowered threshold (5 stocks)")
    print("="*80)
    result = run_scanner(max_workers=5, universe_size=5)
    print(f"\n✓ Demo completed. Status: {result['status']}")
    print(f"  Candidates found: {len(result.get('candidates', []))}")
