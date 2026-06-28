import os
from flask import Flask
from config import Config
from app.extensions import db, login_manager, migrate, csrf, socketio

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app)
    csrf.init_app(app)
    socketio.init_app(app)

    # SocketIO Rooms Connection Logic
    from flask_socketio import join_room, leave_room
    from flask_login import current_user

    @socketio.on('connect')
    def handle_connect():
        if current_user.is_authenticated:
            join_room(f"user_{current_user.id}")

    @socketio.on('disconnect')
    def handle_disconnect():
        if current_user.is_authenticated:
            leave_room(f"user_{current_user.id}")

    # Register user loader
    from app.models.user import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from app.blueprints.auth import auth_bp
    from app.blueprints.events import events_bp
    from app.blueprints.guests import guests_bp
    from app.blueprints.chatbot import chatbot_bp
    from app.blueprints.invitations import invitations_bp
    from app.blueprints.budget import budget_bp
    from app.blueprints.tasks import tasks_bp
    from app.blueprints.vendors import vendors_bp
    from app.blueprints.analytics import analytics_bp
    from app.blueprints.feedback import feedback_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(events_bp, url_prefix='/')
    app.register_blueprint(guests_bp, url_prefix='/guests')
    app.register_blueprint(chatbot_bp, url_prefix='/')
    app.register_blueprint(invitations_bp, url_prefix='/invitations')
    app.register_blueprint(budget_bp, url_prefix='/budget')
    app.register_blueprint(tasks_bp, url_prefix='/tasks')
    app.register_blueprint(vendors_bp, url_prefix='/vendors')
    app.register_blueprint(analytics_bp, url_prefix='/analytics')
    app.register_blueprint(feedback_bp, url_prefix='/feedback')

    # Register context processor for notifications
    @app.context_processor
    def inject_notifications():
        from flask_login import current_user
        from app.models.reminder import Reminder
        if current_user.is_authenticated:
            reminders = Reminder.query.filter_by(user_id=current_user.id).order_by(Reminder.created_at.desc()).limit(5).all()
            unread_count = Reminder.query.filter_by(user_id=current_user.id, is_read=False).count()
            return {
                'notifications': reminders,
                'notification_count': unread_count
            }
        return {
            'notifications': [],
            'notification_count': 0
        }

    # Create database and seed demo data on first start
    with app.app_context():
        # Ensure database directory exists
        db_path = app.config['SQLALCHEMY_DATABASE_URI']
        if db_path.startswith('sqlite:///'):
            file_path = db_path.replace('sqlite:///', '')
            dir_name = os.path.dirname(file_path)
            if dir_name and not os.path.exists(dir_name):
                os.makedirs(dir_name, exist_ok=True)

        db.create_all()

        # Enable WAL mode for SQLite database
        if db_path.startswith('sqlite:///'):
            try:
                from sqlalchemy import text
                db.session.execute(text("PRAGMA journal_mode=WAL;"))
                db.session.commit()
            except Exception as e:
                app.logger.warning(f"Could not enable WAL mode: {e}")

        # Create upload folder
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

        # Seed data if user table is empty
        if User.query.first() is None:
            from app.seed_data import seed_database
            seed_database(db)

    return app
