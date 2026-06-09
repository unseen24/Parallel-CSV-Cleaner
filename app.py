import streamlit as st
import pandas as pd
import tempfile
import os
import time

import functions.file as f
import functions.workers as w
import functions.database as db

os.makedirs("db", exist_ok=True)
db.create_db()

st.title("Parallel CSV Cleaner")
st.markdown("Upload a sales CSV to clean it using parallel processing and store results in a database.")

uploaded_file = st.file_uploader("Upload your CSV", type=["csv"])

if uploaded_file is not None:

    # save upload to a temp file so pandas can read it
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    raw_df = pd.read_csv(tmp_path)
    st.subheader("Raw Data Preview")
    st.dataframe(raw_df.head(10))
    st.write(f"Total rows before cleaning: **{len(raw_df)}**")

    if st.button("Clean CSV"):
        with st.spinner("Cleaning in parallel..."):
            start = time.time()
            chunks = f.split_csv(tmp_path)
            cleaned_df = w.distribute_work(chunks)
            db.insert_records(cleaned_df)
            elapsed = time.time() - start

        st.success(f"Done in {elapsed:.2f} seconds using 4 workers")
        st.write(f"Rows after cleaning: **{len(cleaned_df)}**")
        st.write(f"Rows removed: **{len(raw_df) - len(cleaned_df)}**")

        # fetch from DB and display
        st.subheader("Cleaned Data (from database)")
        result_df = db.fetch_records()
        st.dataframe(result_df.head(10))

        # charts
        st.subheader("Sales by Category")
        category_sales = result_df.groupby("category")["sales"].sum().reset_index()
        st.bar_chart(category_sales.set_index("category"))

        st.subheader("Sales by Region")
        region_sales = result_df.groupby("region")["sales"].sum().reset_index()
        st.bar_chart(region_sales.set_index("region"))

        st.subheader("Sales Over Time")
        result_df["order_date"] = pd.to_datetime(result_df["order_date"])
        time_sales = result_df.groupby("order_date")["sales"].sum().reset_index()
        st.line_chart(time_sales.set_index("order_date"))

        os.unlink(tmp_path)