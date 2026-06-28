from flask import render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models.event import Event
from app.models.feedback import Feedback
from app.blueprints.feedback import feedback_bp
from app.ai.sentiment_engine import SentimentEngine

sentiment_engine = SentimentEngine()

@feedback_bp.route('/')
@login_required
def feedback_page():
    events = current_user.events.all()
    if not events:
        flash('Create an event first to manage feedback.', 'info')
        return redirect(url_for('events.dashboard'))
        
    event_id = request.args.get('event_id', type=int)
    if event_id:
        event = Event.query.get_or_404(event_id)
        if event.user_id != current_user.id:
            flash('Unauthorized access.', 'danger')
            return redirect(url_for('events.dashboard'))
    else:
        event = events[0]
        
    feedback_items = event.feedback_items.order_by(Feedback.created_at.desc()).all()
    
    # Calculate stats
    total = len(feedback_items)
    avg_rating = 0.0
    positive_count = 0
    neutral_count = 0
    negative_count = 0
    
    for f in feedback_items:
        avg_rating += f.rating
        sent = f.sentiment.lower() if f.sentiment else 'neutral'
        if sent == 'positive':
            positive_count += 1
        elif sent == 'negative':
            negative_count += 1
        else:
            neutral_count += 1
            
    if total > 0:
        avg_rating = round(avg_rating / total, 1)
        
    stats = {
        'total': total,
        'average_rating': avg_rating,
        'positive_percent': round((positive_count / total * 100)) if total > 0 else 0,
        'neutral_percent': round((neutral_count / total * 100)) if total > 0 else 0,
        'negative_percent': round((negative_count / total * 100)) if total > 0 else 0
    }
    
    # Generate word cloud data (mocked from sentiment engine)
    feedbacks_text = [f.comment for f in feedback_items if f.comment]
    words_summary = sentiment_engine.analyze_batch(feedbacks_text)
    common_themes = words_summary.get('common_themes', [])
    
    return render_template('feedback/feedback_page.html', event=event, events=events, feedback=feedback_items, stats=stats, common_themes=common_themes)

@feedback_bp.route('/form/<int:event_id>')
def feedback_form(event_id):
    # Public route - no login required
    event = Event.query.get_or_404(event_id)
    return render_template('feedback/feedback_form.html', event=event)

@feedback_bp.route('/submit/<int:event_id>', methods=['POST'])
def submit_feedback(event_id):
    # Public route - no login required
    event = Event.query.get_or_404(event_id)
    
    guest_name = request.form.get('guest_name', '').strip() or 'Anonymous Guest'
    rating = int(request.form.get('rating', 5) or 5)
    comment = request.form.get('comment', '').strip()
    emoji = request.form.get('emoji', '😊')
    
    # Analyze sentiment
    analysis = sentiment_engine.analyze(comment)
    sentiment = analysis.get('sentiment', 'Neutral')
    
    try:
        feedback = Feedback(
            guest_name=guest_name,
            rating=rating,
            comment=comment,
            sentiment=sentiment,
            emoji=emoji,
            event_id=event.id
        )
        db.session.add(feedback)
        db.session.commit()
        
        # If AJAX, return JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.args.get('ajax') == 'true':
            return jsonify({'success': True, 'message': 'Thank you for your feedback!'})
            
        flash('Thank you for your feedback!', 'success')
        return render_template('feedback/feedback_success.html', event=event)
    except Exception as e:
        db.session.rollback()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.args.get('ajax') == 'true':
            return jsonify({'success': False, 'message': str(e)}), 500
        flash(f'Error submitting feedback: {str(e)}', 'danger')
        return redirect(url_for('feedback.feedback_form', event_id=event.id))
