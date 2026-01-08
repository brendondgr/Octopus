from flask import Blueprint, render_template

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    # Mock Data for Plan #1
    projects = [
        {
            'id': 1,
            'title': 'Website Redesign',
            'description': 'Overhaul the homepage and contact form.',
            'status': 'Active',
            'category': 'Blue',
            'progress': 45
        },
        {
            'id': 2,
            'title': 'Q1 Marketing Plan',
            'description': 'Draft social media strategy for new product launch.',
            'status': 'Active',
            'category': 'Green',
            'progress': 10
        },
        {
            'id': 3,
            'title': 'Legacy Database Migration',
            'description': 'Move user data to the new SQL server.',
            'status': 'Completed',
            'category': 'Purple',
            'progress': 100
        },
        {
            'id': 4,
            'title': 'User Interview Analysis',
            'description': 'Compile notes from last weeks user testing.',
            'status': 'On-Hold',
            'category': 'Orange',
            'progress': 30
        },
        {
            'id': 5,
            'title': 'Mobile App Concept',
            'description': 'Initial sketches for the iOS app.',
            'status': 'Abandoned',
            'category': 'Red',
            'progress': 5
        }
    ]
    return render_template('index.html', projects=projects)
