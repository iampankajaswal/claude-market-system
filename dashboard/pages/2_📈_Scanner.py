"""
Page 2: Quantitative Scanner
Shows scanner results with factor breakdown.
"""
import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="Scanner", page_icon="📈", layout="wide")

# Title
st.title("📈 L2: Quantitative Scanner")
st.markdown("**5 factors → percentile ranks → macro-gated activation**")
st.markdown("---")

# Load data
data_file = Path(__file__).parent.parent.parent / 'data' / 'results' / 'scanner_results.json'

if not data_file.exists():
    st.error("⚠️ Scanner results not found. Run `python scanner/run_scanner.py` first.")
    st.stop()

with open(data_file) as f:
    data = json.load(f)

# Status check
status = data.get('status', 'unknown')

if status == 'disabled':
    st.warning("⚠️ Scanner is DISABLED")
    st.info(f"**Reason**: {data.get('reason', 'Unknown')}")

    # Show macro gate status
    macro_gate = data.get('macro_gate', {})
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Macro Composite Score", f"{macro_gate.get('composite_score', 0):.1f}/100")
    with col2:
        st.metric("Green Light", "❌ NO" if not macro_gate.get('green_light') else "✅ YES")

    st.markdown("---")
    st.info("Scanner only activates when macro gate is GREEN. Run `python signals/run_signals.py` to update macro status.")
    st.stop()

# Header metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Status", "✅ ACTIVE")

with col2:
    st.metric("Mode", data.get('scanner_mode', 'N/A'))

with col3:
    st.metric("Tickers Scanned", data.get('tickers_scanned', 0))

with col4:
    st.metric("Candidates", len(data.get('candidates', [])))

st.markdown("---")

# Candidates
candidates = data.get('candidates', [])

if not candidates:
    st.warning("No candidates found. All stocks scored below threshold.")
    st.stop()

# Top candidates table
st.subheader("🎯 Top Candidates")

# Build dataframe
rows = []
for candidate in candidates[:20]:  # Top 20
    row = {
        'Ticker': candidate['ticker'],
        'Score': candidate['composite_score']
    }

    # Add factor scores
    for factor in candidate.get('factors', []):
        factor_name = factor.get('factor_name', 'Unknown')
        row[factor_name] = factor.get('score', 0)

    rows.append(row)

df = pd.DataFrame(rows)

# Display table with color coding
def highlight_score(val):
    if isinstance(val, (int, float)):
        if val >= 75:
            return 'background-color: lightgreen'
        elif val >= 50:
            return 'background-color: lightyellow'
        else:
            return 'background-color: lightcoral'
    return ''

st.dataframe(
    df.style.map(highlight_score, subset=df.columns[1:]),
    use_container_width=True,
    height=600
)

st.markdown("---")

# Top 10 candidates bar chart
st.subheader("📊 Top 10 Composite Scores")

top_10 = candidates[:10]
tickers = [c['ticker'] for c in top_10]
scores = [c['composite_score'] for c in top_10]

fig_bar = go.Figure(data=[
    go.Bar(
        x=tickers,
        y=scores,
        text=[f"{s:.1f}" for s in scores],
        textposition='outside',
        marker_color=['green' if s >= 75 else 'orange' if s >= 50 else 'lightblue' for s in scores]
    )
])

fig_bar.update_layout(
    xaxis_title="Ticker",
    yaxis_title="Composite Score",
    yaxis_range=[0, 110],
    height=400
)

st.plotly_chart(fig_bar, use_container_width=True)

# Factor breakdown for selected ticker
st.markdown("---")
st.subheader("🔍 Factor Breakdown")

selected_ticker = st.selectbox(
    "Select ticker to view details:",
    [c['ticker'] for c in candidates]
)

selected_candidate = next((c for c in candidates if c['ticker'] == selected_ticker), None)

if selected_candidate:
    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown(f"### {selected_ticker}")
        st.metric("Composite Score", f"{selected_candidate['composite_score']:.2f}/100")

    with col2:
        # Factor scores radar chart
        factors = selected_candidate.get('factors', [])
        factor_names = [f['factor_name'] for f in factors]
        factor_scores = [f.get('score', 0) for f in factors]

        fig_radar = go.Figure(data=go.Scatterpolar(
            r=factor_scores,
            theta=factor_names,
            fill='toself',
            name=selected_ticker
        ))

        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            showlegend=False,
            height=400
        )

        st.plotly_chart(fig_radar, use_container_width=True)

    # Factor details
    st.markdown("#### Factor Details")
    for factor in factors:
        with st.expander(f"📌 {factor['factor_name']} - {factor.get('score', 0):.2f}/100"):
            factor_details = {k: v for k, v in factor.items() if k not in ['factor_name', 'score', 'ticker']}
            for key, value in factor_details.items():
                if isinstance(value, bool):
                    st.write(f"**{key}**: {'✅' if value else '❌'}")
                elif isinstance(value, (int, float)):
                    st.write(f"**{key}**: {value:.2f}")
                else:
                    st.write(f"**{key}**: {value}")

# Distribution of scores
st.markdown("---")
st.subheader("📊 Score Distribution")

all_scores = [c['composite_score'] for c in candidates]
fig_hist = px.histogram(
    x=all_scores,
    nbins=20,
    labels={'x': 'Composite Score', 'y': 'Count'},
    title='Distribution of Composite Scores'
)
fig_hist.update_layout(height=400)
st.plotly_chart(fig_hist, use_container_width=True)

# Timestamp
st.markdown("---")
st.caption(f"Last updated: {data.get('timestamp', 'N/A')}")

# Refresh button
if st.button("🔄 Refresh Data"):
    st.rerun()
