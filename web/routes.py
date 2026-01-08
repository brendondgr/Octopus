from flask import Blueprint, render_template

bp = Blueprint('main', __name__)

from flask import Blueprint, render_template, request, jsonify
from . import db
from .models import Project
from datetime import datetime

bp = Blueprint('main', __name__)

from flask import Blueprint, render_template, request, jsonify
from . import db
from .models import Project, Category
from datetime import datetime

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
