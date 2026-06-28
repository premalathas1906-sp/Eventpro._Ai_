import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'eventpro-ai-secret-key-2026'
    if 'VERCEL' in os.environ:
        SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/eventpro.db'
        UPLOAD_FOLDER = '/tmp'
    else:
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
            'sqlite:///' + os.path.join(basedir, 'instance', 'eventpro.db')
        UPLOAD_FOLDER = os.path.join(basedir, 'app', 'static', 'uploads')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_TIME_LIMIT = None
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
