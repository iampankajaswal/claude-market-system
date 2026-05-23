"""
L1: Macro Deployment Gate
Six-signal composite scoring system for market deployment decisions.
"""
from .vix_level import calculate_vix_level_score
from .vix_term_structure import calculate_vix_term_structure_score
from .breadth import calculate_breadth_score
from .credit_spreads import calculate_credit_spreads_score
from .put_call import calculate_put_call_score
from .market_momentum import calculate_market_momentum_score
from .run_signals import run_macro_gate

__all__ = [
    'calculate_vix_level_score',
    'calculate_vix_term_structure_score',
    'calculate_breadth_score',
    'calculate_credit_spreads_score',
    'calculate_put_call_score',
    'calculate_market_momentum_score',
    'run_macro_gate'
]
