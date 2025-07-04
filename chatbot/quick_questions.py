import re
from typing import Dict

quick_question_patterns: Dict[str, list] = {
    'most_focused_day': [
        r'which day.*most focused',
        r'most focused day',
        r'focus.*day',
        r'most productive day',
        r'best focused day'
    ],
    'daily_total': [
        r'today.*total',
        r'daily.*total',
        r'today.*how many minutes',
        r'how much.*today'
    ],
    'app_ranking': [
        r'most.*used',
        r'which app.*most',
        r'top.*app',
        r'most.*frequent',
        r'most used app',
        r'which app did i use most',
        r'what app.*most',
        r'what.*top.*app'
    ],
    'yesterday_comparison': [
        r'yesterday.*today',
        r'compare.*yesterday',
        r'difference.*yesterday',
        r'change.*yesterday'
    ],
    'weekly_trend': [
        r'week.*trend',
        r'weekly.*usage',
        r'last.*week',
        r'past.*week',
        r'weekly.*pattern'
    ],
    'hourly_pattern': [
        r'which hour.*most',
        r'peak.*hour',
        r'time.*active',
        r'hour.*usage',
        r'most active hour',
        r'active hours'
    ],
    'weekly_productivity': [
        r'productive.*week',
        r'how productive.*week',
        r'weekly.*productivity',
        r'week.*usage'
    ]
}


def classify_question(question: str, patterns=quick_question_patterns) -> str:
    priority_order = [
        'most_focused_day',
        'daily_total',
        'app_ranking',
        'yesterday_comparison',
        'weekly_trend',
        'hourly_pattern',
        'weekly_productivity'
    ]
    question_lower = question.lower()
    for category in priority_order:
        regex_list = patterns.get(category, [])
        for pattern in regex_list:
            if re.search(pattern, question_lower):
                return category
    return 'general'
