"""
Score Blender: 60% Quantitative + 40% Claude Fundamental
Identifies rank divergence (disagreement = insight)
"""
from typing import List, Dict, Optional


def blend_scores(candidates: List[Dict], analyses: List[Dict]) -> List[Dict]:
    """
    Blend quantitative scanner scores with Claude fundamental scores.

    Formula: 60% quant_score + 40% claude_score
    Flag divergence: rank change >= 3 positions

    Args:
        candidates: Scanner results with composite_score
        analyses: Claude analysis results with claude_score

    Returns:
        list: Blended results sorted by blended_score, with divergence flags
    """
    # Create lookup for Claude scores
    claude_lookup = {a['ticker']: a for a in analyses}

    # Build blended results
    blended = []
    for candidate in candidates:
        ticker = candidate['ticker']
        quant_score = candidate.get('composite_score', 0)

        # Get Claude score
        claude_analysis = claude_lookup.get(ticker)
        if not claude_analysis or claude_analysis.get('error'):
            # If no Claude score, use only quant score
            blended_score = quant_score
            claude_score = None
        else:
            claude_score = claude_analysis.get('claude_score', 0)
            blended_score = (0.6 * quant_score) + (0.4 * claude_score)

        blended.append({
            'ticker': ticker,
            'quant_score': quant_score,
            'claude_score': claude_score,
            'blended_score': round(blended_score, 2),
            'quant_rank': None,  # Will be set after sorting
            'blended_rank': None,
            'rank_change': None,
            'divergence_flag': None,
            'candidate_data': candidate,
            'claude_analysis': claude_analysis
        })

    # Sort by quant score and assign ranks
    blended_by_quant = sorted(blended, key=lambda x: x['quant_score'], reverse=True)
    for i, item in enumerate(blended_by_quant, 1):
        item['quant_rank'] = i

    # Sort by blended score and assign ranks
    blended_by_blend = sorted(blended, key=lambda x: x['blended_score'], reverse=True)
    for i, item in enumerate(blended_by_blend, 1):
        item['blended_rank'] = i

    # Calculate rank changes and flag divergences
    for item in blended:
        if item['claude_score'] is not None:
            rank_change = item['quant_rank'] - item['blended_rank']
            item['rank_change'] = rank_change

            # Flag if rank changed by 3+ positions
            if abs(rank_change) >= 3:
                if rank_change > 0:
                    item['divergence_flag'] = 'UPGRADE'  # Claude sees more value
                else:
                    item['divergence_flag'] = 'DOWNGRADE'  # Claude sees less value
            else:
                item['divergence_flag'] = 'ALIGNED'
        else:
            item['divergence_flag'] = 'NO_CLAUDE_DATA'

    return blended_by_blend


def format_blended_results(blended: List[Dict], top_n: int = 20) -> str:
    """
    Format blended results for display.

    Args:
        blended: Blended results from blend_scores()
        top_n: Number of top results to display

    Returns:
        str: Formatted output
    """
    output = []
    output.append("=" * 100)
    output.append("BLENDED RANKINGS (60% Quant + 40% Claude)")
    output.append("=" * 100)
    output.append(f"{'Rank':>4} {'Ticker':>6} {'Blended':>8} {'Quant':>7} {'Claude':>7} {'ΔRank':>7} {'Flag':>12}")
    output.append("-" * 100)

    for i, item in enumerate(blended[:top_n], 1):
        ticker = item['ticker']
        blended_score = item['blended_score']
        quant_score = item['quant_score']
        claude_score = item['claude_score'] if item['claude_score'] is not None else 'N/A'
        rank_change = item['rank_change'] if item['rank_change'] is not None else 'N/A'
        flag = item['divergence_flag']

        # Add emoji for divergence flags
        flag_display = flag
        if flag == 'UPGRADE':
            flag_display = '🟢 UPGRADE'
        elif flag == 'DOWNGRADE':
            flag_display = '🔴 DOWNGRADE'
        elif flag == 'ALIGNED':
            flag_display = '⚪ ALIGNED'

        claude_display = f"{claude_score:>7.2f}" if isinstance(claude_score, (int, float)) else f"{claude_score:>7}"
        rank_display = f"{rank_change:>+3}" if isinstance(rank_change, int) else f"{rank_change:>7}"

        output.append(
            f"{i:>4} {ticker:>6} {blended_score:>8.2f} {quant_score:>7.2f} "
            f"{claude_display} {rank_display} {flag_display:>20}"
        )

    output.append("=" * 100)

    # Summary of divergences
    upgrades = [x for x in blended if x['divergence_flag'] == 'UPGRADE']
    downgrades = [x for x in blended if x['divergence_flag'] == 'DOWNGRADE']

    output.append(f"\nDivergence Summary:")
    output.append(f"  🟢 Upgrades (Claude more bullish): {len(upgrades)}")
    output.append(f"  🔴 Downgrades (Claude more bearish): {len(downgrades)}")

    if upgrades:
        output.append(f"\n  Top Upgrades:")
        for item in sorted(upgrades, key=lambda x: x['rank_change'], reverse=True)[:5]:
            output.append(f"    {item['ticker']:>6}: +{item['rank_change']} positions")

    if downgrades:
        output.append(f"\n  Top Downgrades:")
        for item in sorted(downgrades, key=lambda x: x['rank_change'])[:5]:
            output.append(f"    {item['ticker']:>6}: {item['rank_change']} positions")

    return "\n".join(output)


def get_divergence_insights(blended: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Extract tickers with significant rank divergence.

    Args:
        blended: Blended results

    Returns:
        dict: {
            'upgrades': [...],
            'downgrades': [...]
        }
    """
    upgrades = [
        {
            'ticker': x['ticker'],
            'rank_change': x['rank_change'],
            'quant_score': x['quant_score'],
            'claude_score': x['claude_score'],
            'blended_score': x['blended_score'],
            'summary': x['claude_analysis']['analysis'].get('summary', 'N/A') if x.get('claude_analysis') else 'N/A'
        }
        for x in blended if x['divergence_flag'] == 'UPGRADE'
    ]

    downgrades = [
        {
            'ticker': x['ticker'],
            'rank_change': x['rank_change'],
            'quant_score': x['quant_score'],
            'claude_score': x['claude_score'],
            'blended_score': x['blended_score'],
            'summary': x['claude_analysis']['analysis'].get('summary', 'N/A') if x.get('claude_analysis') else 'N/A'
        }
        for x in blended if x['divergence_flag'] == 'DOWNGRADE'
    ]

    return {
        'upgrades': sorted(upgrades, key=lambda x: x['rank_change'], reverse=True),
        'downgrades': sorted(downgrades, key=lambda x: x['rank_change'])
    }
