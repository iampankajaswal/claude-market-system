"""
Main Orchestrator: Run full end-to-end analysis pipeline.
Executes L1 → L2 → L3 in sequence with proper gating.
"""
import argparse
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from signals.run_signals import run_macro_gate
from scanner.run_scanner import run_scanner
from analyst.run_analysis import run_analysis


def main():
    parser = argparse.ArgumentParser(
        description='Claude Market System - Full Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full pipeline (L1 + L2 + L3)
  python run_analysis.py --scan-and-analyze

  # Run only L1 (macro gate)
  python run_analysis.py --signals-only

  # Run L1 + L2 (skip Claude analysis)
  python run_analysis.py --scan-only

  # Run L3 only (requires existing scanner results)
  python run_analysis.py --analyze-only

  # Force refresh Claude cache
  python run_analysis.py --scan-and-analyze --force-refresh
        """
    )

    parser.add_argument(
        '--scan-and-analyze',
        action='store_true',
        help='Run full pipeline: L1 → L2 → L3'
    )

    parser.add_argument(
        '--signals-only',
        action='store_true',
        help='Run L1 only (macro deployment gate)'
    )

    parser.add_argument(
        '--scan-only',
        action='store_true',
        help='Run L1 + L2 (skip Claude analysis)'
    )

    parser.add_argument(
        '--analyze-only',
        action='store_true',
        help='Run L3 only (requires existing scanner results)'
    )

    parser.add_argument(
        '--max-candidates',
        type=int,
        default=20,
        help='Maximum candidates to analyze in L3 (default: 20)'
    )

    parser.add_argument(
        '--force-refresh',
        action='store_true',
        help='Force refresh Claude API cache'
    )

    parser.add_argument(
        '--universe-size',
        type=int,
        default=100,
        help='Number of stocks to scan in L2 (default: 100)'
    )

    args = parser.parse_args()

    # Determine what to run
    if not any([args.scan_and_analyze, args.signals_only, args.scan_only, args.analyze_only]):
        parser.print_help()
        sys.exit(1)

    print("="*80)
    print("CLAUDE MARKET SYSTEM - Full Pipeline")
    print("="*80)
    print()

    # L1: Macro Gate
    if args.signals_only or args.scan_only or args.scan_and_analyze:
        print("🔄 Running L1: Macro Deployment Gate...")
        print("-"*80)
        macro_result = run_macro_gate()
        print()

        if not macro_result.get('green_light'):
            print("⚠️  Macro gate is RED. Scanner will be disabled.")
            if args.signals_only:
                print("✅ L1 complete. Exiting (signals-only mode).")
                return
            elif args.scan_only or args.scan_and_analyze:
                print("Continuing with scanner (will show disabled status)...")
                print()

    # L2: Scanner
    if args.scan_only or args.scan_and_analyze:
        print("🔄 Running L2: Quantitative Scanner...")
        print("-"*80)
        scanner_result = run_scanner(universe_size=args.universe_size)
        print()

        if scanner_result.get('status') == 'disabled':
            print("❌ Scanner disabled. Cannot proceed to L3.")
            print("✅ L1 + L2 complete. Exiting.")
            return

        candidates = scanner_result.get('candidates', [])
        if not candidates:
            print("⚠️  No candidates found. Cannot proceed to L3.")
            print("✅ L1 + L2 complete. Exiting.")
            return

        if args.scan_only:
            print("✅ L1 + L2 complete. Exiting (scan-only mode).")
            return

    # L3: Claude Analyst
    if args.scan_and_analyze or args.analyze_only:
        print("🔄 Running L3: Claude Analyst...")
        print("-"*80)

        try:
            analyst_result = run_analysis(
                max_candidates=args.max_candidates,
                force_refresh=args.force_refresh
            )
            print()

            if analyst_result.get('status') == 'success':
                print("✅ L3 complete.")
            else:
                print(f"⚠️  L3 status: {analyst_result.get('status')}")

        except Exception as e:
            print(f"❌ L3 failed: {e}")
            print("Check ANTHROPIC_API_KEY environment variable.")
            sys.exit(1)

    print()
    print("="*80)
    print("✅ PIPELINE COMPLETE")
    print("="*80)
    print()
    print("View results:")
    print("  - Dashboard: streamlit run dashboard/app.py")
    print("  - L1 JSON: data/results/macro_gate.json")
    print("  - L2 JSON: data/results/scanner_results.json")
    print("  - L3 JSON: data/results/analyst_results.json")
    print()


if __name__ == '__main__':
    main()
