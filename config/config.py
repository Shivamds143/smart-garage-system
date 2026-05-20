import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-123'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///smart_garage.db'  # Fallback to SQLite for easy dev start
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'app/static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
    GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY') or ''
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
