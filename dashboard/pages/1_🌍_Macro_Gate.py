"""
Page 1: Macro Deployment Gate
Shows 6 signals, composite score, and deployment zone.
"""
import streamlit as st
import json
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime

st.set_page_config(page_title="Macro Gate", page_icon="🌍", layout="wide")

# Title
st.title("🌍 L1: Macro Deployment Gate")
st.markdown("**6 macro signals → composite score → deployment zone gating**")
st.markdown("---")

# Load data
data_file = Path(__file__).parent.parent.parent / 'data' / 'results' / 'macro_gate.json'

if not data_file.exists():
    st.error("⚠️ Macro gate results not found. Run `python signals/run_signals.py` first.")
    st.stop()

with open(data_file) as f:
    data = json.load(f)

# Header metrics
col1, col2, col3, col4 = st.columns(4)

composite_score = data['composite_score']
deployment_zone = data['deployment_zone']
green_light = data['green_light']
threshold = data.get('threshold', 60)

with col1:
    st.metric("Composite Score", f"{composite_score:.1f}/100")

with col2:
    st.metric("Deployment Zone", deployment_zone)

with col3:
    if green_light:
        st.markdown("### 🟢 GREEN LIGHT")
    else:
        st.markdown("### 🔴 RED LIGHT")

with col4:
    st.metric("Threshold", f"{threshold:.0f}")

st.markdown("---")

# Composite score gauge
st.subheader("Composite Score")

fig = go.Figure(go.Indicator(
    mode="gauge+number+delta",
    value=composite_score,
    domain={'x': [0, 1], 'y': [0, 1]},
    title={'text': "Macro Deployment Score"},
    delta={'reference': threshold},
    gauge={
        'axis': {'range': [None, 100]},
        'bar': {'color': "darkblue"},
        'steps': [
            {'range': [0, 40], 'color': "lightgray", 'name': 'DEFENSIVE'},
            {'range': [40, 60], 'color': "lightyellow", 'name': 'REDUCED'},
            {'range': [60, 75], 'color': "lightgreen", 'name': 'NORMAL'},
            {'range': [75, 100], 'color': "green", 'name': 'AGGRESSIVE'}
        ],
        'threshold': {
            'line': {'color': "red", 'width': 4},
            'thickness': 0.75,
            'value': threshold
        }
    }
))

fig.update_layout(height=400)
st.plotly_chart(fig, use_container_width=True)

# Zone descriptions
st.markdown("### Deployment Zones")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("**🔴 DEFENSIVE (0-40)**")
    st.caption("High risk. No new positions.")

with col2:
    st.markdown("**🟡 REDUCED (40-60)**")
    st.caption("Elevated risk. Reduce exposure.")

with col3:
    st.markdown("**🟢 NORMAL (60-75)**")
    st.caption("Favorable. Standard deployment.")

with col4:
    st.markdown("**🟢 AGGRESSIVE (75-100)**")
    st.caption("Ideal. Maximum deployment.")

st.markdown("---")

# Individual signals
st.subheader("📊 Individual Signals")

signals = data.get('signals', [])

# Create bar chart
signal_names = [s['signal_name'] for s in signals]
signal_scores = [s['score'] for s in signals]

fig_bars = go.Figure(data=[
    go.Bar(
        x=signal_names,
        y=signal_scores,
        text=[f"{s:.1f}" for s in signal_scores],
        textposition='outside',
        marker_color=['green' if s >= 60 else 'orange' if s >= 40 else 'red' for s in signal_scores]
    )
])

fig_bars.update_layout(
    title="Signal Scores (0-100)",
    xaxis_title="Signal",
    yaxis_title="Score",
    yaxis_range=[0, 110],
    height=400
)

st.plotly_chart(fig_bars, use_container_width=True)

# Signal details
st.subheader("Signal Details")

for signal in signals:
    with st.expander(f"📌 {signal['signal_name']} - Score: {signal['score']:.2f}/100"):
        cols = st.columns(2)

        # Remove score and signal_name from display
        details = {k: v for k, v in signal.items() if k not in ['score', 'signal_name', 'timestamp']}

        for i, (key, value) in enumerate(details.items()):
            col_idx = i % 2
            with cols[col_idx]:
                if isinstance(value, bool):
                    st.write(f"**{key}**: {'✅' if value else '❌'}")
                elif isinstance(value, (int, float)):
                    st.write(f"**{key}**: {value:.2f}")
                else:
                    st.write(f"**{key}**: {value}")

# Timestamp
st.markdown("---")
st.caption(f"Last updated: {data.get('timestamp', 'N/A')}")

# Refresh button
if st.button("🔄 Refresh Data"):
    st.rerun()
