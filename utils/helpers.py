from datetime import timedelta
import streamlit as st

def format_duration(hours_float):
    total_minutes = int(hours_float * 60)
    h = total_minutes // 60
    m = total_minutes % 60
    return f"{h}h {m}min"

def apply_filters(df):
    st.sidebar.title("Filter Options")
    min_date = df["date"].min()
    max_date = df["date"].max()
    default_start = max_date - timedelta(days=7)
    if default_start < min_date:
        default_start = min_date
    date_range = st.sidebar.date_input("Select date range", value=(default_start, max_date),
                                       min_value=min_date, max_value=max_date)
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]
    else:
        filtered_df = df
    app_names = ["All Apps"] + sorted(filtered_df["app_name"].unique().tolist())
    selected_app = st.sidebar.selectbox("Select application", app_names)
    if selected_app != "All Apps":
        filtered_df = filtered_df[filtered_df["app_name"] == selected_app]
    return filtered_df, selected_app