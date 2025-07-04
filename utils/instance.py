import streamlit as st
from chatbot.usage_data_rag import UsageDataRAG


def get_rag_instance():
    # Session state
    if 'rag_instance' not in st.session_state:
        st.session_state.rag_instance = UsageDataRAG()
    return st.session_state.rag_instance

