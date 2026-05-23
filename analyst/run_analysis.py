"""
L3: Claude Analyst Runner
Runs fundamental analysis on scanner candidates and blends scores.
"""
import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent))

from analyst.analyzer import ClaudeAnalyst
from analyst.blender import blend_scores, format_blended_results, get_divergence_insights
from analyst.cache import AnalysisCache


def load_scanner_results() -> dict:
    """Load scanner results from L2."""
    results_file = Path(__file__).parent.parent / 'data' / 'results' / 'scanner_results.json'

    if not results_file.exists():
        print("⚠️  Scanner results not found. Run scanner/run_scanner.py first.")
        return {'candidates': []}

    with open(results_file) as f:
        return json.load(f)


def run_analysis(max_candidates: int = 20, force_refresh: bool = False) -> dict:
    """
    Run Claude analysis on scanner candidates.

    Args:
        max_candidates: Maximum number of candidates to analyze (cost control)
        force_refresh: Skip cache and force new API calls

    Returns:
        dict: Analysis results with blended rankings
    """
    print("Running L3: Claude Analyst...\n")

    # Load scanner results
    scanner_results = load_scanner_results()
    candidates = scanner_results.get('candidates', [])

    if not candidates:
        print("❌ No candidates to analyze (scanner returned empty list)\n")
        return {
            'status': 'no_candidates',
            'blended_results': [],
            'timestamp': datetime.now().isoformat()
        }

    # Limit candidates for cost control
    if len(candidates) > max_candidates:
        print(f"ℹ️  Limiting to top {max_candidates} candidates (cost control)")
        candidates = candidates[:max_candidates]

    print(f"Analyzing {len(candidates)} candidates with Claude API...")
    print(f"Cache: {'Disabled (force refresh)' if force_refresh else 'Enabled'}\n")

    # Initialize analyst
    try:
        analyst = ClaudeAnalyst(use_cache=not force_refresh)
    except ValueError as e:
        print(f"❌ {e}")
        print("Set ANTHROPIC_API_KEY environment variable")
        return {
            'status': 'error',
            'error': str(e),
            'blended_results': [],
            'timestamp': datetime.now().isoformat()
        }

    # Analyze each candidate
    tickers = [c['ticker'] for c in candidates]
    analyses = analyst.analyze_batch(tickers)

    print(f"\n✓ Analyzed {len(analyses)} tickers\n")

    # Show cache stats
    if not force_refresh:
        cache = AnalysisCache()
        stats = cache.get_stats()
        print(f"Cache stats: {stats['total_entries']} entries, {stats['unique_tickers']} unique tickers")

    # Blend scores
    print("\nBlending scores (60% quant + 40% Claude)...\n")
    blended = blend_scores(candidates, analyses)

    # Display results
    print(format_blended_results(blended))

    # Get divergence insights
    insights = get_divergence_insights(blended)

    # Prepare result
    result = {
        'status': 'success',
        'scanner_results': scanner_results,
        'analyses': analyses,
        'blended_results': blended,
        'divergence_insights': insights,
        'timestamp': datetime.now().isoformat()
    }

    # Save results
    save_results(result)

    return result


def save_results(result: dict):
    """Save analysis results to JSON file."""
    output_dir = Path(__file__).parent.parent / 'data' / 'results'
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / 'analyst_results.json'

    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"\nResults saved to: {output_file}")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Run Claude fundamental analysis')
    parser.add_argument('--max-candidates', type=int, default=20,
                        help='Maximum candidates to analyze (default: 20)')
    parser.add_argument('--force-refresh', action='store_true',
                        help='Skip cache and force new API calls')

    args = parser.parse_args()

    result = run_analysis(
        max_candidates=args.max_candidates,
        force_refresh=args.force_refresh
    )

    if result['status'] == 'success':
        insights = result['divergence_insights']
        print(f"\n{'='*80}")
        print("KEY INSIGHTS")
        print(f"{'='*80}")
        print(f"Candidates analyzed: {len(result['blended_results'])}")
        print(f"Significant upgrades: {len(insights['upgrades'])}")
        print(f"Significant downgrades: {len(insights['downgrades'])}")
