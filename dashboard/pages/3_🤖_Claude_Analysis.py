"""
Page 3: Claude Analyst
Shows blended rankings, divergence flags, and Claude analysis details.
"""
import streamlit as st
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Claude Analysis", page_icon="🤖", layout="wide")

# Title
st.title("🤖 L3: Claude Analyst")
st.markdown("**Fundamental quality → 60/40 blend → rank divergence flags**")
st.markdown("---")

# Load data
data_file = Path(__file__).parent.parent.parent / 'data' / 'results' / 'analyst_results.json'

if not data_file.exists():
    st.error("⚠️ Analyst results not found. Run `python analyst/run_analysis.py` first.")
    st.info("Note: Requires ANTHROPIC_API_KEY environment variable.")
    st.stop()

with open(data_file) as f:
    data = json.load(f)

# Status check
status = data.get('status', 'unknown')

if status == 'no_candidates':
    st.warning("⚠️ No candidates to analyze")
    st.info("Scanner returned empty list. Check L2 Scanner results.")
    st.stop()

if status == 'error':
    st.error(f"❌ Error: {data.get('error', 'Unknown error')}")
    st.stop()

# Header metrics
blended_results = data.get('blended_results', [])
insights = data.get('divergence_insights', {})

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Candidates Analyzed", len(blended_results))

with col2:
    upgrades = len(insights.get('upgrades', []))
    st.metric("🟢 Upgrades", upgrades)

with col3:
    downgrades = len(insights.get('downgrades', []))
    st.metric("🔴 Downgrades", downgrades)

with col4:
    aligned = len([x for x in blended_results if x.get('divergence_flag') == 'ALIGNED'])
    st.metric("⚪ Aligned", aligned)

st.markdown("---")

# Blended rankings table
st.subheader("🎯 Blended Rankings (60% Quant + 40% Claude)")

if not blended_results:
    st.warning("No blended results available.")
    st.stop()

# Build dataframe
rows = []
for item in blended_results[:20]:  # Top 20
    flag = item.get('divergence_flag', 'N/A')
    flag_emoji = {
        'UPGRADE': '🟢',
        'DOWNGRADE': '🔴',
        'ALIGNED': '⚪',
        'NO_CLAUDE_DATA': '⚫'
    }.get(flag, '⚪')

    rows.append({
        'Rank': item.get('blended_rank', '-'),
        'Flag': flag_emoji,
        'Ticker': item['ticker'],
        'Blended': item['blended_score'],
        'Quant': item['quant_score'],
        'Claude': item['claude_score'] if item['claude_score'] is not None else '-',
        'Δ Rank': item.get('rank_change', '-'),
        'Divergence': flag
    })

df = pd.DataFrame(rows)

# Color coding function
def highlight_divergence(row):
    if row['Divergence'] == 'UPGRADE':
        return ['background-color: #d4edda'] * len(row)
    elif row['Divergence'] == 'DOWNGRADE':
        return ['background-color: #f8d7da'] * len(row)
    else:
        return [''] * len(row)

st.dataframe(
    df.style.apply(highlight_divergence, axis=1),
    use_container_width=True,
    height=600
)

st.markdown("---")

# Quant vs Claude scatter plot
st.subheader("📊 Quant vs Claude Scores")

# Filter items with both scores
scatter_data = [
    {
        'ticker': item['ticker'],
        'quant': item['quant_score'],
        'claude': item['claude_score'],
        'flag': item['divergence_flag']
    }
    for item in blended_results
    if item['claude_score'] is not None
]

if scatter_data:
    scatter_df = pd.DataFrame(scatter_data)

    fig_scatter = px.scatter(
        scatter_df,
        x='quant',
        y='claude',
        text='ticker',
        color='flag',
        color_discrete_map={
            'UPGRADE': 'green',
            'DOWNGRADE': 'red',
            'ALIGNED': 'lightblue'
        },
        labels={'quant': 'Quantitative Score', 'claude': 'Claude Score'},
        title='Quantitative vs Claude Fundamental Scores',
        height=500
    )

    # Add diagonal line (perfect agreement)
    fig_scatter.add_trace(go.Scatter(
        x=[0, 100],
        y=[0, 100],
        mode='lines',
        line=dict(color='gray', dash='dash'),
        name='Perfect Agreement',
        showlegend=True
    ))

    fig_scatter.update_traces(textposition='top center')
    fig_scatter.update_layout(height=500)

    st.plotly_chart(fig_scatter, use_container_width=True)
else:
    st.info("No data available for scatter plot.")

st.markdown("---")

# Divergence insights
st.subheader("🔍 Key Divergences")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🟢 Top Upgrades")
    st.caption("Claude sees more value than quant signals")

    upgrades_list = insights.get('upgrades', [])
    if upgrades_list:
        for item in upgrades_list[:5]:
            with st.expander(f"**{item['ticker']}** (+{item['rank_change']} positions)"):
                st.write(f"**Quant Score**: {item['quant_score']:.1f}")
                st.write(f"**Claude Score**: {item['claude_score']:.1f}")
                st.write(f"**Blended Score**: {item['blended_score']:.1f}")
                st.write(f"**Summary**: {item.get('summary', 'N/A')}")
    else:
        st.info("No significant upgrades found.")

