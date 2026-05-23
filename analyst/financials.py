"""
Financial data gathering and ratio calculation.
Fetches 4 quarters of data from yfinance.
"""
import yfinance as yf
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime


def get_financial_data(ticker: str) -> Optional[Dict]:
    """
    Gather 4 quarters of financial data and calculate key ratios.

    Args:
        ticker: Stock ticker symbol

    Returns:
        dict: {
            'ticker': str,
            'quarters': list of quarter data,
            'ratios': dict of calculated ratios,
            'error': str (if failed)
        }
    """
    try:
        stock = yf.Ticker(ticker)

        # Get quarterly financials
        income_stmt = stock.quarterly_financials
        balance_sheet = stock.quarterly_balance_sheet
        cashflow = stock.quarterly_cashflow

        if income_stmt is None or income_stmt.empty:
            return {
                'ticker': ticker,
                'error': 'No financial data available',
                'quarters': []
            }

        # Get last 4 quarters
        quarters_data = []
        available_quarters = min(4, len(income_stmt.columns))

        for i in range(available_quarters):
            quarter_date = income_stmt.columns[i]

            quarter_info = {
                'quarter_end': quarter_date.strftime('%Y-%m-%d'),
                'revenue': safe_get(income_stmt, 'Total Revenue', i),
                'net_income': safe_get(income_stmt, 'Net Income', i),
                'operating_income': safe_get(income_stmt, 'Operating Income', i),
                'gross_profit': safe_get(income_stmt, 'Gross Profit', i),
                'operating_cashflow': safe_get(cashflow, 'Operating Cash Flow', i),
                'free_cashflow': safe_get(cashflow, 'Free Cash Flow', i),
                'total_debt': safe_get(balance_sheet, 'Total Debt', i),
                'total_equity': safe_get(balance_sheet, 'Stockholders Equity', i),
                'accounts_receivable': safe_get(balance_sheet, 'Accounts Receivable', i),
            }

            quarters_data.append(quarter_info)

        # Calculate ratios using most recent quarter
        ratios = calculate_ratios(quarters_data)

        return {
            'ticker': ticker,
            'quarters': quarters_data,
            'ratios': ratios,
            'timestamp': datetime.now().isoformat()
        }

    except Exception as e:
        return {
            'ticker': ticker,
            'error': str(e),
            'quarters': []
        }


def safe_get(df: pd.DataFrame, key: str, col_index: int) -> Optional[float]:
    """Safely get value from DataFrame."""
    try:
        if key in df.index:
            value = df.loc[key].iloc[col_index]
            if pd.notna(value):
                return float(value)
    except Exception:
        pass
    return None


