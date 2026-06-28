from flask import render_template, redirect, url_for, flash, request, send_file, Response, jsonify
from flask_login import login_required, current_user
from app.extensions import db, socketio
from app.models.event import Event
from app.models.guest import Guest
from app.blueprints.guests import guests_bp
import qrcode
from io import BytesIO
from datetime import datetime
import csv

@guests_bp.route('/')
@login_required
def guest_list_all():
    events = current_user.events.all()
    # Fetch all guests for all user events or default to first event
    current_event = events[0] if events else None
    current_event_id = current_event.id if current_event else None
    
    guests = []
    if current_event:
        for g in current_event.guests.all():
            guests.append({
                'id': g.id,
                'name': g.name,
                'email': g.email,
                'phone': g.phone,
                'rsvp_status': g.rsvp_status,
                'checked_in': g.checked_in,
                'event_name': current_event.name,
                'qr_token': g.qr_token
            })
    return render_template('guests/guest_list.html', guests=guests, events=events, current_event_id=current_event_id, current_event=current_event)

@guests_bp.route('/event/<int:event_id>')
@login_required
def guest_list_event(event_id):
    event = Event.query.get_or_404(event_id)
    if event.user_id != current_user.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('events.dashboard'))
        
    guests = []
    for g in event.guests.all():
        guests.append({
            'id': g.id,
            'name': g.name,
            'email': g.email,
            'phone': g.phone,
            'rsvp_status': g.rsvp_status,
            'checked_in': g.checked_in,
            'event_name': event.name,
            'qr_token': g.qr_token
        })
        
    events = current_user.events.all()
    return render_template('guests/guest_list.html', guests=guests, events=events, current_event_id=event_id, current_event=event)

