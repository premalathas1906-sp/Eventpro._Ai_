from flask import render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models.event import Event
from app.models.vendor import Vendor
from app.blueprints.vendors import vendors_bp

@vendors_bp.route('/')
@login_required
def vendor_list():
    events = current_user.events.all()
    if not events:
        flash('Create an event first to manage vendors.', 'info')
        return redirect(url_for('events.dashboard'))
        
    event_id = request.args.get('event_id', type=int)
    if event_id:
        event = Event.query.get_or_404(event_id)
        if event.user_id != current_user.id:
            flash('Unauthorized access.', 'danger')
            return redirect(url_for('events.dashboard'))
    else:
        event = events[0]
        
    vendors = event.vendors.all()
    
    # Categories for filters/options
    categories = ['Catering', 'Decoration', 'Photography', 'Music', 'Venue', 'General']
    
    return render_template('vendor_list.html', event=event, events=events, vendors=vendors, categories=categories)

@vendors_bp.route('/add/<int:event_id>', methods=['POST'])
@login_required
def add_vendor(event_id):
    event = Event.query.get_or_404(event_id)
    if event.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
    data = request.get_json() if request.is_json else request.form
    name = data.get('name', '').strip()
    category = data.get('category', 'General')
    contact = data.get('contact', '').strip()
    email = data.get('email', '').strip()
    cost = float(data.get('cost', 0.0) or 0.0)
    status = data.get('status', 'Contacted')
    rating = int(data.get('rating', 5) or 5)
    notes = data.get('notes', '').strip()
    
    if not name:
        return jsonify({'success': False, 'message': 'Name is required'}), 400
        
    try:
        vendor = Vendor(
            name=name,
            category=category,
            contact=contact,
            email=email,
            cost=cost,
            status=status,
            rating=rating,
            notes=notes,
            event_id=event.id
        )
        db.session.add(vendor)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Vendor added successfully',
            'vendor': {
                'id': vendor.id,
                'name': vendor.name,
                'category': vendor.category,
                'contact': vendor.contact,
                'email': vendor.email,
                'cost': vendor.cost,
                'status': vendor.status,
                'rating': vendor.rating,
                'notes': vendor.notes
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@vendors_bp.route('/update/<int:id>', methods=['POST'])
@login_required
def update_vendor(id):
    vendor = Vendor.query.get_or_404(id)
    if vendor.event.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
    data = request.get_json() if request.is_json else request.form
    name = data.get('name', '').strip()
    category = data.get('category', '')
    contact = data.get('contact', '').strip()
    email = data.get('email', '').strip()
    cost_str = data.get('cost')
    status = data.get('status', '')
    rating_str = data.get('rating')
    notes = data.get('notes', '').strip()
    
    if name:
        vendor.name = name
    if category:
        vendor.category = category
    if contact is not None:
        vendor.contact = contact
    if email is not None:
        vendor.email = email
    if cost_str is not None:
        vendor.cost = float(cost_str or 0.0)
    if status:
        vendor.status = status
    if rating_str is not None:
        vendor.rating = int(rating_str or 5)
    if notes is not None:
        vendor.notes = notes
        
    try:
        db.session.commit()
        return jsonify({'success': True, 'message': 'Vendor updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@vendors_bp.route('/delete/<int:id>', methods=['POST', 'DELETE'])
@login_required
def delete_vendor(id):
    vendor = Vendor.query.get_or_404(id)
    if vendor.event.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
    try:
        db.session.delete(vendor)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Vendor removed successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
