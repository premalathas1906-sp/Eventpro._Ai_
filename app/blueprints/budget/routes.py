from flask import render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models.event import Event
from app.models.budget import BudgetItem
from app.blueprints.budget import budget_bp
from app.ai.budget_engine import BudgetEngine

budget_engine = BudgetEngine()

@budget_bp.route('/')
@login_required
def budget_page():
    events = current_user.events.all()
    if not events:
        flash('Create an event first to manage budgets.', 'info')
        return redirect(url_for('events.dashboard'))
        
    event_id = request.args.get('event_id', type=int)
    if event_id:
        event = Event.query.get_or_404(event_id)
        if event.user_id != current_user.id:
            flash('Unauthorized access.', 'danger')
            return redirect(url_for('events.dashboard'))
    else:
        event = events[0]
        
    budget_items = event.budget_items.all()
    
    # Compute totals
    total_allocated = sum(b.allocated_amount for b in budget_items)
    total_spent = sum(b.spent_amount for b in budget_items)
    total_remaining = event.budget - total_spent
    
    stats = {
        'total_budget': event.budget,
        'allocated': total_allocated,
        'spent': total_spent,
        'remaining': total_remaining,
        'spent_percent': round((total_spent / event.budget) * 100) if event.budget > 0 else 0
    }
    
    # Get recommendations
    recs = budget_engine.get_recommendations(event.budget, event.event_type, event.guests.count() or event.guest_count)
    
    return render_template('budget/budget_page.html', event=event, events=events, budget_items=budget_items, stats=stats, recommendations=recs['recommendations'], venues=recs['venues'])

@budget_bp.route('/recommend', methods=['POST'])
@login_required
def recommend():
    data = request.get_json() or {}
    total_budget = float(data.get('total_budget', 0.0) or 0.0)
    event_type = data.get('event_type', 'Wedding')
    guest_count = int(data.get('guest_count', 0) or 0)
    
    recs = budget_engine.get_recommendations(total_budget, event_type, guest_count)
    return jsonify(recs)

@budget_bp.route('/update/<int:event_id>', methods=['POST'])
@login_required
def update_budget(event_id):
    event = Event.query.get_or_404(event_id)
    if event.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
    # Expect JSON mapping of item_id -> spent_amount or category -> (allocated, spent)
    # We can also receive form parameters to update a single budget item
    item_id = request.form.get('item_id', type=int)
    allocated = request.form.get('allocated', type=float)
    spent = request.form.get('spent', type=float)
    
    if item_id:
        b_item = BudgetItem.query.get_or_404(item_id)
        if b_item.event_id != event.id:
            return jsonify({'success': False, 'message': 'Invalid item'}), 400
            
        if allocated is not None:
            b_item.allocated_amount = allocated
        if spent is not None:
            b_item.spent_amount = spent
            
        try:
            db.session.commit()
            return jsonify({
                'success': True,
                'message': 'Budget item updated',
                'item': {
                    'id': b_item.id,
                    'category': b_item.category,
                    'allocated': b_item.allocated_amount,
                    'spent': b_item.spent_amount,
                    'remaining': b_item.remaining,
                    'percent': b_item.usage_percent
                }
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)}), 500
            
    # Batch update from budget grid
    try:
        # Check if form has data for multiple inputs
        for key, value in request.form.items():
            if key.startswith('allocated_'):
                b_id = int(key.split('_')[1])
                b_item = BudgetItem.query.get(b_id)
                if b_item and b_item.event_id == event.id:
                    b_item.allocated_amount = float(value or 0)
            elif key.startswith('spent_'):
                b_id = int(key.split('_')[1])
                b_item = BudgetItem.query.get(b_id)
                if b_item and b_item.event_id == event.id:
                    b_item.spent_amount = float(value or 0)
        db.session.commit()
        flash('Budget updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating budget: {str(e)}', 'danger')
        
    return redirect(url_for('budget.budget_page', event_id=event.id))
