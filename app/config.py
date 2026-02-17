import os
from dotenv import load_dotenv
load_dotenv()
class Config:
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    # PostgreSQL
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://voicebot_user:password@localhost/voicebot_db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # MongoDB
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    MONGODB_DB_NAME = 'voicebot_analytics'
    # API Keys
    DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY')
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    # Groq Model
    GROQ_MODEL = 'llama-3.3-70b-versatile'
    # Upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
