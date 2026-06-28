from flask import render_template
from flask_login import login_required, current_user
from app.blueprints.invitations import invitations_bp

@invitations_bp.route('/')
@login_required
def invitation_page():
    events = current_user.events.all()
    return render_template('invitations/invitation_page.html', events=events)
