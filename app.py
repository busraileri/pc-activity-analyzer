import streamlit as st
from datetime import timedelta
from utils.data_loader import load_usage_data
from utils.helpers import apply_filters
from components.dashboard import render_dashboard
from components.analytics import render_analytics
from components.ai_chat import render_ai_chat
from components.settings import render_settings



st.set_page_config(
    page_title="PC Activity Analyzer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)


with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


st.markdown('''
    <div class="main-header">
    📈 Personal Computer Activity Analyzer
    </div>
    <div class="description">
        Understand your digital habits and take control of your screen time
    </div>
''', unsafe_allow_html=True)


df = load_usage_data()
if df.empty:
    st.error("⚠️ No usage data found. Make sure 'data/usage_log.csv' exists.")
    st.stop()

# Sidebar 
filtered_df, selected_app = apply_filters(df)

# Session state 
if "current_page" not in st.session_state:
    st.session_state.current_page = "dashboard"

# Navigation bar
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("📊 Dashboard", key="nav_dashboard", 
                use_container_width=True,
                type="primary" if st.session_state.current_page == "dashboard" else "secondary"):
        st.session_state.current_page = "dashboard"
        st.rerun()

with col2:
    if st.button("📈 Analytics", key="nav_analytics", 
                use_container_width=True,
                type="primary" if st.session_state.current_page == "analytics" else "secondary"):
        st.session_state.current_page = "analytics"
        st.rerun()

with col3:
    if st.button("🤖 AI Chat", key="nav_ai_chat", 
                use_container_width=True,
                type="primary" if st.session_state.current_page == "ai_chat" else "secondary"):
        st.session_state.current_page = "ai_chat"
        st.rerun()

with col4:
    if st.button("⚙️ Settings", key="nav_settings", 
                use_container_width=True,
                type="primary" if st.session_state.current_page == "settings" else "secondary"):
        st.session_state.current_page = "settings"
        st.rerun()

st.markdown("---")

# Page content
if st.session_state.current_page == "dashboard":
    render_dashboard(filtered_df)
elif st.session_state.current_page == "analytics":
    render_analytics(filtered_df)
elif st.session_state.current_page == "ai_chat":
    render_ai_chat()
elif st.session_state.current_page == "settings":
    render_settings(df)