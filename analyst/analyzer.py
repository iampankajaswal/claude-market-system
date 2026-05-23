"""
Claude API analyst for fundamental quality scoring.
Uses Anthropic SDK with prompt caching.
"""
import os
import json
from typing import Dict, Optional
from anthropic import Anthropic

from analyst.financials import get_financial_data, format_financial_summary
from analyst.cache import AnalysisCache


ANALYST_SYSTEM_PROMPT = """You are a senior equity research analyst with 20 years of experience analyzing public companies.

Your task is to evaluate the fundamental quality of a company based on its financial data.

Score the company on a scale of 1-10 for each of the following dimensions:

1. **Earnings Quality** (1-10)
   - Cash flow vs reported earnings
   - Consistency and sustainability
   - Red flags: CF0 << Net Income, declining margins

2. **Growth Trajectory** (1-10)
   - Revenue growth trend
   - Profitability expansion
   - Red flags: Slowing growth, margin compression

3. **Balance Sheet Health** (1-10)
   - Debt levels and coverage
   - Liquidity position
   - Red flags: High debt/equity, deteriorating ratios

4. **Margin Trends** (1-10)
   - Gross and operating margins
   - Direction and stability
   - Red flags: Declining margins, negative trends

5. **Red Flags** (1-10, where 10 = no red flags)
   - Accounts receivable growth vs revenue
   - Quality of earnings issues
   - Balance sheet concerns
   - Any accounting irregularities

Provide your response as JSON with this exact structure:
{
  "earnings_quality": <1-10>,
  "growth_trajectory": <1-10>,
  "balance_sheet_health": <1-10>,
  "margin_trends": <1-10>,
  "red_flags": <1-10>,
  "composite_score": <average of above 5>,
  "summary": "<2-3 sentence summary of key findings>",
  "key_concerns": ["<concern 1>", "<concern 2>"],
  "key_strengths": ["<strength 1>", "<strength 2>"]
}

Be objective and analytical. Focus on what the numbers actually show."""


class ClaudeAnalyst:
    """Claude-powered fundamental analyst."""

    def __init__(self, api_key: Optional[str] = None, use_cache: bool = True):
        """
        Initialize Claude analyst.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            use_cache: Enable SQLite caching
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")

        self.client = Anthropic(api_key=self.api_key)
        self.use_cache = use_cache
        self.cache = AnalysisCache() if use_cache else None

    def analyze_ticker(self, ticker: str, force_refresh: bool = False) -> Dict:
        """
        Analyze a ticker's fundamental quality.

        Args:
            ticker: Stock ticker symbol
            force_refresh: Skip cache and force new API call

        Returns:
            dict: Analysis results with Claude scores
        """
        # Get financial data
        financial_data = get_financial_data(ticker)

        if financial_data.get('error') or not financial_data.get('quarters'):
            return {
                'ticker': ticker,
                'error': financial_data.get('error', 'No financial data'),
                'claude_score': 0,
                'analysis': {}
            }

        # Get quarter end for caching
        quarter_end = financial_data['quarters'][0]['quarter_end']

        # Check cache
        if self.use_cache and not force_refresh:
            cached = self.cache.get(ticker, quarter_end)
            if cached:
                return {
                    **cached,
                    'cache_hit': True
                }

        # Format data for Claude
        financial_summary = format_financial_summary(financial_data)

        # Call Claude API with prompt caching
        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=2000,
                system=[
                    {
                        "type": "text",
                        "text": ANALYST_SYSTEM_PROMPT,
                        "cache_control": {"type": "ephemeral"}
                    }
                ],
                messages=[
                    {
                        "role": "user",
                        "content": financial_summary
                    }
                ]
            )

            # Parse JSON response
            response_text = response.content[0].text
            analysis = json.loads(response_text)

            # Calculate composite Claude score (1-10 -> 0-100)
            claude_score = analysis.get('composite_score', 5.0) * 10

            result = {
                'ticker': ticker,
                'quarter_end': quarter_end,
                'claude_score': round(claude_score, 2),
                'analysis': analysis,
                'financial_data': financial_data,
                'cache_hit': False,
                'usage': {
                    'input_tokens': response.usage.input_tokens,
                    'output_tokens': response.usage.output_tokens,
                    'cache_creation_tokens': getattr(response.usage, 'cache_creation_input_tokens', 0),
                    'cache_read_tokens': getattr(response.usage, 'cache_read_input_tokens', 0)
                }
            }

            # Cache result
            if self.use_cache:
                self.cache.set(ticker, quarter_end, result)

            return result

        except json.JSONDecodeError as e:
            return {
                'ticker': ticker,
                'error': f'Failed to parse Claude response: {e}',
                'claude_score': 0,
                'analysis': {}
            }
        except Exception as e:
            return {
                'ticker': ticker,
                'error': f'Claude API error: {e}',
                'claude_score': 0,
                'analysis': {}
            }

    def analyze_batch(self, tickers: list, max_tickers: Optional[int] = None) -> list:
        """
        Analyze multiple tickers.

        Args:
            tickers: List of ticker symbols
            max_tickers: Maximum number to analyze (for cost control)

        Returns:
            list: Analysis results for each ticker
        """
        if max_tickers:
            tickers = tickers[:max_tickers]

        results = []
        for i, ticker in enumerate(tickers, 1):
            print(f"  Analyzing {ticker} ({i}/{len(tickers)})...")
            result = self.analyze_ticker(ticker)
            results.append(result)

            # Show cache hit info
            if result.get('cache_hit'):
                print(f"    ✓ Cache hit")
            elif result.get('error'):
                print(f"    ✗ Error: {result['error']}")
            else:
                score = result.get('claude_score', 0)
                print(f"    ✓ Claude score: {score:.1f}/100")

        return results
