from datetime import datetime, timedelta, timezone
from typing import List, Dict, Tuple, Optional


def parse_date(date_val: Optional[str]) -> Optional[datetime]:
    """
    Parse a date string (ISO format) and return a naive UTC datetime.
    Ensures compatibility with database-stored naive datetimes.
    """
    if not date_val:
        return None
    try:
        # If date has 'Z' suffix, treat as explicit UTC
        if date_val.endswith('Z'):
            dt = datetime.fromisoformat(date_val.replace('Z', '+00:00'))
            return dt.astimezone(timezone.utc).replace(tzinfo=None)
        
        # Parse the date
        dt = datetime.fromisoformat(date_val)
        
        # If it has timezone info, convert to naive UTC
        if dt.tzinfo is not None:
            return dt.astimezone(timezone.utc).replace(tzinfo=None)
        
        # If already naive, assume it's already in UTC (database format)
        return dt
    except (ValueError, TypeError):
        return None


def get_timeline_items_for_dashboard(projects: List) -> List[Dict]:
    """
    Return all projects and their goals as timeline items.
    
    Each item contains: id, name, type, start_date, end_date, status, 
    category_color, project_id, duration_days
    """
    items = []
    
    for project in projects:
        # Add project as timeline item
        items.append(project.get_timeline_item())
        
        # Add all goals for this project
        for goal in project.goals:
            items.append(goal.get_timeline_item())
    
    return items


def get_timeline_items_for_project(project) -> List[Dict]:
    """
    Return a project and its goals as timeline items.
    Includes the project itself as a reference bar.
    """
    items = [project.get_timeline_item()]
    
    for goal in project.goals:
        items.append(goal.get_timeline_item())
    
    return items


def calculate_date_range(items: List[Dict], padding_days: int = 7, explicit_range: Optional[Tuple[datetime, datetime]] = None) -> Tuple[datetime, datetime]:
    """
    Determine min/max dates for timeline view.
    If explicit_range is provided (min, max), it uses those as the bounds.
    Otherwise, it calculates from items with padding.
    """
    if explicit_range:
        return explicit_range
        
    if not items:
        now = datetime.utcnow()
        return (now - timedelta(days=30), now + timedelta(days=30))
    
    min_date = None
    max_date = None
    
    for item in items:
        start = parse_date(item.get('start_date')) if isinstance(item.get('start_date'), str) else item.get('start_date')
        end = parse_date(item.get('end_date')) if isinstance(item.get('end_date'), str) else item.get('end_date')
        
        if start:
            if min_date is None or start < min_date:
                min_date = start
        
        if end:
            if max_date is None or end > max_date:
                max_date = end
        elif start:  # Item without end date - use start as potential max
            if max_date is None or start > max_date:
                max_date = start
    
    # Default to current date if no dates found
    now = datetime.utcnow()
    if min_date is None:
        min_date = now - timedelta(days=30)
    if max_date is None:
        max_date = now
    
    # Add padding only if we didn't have an explicit range
    min_date = min_date - timedelta(days=padding_days)
    max_date = max_date + timedelta(days=padding_days)
    
    return (min_date, max_date)


def filter_timeline_items(
    items: List[Dict],
    date_start: Optional[datetime] = None,
    date_end: Optional[datetime] = None,
    status: Optional[List[str]] = None,
    project_id: Optional[int] = None,
    item_type: Optional[str] = None
) -> List[Dict]:
    """
    Filter timeline items by various criteria.
    
    Args:
        items: List of timeline item dicts
        date_start: Only include items ending after this date
        date_end: Only include items starting before this date
        status: List of statuses to include (e.g., ['Active', 'Completed'])
        project_id: Filter to specific project (for goals)
        item_type: 'project' or 'goal'
    
    Returns filtered list of items.
    """
    filtered = items
    
    if item_type:
        filtered = [i for i in filtered if i.get('type') == item_type]
    
    if status:
        filtered = [i for i in filtered if i.get('status') in status]
    
    if project_id is not None:
        # Include the project itself and its goals
        filtered = [i for i in filtered 
                   if i.get('project_id') == project_id 
                   or (i.get('type') == 'project' and i.get('id') == project_id)]
    
    if date_start:
        # Include items that end after date_start (or have no end date)
        def ends_after(item):
            end = item.get('end_date')
            if end is None:
                return True
            if isinstance(end, str):
                end = parse_date(end)
            # If end is a datetime, ensure it's naive for comparison
            if isinstance(end, datetime) and end.tzinfo is not None:
                end = end.astimezone(timezone.utc).replace(tzinfo=None)
            return end >= date_start
        filtered = [i for i in filtered if ends_after(i)]
    
    if date_end:
        # Include items that start before date_end
        def starts_before(item):
            start = item.get('start_date')
            if start is None:
                return True
            if isinstance(start, str):
                start = parse_date(start)
            # If start is a datetime, ensure it's naive for comparison
            if isinstance(start, datetime) and start.tzinfo is not None:
                start = start.astimezone(timezone.utc).replace(tzinfo=None)
            return start <= date_end
        filtered = [i for i in filtered if starts_before(i)]
    
    return filtered


def prepare_gantt_data(items: List[Dict], date_range: Tuple[datetime, datetime]) -> Dict:
    """
    Convert timeline items to full Gantt format with date axis.
    
    Returns: {
        "items": [...],
        "dateAxis": [...],
        "minDate": "...",
        "maxDate": "...",
        "zoomLevel": "week"
    }
    """
    min_date, max_date = date_range
    
    # Generate date axis based on range
    total_days = (max_date - min_date).days
    
    # Determine zoom level based on date range
    if total_days <= 14:
        zoom_level = "day"
        step_days = 1
    elif total_days <= 90:
        zoom_level = "week"
        step_days = 7
    else:
        zoom_level = "month"
        step_days = 30
    
    # Generate date axis labels
    date_axis = []
    current = min_date
    position = 0
    
    while current <= max_date:
        if zoom_level == "day":
            label = current.strftime("%b %d")
        elif zoom_level == "week":
            label = current.strftime("%b %d")
        else:
            label = current.strftime("%b %Y")
        
        date_axis.append({
            "date": current.isoformat(),
            "label": label,
            "position": position
        })
        
        current += timedelta(days=step_days)
        position += 1
    
    return {
        "items": items,
        "dateAxis": date_axis,
        "minDate": min_date.isoformat(),
        "maxDate": max_date.isoformat(),
        "zoomLevel": zoom_level
    }
