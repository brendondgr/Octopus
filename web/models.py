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
    deadline = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'category': self.category.to_dict() if self.category else None,
            'progress': self.progress,
            'order_index': self.order_index,
            'date_created': self.date_created.isoformat() if self.date_created else None,
            'deadline': self.deadline.isoformat() if self.deadline else None
        }
