"""
Macro Deployment Gate Runner
Calculates composite score from all 6 signals and determines deployment zone.
"""
import json
import os
from datetime import datetime
from pathlib import Path

from .vix_level import calculate_vix_level_score
from .vix_term_structure import calculate_vix_term_structure_score
from .breadth import calculate_breadth_score
from .credit_spreads import calculate_credit_spreads_score
from .put_call import calculate_put_call_score
from .market_momentum import calculate_market_momentum_score


DEPLOYMENT_ZONES = {
    'DEFENSIVE': (0, 40),
    'REDUCED': (40, 60),
    'NORMAL': (60, 75),
    'AGGRESSIVE': (75, 100)
}


def calculate_composite_score(signal_results: list) -> float:
    """
    Calculate composite score as equal-weighted average of all signals.

    Args:
        signal_results: List of signal result dictionaries

    Returns:
        float: Composite score (0-100)
    """
    scores = [result['score'] for result in signal_results]
    return sum(scores) / len(scores)


def determine_deployment_zone(composite_score: float) -> str:
    """
    Map composite score to deployment zone.

    Args:
        composite_score: Composite score (0-100)

    Returns:
        str: Deployment zone name
    """
    for zone, (low, high) in DEPLOYMENT_ZONES.items():
        if low <= composite_score < high:
            return zone

    return 'AGGRESSIVE'


def run_macro_gate() -> dict:
    """
    Run all 6 macro signals and calculate composite score.

    Returns:
        dict: {
            'composite_score': float,
            'deployment_zone': str,
            'green_light': bool,
            'signals': list of signal results,
            'timestamp': str
        }
    """
    print("Running L1: Macro Deployment Gate...\n")

    # Run all signals
    signal_functions = [
        ('VIX Level', calculate_vix_level_score),
        ('VIX Term Structure', calculate_vix_term_structure_score),
        ('Market Breadth', calculate_breadth_score),
        ('Credit Spreads', calculate_credit_spreads_score),
        ('Put/Call Sentiment', calculate_put_call_score),
        ('Market Momentum', calculate_market_momentum_score)
    ]

    signal_results = []
    for name, func in signal_functions:
        try:
            result = func()
            signal_results.append(result)
            print(f"✓ {name}: {result['score']:.2f}/100")
        except Exception as e:
            print(f"✗ {name}: ERROR - {e}")
            signal_results.append({
                'signal_name': name,
                'score': 0,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })

    # Calculate composite score
    composite_score = calculate_composite_score(signal_results)
    deployment_zone = determine_deployment_zone(composite_score)

    # Determine if green light (NORMAL or AGGRESSIVE)
    green_light = deployment_zone in ['NORMAL', 'AGGRESSIVE']

    # Get threshold from environment or use default
    min_threshold = float(os.getenv('MIN_COMPOSITE_SCORE', '60'))
    green_light_threshold = composite_score >= min_threshold

    print(f"\n{'='*60}")
    print(f"COMPOSITE SCORE: {composite_score:.2f}/100")
    print(f"DEPLOYMENT ZONE: {deployment_zone}")
    print(f"GREEN LIGHT: {'🟢 YES' if green_light_threshold else '🔴 NO'} (threshold: {min_threshold})")
    print(f"{'='*60}\n")

    result = {
        'composite_score': round(composite_score, 2),
        'deployment_zone': deployment_zone,
        'green_light': bool(green_light_threshold),
        'signals': signal_results,
        'timestamp': datetime.now().isoformat(),
        'threshold': float(min_threshold)
    }

    # Save results
    save_results(result)

    return result


def save_results(result: dict):
    """Save results to JSON file."""
    output_dir = Path(__file__).parent.parent / 'data' / 'results'
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / 'macro_gate.json'

    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"Results saved to: {output_file}")


if __name__ == '__main__':
    result = run_macro_gate()

    # Display zone descriptions
    print("\nDeployment Zone Guide:")
    print("  DEFENSIVE (0-40):   High risk. No new positions.")
    print("  REDUCED (40-60):    Elevated risk. Reduce exposure.")
    print("  NORMAL (60-75):     Favorable conditions. Standard deployment.")
    print("  AGGRESSIVE (75-100): Ideal conditions. Maximum deployment.")
