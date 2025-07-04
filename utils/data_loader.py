import pandas as pd
import streamlit as st

@st.cache_data
def load_usage_data():
    try:
        df = pd.read_csv("data/usage_log.csv")
        df["duration"] = df["duration"].astype(int)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["date"] = df["timestamp"].dt.date
        df["hour"] = df["timestamp"].dt.hour
        return df
    except:
        return pd.DataFrame()