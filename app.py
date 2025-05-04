import streamlit as st
import pandas as pd
import plotly.express as px

# Page setup
st.set_page_config(page_title="BankTrust RFM Dashboard", layout="wide", initial_sidebar_state="expanded")

# === Load Data ===
@st.cache_data
def load_data():
    return pd.read_csv("output/rfm_segmented.csv")

df = load_data()

# === Sidebar ===
with st.sidebar:
    st.title("🛠️ Dashboard Controls")

    st.markdown("### 🎯 Filter Customers")
    segments = st.multiselect("Segment", options=sorted(df['Segment'].unique()), default=df['Segment'].unique())
    clusters = st.multiselect("Cluster", options=sorted(df['Cluster'].unique()), default=sorted(df['Cluster'].unique()))

    st.markdown("### 📊 What to Show")
    show_profiles = st.checkbox("Cluster Profiles", value=False)
    show_scatter = st.checkbox("RFM Scatter", value=False)
    show_boxplots = st.checkbox("RFM Boxplots", value=False)
    show_segment_table = st.checkbox("Segment Info Table", value=False)

    st.markdown("---")
    st.caption("⚡ Optimized for Performance")

# === Filtered Data ===
filtered_df = df[(df['Segment'].isin(segments)) & (df['Cluster'].isin(clusters))]

# === Dashboard Header ===
st.title("🏦 BankTrust RFM Dashboard")
st.markdown("Identify customer groups using **Recency, Frequency, Monetary** scores for targeted marketing and retention.")

# === KPI Metrics ===
st.markdown("### 📈 Customer Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Customers", len(filtered_df))
col2.metric("Avg. Recency", f"{filtered_df['Recency'].mean():.1f} days")
col3.metric("Avg. Frequency", f"{filtered_df['Frequency'].mean():.1f} txns")
col4.metric("Avg. Monetary", f"₹{filtered_df['Monetary'].mean():,.0f}")

# === Cluster Descriptions + RFM Bar Chart ===
if show_profiles:
    st.markdown("### 🔎 Cluster Insights")
    cluster_descriptions = {
        0: "💰 High-value, frequent, recent – VIPs.",
        1: "⏳ Recent but less frequent – re-engage them.",
        2: "📉 Low activity and value – low ROI or new.",
        3: "⚠️ High recency, low frequency – likely to churn."
    }

    # Summary expandable views
    for c in sorted(filtered_df['Cluster'].unique()):
        with st.expander(f"Cluster {c}"):
            st.markdown(cluster_descriptions.get(c, "No description."))
            preview = filtered_df[filtered_df['Cluster'] == c].head(5)
            st.dataframe(preview[['CustomerID', 'Recency', 'Frequency', 'Monetary', 'Segment']], use_container_width=True)

    # Average RFM per cluster
    rfm_avg = filtered_df.groupby('Cluster')[['Recency', 'Frequency', 'Monetary']].mean().reset_index()
    rfm_long = rfm_avg.melt(id_vars='Cluster', var_name='Metric', value_name='Value')
    fig_bar = px.bar(rfm_long, x='Cluster', y='Value', color='Metric', barmode='group',
                     title='Avg. RFM Metrics per Cluster')
    st.plotly_chart(fig_bar, use_container_width=True)

# === Segment Pie Chart ===
st.markdown("### 🧩 Segment Distribution")
segment_counts = filtered_df['Segment'].value_counts().reset_index()
segment_counts.columns = ['Segment', 'Count']
fig_pie = px.pie(segment_counts, names='Segment', values='Count',
                 title='Customer Segment Distribution', hole=0.4)
st.plotly_chart(fig_pie, use_container_width=True)

# === Segment Description Table ===
if show_segment_table:
    st.markdown("### 📘 Segment Info")
    seg_table = pd.DataFrame({
        "RFM Score Range": ["9–12", "6–8", "4–5", "1–3"],
        "Segment Name": ["Best Customers", "Loyal Customers", "At Risk", "Churned"],
        "Description": [
            "Recently active, frequent, high spenders",
            "Good but less recent",
            "Spending dropped, less frequent",
            "Long gone, infrequent, low spending"
        ]
    })
    st.dataframe(seg_table, use_container_width=True)

# === Scatter Plot ===
if show_scatter:
    st.markdown("### 🧬 RFM Bubble Chart")
    fig_scatter = px.scatter(
        filtered_df, x='Recency', y='Monetary',
        size='Frequency', color='Cluster',
        hover_data=['CustomerID', 'Segment'],
        title="Recency vs. Monetary (Bubble = Frequency)"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

# === Boxplots ===
if show_boxplots:
    st.markdown("### 📦 RFM Boxplots by Cluster")
    for metric in ['Recency', 'Frequency', 'Monetary']:
        fig_box = px.box(filtered_df, x='Cluster', y=metric, color='Cluster',
                         title=f"{metric} by Cluster")
        st.plotly_chart(fig_box, use_container_width=True)

# === Download Button ===
st.markdown("### 💾 Download Filtered Data")
st.download_button("📥 Download CSV", data=filtered_df.to_csv(index=False), file_name="filtered_rfm.csv")





