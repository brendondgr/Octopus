from flask import Blueprint, render_template, request, jsonify, make_response
from . import db
from .models import Project, Category, Goal
from datetime import datetime
import json

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    # Fetch real projects from DB, ordered by their drag-and-drop index
    # We join with Category to ensure we have the data
    projects = Project.query.join(Category).order_by(Project.order_index).all()
    return render_template('index.html', projects=projects)

@bp.route('/project/modal/new', methods=['GET'])
def new_project_modal():
    categories = Category.query.all()
    return render_template('components/modals/new_project.html', categories=categories)

@bp.route('/project/new', methods=['POST'])
def create_project():
    data = request.form
    
    # Category Logic
    cat_name = data.get('category_name')
    cat_color = data.get('category_color', 'blue')
    
    # 1. Check if category exists
    category = Category.query.filter_by(name=cat_name).first()
    
    if category:
        # 2. Existing: Update color globally if changed (User Requirement)
        if category.color != cat_color:
            category.color = cat_color
            # No commit yet, we do it at the end
    else:
        # 3. New: Create it
        category = Category(name=cat_name, color=cat_color)
        db.session.add(category)
        db.session.flush() # Flush to get ID if needed
    
    # Calculate new order index
    max_order = db.session.query(db.func.max(Project.order_index)).scalar()
    new_order = (max_order or 0) + 1
    
    # Parse optional deadline
    deadline = None
    deadline_str = data.get('deadline')
    if deadline_str:
        try:
            deadline = datetime.fromisoformat(deadline_str)
        except ValueError:
            pass  # Invalid date format, ignore
    
    new_project = Project(
        title=data.get('title'),
        description=data.get('description'),
        category=category, # SQLAlchemy handles the relationshp
        status='Active',
        order_index=new_order,
        deadline=deadline
    )
    
    db.session.add(new_project)
    db.session.commit()
    
    # Return the encoded card to be appended to the Active column
    return render_template('components/project_card.html', project=new_project)

@bp.route('/project/<int:project_id>/edit', methods=['GET'])
def edit_project_modal(project_id):
    project = Project.query.get_or_404(project_id)
    categories = Category.query.all()
    return render_template('components/modals/edit_project.html', project=project, categories=categories)

@bp.route('/project/<int:project_id>/edit', methods=['POST'])
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    data = request.form
    
    # Category Logic (same as create)
    cat_name = data.get('category_name')
    cat_color = data.get('category_color', 'blue')
    
    category = Category.query.filter_by(name=cat_name).first()
    
    if category:
        if category.color != cat_color:
            category.color = cat_color
    else:
        category = Category(name=cat_name, color=cat_color)
        db.session.add(category)
        db.session.flush()
        
    # Update Project Fields
    project.title = data.get('title')
    project.description = data.get('description')
    project.category = category
    
    # Parse optional deadline
    deadline_str = data.get('deadline')
    if deadline_str:
        try:
            project.deadline = datetime.fromisoformat(deadline_str)
        except ValueError:
            pass
    else:
        project.deadline = None
        
    db.session.commit()
    
    # Return updated card and trigger timeline update
    response = make_response(render_template('components/project_card.html', project=project))
    response.headers['HX-Trigger'] = json.dumps({"timeline-updated": {}})
    return response

@bp.route('/project/<int:project_id>', methods=['PATCH'])
def update_project(project_id):
    project = Project.query.get_or_404(project_id)
    
    # Update Status
    if 'status' in request.form:
        new_status = request.form['status']
        project.status = new_status
        
        # Update corresponding timestamp
        now = datetime.utcnow()
        if new_status == 'Completed':
            project.date_completed = now
        elif new_status == 'On-Hold':
            project.date_on_hold = now
        elif new_status == 'Abandoned':
            project.date_abandoned = now
        else:
            # Reset dates if moved back to Active
            project.date_completed = None
            project.date_on_hold = None
            project.date_abandoned = None
        
    db.session.commit()
    
    # Return updated card and trigger timeline update
    response = make_response(render_template('components/project_card.html', project=project))
    response.headers['HX-Trigger'] = json.dumps({"timeline-updated": {}})
    return response