with col2:
    st.markdown("### 🔴 Top Downgrades")
    st.caption("Claude sees less value than quant signals")

    downgrades_list = insights.get('downgrades', [])
    if downgrades_list:
        for item in downgrades_list[:5]:
            with st.expander(f"**{item['ticker']}** ({item['rank_change']} positions)"):
                st.write(f"**Quant Score**: {item['quant_score']:.1f}")
                st.write(f"**Claude Score**: {item['claude_score']:.1f}")
                st.write(f"**Blended Score**: {item['blended_score']:.1f}")
                st.write(f"**Summary**: {item.get('summary', 'N/A')}")
    else:
        st.info("No significant downgrades found.")

st.markdown("---")

# Detailed analysis for selected ticker
st.subheader("📋 Detailed Claude Analysis")

tickers_with_analysis = [
    item['ticker'] for item in blended_results
    if item.get('claude_analysis') and not item['claude_analysis'].get('error')
]

if tickers_with_analysis:
    selected_ticker = st.selectbox(
        "Select ticker for detailed analysis:",
        tickers_with_analysis
    )

    selected_item = next((item for item in blended_results if item['ticker'] == selected_ticker), None)

    if selected_item and selected_item.get('claude_analysis'):
        analysis = selected_item['claude_analysis'].get('analysis', {})

        col1, col2 = st.columns([1, 2])

        with col1:
            st.markdown(f"### {selected_ticker}")
            st.metric("Claude Score", f"{selected_item['claude_score']:.1f}/100")
            st.metric("Blended Score", f"{selected_item['blended_score']:.1f}/100")
            st.metric("Rank Change", f"{selected_item.get('rank_change', 'N/A')}")

        with col2:
            # Dimension scores
            dimensions = [
                'Earnings Quality',
                'Growth Trajectory',
                'Balance Sheet Health',
                'Margin Trends',
                'Red Flags'
            ]

            dimension_scores = [
                analysis.get('earnings_quality', 5),
                analysis.get('growth_trajectory', 5),
                analysis.get('balance_sheet_health', 5),
                analysis.get('margin_trends', 5),
                analysis.get('red_flags', 5)
            ]

            fig_dims = go.Figure(data=go.Scatterpolar(
                r=dimension_scores,
                theta=dimensions,
                fill='toself',
                name=selected_ticker
            ))

            fig_dims.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 10]
                    )
                ),
                showlegend=False,
                height=400
            )

            st.plotly_chart(fig_dims, use_container_width=True)

        # Summary and insights
        st.markdown("#### 📝 Summary")
        st.write(analysis.get('summary', 'No summary available.'))

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### ✅ Key Strengths")
            strengths = analysis.get('key_strengths', [])
            for strength in strengths:
                st.write(f"- {strength}")

        with col2:
            st.markdown("#### ⚠️ Key Concerns")
            concerns = analysis.get('key_concerns', [])
            for concern in concerns:
                st.write(f"- {concern}")

        # Financial data
        if selected_item['claude_analysis'].get('financial_data'):
            with st.expander("📊 View Financial Data"):
                fin_data = selected_item['claude_analysis']['financial_data']
                quarters = fin_data.get('quarters', [])

                if quarters:
                    fin_rows = []
                    for q in quarters:
                        fin_rows.append({
                            'Quarter': q['quarter_end'],
                            'Revenue': f"${q.get('revenue', 0):,.0f}",
                            'Net Income': f"${q.get('net_income', 0):,.0f}",
                            'Operating CF': f"${q.get('operating_cashflow', 0):,.0f}",
                            'Free CF': f"${q.get('free_cashflow', 0):,.0f}"
                        })

                    st.dataframe(pd.DataFrame(fin_rows), use_container_width=True)

                    # Ratios
                    ratios = fin_data.get('ratios', {})
                    st.markdown("**Key Ratios**")
                    ratio_cols = st.columns(3)
                    with ratio_cols[0]:
                        cfo_ni = ratios.get('cfo_ni_ratio')
                        st.metric("CF0/NI Ratio", f"{cfo_ni:.2f}" if cfo_ni else "N/A")
                    with ratio_cols[1]:
                        roe = ratios.get('roe')
                        st.metric("ROE", f"{roe:.1%}" if roe else "N/A")
                    with ratio_cols[2]:
                        debt_eq = ratios.get('debt_to_equity')
                        st.metric("Debt/Equity", f"{debt_eq:.2f}" if debt_eq else "N/A")
else:
    st.info("No detailed analysis available for any ticker.")

# Timestamp
st.markdown("---")
st.caption(f"Last updated: {data.get('timestamp', 'N/A')}")

# Refresh button
if st.button("🔄 Refresh Data"):
    st.rerun()
