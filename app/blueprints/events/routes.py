from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db, socketio

from app.models.event import Event
from app.models.guest import Guest
from app.models.task import Task
from app.models.vendor import Vendor
from app.models.budget import BudgetItem
from app.blueprints.events import events_bp
from datetime import datetime

@events_bp.route('/')
@login_required
def dashboard():
    # Calculate stats for current user
    events = current_user.events.all()
    total_events = len(events)
    
    total_guests = 0
    confirmed_guests = 0
    checked_in_guests = 0
    total_spent = 0.0
    total_allocated = 0.0
    
    for event in events:
        total_guests += event.guests.count()
        confirmed_guests += event.guests.filter_by(rsvp_status='Confirmed').count()
        checked_in_guests += event.guests.filter_by(checked_in=True).count()
        
        # Budget
        for b_item in event.budget_items.all():
            total_spent += b_item.spent_amount
            total_allocated += b_item.allocated_amount
            
    attendance_rate = 0
    if confirmed_guests > 0:
        attendance_rate = round((checked_in_guests / confirmed_guests) * 100)
    elif total_guests > 0:
        attendance_rate = round((checked_in_guests / total_guests) * 100)
        
    wedding_count = current_user.events.filter_by(event_type='Wedding').count()
    birthday_count = current_user.events.filter_by(event_type='Birthday').count()
    college_count = current_user.events.filter_by(event_type='College Event').count()
    corporate_count = current_user.events.filter_by(event_type='Corporate').count()

    stats = {
        'total_events': total_events,
        'total_guests': total_guests,
        'attendance_rate': attendance_rate,
        'budget_used': total_spent,
        'event_types': [wedding_count, birthday_count, college_count, corporate_count]
    }
    
    # Recent upcoming events (up to 3)
    upcoming_events = current_user.events.filter(Event.date >= datetime.utcnow().date()).order_by(Event.date.asc()).limit(3).all()
    
    # Enrich upcoming events with progress and counts
    enriched_upcoming = []
    for ev in upcoming_events:
        total_t = ev.tasks.count()
        done_t = ev.tasks.filter_by(status='Completed').count()
        progress = round((done_t / total_t) * 100) if total_t > 0 else 0
        
        enriched_upcoming.append({
            'id': ev.id,
            'name': ev.name,
            'event_type': ev.event_type,
            'type': ev.event_type,
            'date': ev.date.strftime('%Y-%m-%d'),
            'time': ev.time.strftime('%I:%M %p') if ev.time else 'TBD',
            'venue': ev.venue or 'TBD',
            'guests_confirmed': ev.guests.filter_by(rsvp_status='Confirmed').count(),
            'guests_total': ev.guest_count,
            'guests': ev.guests.count(),
            'max_guests': ev.guest_count,
            'progress': progress
        })
        
    return render_template('events/dashboard.html', stats=stats, upcoming_events=enriched_upcoming)

@events_bp.route('/events')
@login_required
def events_list():
    events = current_user.events.order_by(Event.date.desc()).all()
    formatted_events = []
    
    for ev in events:
        total_t = ev.tasks.count()
        done_t = ev.tasks.filter_by(status='Completed').count()
        progress = round((done_t / total_t) * 100) if total_t > 0 else 0
        
        # Map statuses dynamically based on date
        today = datetime.utcnow().date()
        if ev.date < today:
            status = 'Completed'
        elif ev.status == 'Draft':
            status = 'Draft'
        else:
            status = 'Active' if ev.date == today else 'Upcoming'
            
        formatted_events.append({
            'id': ev.id,
            'name': ev.name,
            'event_type': ev.event_type,
            'type': ev.event_type,
            'date': ev.date.strftime('%Y-%m-%d'),
            'venue': ev.venue or 'TBD',
            'guests': ev.guests.count(),
            'max_guests': ev.guest_count,
            'budget': ev.budget,
            'status': status,
            'progress': progress
        })
        
    return render_template('events/events_list.html', events=formatted_events)

