import streamlit as st
import pandas as pd
import tempfile
import os
import time
import plotly.express as px  # type: ignore[import]

import functions.file as f
import functions.workers as w
import functions.database as db

st.set_page_config(
    page_title="Parallel CSV Cleaner",
    layout="wide"
)

# custom CSS
st.markdown("""
<style>
/* global */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #F0F4F0;
    font-family: 'Inter', sans-serif;
}

/* hide default header */
[data-testid="stHeader"] { background: transparent; }

/* sidebar */
[data-testid="stSidebar"] {
    background-color: #1B3A2D;
    border-right: none;
}
[data-testid="stSidebar"] * {
    color: #E8F5E2 !important;
}
[data-testid="stSidebar"] .stSlider label { color: #A8D5B5 !important; }
[data-testid="stSidebar"] hr { border-color: #2E5A42; }

/* main content padding */
.block-container { padding: 2rem 2.5rem 2rem 2.5rem !important; }

/* card style */
.card {
    background: #FFFFFF;
    border-radius: 16px;
    padding: 24px 28px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    margin-bottom: 1rem;
}

/* metric cards */
.metric-card {
    background: #FFFFFF;
    border-radius: 16px;
    padding: 20px 24px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    border-left: 4px solid #2E7D32;
}
.metric-label {
    font-size: 12px;
    font-weight: 600;
    color: #6B7280;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 6px;
}
.metric-value {
    font-size: 28px;
    font-weight: 700;
    color: #1B3A2D;
    line-height: 1.1;
}
.metric-sub {
    font-size: 12px;
    color: #2E7D32;
    margin-top: 4px;
    font-weight: 500;
}

/* section headers */
.section-header {
    font-size: 18px;
    font-weight: 700;
    color: #1B3A2D;
    margin-bottom: 16px;
}

/* success banner */
.success-banner {
    background: linear-gradient(135deg, #1B3A2D, #2E7D32);
    color: white;
    border-radius: 12px;
    padding: 16px 24px;
    font-size: 15px;
    font-weight: 600;
    margin-bottom: 1.5rem;
}

/* page title */
.page-title {
    font-size: 28px;
    font-weight: 800;
    color: #1B3A2D;
    margin-bottom: 4px;
}
.page-subtitle {
    font-size: 14px;
    color: #6B7280;
    margin-bottom: 2rem;
}

/* upload area */
[data-testid="stFileUploader"] {
    background: #FFFFFF;
    border-radius: 16px;
    padding: 8px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}

/* primary button */
.stButton > button {
    background: linear-gradient(135deg, #1B3A2D, #2E7D32) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 12px 24px !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    width: 100% !important;
}
.stButton > button:hover {
    opacity: 0.9 !important;
    transform: translateY(-1px);
}
</style>
""", unsafe_allow_html=True)

os.makedirs("db", exist_ok=True)
db.create_db()

# sidebar
with st.sidebar:
    st.markdown("## CSV Cleaner")
    st.markdown("---")
    st.markdown("**How it works**")
    st.markdown("""
1. Upload the Superstore CSV  
2. Preview raw data  
3. Click **Clean CSV**  
4. View analytics
    """)
    st.markdown("---")
    num_workers = st.slider("Workers", min_value=1, max_value=8, value=4)
    st.markdown("---")
    st.info("Designed for the Superstore Sales dataset from Kaggle.")

# page header
st.markdown('<div class="page-title">Parallel CSV Cleaner</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload your CSV", type=["csv"])

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    raw_df = pd.read_csv(tmp_path)

    # metric cards row
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Rows</div>
            <div class="metric-value">{len(raw_df):,}</div>
            <div class="metric-sub">Raw records</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Columns</div>
            <div class="metric-value">{len(raw_df.columns)}</div>
            <div class="metric-sub">Data fields</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">File Size</div>
            <div class="metric-value">{uploaded_file.size / 1024:.1f} KB</div>
            <div class="metric-sub">Uploaded</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # raw preview card
    with st.expander("Preview Raw Data", expanded=False):
        st.dataframe(raw_df.head(10), use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button(f"Clean CSV with {num_workers} Workers"):
        with st.spinner("Processing in parallel..."):
            start = time.time()
            chunks = f.split_csv(tmp_path)
            cleaned_df = w.distribute_work(chunks)
            db.insert_data(cleaned_df)
            elapsed = time.time() - start

        rows_removed = len(raw_df) - len(cleaned_df)

        st.markdown(f"""
        <div class="success-banner">
            ✅ &nbsp; Cleaned {len(cleaned_df):,} rows in {elapsed:.2f}s using {num_workers} workers
        </div>""", unsafe_allow_html=True)

        # cleaning summary cards
        d1, d2, d3 = st.columns(3)
        with d1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Rows Before</div>
                <div class="metric-value">{len(raw_df):,}</div>
            </div>""", unsafe_allow_html=True)
        with d2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Rows After</div>
                <div class="metric-value">{len(cleaned_df):,}</div>
            </div>""", unsafe_allow_html=True)
        with d3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Rows Removed</div>
                <div class="metric-value" style="color:#C62828;">{rows_removed:,}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # cleaned data preview
        result_df = db.fetch_data()
        with st.expander("Preview Cleaned Data", expanded=False):
            display_df = result_df.copy()
            display_df.columns = [col.replace("_", " ").title() for col in display_df.columns]
            st.dataframe(display_df.head(10), use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # charts
        st.markdown('<div class="section-header">Analytics</div>', unsafe_allow_html=True)

        chart_col1, chart_col2 = st.columns(2)
        green_palette = ["#1B3A2D", "#2E7D32", "#388E3C", "#43A047", "#66BB6A", "#A5D6A7"]

        with chart_col1:
            category_sales = result_df.groupby("category")["sales"].sum().reset_index()
            fig1 = px.bar(category_sales, x="category", y="sales",
                          color="category",
                          color_discrete_sequence=green_palette)
            fig1.update_layout(
                title="Sales by Category",
                plot_bgcolor="white", paper_bgcolor="white",
                showlegend=False,
                font=dict(color="#1B3A2D"),
                margin=dict(t=40, b=20, l=10, r=10)
            )
            st.plotly_chart(fig1, use_container_width=True)

        with chart_col2:
            region_sales = result_df.groupby("region")["sales"].sum().reset_index()
            fig2 = px.bar(region_sales, x="region", y="sales",
                          color="region",
                          color_discrete_sequence=green_palette)
            fig2.update_layout(
                title="Sales by Region",
                plot_bgcolor="white", paper_bgcolor="white",
                showlegend=False,
                font=dict(color="#1B3A2D"),
                margin=dict(t=40, b=20, l=10, r=10)
            )
            st.plotly_chart(fig2, use_container_width=True)

        result_df["order_date"] = pd.to_datetime(result_df["order_date"], format='mixed')
        time_sales = result_df.groupby("order_date")["sales"].sum().reset_index()
        fig3 = px.area(time_sales, x="order_date", y="sales",
                       color_discrete_sequence=["#2E7D32"])
        fig3.update_layout(
            title="Sales Over Time",
            plot_bgcolor="white", paper_bgcolor="white",
            font=dict(color="#1B3A2D"),
            margin=dict(t=40, b=20, l=10, r=10)
        )
        fig3.update_traces(fill='tozeroy', fillcolor='rgba(46,125,50,0.15)')
        st.plotly_chart(fig3, use_container_width=True)

        os.unlink(tmp_path)