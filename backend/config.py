import os
from datetime import timedelta

class Config:
    """Temel yapılandırma"""
    SQLALCHEMY_DATABASE_URI = 'sqlite:///reference_checker.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'uploads'
    REPORTS_FOLDER = 'reports'
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # API Keys
    CROSSREF_API_KEY = os.getenv('CROSSREF_API_KEY', '')
    OPENALEX_API_KEY = os.getenv('OPENALEX_API_KEY', '')
    PUBMED_API_KEY = os.getenv('PUBMED_API_KEY', '')
    
    # Veritabanı ayarları
    DB_TIMEOUT = 30
    DB_CHECK_SAME_THREAD = False

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
