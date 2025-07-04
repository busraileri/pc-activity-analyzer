import pandas as pd
import streamlit as st
import plotly.express as px
from utils.helpers import format_duration


def render_analytics(filtered_df):
    if not filtered_df.empty:
        filtered_df = filtered_df.copy()

        st.subheader("⏰ Usage Over Time")

        if not pd.api.types.is_datetime64_any_dtype(filtered_df['date']):
            filtered_df['date'] = pd.to_datetime(filtered_df['date'], errors='coerce')

        filtered_df.loc[:, 'day_only'] = filtered_df['date'].dt.date


        if pd.api.types.is_timedelta64_dtype(filtered_df['duration']):
            filtered_df.loc[:, 'duration_sec'] = filtered_df['duration'].dt.total_seconds()
        else:
            filtered_df.loc[:, 'duration'] = pd.to_numeric(filtered_df['duration'], errors='coerce')
            filtered_df = filtered_df[filtered_df['duration'].notnull()].copy()
            filtered_df.loc[:, 'duration_sec'] = filtered_df['duration'].astype(float)

        filtered_df.loc[:, 'day_only'] = filtered_df['date'].dt.date
        daily_usage = filtered_df.groupby('day_only')['duration_sec'].sum().reset_index()
        daily_usage['duration_hours'] = daily_usage['duration_sec'] / 3600
        daily_usage['date_formatted'] = pd.to_datetime(daily_usage['day_only']).dt.strftime('%d %b')
        daily_usage['formatted_duration'] = daily_usage['duration_hours'].apply(format_duration)
        daily_usage = daily_usage.sort_values('day_only')

        fig = px.bar(daily_usage, x='date_formatted', y='duration_hours',
                     title="Daily Usage Trends", text='formatted_duration',
                     color_discrete_sequence=["#4C72B0"],
                     labels={"date_formatted": "Date", "duration_hours": "Hours"})
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("🕐 Hourly Activity Patterns")
        hourly_activity = filtered_df.groupby("hour")["duration"].sum().reset_index()
        hourly_activity["duration_minutes"] = hourly_activity["duration"] / 60

        fig = px.line(hourly_activity, x="hour", y="duration_minutes",
                      title="Activity Pattern Throughout the Day",
                      labels={'hour': 'Hour of Day', 'duration_minutes': 'Total Minutes'},
                      markers=True, line_shape='spline')

        fig.update_traces(
            line=dict(width=3, color='#1f77b4'),
            marker=dict(size=6, color='#1f77b4')
        )

        fig.update_layout(
            xaxis=dict(
                tickmode='array',
                tickvals=list(range(0, 25, 2)),
                ticktext=[f"{i:02d}:00" for i in range(0, 25, 2)],
                title="Time of Day",
                range=[0, 23]
            ),
            yaxis=dict(title="Minutes")
        )

        # Time period background colors
        fig.add_vrect(x0=6, x1=12, fillcolor="rgba(255, 255, 0, 0.1)", 
                      layer="below", line_width=0, annotation_text="Morning", 
                      annotation_position="top")
        fig.add_vrect(x0=12, x1=18, fillcolor="rgba(255, 165, 0, 0.1)", 
                      layer="below", line_width=0, annotation_text="Afternoon", 
                      annotation_position="top")
        fig.add_vrect(x0=18, x1=22, fillcolor="rgba(255, 0, 0, 0.1)", 
                      layer="below", line_width=0, annotation_text="Evening", 
                      annotation_position="top")

        fig.update_layout(
            height=400,
            showlegend=False,
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("🎯 Application Breakdown")
        session_stats = filtered_df.groupby("app_name").agg({"duration": ["count", "mean", "sum"]}).round(2)
        session_stats.columns = ["Sessions", "Avg Duration (s)", "Total Duration (s)"]
        session_stats["Avg Duration (min)"] = (session_stats["Avg Duration (s)"] / 60).round(1)
        session_stats = session_stats.sort_values("Total Duration (s)", ascending=False).head(10)
        st.dataframe(session_stats[["Sessions", "Avg Duration (min)", "Total Duration (s)"]],
                     use_container_width=True)
