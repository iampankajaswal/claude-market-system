"""
Claude Market System Dashboard
Multi-page Streamlit app for L1, L2, L3 visualization.
"""
import streamlit as st
from pathlib import Path

# Page config
st.set_page_config(
    page_title="Claude Market System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
        color: #1f77b4;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .green-light {
        color: #00ff00;
        font-size: 2rem;
    }
    .red-light {
        color: #ff0000;
        font-size: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("📊 Claude Market System")
st.sidebar.markdown("---")
st.sidebar.markdown("""
### System Architecture
**L1: Macro Deployment Gate**
6 signals → composite score → gating

**L2: Quantitative Scanner**
5 factors → percentile ranks

**L3: Claude Analyst**
Fundamental quality → blending
""")

st.sidebar.markdown("---")
st.sidebar.info("""
**Navigation:**
Use the pages in the sidebar to view:
- Page 1: Macro Gate
- Page 2: Scanner Results
- Page 3: Claude Analysis
""")

# Main page
st.markdown('<div class="main-header">📊 Claude Market System</div>', unsafe_allow_html=True)

st.markdown("""
## AI-Powered Market Deployment Gating System

This system uses a three-layer architecture to answer:
**"Should I be deploying capital right now, and how aggressively?"**

### How It Works

1. **L1: Macro Deployment Gate** 🌍
   - Analyzes 6 macro signals (VIX, breadth, credit spreads, etc.)
   - Outputs composite score 0-100 with deployment zones
   - Gates activation of downstream layers

2. **L2: Quantitative Scanner** 📈
   - Only activates when macro gate is GREEN
   - Scans S&P 500 with 5 technical factors
   - Percentile ranks candidates

3. **L3: Claude Analyst** 🤖
   - Claude API analyzes fundamental quality
   - Scores: Earnings, Growth, Balance Sheet, Margins, Red Flags
   - Blends 60% quant + 40% fundamental
   - Flags rank divergence (disagreement = insight)

### Get Started

Use the **sidebar** to navigate to:
- **Page 1**: View macro deployment gate status
- **Page 2**: See quantitative scanner results
- **Page 3**: Explore Claude analysis and blended rankings

---

💡 **Tip**: The system is designed with "No Half-Measures" - either all layers work together, or nothing deploys.
""")

# Quick status check
st.markdown("---")
st.subheader("Quick Status Check")

col1, col2, col3 = st.columns(3)

# Check for results files
data_dir = Path(__file__).parent.parent / 'data' / 'results'

with col1:
    macro_file = data_dir / 'macro_gate.json'
    if macro_file.exists():
        st.success("✅ L1: Macro Gate")
        st.caption("Results available")
    else:
        st.warning("⚠️ L1: Not Run")
        st.caption("Run signals/run_signals.py")

with col2:
    scanner_file = data_dir / 'scanner_results.json'
    if scanner_file.exists():
        st.success("✅ L2: Scanner")
        st.caption("Results available")
    else:
        st.warning("⚠️ L2: Not Run")
        st.caption("Run scanner/run_scanner.py")

with col3:
    analyst_file = data_dir / 'analyst_results.json'
    if analyst_file.exists():
        st.success("✅ L3: Analyst")
        st.caption("Results available")
    else:
        st.warning("⚠️ L3: Not Run")
        st.caption("Run analyst/run_analysis.py")

st.markdown("---")
st.caption("Built with Claude Code | Powered by Anthropic Claude API")
