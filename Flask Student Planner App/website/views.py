from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, send_file, current_app
from flask_login import login_required, current_user
from .models import Note, Image, Todo, Planner, Task, StudentPlanner, PlannerTask
from . import db
import json
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from sqlalchemy.sql import func
from io import BytesIO
from fpdf import FPDF
import tempfile

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    # Query totals for notes and images
    notes_total = Note.query.filter_by(user_id=current_user.id).count()
    images_total = Image.query.filter_by(user_id=current_user.id).count()

    # Query totals for tasks
    completed_tasks = Todo.query.filter_by(user_id=current_user.id, completed=True).count()
    in_progress_tasks = Todo.query.filter_by(user_id=current_user.id, completed=False).count()
    overdue_tasks = Todo.query.filter(
        Todo.user_id == current_user.id,
        Todo.due_date < datetime.utcnow(),
        Todo.completed == False
    ).count()

    # Query total number of planners
    total_planners = StudentPlanner.query.filter_by(user_id=current_user.id).count()

    return render_template(
        "home.html",
        user=current_user,
        notes_total=notes_total,
        images_total=images_total,
        completed_tasks=completed_tasks,
        in_progress_tasks=in_progress_tasks,
        overdue_tasks=overdue_tasks,
        total_planners=total_planners  # Pass total planners to the template
    )



# Planner Page
@views.route('/planner', methods=['GET', 'POST'])
@login_required
def planner():
    if request.method == 'POST':
        title = request.form.get('title')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')

        if not title or not start_date or not end_date:
            flash('All fields are required!', category='error')
            return redirect(url_for('views.planner'))

        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            if start_date > end_date:
                flash('Start date cannot be after the end date.', category='error')
                return redirect(url_for('views.planner'))
        except ValueError:
            flash('Invalid date format. Use YYYY-MM-DD.', category='error')
            return redirect(url_for('views.planner'))

        # Create a new student planner
        new_planner = StudentPlanner(
            title=title,
            start_date=start_date,
            end_date=end_date,
            user_id=current_user.id
        )
        db.session.add(new_planner)
        db.session.commit()

        # Add tasks
        tasks = request.form.getlist('tasks')
        days = request.form.getlist('days')
        for task, day in zip(tasks, days):
            if task.strip():
                new_task = PlannerTask(description=task.strip(), day=day, student_planner_id=new_planner.id)
                db.session.add(new_task)

        db.session.commit()
        flash('Planner created successfully!', category='success')
        return redirect(url_for('views.planner_history'))

    # Fetch all planners for the user to display the total count
    total_planners = StudentPlanner.query.filter_by(user_id=current_user.id).count()

    return render_template('planner.html', user=current_user, total_planners=total_planners)


@views.route('/planner-history', methods=['GET'])
@login_required
def planner_history():
    planners = StudentPlanner.query.filter_by(user_id=current_user.id).all()
    for planner in planners:
        planner.tasks = PlannerTask.query.filter_by(student_planner_id=planner.id).all()  # Explicitly fetch tasks
    return render_template('planner_history.html', user=current_user, planners=planners)


@views.route('/planner/<int:planner_id>', methods=['GET'])
@login_required
def view_planner(planner_id):
    planner = StudentPlanner.query.filter_by(id=planner_id, user_id=current_user.id).first()
    if not planner:
        flash('Planner not found or access denied.', category='error')
        return redirect(url_for('views.planner_history'))

    tasks = PlannerTask.query.filter_by(student_planner_id=planner.id).all()
    return render_template('view_planner.html', planner=planner, tasks=tasks)

@views.route('/delete-planner/<int:planner_id>', methods=['POST'])
@login_required
def delete_planner(planner_id):
    planner = StudentPlanner.query.filter_by(id=planner_id, user_id=current_user.id).first()
    if not planner:
        flash('Planner not found or you do not have permission to delete it.', category='error')
        return redirect(url_for('views.planner_history'))

    # Delete all associated tasks
    PlannerTask.query.filter_by(student_planner_id=planner_id).delete()

    # Delete the planner
    db.session.delete(planner)
    db.session.commit()
    flash('Planner deleted successfully!', category='success')
    return redirect(url_for('views.planner_history'))



@views.route('/notes', methods=['GET', 'POST'])
@login_required
def notes():
    if request.method == 'POST':
        note = request.form.get('note')#Gets the note from the HTML 

        if len(note) < 1:
            flash('Note is too short!', category='error') 
        else:
            new_note = Note(data=note, user_id=current_user.id)  #providing the schema for the note 
            db.session.add(new_note) #adding the note to the database 
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("notes.html", user=current_user)

@views.route('/delete-note', methods=['POST'])
@login_required
def delete_note():  
    try:
        note = json.loads(request.data)  # this function expects a JSON from the frontend
        noteId = note['noteId']
        note = Note.query.get(noteId)
        if note and note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Note not found or unauthorized'}), 403
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


    return jsonify({})

