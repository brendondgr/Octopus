"""
Deadline calculation utilities for projects and goals.
"""
from datetime import datetime, timedelta
from typing import Dict, Optional


def calculate_time_remaining(deadline: datetime) -> Dict:
    """
    Calculate time remaining until deadline.
    
    Returns:
        dict with keys:
        - days: int (negative if overdue)
        - hours: int
        - is_overdue: bool
        - is_approaching: bool (within 3 days)
    """
    if deadline is None:
        return None
    
    now = datetime.utcnow()
    delta = deadline - now
    
    total_seconds = delta.total_seconds()
    is_overdue = total_seconds < 0
    
    # Convert to absolute values for display
    abs_delta = abs(delta)
    days = abs_delta.days
    hours = abs_delta.seconds // 3600
    
    return {
        'days': days if not is_overdue else -days,
        'hours': hours,
        'is_overdue': is_overdue,
        'is_approaching': not is_overdue and delta.days <= 3
    }


def format_time_remaining(deadline: datetime) -> str:
    """
    Format time remaining as human-readable string.
    
    Examples:
        "Due in 5 days"
        "Due in 2 hours"
        "Due today"
        "Overdue by 3 days"
    """
    if deadline is None:
        return None
    
    remaining = calculate_time_remaining(deadline)
    
    if remaining['is_overdue']:
        days = abs(remaining['days'])
        if days == 0:
            return "Overdue"
        elif days == 1:
            return "Overdue by 1 day"
        else:
            return f"Overdue by {days} days"
    else:
        days = remaining['days']
        hours = remaining['hours']
        
        if days >= 730:
            years = days // 365
            if years == 1:
                return "Due in 1 year"
            else:
                return f"Due in {years} years"
        elif days == 0:
            if hours == 0:
                return "Due now"
            elif hours == 1:
                return "Due in 1 hour"
            else:
                return f"Due in {hours} hours"
        elif days == 1:
            return "Due tomorrow"
        else:
            return f"Due in {days} days"


def is_overdue(deadline: datetime) -> bool:
    """Check if deadline has passed."""
    if deadline is None:
        return False
    return datetime.utcnow() > deadline


def is_approaching(deadline: datetime, days: int = 3) -> bool:
    """Check if deadline is within warning threshold."""
    if deadline is None:
        return False
    
    now = datetime.utcnow()
    threshold = now + timedelta(days=days)
    
    return now < deadline <= threshold


def get_deadline_status(deadline: datetime) -> Optional[Dict]:
    """
    Get comprehensive deadline status for template rendering.
    
    Returns:
        dict with keys:
        - display: str (formatted time remaining)
        - css_class: str (CSS class for styling)
        - date_formatted: str (formatted deadline date)
        - is_overdue: bool
        - is_approaching: bool
    
    Returns None if deadline is None.
    """
    if deadline is None:
        return None
    
    remaining = calculate_time_remaining(deadline)
    display = format_time_remaining(deadline)
    
    # Determine CSS class
    if remaining['is_overdue']:
        css_class = 'deadline-overdue'
    elif remaining['is_approaching']:
        css_class = 'deadline-warning'
    else:
        css_class = 'deadline-normal'
    
    return {
        'display': display,
        'css_class': css_class,
        'date_formatted': deadline.strftime('%b %d, %Y'),
        'date_short': deadline.strftime('%y-%m-%d'),
        'is_overdue': remaining['is_overdue'],
        'is_approaching': remaining['is_approaching']
    }
