from datetime import datetime, timedelta
import streamlit as st
import plotly.express as px


def render_dashboard(filtered_df):
    st.subheader("📊 Usage Overview")
    if not filtered_df.empty:
        col1, col2, col3, col4 = st.columns(4)
        total_time = filtered_df["duration"].sum()
        total_apps = filtered_df["app_name"].nunique()
        avg_session = filtered_df["duration"].mean()
        most_used = filtered_df.groupby("app_name")["duration"].sum().idxmax()

        with col1:
            st.metric("Total Time", f"{total_time // 3600}h {(total_time % 3600) // 60}m")
        with col2:
            st.metric("Applications Used", total_apps)
        with col3:
            st.metric("Avg Session", f"{avg_session // 60:.0f}m")
        with col4:
            st.markdown(f"""
            <div style='text-align: center; color: white;'>Most Used App</div>
            <div style='text-align: center; font-size: 22px; color: white;'>{most_used}</div>
            """, unsafe_allow_html=True)

        # Daily Comparison
        st.subheader("📅 Daily Comparison")
        col1, col2 = st.columns(2)
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)

        today_total = filtered_df[filtered_df["date"] == today]["duration"].sum() // 60
        yesterday_total = filtered_df[filtered_df["date"] == yesterday]["duration"].sum() // 60

        with col1:
            st.metric("Today", f"{today_total} minutes", delta=f"{today_total - yesterday_total} min")
        with col2:
            st.metric("Yesterday", f"{yesterday_total} minutes")

        # Top Applications
        st.subheader("🏆 Top Applications")
        app_usage = filtered_df.groupby("app_name")["duration"].sum().sort_values(ascending=False).head(5)
        app_usage_min = (app_usage / 60).round(1)
        fig = px.bar(x=app_usage_min.values,
                     y=app_usage_min.index, orientation='h',
                     title="Top 5 Applications by Usage Time (minutes)",
                     labels={'x': 'Minutes', 'y': 'Application'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data available for the selected filters.")