@bp.route('/project/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    
    response = make_response('')
    response.headers['HX-Trigger'] = json.dumps({"timeline-updated": {}, "project-updated": {}})
    return response


# =====================
# Project Details Modal
# =====================
@bp.route('/project/<int:project_id>/details', methods=['GET'])
def project_details(project_id):
    project = Project.query.get_or_404(project_id)
    # Sort goals: Pending first, then Completed
    # Python's sort is stable, and False < True. 
    # status == 'Completed' will be True (1) for completed and False (0) for pending.
    sorted_goals = sorted(project.goals, key=lambda g: g.status == 'Completed')
    return render_template('components/modals/project_details.html', project=project, goals=sorted_goals)


# ================
# Goal Management
# ================
@bp.route('/project/<int:project_id>/goal', methods=['POST'])
def create_goal(project_id):
    project = Project.query.get_or_404(project_id)
    title = request.form.get('title', '').strip()
    
    if not title:
        return '', 400
    
    # Parse optional deadline
    deadline = None
    deadline_str = request.form.get('deadline')
    if deadline_str:
        try:
            deadline = datetime.fromisoformat(deadline_str)
        except ValueError:
            pass  # Invalid date format, ignore
    
    goal = Goal(
        project_id=project.id,
        title=title,
        status='Pending',
        deadline=deadline
    )
    db.session.add(goal)
    db.session.commit()
    
    # Prepare progress data for trigger
    completed = sum(1 for g in project.goals if g.status == 'Completed')
    trigger_data = {
        "updateProgress": {
            "projectId": project.id,
            "progress": project.calculate_progress(),
            "goalCount": f"{completed}/{len(project.goals)}"
        },
        "timeline-updated": {}
    }
    
    response = make_response(render_template('components/goal_item.html', goal=goal))
    response.headers['HX-Trigger'] = json.dumps(trigger_data)
    return response


@bp.route('/goal/<int:goal_id>/toggle', methods=['POST'])
def toggle_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    project = goal.project
    
    if goal.status == 'Pending':
        goal.status = 'Completed'
        goal.date_completed = datetime.utcnow()
    else:
        goal.status = 'Pending'
        goal.date_completed = None
    
    db.session.commit()
    
    # Prepare progress data for trigger
    completed = sum(1 for g in project.goals if g.status == 'Completed')
    trigger_data = {
        "updateProgress": {
            "projectId": project.id,
            "progress": project.calculate_progress(),
            "goalCount": f"{completed}/{len(project.goals)}"
        },
        "timeline-updated": {}
    }
    
    response = make_response(render_template('components/goal_item.html', goal=goal))
    response.headers['HX-Trigger'] = json.dumps(trigger_data)
    return response


@bp.route('/goal/<int:goal_id>', methods=['DELETE'])
def delete_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    project = goal.project
    db.session.delete(goal)
    db.session.commit()
    
    # Prepare progress data for trigger
    completed = sum(1 for g in project.goals if g.status == 'Completed')
    trigger_data = {
        "updateProgress": {
            "projectId": project.id,
            "progress": project.calculate_progress(),
            "goalCount": f"{completed}/{len(project.goals)}"
        },
        "timeline-updated": {}
    }
    
    response = make_response('')
    response.headers['HX-Trigger'] = json.dumps(trigger_data)
    return response

@bp.route('/goal/<int:goal_id>/edit', methods=['GET'])
def edit_goal_form(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    return render_template('components/goal_edit_form.html', goal=goal)

@bp.route('/goal/<int:goal_id>/edit', methods=['POST'])
def edit_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    project = goal.project
    
    title = request.form.get('title', '').strip()
    if not title:
        # Simple validation: if empty, reload form with existing data (or could return error)
        return render_template('components/goal_edit_form.html', goal=goal)
        
    goal.title = title
    
    deadline_str = request.form.get('deadline')
    if deadline_str:
        try:
            goal.deadline = datetime.fromisoformat(deadline_str)
        except ValueError:
            pass
    else:
        goal.deadline = None
        
    db.session.commit()
    
    # Prepare progress trigger (timeline needs update too)
    trigger_data = {
        "timeline-updated": {}
    }
    
    response = make_response(render_template('components/goal_item.html', goal=goal))
    response.headers['HX-Trigger'] = json.dumps(trigger_data)
    return response

@bp.route('/goal/<int:goal_id>/cancel', methods=['GET'])
def cancel_edit_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    return render_template('components/goal_item.html', goal=goal)


@bp.route('/project/<int:project_id>/progress', methods=['GET'])
def project_progress(project_id):
    """Return updated progress bar for a project"""
    project = Project.query.get_or_404(project_id)
    progress = project.calculate_progress()
    color = project.category.color.lower()
    return f'''
        <div class="progress-bar cat-{color}" style="width: {progress}%"></div>
        <span class="progress-text-overlay">{progress}%</span>
    '''


# =====================
# Timeline API Routes
# =====================
from utils.timeline import (
    get_timeline_items_for_dashboard,
    get_timeline_items_for_project,
    calculate_date_range,
    filter_timeline_items,
    prepare_gantt_data,
    parse_date
)


@bp.route('/api/timeline/dashboard', methods=['GET'])
def timeline_dashboard():
    """Return Gantt timeline data for all projects and goals."""
    projects = Project.query.join(Category).order_by(Project.order_index).all()
    
    # Get all timeline items
    items = get_timeline_items_for_dashboard(projects)
    
    # Apply filters from query params
    status_filter = request.args.get('status')
    type_filter = request.args.get('type')
    date_start = request.args.get('start_date')
    date_end = request.args.get('end_date')
    
    dt_start = parse_date(date_start)
    dt_end = parse_date(date_end)
    
    if status_filter or type_filter or date_start or date_end:
        status_list = status_filter.split(',') if status_filter else None
        
        items = filter_timeline_items(
            items,
            date_start=dt_start,
            date_end=dt_end,
            status=status_list,
            item_type=type_filter
        )
    
    # Calculate date range and prepare Gantt data
    explicit_range = (dt_start, dt_end) if (dt_start and dt_end) else None
    date_range = calculate_date_range(items, explicit_range=explicit_range)
    gantt_data = prepare_gantt_data(items, date_range)
    
    return jsonify(gantt_data)


@bp.route('/api/timeline/project/<int:project_id>', methods=['GET'])
def timeline_project(project_id):
    """Return Gantt timeline data for a specific project's goals."""
    project = Project.query.get_or_404(project_id)
    
    # Get timeline items for this project
    items = get_timeline_items_for_project(project)
    
    # Apply filters from query params
    status_filter = request.args.get('status')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    dt_start = parse_date(start_date)
    dt_end = parse_date(end_date)
    
    if status_filter or start_date or end_date:
        status_list = status_filter.split(',') if status_filter else None
        
        items = filter_timeline_items(
            items,
            date_start=dt_start,
            date_end=dt_end,
            status=status_list
        )
    
    # Calculate date range and prepare Gantt data
    explicit_range = (dt_start, dt_end) if (dt_start and dt_end) else None
    date_range = calculate_date_range(items, explicit_range=explicit_range)
    gantt_data = prepare_gantt_data(items, date_range)
    
    return jsonify(gantt_data)


@bp.route('/api/timeline/filter', methods=['GET'])
def timeline_filter():
    """Advanced filtering endpoint supporting multiple filters."""
    projects = Project.query.join(Category).order_by(Project.order_index).all()
    items = get_timeline_items_for_dashboard(projects)
    
    # Parse all filter parameters
    status_filter = request.args.get('status')
    type_filter = request.args.get('type')
    project_id = request.args.get('project_id', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    status_list = status_filter.split(',') if status_filter else None
    dt_start = parse_date(start_date)
    dt_end = parse_date(end_date)
    
    items = filter_timeline_items(
        items,
        date_start=dt_start,
        date_end=dt_end,
        status=status_list,
        project_id=project_id,
        item_type=type_filter
    )
    
    explicit_range = (dt_start, dt_end) if (dt_start and dt_end) else None
    date_range = calculate_date_range(items, explicit_range=explicit_range)
    gantt_data = prepare_gantt_data(items, date_range)
    
    return jsonify(gantt_data)

