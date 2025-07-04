import logging
import re
import pandas as pd
from typing import List, Dict, Any
from langchain.schema import Document
from sentence_transformers import SentenceTransformer
from chatbot.vector_store_manager import VectorStoreManager
from chatbot.llm_handler import LLMHandler
from chatbot.quick_questions import quick_question_patterns
from chatbot.quick_analysis import perform_quick_analysis
from chatbot.quick_questions import classify_question as external_classify_question


class UsageDataRAG:
    def __init__(self, csv_path="data/usage_log.csv", model_name="llama3.1:8b-instruct-q4_0"):
        self.csv_path = csv_path
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.vector_store = VectorStoreManager(collection_name="usage_data")
        self.llm_handler = LLMHandler(model_name=model_name)

        self.df = None
        self.quick_question_patterns = quick_question_patterns

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        self._load_and_process_data()

    def _load_usage_data(self):
        if self.df is not None:
            return self.df

        try:
            df = pd.read_csv(self.csv_path)
            df["duration"] = pd.to_numeric(df["duration"], errors="coerce")
            df = df[df["duration"].notnull()].copy()
            df["duration"] = df["duration"].astype(int)
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df["date"] = df["timestamp"].dt.date
            df["hour"] = df["timestamp"].dt.hour
            df["weekday"] = df["timestamp"].dt.day_name()
            self.df = df
            return df
        except Exception as e:
            self.logger.error(f"❌ Error loading data: {e}")
            return pd.DataFrame()

    def _create_documents(self, df: pd.DataFrame) -> List[Document]:
        documents = []

        # Daily app-based total time
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

        # Hourly total activity
        hourly_stats = df.groupby(['date', 'hour'])['duration'].sum().reset_index()
        for _, row in hourly_stats.iterrows():
            if row['duration'] > 300:  # 5 dakikadan fazla
                content = f"Date: {row['date']}, Hour: {row['hour']}:00, Total Activity: {row['duration']//60} minutes"
                documents.append(Document(
                    page_content=content,
                    metadata={
                        "date": str(row['date']),
                        "hour": row['hour'],
                        "duration": row['duration'],
                        "type": "hourly_activity"
                    }
                ))

        # App-based total and average usage
        app_totals = df.groupby('app_name')['duration'].agg(['sum', 'count']).reset_index()
        for _, row in app_totals.iterrows():
            total_minutes = row['sum'] // 60
            avg_session = (row['sum'] / row['count']) // 60
            content = (f"App: {row['app_name']}, Total Usage: {total_minutes} minutes, "
                      f"Average Session: {avg_session} minutes, Used {row['count']} times")
            documents.append(Document(
                page_content=content,
                metadata={
                    "app_name": row['app_name'],
                    "total_duration": row['sum'],
                    "session_count": row['count'],
                    "type": "app_summary"
                }
            ))

        self.logger.info(f"✅ {len(documents)} documents created")
        return documents

    def _load_and_process_data(self):
        df = self._load_usage_data()
        if df.empty:
            self.logger.warning("Dataframe is empty, skipping vector store load")
            return
        existing_count = self.vector_store.get_collection_count()
        if existing_count == 0:
            documents = self._create_documents(df)
            texts = [doc.page_content for doc in documents]
            embeddings = self.embedding_model.encode(texts)
            self.vector_store.add_documents(embeddings.tolist(), texts, [doc.metadata for doc in documents])
            self.logger.info(f"✅ {len(documents)} records added to vector store")
        else:
            self.logger.info(f"✅ Vector store already has {existing_count} records")

    def _classify_question(self, question: str) -> str:
        category = external_classify_question(question)
        self.logger.info(f"Question matched category: {category}")
        return category

    def _generate_explanation_from_analysis(self, analysis_result: Dict[str, Any], original_question: str) -> str:
        if 'error' in analysis_result:
            return f"Sorry, {analysis_result['error']}"

        result_type = analysis_result.get('type')

        if result_type == 'app_ranking':
            top_app = analysis_result.get('top_app', 'an app')
            top_minutes = analysis_result.get('top_minutes', 0)
            percentage = analysis_result.get('percentage', 0)
            return (f"You used {top_app} the most today, for about "
                f"{top_minutes} minutes, which is {percentage}% of your total usage.")

        if result_type == 'hourly_pattern':
            peak_hour = analysis_result.get('peak_hour', None)
            peak_minutes = analysis_result.get('peak_minutes', 0)
            most_active = analysis_result.get('most_active_hours', {})
            active_hours_str = ", ".join([f"{hour}:00 ({mins} minutes)" for hour, mins in most_active.items()])
            return (f"Your most active hour was {peak_hour}:00 with {peak_minutes} minutes of usage. "
                f"Other active hours include: {active_hours_str}.")

        if result_type == 'weekly_productivity':
            total_hours = analysis_result.get('total_hours', 0)
            remaining_minutes = analysis_result.get('remaining_minutes', 0)
            app_count = analysis_result.get('app_count', 0)
            return (f"This week, you were productive for {total_hours} hours and "
                f"{remaining_minutes} minutes, using {app_count} different apps.")

        if result_type == 'most_focused_day':
            day = analysis_result.get('day', 'a day')
            hours = analysis_result.get('total_hours', 0)
            minutes = analysis_result.get('remaining_minutes', 0)
            return f"You were most focused on {day}, spending {hours} hours and {minutes} minutes working."

        # LLM
        prompt = f"""
User asked the question: "{original_question}"

Python analysis gave the following result: {analysis_result}

Based on this data, generate a clear, friendly, and informative answer in English.
Express numbers in natural language and add extra comments if needed. 
"""
        try:
            return self.llm_handler.generate_simple_response(prompt)
        except Exception as e:
            self.logger.error(f"Error generating LLM response: {e}")
            return "Sorry, an error occurred while generating the response."


    def answer_question(self, question: str) -> str:
        question_type = self._classify_question(question)
        self.logger.info(f"Classified question type: {question_type}")

        if question_type != 'general':
            self.logger.info(f"Performing quick analysis for question type: {question_type}")
            analysis_result = perform_quick_analysis(self._load_usage_data(), question_type, question)
            response = self._generate_explanation_from_analysis(analysis_result, question)
            return response.strip()
        else:
            self.logger.info("Performing general query using vector store")
            try:
                context = self.vector_store.query_relevant_docs(question)
                response = self.llm_handler.generate_response(context, question)
                return response.strip()
            except Exception as e:
                self.logger.error(f"Error in vector store or LLM response: {e}")
                return "Sorry, an error occurred while answering the general question."