def calculate_ratios(quarters: List[Dict]) -> Dict[str, Optional[float]]:
    """
    Calculate key financial ratios from quarterly data.

    Ratios:
    - CF0/NI: Operating cashflow / Net income (quality of earnings)
    - AR/Revenue Growth: Accounts receivable growth vs revenue growth
    - Debt/Equity: Total debt / Total equity
    - ROE: Net income / Equity (annualized)
    - Gross Margin: Gross profit / Revenue
    - Operating Margin: Operating income / Revenue
    """
    if not quarters or len(quarters) == 0:
        return {}

    latest = quarters[0]
    ratios = {}

    # CF0/NI Ratio (earnings quality)
    if latest.get('operating_cashflow') and latest.get('net_income'):
        if latest['net_income'] != 0:
            ratios['cfo_ni_ratio'] = latest['operating_cashflow'] / latest['net_income']
        else:
            ratios['cfo_ni_ratio'] = None
    else:
        ratios['cfo_ni_ratio'] = None

    # AR Growth vs Revenue Growth (if we have 2+ quarters)
    if len(quarters) >= 2:
        curr_ar = latest.get('accounts_receivable')
        prev_ar = quarters[1].get('accounts_receivable')
        curr_rev = latest.get('revenue')
        prev_rev = quarters[1].get('revenue')

        if all([curr_ar, prev_ar, curr_rev, prev_rev]) and prev_ar != 0 and prev_rev != 0:
            ar_growth = (curr_ar - prev_ar) / prev_ar
            rev_growth = (curr_rev - prev_rev) / prev_rev
            ratios['ar_vs_revenue_growth'] = ar_growth - rev_growth
        else:
            ratios['ar_vs_revenue_growth'] = None
    else:
        ratios['ar_vs_revenue_growth'] = None

    # Debt/Equity
    if latest.get('total_debt') and latest.get('total_equity'):
        if latest['total_equity'] != 0:
            ratios['debt_to_equity'] = latest['total_debt'] / latest['total_equity']
        else:
            ratios['debt_to_equity'] = None
    else:
        ratios['debt_to_equity'] = None

    # ROE (annualized from quarterly)
    if latest.get('net_income') and latest.get('total_equity'):
        if latest['total_equity'] != 0:
            ratios['roe'] = (latest['net_income'] * 4) / latest['total_equity']  # Annualize
        else:
            ratios['roe'] = None
    else:
        ratios['roe'] = None

    # Gross Margin
    if latest.get('gross_profit') and latest.get('revenue'):
        if latest['revenue'] != 0:
            ratios['gross_margin'] = latest['gross_profit'] / latest['revenue']
        else:
            ratios['gross_margin'] = None
    else:
        ratios['gross_margin'] = None

    # Operating Margin
    if latest.get('operating_income') and latest.get('revenue'):
        if latest['revenue'] != 0:
            ratios['operating_margin'] = latest['operating_income'] / latest['revenue']
        else:
            ratios['operating_margin'] = None
    else:
        ratios['operating_margin'] = None

    return ratios


def format_financial_summary(data: Dict) -> str:
    """
    Format financial data for Claude API prompt.

    Args:
        data: Financial data dict from get_financial_data()

    Returns:
        str: Formatted summary
    """
    if data.get('error'):
        return f"Error gathering data: {data['error']}"

    ticker = data['ticker']
    quarters = data['quarters']
    ratios = data['ratios']

    summary = f"# Financial Summary: {ticker}\n\n"
    summary += f"## Last 4 Quarters\n\n"

    for i, q in enumerate(quarters, 1):
        summary += f"### Q{i} ({q['quarter_end']})\n"
        summary += f"- Revenue: ${q.get('revenue', 0):,.0f}\n"
        summary += f"- Net Income: ${q.get('net_income', 0):,.0f}\n"
        summary += f"- Operating Cashflow: ${q.get('operating_cashflow', 0):,.0f}\n"
        summary += f"- Free Cashflow: ${q.get('free_cashflow', 0):,.0f}\n\n"

    summary += f"## Key Ratios\n\n"

    cfo_ni = ratios.get('cfo_ni_ratio')
    summary += f"- CF0/NI Ratio: {f'{cfo_ni:.2f}' if cfo_ni else 'N/A'}\n"

    ar_growth = ratios.get('ar_vs_revenue_growth')
    summary += f"- AR vs Revenue Growth Delta: {f'{ar_growth:.2%}' if ar_growth is not None else 'N/A'}\n"

    debt_eq = ratios.get('debt_to_equity')
    summary += f"- Debt/Equity: {f'{debt_eq:.2f}' if debt_eq else 'N/A'}\n"

    roe = ratios.get('roe')
    summary += f"- ROE (annualized): {f'{roe:.2%}' if roe else 'N/A'}\n"

    gross_m = ratios.get('gross_margin')
    summary += f"- Gross Margin: {f'{gross_m:.2%}' if gross_m else 'N/A'}\n"

    op_m = ratios.get('operating_margin')
    summary += f"- Operating Margin: {f'{op_m:.2%}' if op_m else 'N/A'}\n"

    return summary
