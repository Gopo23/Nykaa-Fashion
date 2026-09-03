import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(page_title="Nykaa Fashion Product Growth Analytics", layout="wide")

# Custom CSS
st.markdown("""
    <style>
        .stApp { background-color: #FAFAFA; }
        h1, h2, h3, h4, h5, h6 { font-family: 'Inter', sans-serif; color: #1A1A1A; font-weight: 600; }
        .stMetric { background-color: #FFFFFF; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-left: 4px solid #FC2779; }
        .insight-card { background-color: #FFFFFF; padding: 20px; border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.08); margin-bottom: 20px; border-left: 4px solid #4F46E5; }
    </style>
""", unsafe_allow_html=True)

API_URL = os.environ.get("API_URL", "http://localhost:8000")

# --- Filters Sidebar ---
with st.sidebar:
    st.header("Global Filters")
    # Mapping friendly names to integer days
    date_map = {"Last 7 Days": 7, "Last 30 Days": 30, "Last 90 Days": 90}
    selected_date = st.selectbox("Date Range", list(date_map.keys()), index=1)
    days_val = date_map[selected_date]
    
    source_val = st.selectbox("Data Source Segment", ["All", "App Store", "Play Store", "YouTube", "Zendesk", "Instagram"])
    
    # We fetch categories dynamically for the filter, but hardcode 'All'
    try:
        cat_resp = requests.get(f"{API_URL}/categories")
        cat_options = ["All Categories"] + cat_resp.json()
    except:
        cat_options = ["All Categories"]
        
    category_val = st.selectbox("Barrier Category", cat_options)

# --- Data Fetchers with dynamic params ---
@st.cache_data(ttl=30, show_spinner=False)
def fetch_data(endpoint, d, s, c):
    try:
        response = requests.get(f"{API_URL}/api/v2/{endpoint}", params={"days": d, "source": s, "category": c})
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching {endpoint}: {e}")
        return None

with st.spinner("Fetching Real-Time Dashboard Data..."):
    kpis = fetch_data("kpis", days_val, source_val, category_val) or {}
    trends_data = fetch_data("trends", days_val, source_val, category_val) or []
    barriers = fetch_data("barriers", days_val, source_val, category_val) or []
    segments = fetch_data("segments", days_val, source_val, category_val) or {}

# For Insights we do NOT cache so tightly, or we cache based on exact filters. It takes time.
@st.cache_data(ttl=120, show_spinner="Generating AI Insights from live complaints... (Takes a few seconds)")
def fetch_insights(d, s, c):
    try:
        response = requests.get(f"{API_URL}/api/v2/insights", params={"days": d, "source": s, "category": c})
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return [{"barrier": "Error", "evidence": str(e), "impact": "N/A", "recommendation": ""}]

# --- Header ---
st.title("👗 Nykaa Fashion - Real User Friction Dashboard")
st.markdown(f"Diagnosing intent drop-offs using **actual user complaints** from the **{selected_date}**.")

# --- ROW 1: Executive KPIs ---
st.markdown("### Executive Summary")
col1, col2, col3 = st.columns(3)

if kpis:
    col1.metric("Identified Feedback/Complaints (High Intent)", f"{kpis.get('high_intent_users', 0):,}")
    col2.metric("Top Friction Category", kpis.get("largest_barrier", "N/A"))
    col3.metric("Volume Trend (vs Previous Period)", kpis.get("trend_30d", "Stable"))

st.divider()

# --- ROW 2: Complaint Trends & Volume ---
st.markdown("### Complaint Volume & Trends")
trend_col, journey_col = st.columns([3, 2])

with trend_col:
    st.markdown("#### Daily Volume of Friction Reports")
    if trends_data:
        df_trends = pd.DataFrame(trends_data)
        if not df_trends.empty:
            fig_trend = px.line(df_trends, x="date", y="complaint_volume", 
                                labels={"complaint_volume": "Daily Complaints", "date": "Date"})
            fig_trend.update_traces(line_color="#FC2779")
            fig_trend.update_layout(margin=dict(l=0, r=0, t=30, b=0), plot_bgcolor="white")
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info("No data available for this timeframe.")

with journey_col:
    st.markdown("#### The Funnel Reality")
    st.info("Because we are using unstructured external reviews (App Store/Play Store) rather than internal clickstream data (Mixpanel), we cannot plot an exact 'Wishlist -> Cart -> Checkout' funnel.")
    st.markdown("Instead, the matrix below prioritizes complaints by their frequency and negative sentiment rating, highlighting exactly what stops the user.")

st.divider()

# --- ROW 3: Barrier Impact Matrix + Ranking ---
st.markdown("### Barrier Analysis Matrix")
matrix_col, ranking_col = st.columns([2, 3])

if barriers:
    df_barriers = pd.DataFrame(barriers)
    if not df_barriers.empty:
        with matrix_col:
            st.markdown("#### Prioritization Matrix")
            # X: Frequency, Y: Severity
            fig_matrix = px.scatter(
                df_barriers, 
                x="users_affected", 
                y="purchase_impact", 
                color="barrier",
                size="purchase_impact",
                hover_name="barrier",
                labels={"users_affected": "Complaint Volume", "purchase_impact": "Severity Score (Impact)"}
            )
            fig_matrix.update_layout(margin=dict(l=0, r=0, t=30, b=0), plot_bgcolor="white")
            st.plotly_chart(fig_matrix, use_container_width=True)
            
        with ranking_col:
            st.markdown("#### Ranked Priorities")
            st.dataframe(
                df_barriers[["barrier", "users_affected", "avg_rating", "purchase_impact", "priority"]],
                column_config={
                    "barrier": "Barrier Category",
                    "users_affected": "Volume of Complaints",
                    "avg_rating": "Average Rating (1-5)",
                    "purchase_impact": "Impact Severity Score",
                    "priority": "Priority Tag"
                },
                use_container_width=True, hide_index=True
            )
    else:
        st.info("No barriers identified for these filters.")

st.divider()

# --- ROW 4: Segment Breakdowns ---
st.markdown("### Breakdown by Data Source")
if segments and "source" in segments:
    df_src = pd.DataFrame(segments["source"])
    if not df_src.empty:
        fig_src = px.bar(df_src, x="segment", y="volume", color="top_barrier",
                         labels={"volume": "Total Complaints", "segment": "Data Source", "top_barrier": "Dominant Barrier"})
        fig_src.update_layout(margin=dict(l=0, r=0, t=30, b=0), plot_bgcolor="white")
        st.plotly_chart(fig_src, use_container_width=True)

st.divider()

# --- ROW 5: AI Insights ---
st.markdown("### 🧠 Live AI Strategic Insights")
st.caption("Groq is analyzing the most recent complaints based on your current filters...")

insights = fetch_insights(days_val, source_val, category_val)

if insights:
    for insight in insights:
        try:
            st.markdown(f"""
            <div class="insight-card">
                <strong>{insight.get('barrier', 'Insight')}</strong><br/>
                <span style="color: #666; font-size: 14px;"><em>Evidence directly from users:</em> {insight.get('evidence', '')}</span><br/>
                <span style="color: #FC2779; font-weight: bold; font-size: 14px;">Impact Level: {insight.get('impact', 'Unknown')}</span><br/>
                <span style="color: #1A1A1A; font-size: 14px; margin-top: 8px; display: inline-block;"><strong>Recommended Action:</strong> {insight.get('recommendation', '')}</span>
            </div>
            """, unsafe_allow_html=True)
        except AttributeError:
            # Fallback if LLM failed to return a proper dict structure
            st.error(f"Error parsing insight: {insight}")
else:
    st.info("No insights generated.")
