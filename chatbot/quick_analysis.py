from datetime import datetime, timedelta
from typing import Dict, Any
import pandas as pd

def perform_quick_analysis(df: pd.DataFrame, question_type: str, question: str) -> Dict[str, Any]:
    if df.empty:
        return {"error": "No data found"}

    today = datetime.now().date()
    yesterday = today - timedelta(days=1)

    if question_type == 'daily_total':
        today_data = df[df['date'] == today]
        total_seconds = today_data['duration'].sum()
        total_minutes = total_seconds // 60
        total_hours = total_minutes // 60
        remaining_minutes = total_minutes % 60
        return {
            'type': 'daily_total',
            'total_seconds': total_seconds,
            'total_minutes': total_minutes,
            'total_hours': total_hours,
            'remaining_minutes': remaining_minutes,
            'app_count': today_data['app_name'].nunique(),
            'most_used_today': today_data.groupby('app_name')['duration'].sum().idxmax() if not today_data.empty else None
        }

    elif question_type == 'app_ranking':
        today = datetime.now().date()
        today_data = df[df['date'] == today]
        if today_data.empty:
            return {"error": "No usage data found for today"}

        app_totals = today_data.groupby('app_name')['duration'].sum().sort_values(ascending=False)
        if app_totals.empty:
            return {"error": "No app usage data"}

        top_app = app_totals.idxmax()
        top_duration = app_totals.max()
        top_minutes = top_duration // 60
        total_duration = today_data['duration'].sum()

        return {
            'type': 'app_ranking',
            'top_app': top_app,
            'top_minutes': top_minutes,
            'total_duration_minutes': total_duration // 60,
            'percentage': round((top_duration / total_duration) * 100, 1) if total_duration > 0 else 0
        }


    elif question_type == 'yesterday_comparison':
        today_data = df[df['date'] == today]
        yesterday_data = df[df['date'] == yesterday]

        today_total = today_data['duration'].sum() // 60
        yesterday_total = yesterday_data['duration'].sum() // 60
        change = today_total - yesterday_total
        change_percent = round((change / yesterday_total * 100), 1) if yesterday_total > 0 else 0

        return {
            'type': 'yesterday_comparison',
            'today_minutes': today_total,
            'yesterday_minutes': yesterday_total,
            'change_minutes': change,
            'change_percent': change_percent,
            'trend': 'increase' if change > 0 else 'decrease' if change < 0 else 'same'
        }

    elif question_type == 'weekly_trend':
        week_ago = today - timedelta(days=7)
        weekly_data = df[df['date'] >= week_ago]
        daily_totals = weekly_data.groupby('date')['duration'].sum() // 60

        return {
            'type': 'weekly_trend',
            'daily_totals': daily_totals.to_dict(),
            'average_daily': round(daily_totals.mean(), 1),
            'peak_day': daily_totals.idxmax(),
            'peak_minutes': daily_totals.max(),
            'lowest_day': daily_totals.idxmin(),
            'lowest_minutes': daily_totals.min()
        }

    elif question_type == 'hourly_pattern':
        hourly_totals = df.groupby('hour')['duration'].sum() // 60
        peak_hour = hourly_totals.idxmax()

        return {
            'type': 'hourly_pattern',
            'hourly_data': hourly_totals.to_dict(),
            'peak_hour': peak_hour,
            'peak_minutes': hourly_totals.max(),
            'most_active_hours': hourly_totals.nlargest(3).to_dict()
        }
    

    elif question_type == "weekly_productivity":
        week_ago = today - timedelta(days=7)
        week_data = df[df['date'] >= week_ago]
        total_seconds = week_data['duration'].sum()
        total_minutes = total_seconds // 60
        total_hours = total_minutes // 60
        remaining_minutes = total_minutes % 60

        return {
            "type": "weekly_productivity",
            "total_seconds": total_seconds,
            "total_minutes": total_minutes,
            "total_hours": total_hours,
            "remaining_minutes": remaining_minutes,
            "app_count": week_data['app_name'].nunique()
        }
    
    elif question_type == 'most_focused_day':
        week_ago = today - timedelta(days=7)
        week_data = df[df['date'] >= week_ago]
        if week_data.empty:
            return {"error": "No data for the last week"}

        daily_totals = week_data.groupby('date')['duration'].sum()
        max_day = daily_totals.idxmax()
        max_duration = daily_totals.max()

        max_minutes = max_duration // 60
        max_hours = max_minutes // 60
        rem_minutes = max_minutes % 60

        return {
            "type": "most_focused_day",
            "day": max_day,
            "total_seconds": max_duration,
            "total_minutes": max_minutes,
            "total_hours": max_hours,
            "remaining_minutes": rem_minutes
        }

    return {"error": "Unknown question type"}