@guests_bp.route('/add/<int:event_id>', methods=['POST'])
@login_required
def add_guest(event_id):
    event = Event.query.get_or_404(event_id)
    if event.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
    data = request.get_json() if request.is_json else request.form
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    phone = data.get('phone', '').strip()
    rsvp_status = data.get('rsvp_status', 'Pending')
    
    if not name:
        return jsonify({'success': False, 'message': 'Name is required'}), 400
        
    try:
        guest = Guest(
            name=name,
            email=email,
            phone=phone,
            rsvp_status=rsvp_status,
            event_id=event.id
        )
        db.session.add(guest)
        db.session.commit()
        return jsonify({
            'success': True, 
            'message': 'Guest added successfully',
            'guest': {
                'id': guest.id,
                'name': guest.name,
                'email': guest.email,
                'phone': guest.phone,
                'rsvp_status': guest.rsvp_status,
                'qr_token': guest.qr_token
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@guests_bp.route('/qr/<token>')
def generate_qr_code(token):
    # Public route to get the QR code image
    guest = Guest.query.filter_by(qr_token=token).first_or_404()
    
    # We generate a check-in link using the qr_token
    # Using request.url_root gives the base domain: http://localhost:5000/
    checkin_url = f"{request.url_root}guests/checkin/{token}"
    
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(checkin_url)
    qr.make(fit=True)
    
    # Custom colors: purple line (#6c63ff), white background
    img = qr.make_image(fill_color='#6c63ff', back_color='white')
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return send_file(buffer, mimetype='image/png')

@guests_bp.route('/qr/<token>/download')
def download_qr_code(token):
    guest = Guest.query.filter_by(qr_token=token).first_or_404()
    checkin_url = f"{request.url_root}guests/checkin/{token}"
    
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(checkin_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color='#6c63ff', back_color='white')
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    filename = f"qr_{guest.name.replace(' ', '_').lower()}.png"
    return send_file(buffer, mimetype='image/png', as_attachment=True, download_name=filename)

@guests_bp.route('/checkin/<token>', methods=['POST', 'GET'])
def checkin_guest(token):
    # This acts as the scan destination
    guest = Guest.query.filter_by(qr_token=token).first_or_404()
    event = guest.event
    
    if request.method == 'POST' or request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.args.get('api') == 'true':
        if guest.checked_in:
            return jsonify({
                'success': True,
                'already': True,
                'message': f'{guest.name} is already checked in.',
                'guest': {'name': guest.name, 'email': guest.email, 'check_in_time': guest.check_in_time.strftime('%H:%M:%S') if guest.check_in_time else ''}
            })
            
        guest.checked_in = True
        guest.check_in_time = datetime.utcnow()
        
        # Create a check-in notification reminder in database
        from app.models.reminder import Reminder
        notif = Reminder(
            title="Guest Checked In",
            message=f"{guest.name} has checked in to the event '{event.name}'.",
            remind_at=datetime.utcnow(),
            is_read=False,
            event_id=event.id,
            user_id=event.user_id
        )
        db.session.add(notif)
        
        db.session.commit()
        
        # Calculate updated attendance counts
        guests = event.guests.all()
        total = len(guests)
        checked_in = sum(1 for g in guests if g.checked_in)
        remaining = total - checked_in
        
        payload = {
            'guest_name': guest.name,
            'check_in_time': guest.check_in_time.strftime('%I:%M %p'),
            'total': total,
            'checked_in': checked_in,
            'remaining': remaining,
            'percent': round((checked_in / total * 100)) if total > 0 else 0
        }
        
        # Emit WebSocket update to room user_<user_id>
        socketio.emit('attendance_updated', payload, room=f"user_{event.user_id}")
        
        return jsonify({
            'success': True,
            'already': False,
            'message': f'Check-in successful for {guest.name}!',
            'guest': {'name': guest.name, 'email': guest.email, 'check_in_time': guest.check_in_time.strftime('%H:%M:%S')}
        })
        
    # Standard browser visit - show a digital pass ticket page
    return render_template('guests/digital_pass.html', guest=guest, event=event)


@guests_bp.route('/attendance')
@login_required
def attendance_all():
    events = current_user.events.all()
    if not events:
        flash('Create an event first to manage attendance.', 'info')
        return redirect(url_for('events.dashboard'))
    return redirect(url_for('guests.attendance_event', event_id=events[0].id))

@guests_bp.route('/attendance/<int:event_id>')
@login_required
def attendance_event(event_id):
    event = Event.query.get_or_404(event_id)
    if event.user_id != current_user.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('events.dashboard'))
        
    guests = event.guests.all()
    events = current_user.events.all()
    
    total = len(guests)
    checked_in = sum(1 for g in guests if g.checked_in)
    remaining = total - checked_in
    
    recent_check_ins = event.guests.filter_by(checked_in=True).order_by(Guest.check_in_time.desc()).limit(10).all()
    
    return render_template('guests/attendance_dashboard.html', 
                           event=event, 
                           guests=guests, 
                           events=events,
                           total=total,
                           checked_in=checked_in,
                           remaining=remaining,
                           recent_check_ins=recent_check_ins)

@guests_bp.route('/attendance/<int:event_id>/report')
@login_required
def attendance_report(event_id):
    event = Event.query.get_or_404(event_id)
    if event.user_id != current_user.id:
        return "Unauthorized", 403
        
    guests = event.guests.all()
    
    def generate():
        data = [['Guest Name', 'Email', 'Phone', 'RSVP Status', 'Checked In', 'Check-In Time']]
        for g in guests:
            c_time = g.check_in_time.strftime('%Y-%m-%d %H:%M:%S') if g.check_in_time else 'N/A'
            data.append([g.name, g.email or 'N/A', g.phone or 'N/A', g.rsvp_status, 'Yes' if g.checked_in else 'No', c_time])
            
        output = BytesIO()
        writer = csv.writer(Response().markup_safe_cast(output) if hasattr(Response, 'markup_safe_cast') else output)
        # We can just write csv to string
        
    # Simply create CSV as a string
    dest = BytesIO()
    # Workaround for csv writer with BytesIO and text
    wrapper = BytesIO()
    # Write to a string
    csv_data = ""
    for g in guests:
        c_time = g.check_in_time.strftime('%Y-%m-%d %H:%M:%S') if g.check_in_time else 'N/A'
        csv_data += f'"{g.name}","{g.email or ""}","{g.phone or ""}","{g.rsvp_status}","{"Yes" if g.checked_in else "No"}","{c_time}"\n'
        
    headers = "Guest Name,Email,Phone,RSVP Status,Checked In,Check-In Time\n"
    full_csv = headers + csv_data
    
    filename = f"attendance_report_{event.name.replace(' ', '_').lower()}.csv"
    return Response(
        full_csv,
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename={filename}"}
    )

@guests_bp.route('/update/<int:id>', methods=['POST'])
@login_required
def update_guest(id):
    guest = Guest.query.get_or_404(id)
    if guest.event.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
    data = request.get_json() if request.is_json else request.form
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    phone = data.get('phone', '').strip()
    rsvp_status = data.get('rsvp_status', 'Pending')
    
    if not name:
        return jsonify({'success': False, 'message': 'Name is required'}), 400
        
    try:
        guest.name = name
        guest.email = email
        guest.phone = phone
        guest.rsvp_status = rsvp_status
        db.session.commit()
        return jsonify({'success': True, 'message': 'Guest updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@guests_bp.route('/delete/<int:id>', methods=['POST', 'DELETE'])
@login_required
def delete_guest(id):
    guest = Guest.query.get_or_404(id)
    if guest.event.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
    try:
        db.session.delete(guest)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Guest removed successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
