import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page Configuration
st.set_page_config(page_title="BankTrust RFM Dashboard", layout="wide", initial_sidebar_state="expanded")

# Load Data with Cache
@st.cache_data
def load_data():
    return pd.read_csv("output/rfm_segmented.csv")

df = load_data()

# === Sidebar ===
with st.sidebar:
    st.title("🔧 Dashboard Controls")
    st.markdown("Filter and display analysis insights from RFM segments and clusters.")

    st.subheader("🎯 Customer Filters")
    segments = st.multiselect("Select Segment", options=sorted(df['Segment'].unique()), default=sorted(df['Segment'].unique()))
    clusters = st.multiselect("Select Cluster", options=sorted(df['Cluster'].unique()), default=sorted(df['Cluster'].unique()))

    st.subheader("📊 Toggle Views")
    show_cluster_distribution = st.checkbox("Show Cluster Size Bar", value=True)
    show_segment_funnel = st.checkbox("Show Segment Value Funnel", value=True)
    show_rfm_matrix = st.checkbox("Show RFM Heat Table", value=True)
    show_segment_table = st.checkbox("Show Segment Info Table", value=True)
    show_lifecycle_pie = st.checkbox("Show Segment Lifecycle Pie", value=True)
    show_segment_composition = st.checkbox("Show Segment Composition Table", value=True)
    show_top_customers = st.checkbox("Show Top Customers", value=True)

    st.markdown("---")
    st.caption("Optimized for performance • Mobile-compatible")

# === Filtered Data ===
filtered_df = df[(df['Segment'].isin(segments)) & (df['Cluster'].isin(clusters))]

# === Main Title ===
st.title("🏦 BankTrust RFM Segmentation Dashboard")
st.markdown("Segment and prioritize customers based on **Recency**, **Frequency**, and **Monetary** behavior for marketing and retention strategy.")

# === KPIs ===
st.markdown("### 📈 Customer Snapshot")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Customers", len(filtered_df))
col2.metric("Avg. Recency", f"{filtered_df['Recency'].mean():.1f} days")
col3.metric("Avg. Frequency", f"{filtered_df['Frequency'].mean():.1f} txns")
col4.metric("Avg. Monetary", f"₹{filtered_df['Monetary'].mean():,.0f}")

# === Cluster Size Bar Chart ===
if show_cluster_distribution:
    st.markdown("### 👥 Cluster Size Distribution")
    cluster_counts = filtered_df['Cluster'].value_counts().sort_index()
    fig_cluster_bar = px.bar(
        x=cluster_counts.index,
        y=cluster_counts.values,
        labels={'x': 'Cluster', 'y': 'Number of Customers'},
        color=cluster_counts.index.astype(str),
        title="Customer Count per Cluster"
    )
    st.plotly_chart(fig_cluster_bar, use_container_width=True)

# === Segment Funnel Chart ===
if show_segment_funnel:
    st.markdown("### 🔄 Segment Value Funnel")
    seg_mon = filtered_df.groupby('Segment')['Monetary'].mean().sort_values(ascending=False).reset_index()
    fig_funnel = go.Figure(go.Funnel(
        y=seg_mon['Segment'],
        x=seg_mon['Monetary'],
        textinfo="value+percent initial"
    ))
    fig_funnel.update_layout(title="Average Monetary Value by Segment (Funnel View)")
    st.plotly_chart(fig_funnel, use_container_width=True)

# === Lifecycle Pie Chart ===
if show_lifecycle_pie:
    st.markdown("### 📊 Customer Lifecycle Distribution")
    seg_dist = filtered_df['Segment'].value_counts().reset_index()
    seg_dist.columns = ['Segment', 'Count']
    fig_pie = px.pie(seg_dist, names='Segment', values='Count', hole=0.4, title="Customer Lifecycle Segment Share")
    st.plotly_chart(fig_pie, use_container_width=True)

# === Segment Composition Table ===
if show_segment_composition:
    st.markdown("### 📋 Segment Composition Overview")
    comp_df = filtered_df.groupby('Segment').agg({
        'CustomerID': 'count',
        'Monetary': 'sum'
    }).rename(columns={'CustomerID': 'Customers', 'Monetary': 'Total Monetary'}).reset_index()
    comp_df['% of Customers'] = (comp_df['Customers'] / comp_df['Customers'].sum() * 100).round(1)
    comp_df['% of Value'] = (comp_df['Total Monetary'] / comp_df['Total Monetary'].sum() * 100).round(1)
    fig_comp = px.bar(
    comp_df.sort_values(by='% of Value', ascending=False),
    x='Segment',
    y='% of Value',
    text='% of Value',
    color='Segment',
    title="Customer Value Contribution by Segment"
)
st.plotly_chart(fig_comp, use_container_width=True)


# === Top Customers Table ===
if show_top_customers:
    st.markdown("### 🏅 Top 10 High-Value Customers")
    top_customers = filtered_df.sort_values(by='Monetary', ascending=False).head(10)
    fig_top = px.bar(
    top_customers,
    x='CustomerID',
    y='Monetary',
    color='Segment',
    hover_data=['Recency', 'Frequency', 'Cluster'],
    title="Top 10 Customers by Monetary Value"
)
st.plotly_chart(fig_top, use_container_width=True)


# === Segment Info Table ===
if show_segment_table:
    st.markdown("### 📘 Segment Description Table")
    segment_info = pd.DataFrame({
        "RFM Score Range": ["9–12", "6–8", "4–5", "1–3"],
        "Segment Name": ["Best Customers", "Loyal Customers", "At Risk", "Churned"],
        "Description": [
            "Recently active, frequent, high spenders",
            "Good but less recent",
            "Spending dropped, less frequent",
            "Long gone, infrequent, low spending"
        ]
    })
    st.markdown("#### 📘 Segment Descriptions")
for i, row in segment_info.iterrows():
    st.markdown(f"**{row['Segment Name']}** ({row['RFM Score Range']}): {row['Description']}")


# === Cluster Profile Table ===
st.markdown("### 🔍 Cluster Profiles")
cluster_descriptions = {
    0: "💰 High-value, frequent, recent – VIPs.",
    1: "⏳ Recent but less frequent – responsive to re-engagement.",
    2: "📉 Low activity and value – low ROI or new.",
    3: "⚠️ High recency, low frequency – at risk of churning."
}

for c in sorted(df['Cluster'].unique()):
    with st.expander(f"Cluster {c}"):
        st.markdown(cluster_descriptions.get(c, "No description available."))
        st.table(df[df['Cluster'] == c][['CustomerID', 'Recency', 'Frequency', 'Monetary', 'Segment']].head(10))

# === RFM Matrix Table ===
if show_rfm_matrix:
    st.markdown("### 🧱 RFM Profile Table")
    rfm_matrix = filtered_df.groupby('Cluster')[['Recency', 'Frequency', 'Monetary']].mean().round(1).reset_index()
    fig_heat = go.Figure(data=go.Heatmap(
    z=rfm_matrix[['Recency', 'Frequency', 'Monetary']].values,
    x=['Recency', 'Frequency', 'Monetary'],
    y=[f"Cluster {i}" for i in rfm_matrix['Cluster']],
    colorscale='Blues',
    showscale=True
))
fig_heat.update_layout(title='RFM Heatmap by Cluster')
st.plotly_chart(fig_heat, use_container_width=True)


# === Download Button ===
st.markdown("### 💾 Export Data")
st.download_button("📥 Download Filtered Data as CSV", data=filtered_df.to_csv(index=False), file_name="filtered_rfm.csv")






