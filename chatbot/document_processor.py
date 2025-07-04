import pandas as pd
from typing import List
from langchain.schema import Document

class DocumentProcessor:
    @staticmethod
    def create_documents(df: pd.DataFrame) -> List[Document]:
        documents = []

        daily_stats = df.groupby(['date', 'app_name'])['duration'].sum().reset_index()
        for _, row in daily_stats.iterrows():
            minutes = row['duration'] // 60
            seconds = row['duration'] % 60
            content = f"Date: {row['date']}, App: {row['app_name']}, Duration: {minutes} minutes {seconds} seconds"
            documents.append(Document(
                page_content=content,
                metadata={
                    "date": str(row['date']),
                    "app_name": row['app_name'],
                    "duration": row['duration'],
                    "type": "daily_usage"
                }
            ))

        hourly_stats = df.groupby(['date', 'hour'])['duration'].sum().reset_index()
        for _, row in hourly_stats.iterrows():
            if row['duration'] > 300:  # Only if usage > 5 mins
                content = f"Date: {row['date']}, Hour: {row['hour']}:00, Total Activity: {row['duration'] // 60} minutes"
                documents.append(Document(
                    page_content=content,
                    metadata={
                        "date": str(row['date']),
                        "hour": row['hour'],
                        "duration": row['duration'],
                        "type": "hourly_activity"
                    }
                ))

        app_totals = df.groupby('app_name')['duration'].agg(['sum', 'count']).reset_index()
        for _, row in app_totals.iterrows():
            total_minutes = row['sum'] // 60
            avg_session = (row['sum'] / row['count']) // 60 if row['count'] > 0 else 0
            content = f"App: {row['app_name']}, Total Usage: {total_minutes} minutes, Average Session: {avg_session} minutes, Used {row['count']} times"
            documents.append(Document(
                page_content=content,
                metadata={
                    "app_name": row['app_name'],
                    "total_duration": row['sum'],
                    "session_count": row['count'],
                    "type": "app_summary"
                }
            ))

        print(f"✅ {len(documents)} documents created.")
        return documents
