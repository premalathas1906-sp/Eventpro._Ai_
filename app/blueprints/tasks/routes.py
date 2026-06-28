from flask import render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db, socketio
from app.models.event import Event
from app.models.task import Task
from app.blueprints.tasks import tasks_bp
from datetime import datetime

@tasks_bp.route('/')
@login_required
def task_board():
    events = current_user.events.all()
    if not events:
        flash('Create an event first to manage tasks.', 'info')
        return redirect(url_for('events.dashboard'))
        
    event_id = request.args.get('event_id', type=int)
    if event_id:
        event = Event.query.get_or_404(event_id)
        if event.user_id != current_user.id:
            flash('Unauthorized access.', 'danger')
            return redirect(url_for('events.dashboard'))
    else:
        event = events[0]
        
    tasks = event.tasks.all()
    
    # Categorize tasks by status
    todo_tasks = [t for t in tasks if t.status == 'To Do']
    inprogress_tasks = [t for t in tasks if t.status == 'In Progress']
    completed_tasks = [t for t in tasks if t.status == 'Completed']
    
    return render_template('tasks/task_board.html', 
                           event=event, 
                           events=events, 
                           todo=todo_tasks, 
                           in_progress=inprogress_tasks, 
                           completed=completed_tasks)

@tasks_bp.route('/add/<int:event_id>', methods=['POST'])
@login_required
def add_task(event_id):
    event = Event.query.get_or_404(event_id)
    if event.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
    data = request.get_json() if request.is_json else request.form
    title = data.get('title', '').strip()
    description = data.get('description', '').strip()
    deadline_str = data.get('deadline', '')
    priority = data.get('priority', 'Medium')
    category = data.get('category', 'General')
    assigned_to = data.get('assigned_to', '').strip()
    
    if not title:
        return jsonify({'success': False, 'message': 'Title is required'}), 400
        
    try:
        deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date() if deadline_str else None
        
        task = Task(
            title=title,
            description=description,
            deadline=deadline,
            status='To Do',
            priority=priority,
            category=category,
            assigned_to=assigned_to,
            event_id=event.id
        )
        db.session.add(task)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Task added successfully',
            'task': {
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'deadline': task.deadline.strftime('%Y-%m-%d') if task.deadline else '',
                'priority': task.priority,
                'category': task.category,
                'assigned_to': task.assigned_to,
                'status': task.status
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@tasks_bp.route('/update/<int:id>', methods=['POST'])
@login_required
def update_task(id):
    task = Task.query.get_or_404(id)
    if task.event.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
    data = request.get_json() if request.is_json else request.form
    title = data.get('title', '').strip()
    description = data.get('description', '').strip()
    deadline_str = data.get('deadline', '')
    priority = data.get('priority', '')
    category = data.get('category', '')
    assigned_to = data.get('assigned_to', '').strip()
    
    if title:
        task.title = title
    if description is not None:
        task.description = description
    if deadline_str:
        task.deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()
    if priority:
        task.priority = priority
    if category:
        task.category = category
    if assigned_to is not None:
        task.assigned_to = assigned_to
        
    try:
        db.session.commit()
        return jsonify({'success': True, 'message': 'Task updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@tasks_bp.route('/move/<int:id>', methods=['POST'])
@login_required
def move_task(id):
    task = Task.query.get_or_404(id)
    if task.event.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
    direction = request.form.get('direction', 'next')
    
    statuses = ['To Do', 'In Progress', 'Completed']
    curr_idx = statuses.index(task.status)
    
    if direction == 'next' and curr_idx < 2:
        task.status = statuses[curr_idx + 1]
    elif direction == 'prev' and curr_idx > 0:
        task.status = statuses[curr_idx - 1]
    else:
        # Check if direct status target is set (e.g. from drag and drop)
        new_status = request.form.get('status')
        if new_status in statuses:
            task.status = new_status
            
    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'message': f'Task status updated to {task.status}',
            'status': task.status
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@tasks_bp.route('/delete/<int:id>', methods=['POST', 'DELETE'])
@login_required
def delete_task(id):
    task = Task.query.get_or_404(id)
    if task.event.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
    try:
        db.session.delete(task)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Task deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