@events_bp.route('/events/create', methods=['POST'])
@login_required
def create_event():
    data = request.get_json() if request.is_json else request.form
    name = (data.get('name') or data.get('event_name') or '').strip()
    event_type = data.get('event_type', 'Wedding')
    date_str = data.get('date') or data.get('event_date') or ''
    time_str = data.get('time') or data.get('event_time') or ''
    venue = data.get('venue', '').strip()
    expected_guests = int(data.get('guest_count') or data.get('expected_guests') or 0)
    budget = float(data.get('budget') or 0.0)
    description = data.get('description', '').strip()
    
    if not name or not date_str:
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Event Name and Date are required.'}), 400
        flash('Event Name and Date are required.', 'danger')
        return redirect(url_for('events.dashboard'))
        
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        time_obj = datetime.strptime(time_str, '%H:%M').time() if time_str else None
        
        event = Event(
            name=name,
            event_type=event_type,
            date=date_obj,
            time=time_obj,
            venue=venue,
            guest_count=expected_guests,
            budget=budget,
            description=description,
            status='Upcoming',
            user_id=current_user.id
        )
        db.session.add(event)
        db.session.commit()
        
        # Pre-populate default budget categories based on event type
        from app.ai.budget_engine import BudgetEngine
        engine = BudgetEngine()
        recs = engine.get_recommendations(budget, event_type, expected_guests)
        
        for alloc in recs['allocations']:
            b_item = BudgetItem(
                category=alloc['category'],
                allocated_amount=alloc['amount'],
                spent_amount=0.0,
                event_id=event.id
            )
            db.session.add(b_item)
            
        # Add basic checklist of tasks
        default_tasks = [
            ('Book Venue', 'Finalize and book the venue', 'High', 'Venue'),
            ('Finalize Guest List', 'Review and complete the guest invitation list', 'Medium', 'Guests'),
            ('Send Invitations', 'Generate and send personalized invitations', 'High', 'Guests'),
            ('Plan Catering Menu', 'Choose food options and vendor', 'Medium', 'Catering'),
            ('Arrange Decorations', 'Determine floral and visual theme', 'Low', 'Decoration')
        ]
        
        for title, desc, priority, cat in default_tasks:
            t = Task(
                title=title,
                description=desc,
                deadline=date_obj,
                status='To Do',
                priority=priority,
                category=cat,
                event_id=event.id
            )
            db.session.add(t)
            
        # Create a notification reminder in database
        from app.models.reminder import Reminder
        notif = Reminder(
            title="Event Created",
            message=f"Event '{event.name}' has been successfully created.",
            remind_at=datetime.utcnow(),
            is_read=False,
            event_id=event.id,
            user_id=current_user.id
        )
        db.session.add(notif)
            
        db.session.commit()
        
        event_data = {
            'id': event.id,
            'name': event.name,
            'event_type': event.event_type,
            'type': event.event_type,
            'date': event.date.strftime('%Y-%m-%d'),
            'time': event.time.strftime('%I:%M %p') if event.time else 'TBD',
            'venue': event.venue or 'TBD',
            'guests': 0,
            'guests_confirmed': 0,
            'guests_total': event.guest_count,
            'max_guests': event.guest_count,
            'budget': event.budget,
            'progress': 0,
            'status': 'Upcoming'
        }
        
        # Emit Socket.IO event to User Room
        socketio.emit('event_created', event_data, room=f"user_{current_user.id}")
        
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': True,
                'message': 'Event created successfully!',
                'event': event_data
            })
            
        flash('Event created successfully with recommended budget and tasks!', 'success')
        return redirect(url_for('events.event_detail', id=event.id))
    except Exception as e:
        db.session.rollback()
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': str(e)}), 500
        flash(f'Error creating event: {str(e)}', 'danger')
        return redirect(url_for('events.dashboard'))

@events_bp.route('/events/<int:id>')
@login_required
def event_detail(id):
    event = Event.query.get_or_404(id)
    if event.user_id != current_user.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('events.dashboard'))
        
    guests = event.guests.all()
    tasks = event.tasks.all()
    vendors = event.vendors.all()
    budget_items = event.budget_items.all()
    feedback_items = event.feedback_items.all()
    
    # Calculate status counts for UI dashboard tab
    stats = {
        'total_guests': len(guests),
        'confirmed_guests': sum(1 for g in guests if g.rsvp_status == 'Confirmed'),
        'pending_guests': sum(1 for g in guests if g.rsvp_status == 'Pending'),
        'declined_guests': sum(1 for g in guests if g.rsvp_status == 'Declined'),
        'checked_in': sum(1 for g in guests if g.checked_in),
        'total_tasks': len(tasks),
        'completed_tasks': sum(1 for t in tasks if t.status == 'Completed'),
        'in_progress_tasks': sum(1 for t in tasks if t.status == 'In Progress'),
        'pending_tasks': sum(1 for t in tasks if t.status == 'To Do'),
        'total_budget': event.budget,
        'allocated_budget': sum(b.allocated_amount for b in budget_items),
        'spent_budget': sum(b.spent_amount for b in budget_items),
    }
    
    return render_template('events/event_detail.html', event=event, guests=guests, tasks=tasks, vendors=vendors, budget_items=budget_items, feedback_items=feedback_items, stats=stats, now=datetime.utcnow())

@events_bp.route('/events/<int:id>/update', methods=['POST'])
@login_required
def update_event(id):
    event = Event.query.get_or_404(id)
    if event.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
    data = request.get_json() if request.is_json else request.form
    name = data.get('name', '').strip()
    date_str = data.get('date', '')
    venue = data.get('venue', '').strip()
    budget = float(data.get('budget', 0.0) or 0.0)
    description = data.get('description', '').strip()
    
    if not name or not date_str:
        return jsonify({'success': False, 'message': 'Name and date required'}), 400
        
    try:
        event.name = name
        event.date = datetime.strptime(date_str, '%Y-%m-%d').date()
        event.venue = venue
        event.budget = budget
        event.description = description
        db.session.commit()
        return jsonify({'success': True, 'message': 'Event updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@events_bp.route('/events/<int:id>/delete', methods=['POST', 'DELETE'])
@login_required
def delete_event(id):
    event = Event.query.get_or_404(id)
    if event.user_id != current_user.id:
        if request.method == 'DELETE' or request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Accept', ''):
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('events.dashboard'))
        
    try:
        db.session.delete(event)
        db.session.commit()
        if request.method == 'DELETE' or request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Accept', ''):
            return jsonify({'success': True, 'message': 'Event deleted successfully'})
        flash('Event deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        if request.method == 'DELETE' or request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Accept', ''):
            return jsonify({'success': False, 'message': str(e)}), 500
        flash(f'Error deleting event: {str(e)}', 'danger')
        
    return redirect(url_for('events.events_list'))

@events_bp.route('/notifications/mark-read/<int:id>', methods=['POST'])
@login_required
def mark_notification_read(id):
    from app.models.reminder import Reminder
    reminder = Reminder.query.get_or_404(id)
    if reminder.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    reminder.is_read = True
    db.session.commit()
    return jsonify({'success': True})

@events_bp.route('/notifications/mark-all-read', methods=['POST'])
@login_required
def mark_all_notifications_read():
    from app.models.reminder import Reminder
    reminders = Reminder.query.filter_by(user_id=current_user.id, is_read=False).all()
    for r in reminders:
        r.is_read = True
    db.session.commit()
    return jsonify({'success': True})
