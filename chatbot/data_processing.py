import pandas as pd
from langchain.schema import Document

class DataProcessor:
    @staticmethod
    def load_usage_data(csv_path):
        try:
            df = pd.read_csv(csv_path, header=0)
            df["duration"] = pd.to_numeric(df["duration"], errors="coerce")
            df = df[df["duration"].notnull()].copy()
            df["duration"] = df["duration"].fillna(0).astype(int)
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df['date'] = df["timestamp"].apply(lambda x: x.date() if not pd.isnull(x) else x)
            df['hour'] = df["timestamp"].apply(lambda x: x.hour if not pd.isnull(x) else x)
            return df
        except Exception as e:
            print(f"❌ Data loading error: {e}")
            return pd.DataFrame()

    @staticmethod
    def create_documents(df):
        documents = []

        daily_stats = df.groupby(['date', 'app_name'])['duration'].sum().reset_index()
        for _, row in daily_stats.iterrows():
            minutes = row['duration'] // 60
            seconds = row['duration'] % 60
            content = f"Date: {row['date']}, App: {row['app_name']}, Duration: {minutes} minutes {seconds} seconds"
            documents.append(Document(page_content=content,
                                      metadata={"date": str(row['date']),
                                                "app_name": row['app_name'],
                                                "duration": row['duration'],
                                                "type": "daily_usage"}))

        hourly_stats = df.groupby(['date', 'hour'])['duration'].sum().reset_index()
        for _, row in hourly_stats.iterrows():
            if row['duration'] > 300:
                content = f"Date: {row['date']}, Hour: {row['hour']}:00, Total Activity: {row['duration']//60} minutes"
                documents.append(Document(page_content=content,
                                          metadata={"date": str(row['date']),
                                                    "hour": row['hour'],
                                                    "duration": row['duration'],
                                                    "type": "hourly_activity"}))

        app_totals = df.groupby('app_name')['duration'].agg(['sum', 'count']).reset_index()
        for _, row in app_totals.iterrows():
            total_minutes = row['sum'] // 60
            avg_session = (row['sum'] / row['count']) // 60
            content = (f"App: {row['app_name']}, Total Usage: {total_minutes} minutes, "
                       f"Avg Session: {avg_session} minutes, Used {row['count']} times")
            documents.append(Document(page_content=content,
                                      metadata={"app_name": row['app_name'],
                                                "total_duration": row['sum'],
                                                "session_count": row['count'],
                                                "type": "app_summary"}))

        return documents
