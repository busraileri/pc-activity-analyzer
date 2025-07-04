import pandas as pd

def load_usage_data(csv_path="data/usage_log.csv"):
    try:
        df = pd.read_csv(csv_path)
        df["duration"] = pd.to_numeric(df["duration"], errors="coerce").fillna(0).astype(int)
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors='coerce')
        df = df.dropna(subset=["timestamp"])
        df["date"] = df["timestamp"].dt.date
        df["hour"] = df["timestamp"].dt.hour
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame()
