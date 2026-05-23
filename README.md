# Claude Market System

AI-powered market deployment gating system with three-layer analysis architecture.

## System Architecture

```
L1: Macro Deployment Gate (6 signals → composite 0-100 → zone gating)
    ↓ [GREEN LIGHT REQUIRED]
L2: Quantitative Scanner (5 factors → percentile ranks → filtered candidates)
    ↓ [MACRO-GATED ACTIVATION]
L3: Claude Analyst (fundamental quality → 60/40 blend → rank divergence flags)
```

## Components

### L1: Macro Deployment Gate
**Purpose**: Answer "Should I be deploying capital right now, and how aggressively?"

**Signals** (each scored 0-100):
1. VIX Level - Current volatility vs historical
2. VIX Term Structure - Contango/backwardation
3. Market Breadth - % of S&P 500 above 200-day SMA
4. Credit Spreads - HYG vs TLT spread proxy
5. Put/Call Sentiment - VIX rate of change
6. (6th signal to be defined)

**Output**: Composite score 0-100 with deployment zones

### L2: Quantitative Scanner
**Purpose**: Identify candidates when macro gate is green

**Factors** (percentile ranked 0-100):
1. Momentum Crossover - 10-day EMA vs 50-day EMA
2. Volume Surge - 5-day vs 20-day average
3. Relative Strength vs SPY - 20-day comparison
4. 52-Week High Proximity - Current price / 52-week high
5. Short Interest Decline - Change vs prior period

**Universe**: S&P 500 constituents (daily OHLCV via yfinance)
**Modes**: REDUCED (only surface > 75) / DEFENSIVE (disabled)

### L3: Claude Analyst
**Purpose**: Non-deterministic fundamental quality scoring

**Process**:
1. Gather 4 quarters financials (yfinance)
2. Calculate ratios: CF0/NI, AR/Revenue growth, Debt/Equity, ROE
3. Send to Claude API with analyst system prompt
4. Score 1-10: Earnings Quality, Growth, Balance Sheet, Margins, Red Flags
5. Blend: 60% quant + 40% Claude fundamental
6. Flag rank divergence ≥ 3 positions (disagreement = insight)

**Tech**: Anthropic SDK, SQLite caching, prompt caching enabled

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set API key
export ANTHROPIC_API_KEY="your-key-here"

# Run full pipeline
python run_analysis.py --scan-and-analyze

# Run individual layers
python signals/run_signals.py        # L1 only
python scanner/run_scanner.py        # L2 only (requires L1 green)
python analyst/run_analysis.py       # L3 only
```

## Dashboard

Streamlit multi-page dashboard:
- **Page 1**: Macro gate + 6 signals + composite score
- **Page 2**: Scanner results + factor breakdown
- **Page 3**: Claude analysis + blended rankings + divergence flags

```bash
streamlit run dashboard/app.py
```

## Project Structure

```
claude-market-system/
├── signals/                  # L1: Macro deployment gate
│   ├── vix_level.py
│   ├── vix_term_structure.py
│   ├── breadth.py
│   ├── credit_spreads.py
│   ├── put_call.py
│   └── run_signals.py
├── scanner/                  # L2: Quantitative scanner
│   ├── factors/
│   │   ├── momentum.py
│   │   ├── volume.py
│   │   ├── relative_strength.py
│   │   ├── high_proximity.py
│   │   └── short_interest.py
│   └── run_scanner.py
├── analyst/                  # L3: Claude fundamental analysis
│   ├── analyzer.py
│   ├── blender.py
│   └── run_analysis.py
├── dashboard/                # Streamlit UI
│   ├── app.py
│   ├── pages/
│   │   ├── 1_macro_gate.py
│   │   ├── 2_scanner.py
│   │   └── 3_analyst.py
│   └── components/
├── data/                     # SQLite cache + results
│   ├── cache.db
│   └── results/
├── tests/
├── requirements.txt
└── run_analysis.py          # Main orchestrator
```

## Key Design Principles

1. **Gated Activation**: Scanner only runs when macro gate is green
2. **Percentile Ranking**: All scores relative to universe, not absolute
3. **Divergence = Insight**: Where quant and Claude disagree is valuable
4. **Prompt Caching**: Claude API calls cached by (ticker, quarter_end)
5. **No Half-Measures**: Full end-to-end or nothing

## Data Sources

- **Market Data**: yfinance (OHLCV, fundamentals)
- **VIX Data**: yfinance ^VIX, ^VIX3M
- **Credit Spreads**: HYG, TLT ETF prices
- **Universe**: S&P 500 constituents

## Environment Variables

```bash
ANTHROPIC_API_KEY=sk-...    # Required for L3
SCANNER_MODE=REDUCED        # REDUCED / DEFENSIVE
MIN_COMPOSITE_SCORE=60      # Macro gate threshold
```

## License

MIT
