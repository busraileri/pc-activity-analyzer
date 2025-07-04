import streamlit as st
import os
import pandas as pd
from datetime import datetime


def render_settings(df):
    st.subheader("Configuration & Data Management")
    st.subheader("📂 Data Information")
    if not df.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Total Records:** {len(df)}")
            st.info(f"**Date Range:** {df['date'].min()} to {df['date'].max()}")
        with col2:
            st.info(f"**Unique Applications:** {df['app_name'].nunique()}")
            st.info(f"**File Size:** {os.path.getsize('data/usage_log.csv') / 1024:.1f} KB")

    st.subheader("📥 Export Data")
    csv = df.to_csv(index=False)
    st.download_button("💾 Download CSV", data=csv, file_name="usage_data.csv", mime="text/csv")
 