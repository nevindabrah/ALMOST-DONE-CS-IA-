from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Time, ForeignKey
from datetime import datetime

# 1. User model (used in login, signup, and across the app)
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    fullname = db.Column(db.String(150))
    role = db.Column(db.String(50), nullable=False)  # 'student' or 'teacher'
    streak_counter = db.Column(db.Integer, default=0)

    notes = db.relationship('Note', backref='user', lazy=True)
    tasks = db.relationship('Todo', backref='user', lazy=True)
    planners = db.relationship('Planner', backref='user', lazy=True)
    student_planners = db.relationship('StudentPlanner', backref='user', lazy=True)
    feedbacks = db.relationship('PlannerFeedback', backref='user', lazy=True)

# 2. Planner models (used in the planner page)
class StudentPlanner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    tasks = db.relationship('PlannerTask', backref='student_planner', lazy=True, cascade='all, delete-orphan')
    feedbacks = db.relationship('PlannerFeedback', backref='student_planner', lazy='joined', cascade='all, delete-orphan')


class PlannerTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    student_planner_id = db.Column(db.Integer, db.ForeignKey('student_planner.id'), nullable=False)


class PlannerFeedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    student_planner_id = db.Column(db.Integer, db.ForeignKey('student_planner.id'), nullable=False)

# 3. General Planner models (for older planners or other uses)
class Planner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    tasks = db.relationship('Task', backref='planner', lazy=True, cascade='all, delete-orphan')


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    start_time = db.Column(db.Time, nullable=True)
    end_time = db.Column(db.Time, nullable=True)
    planner_id = db.Column(db.Integer, db.ForeignKey('planner.id'), nullable=False)

# 4. Todo list models
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(255), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    due_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(50), default="In Progress")
    priority = db.Column(db.String(50), default="Medium")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

# 5. Timetable models
class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    img = db.Column(db.Text, unique=True, nullable=False)
    name = db.Column(db.Text, nullable=False)
    title = db.Column(db.String(150), nullable=True)
    mimetype = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# 6. Reflection and Notes models
class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    edited_date = db.Column(db.DateTime(timezone=True), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
