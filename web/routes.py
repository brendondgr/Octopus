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
    
    new_project = Project(
        title=data.get('title'),
        description=data.get('description'),
        category=category, # SQLAlchemy handles the relationshp
        status='Active',
        order_index=new_order
    )
    
    db.session.add(new_project)
    db.session.commit()
    
    # Return the encoded card to be appended to the Active column
    return render_template('components/project_card.html', project=new_project)

@bp.route('/project/<int:project_id>', methods=['PATCH'])
def update_project(project_id):
    project = Project.query.get_or_404(project_id)
    
    # Update Status
    if 'status' in request.form:
        project.status = request.form['status']
        
    db.session.commit()
    return jsonify({'success': True})


# =====================
# Project Details Modal
# =====================
@bp.route('/project/<int:project_id>/details', methods=['GET'])
def project_details(project_id):
    project = Project.query.get_or_404(project_id)
    return render_template('components/modals/project_details.html', project=project)


# ================
# Goal Management
# ================
@bp.route('/project/<int:project_id>/goal', methods=['POST'])
def create_goal(project_id):
    project = Project.query.get_or_404(project_id)
    title = request.form.get('title', '').strip()
    
    if not title:
        return '', 400
    
    goal = Goal(
        project_id=project.id,
        title=title,
        status='Pending'
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
        }
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
        }
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
        }
    }
    
    response = make_response('')
    response.headers['HX-Trigger'] = json.dumps(trigger_data)
    return response


@bp.route('/project/<int:project_id>/progress', methods=['GET'])
def project_progress(project_id):
    """Return updated progress bar for a project"""
    project = Project.query.get_or_404(project_id)
    progress = project.calculate_progress()
    return f'<div class="progress-bar" style="width: {progress}%"></div>'
