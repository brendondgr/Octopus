from . import db
from datetime import datetime

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    # Color stores the css variable name suffix, e.g. 'blue', 'green'
    color = db.Column(db.String(20), default='blue', nullable=False)
    projects = db.relationship('Project', backref='category', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'color': self.color
        }

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='Active', nullable=False)
    
    # Foreign Key to Category
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    
    progress = db.Column(db.Integer, default=0)
    order_index = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_completed = db.Column(db.DateTime, nullable=True)
    date_on_hold = db.Column(db.DateTime, nullable=True)
    date_abandoned = db.Column(db.DateTime, nullable=True)
    deadline = db.Column(db.DateTime, nullable=True)

    # Relationship to Goals
    goals = db.relationship('Goal', backref='project', lazy=True, cascade='all, delete-orphan')

    def calculate_progress(self):
        """Calculate progress based on completed goals"""
        if not self.goals:
            return 0
        completed = sum(1 for goal in self.goals if goal.status == 'Completed')
        return int((completed / len(self.goals)) * 100)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'category': self.category.to_dict() if self.category else None,
            'progress': self.calculate_progress(),
            'order_index': self.order_index,
            'date_created': self.date_created.strftime('%y-%m-%d') if self.date_created else None,
            'date_completed': self.date_completed.strftime('%y-%m-%d') if self.date_completed else None,
            'date_on_hold': self.date_on_hold.strftime('%y-%m-%d') if self.date_on_hold else None,
            'date_abandoned': self.date_abandoned.strftime('%y-%m-%d') if self.date_abandoned else None,
            'deadline': self.deadline.isoformat() if self.deadline else None
        }


class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), default='Pending', nullable=False)  # Pending, Completed
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_completed = db.Column(db.DateTime, nullable=True)
    deadline = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'title': self.title,
            'status': self.status,
            'date_created': self.date_created.isoformat() if self.date_created else None,
            'date_completed': self.date_completed.isoformat() if self.date_completed else None,
            'deadline': self.deadline.isoformat() if self.deadline else None
        }
