from flask import render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.event import Event
from app.blueprints.analytics import analytics_bp

@analytics_bp.route('/')
@login_required
def analytics_page():
    events = current_user.events.all()
    if not events:
        flash('Create an event first to view analytics.', 'info')
        return redirect(url_for('events.dashboard'))
        
    event_id = request.args.get('event_id', type=int)
    if event_id:
        event = Event.query.get_or_404(event_id)
        if event.user_id != current_user.id:
            flash('Unauthorized access.', 'danger')
            return redirect(url_for('events.dashboard'))
    else:
        event = events[0]
        
    # Standard numbers
    guests = event.guests.all()
    tasks = event.tasks.all()
    feedback = event.feedback_items.all()
    budget_items = event.budget_items.all()
    
    total_guests = len(guests)
    confirmed_guests = sum(1 for g in guests if g.rsvp_status == 'Confirmed')
    checked_in = sum(1 for g in guests if g.checked_in)
    
    total_tasks = len(tasks)
    completed_tasks = sum(1 for t in tasks if t.status == 'Completed')
    
    total_spent = sum(b.spent_amount for b in budget_items)
    
    avg_rating = 0.0
    if feedback:
        avg_rating = round(sum(f.rating for f in feedback) / len(feedback), 1)
        
    stats = {
        'attendance_rate': round((checked_in / confirmed_guests * 100)) if confirmed_guests > 0 else (round((checked_in / total_guests * 100)) if total_guests > 0 else 0),
        'budget_used_percent': round((total_spent / event.budget * 100)) if event.budget > 0 else 0,
        'task_completion_percent': round((completed_tasks / total_tasks * 100)) if total_tasks > 0 else 0,
        'satisfaction_rating': avg_rating
    }
    
    return render_template('analytics_page.html', event=event, events=events, stats=stats)

@analytics_bp.route('/api/attendance/<int:event_id>')
@login_required
def api_attendance(event_id):
    event = Event.query.get_or_404(event_id)
    if event.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    guests = event.guests.all()
    
    # RSVP categories
    confirmed = sum(1 for g in guests if g.rsvp_status == 'Confirmed')
    pending = sum(1 for g in guests if g.rsvp_status == 'Pending')
    declined = sum(1 for g in guests if g.rsvp_status == 'Declined')
    
    # Checked-in categories
    checked_in = sum(1 for g in guests if g.checked_in)
    absent = confirmed - checked_in
    if absent < 0:
        absent = 0
        
    return jsonify({
        'rsvp': {
            'labels': ['Confirmed', 'Pending', 'Declined'],
            'data': [confirmed, pending, declined]
        },
        'attendance': {
            'labels': ['Present', 'Absent', 'Pending RSVP'],
            'data': [checked_in, absent, pending]
        }
    })

@analytics_bp.route('/api/budget/<int:event_id>')
@login_required
def api_budget(event_id):
    event = Event.query.get_or_404(event_id)
    if event.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    budget_items = event.budget_items.all()
    
    labels = [item.category for item in budget_items]
    allocated = [item.allocated_amount for item in budget_items]
    spent = [item.spent_amount for item in budget_items]
    
    return jsonify({
        'labels': labels,
        'allocated': allocated,
        'spent': spent,
        'total_budget': event.budget
    })

@analytics_bp.route('/api/feedback/<int:event_id>')
@login_required
def api_feedback(event_id):
    event = Event.query.get_or_404(event_id)
    if event.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    feedback = event.feedback_items.all()
    
    ratings_count = [0] * 5  # 1 to 5 stars
    positive = 0
    neutral = 0
    negative = 0
    
    for f in feedback:
        rating = int(f.rating)
        if 1 <= rating <= 5:
            ratings_count[rating - 1] += 1
            
        sentiment = f.sentiment.lower() if f.sentiment else 'neutral'
        if sentiment == 'positive':
            positive += 1
        elif sentiment == 'negative':
            negative += 1
        else:
            neutral += 1
            
    return jsonify({
        'ratings': {
            'labels': ['1 Star', '2 Stars', '3 Stars', '4 Stars', '5 Stars'],
            'data': ratings_count
        },
        'sentiment': {
            'labels': ['Positive', 'Neutral', 'Negative'],
            'data': [positive, neutral, negative]
        }
    })
