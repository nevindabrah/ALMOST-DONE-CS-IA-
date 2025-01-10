from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date
from datetime import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    fullname = db.Column(db.String(150))
    role = db.Column(db.String(50), nullable=False)  # New role field ('student' or 'teacher')
    streak_counter = db.Column(db.Integer, default=0)
    notes = db.relationship('Note', backref='user', lazy=True)
    tasks = db.relationship('Todo', backref='user', lazy=True)
    planners = db.relationship('Planner', backref='user', lazy=True)


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    edited_date = db.Column(db.DateTime(timezone=True), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    img = db.Column(db.Text, unique=True, nullable=False)
    name = db.Column(db.Text, nullable=False)
    title = db.Column(db.String(150), nullable=True)
    mimetype = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(255), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    due_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(50), default="In Progress")
    priority = db.Column(db.String(50), default="Medium")  # New priority field
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

class Planner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tasks = db.relationship('Task', backref='planner', lazy=True)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    start_time = db.Column(db.Time, nullable=True)
    end_time = db.Column(db.Time, nullable=True)
    planner_id = db.Column(db.Integer, db.ForeignKey('planner.id'), nullable=False)

class StudentPlanner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tasks = db.relationship('PlannerTask', backref='student_planner', lazy=True)

class PlannerTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    student_planner_id = db.Column(db.Integer, db.ForeignKey('student_planner.id'), nullable=False)