@views.route('/timetable', methods=['GET', 'POST'])
@login_required
def timetable():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', category='error')
            return redirect(request.url)
        file = request.files['file']
        title = request.form.get('title')  # Capture the title from the form
        if file.filename == '':
            flash('No selected file', category='error')
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            mimetype = file.mimetype
            img = Image(img=file.read(), name=filename, mimetype=mimetype, user_id=current_user.id, title=title)
            db.session.add(img)
            db.session.commit()
            flash('Image uploaded successfully!', category='success')
            return redirect(url_for('views.timetable'))
    images = Image.query.filter_by(user_id=current_user.id).all()
    return render_template("timetable.html", user=current_user, images=images)

@views.route('/delete-image/<int:image_id>', methods=['POST'])
@login_required
def delete_image(image_id):
    image = Image.query.get(image_id)
    if image and image.user_id == current_user.id:
        db.session.delete(image)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False})

@views.route('/edit-image/<int:image_id>', methods=['POST'])
@login_required
def edit_image(image_id):
    image = Image.query.get(image_id)
    if image and image.user_id == current_user.id:
        title = request.form.get('title')
        file = request.files.get('file')
        if title:
            image.title = title
        if file:
            image.img = file.read()
            image.name = secure_filename(file.filename)
            image.mimetype = file.mimetype
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False})

@views.route('/edit-note/<int:note_id>', methods=['POST'])
@login_required
def edit_note(note_id):
    note = Note.query.get(note_id)
    if note and note.user_id == current_user.id:
        note_content = request.json.get('note')
        if note_content:
            # Create a new note with the updated content
            new_note = Note(data=note_content, user_id=current_user.id, edited_date=func.now())
            db.session.add(new_note)
            db.session.commit()
            return jsonify({'success': True, 'new_note_id': new_note.id})
    return jsonify({'success': False})

@views.route('/todo', methods=['GET', 'POST'])
@login_required
def todo():
    if request.method == 'POST':
        task_content = request.form.get('task')
        due_date = request.form.get('due_date')
        priority = request.form.get('priority')  # Capture priority

        if not task_content:
            flash("Task cannot be empty!", category="error")
        else:
            try:
                due_date_obj = datetime.strptime(due_date, '%Y-%m-%d').date() if due_date else None
                new_task = Todo(
                    task=task_content,
                    user_id=current_user.id,
                    due_date=due_date_obj,
                    priority=priority or "Medium",  # Default to Medium if not set
                    completed=False
                )
                db.session.add(new_task)
                db.session.commit()
                flash("Task added successfully!", category="success")
            except ValueError:
                flash("Invalid date format. Please select a valid due date.", category="error")

    sort_by = request.args.get('sort_by', 'date_created')  # Default sorting
    if sort_by == 'status':
        tasks = Todo.query.filter_by(user_id=current_user.id).order_by(Todo.completed).all()
    elif sort_by == 'due_date':
        tasks = Todo.query.filter_by(user_id=current_user.id).order_by(Todo.due_date).all()
    elif sort_by == 'priority':
        tasks = Todo.query.filter_by(user_id=current_user.id).order_by(Todo.priority).all()
    else:
        tasks = Todo.query.filter_by(user_id=current_user.id).order_by(Todo.date_created).all()

    now = datetime.now()  # Current timestamp
    return render_template("todo.html", tasks=tasks, user=current_user, now=now)

@views.route('/delete-task/<int:id>', methods=['POST'])
@login_required
def delete_task(id):
    task = Todo.query.get_or_404(id)
    if task.user_id == current_user.id:  # Ensure the user owns the task
        db.session.delete(task)
        db.session.commit()
        flash("Task deleted successfully!", category="success")
    else:
        flash("You are not authorized to delete this task.", category="error")
    return redirect(url_for('views.todo'))

@views.route('/toggle-task/<int:id>', methods=['POST'])
@login_required
def toggle_task(id):
    task = Todo.query.get_or_404(id)
    if task.user_id == current_user.id:  # Ensure the user owns the task
        task.completed = not task.completed  # Toggle the completion status
        db.session.commit()
        # Return success, the completed state, and the status text
        return jsonify({
            'success': True,
            'completed': task.completed,
            'status': "Complete" if task.completed else "In Progress"
        })
    else:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403

@views.route('/edit-task/<int:id>', methods=['POST'])
@login_required
def edit_task(id):
    task = Todo.query.get_or_404(id)

    # Ensure the user owns the task
    if task.user_id != current_user.id:
        flash("You are not authorized to edit this task.", category="error")
        return redirect(url_for('views.todo'))

    # Fetch updated task content, due date, and priority from the form
    task_content = request.form.get('task')
    due_date = request.form.get('due_date')
    priority = request.form.get('priority')

    # Update the task content
    if task_content:
        task.task = task_content

    # Update the due date if provided
    if due_date:
        try:
            task.due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
        except ValueError:
            flash("Invalid date format. Please select a valid due date.", category="error")
            return redirect(url_for('views.todo'))

    # Update the priority if provided
    if priority:
        task.priority = priority

    db.session.commit()  # Save changes to the database
    flash("Task updated successfully!", category="success")

    return redirect(url_for('views.todo'))
