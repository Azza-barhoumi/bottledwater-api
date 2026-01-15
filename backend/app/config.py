import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, '..', 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT settings
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    if not JWT_SECRET_KEY:
        # Generate a temporary key for development if not set
        import secrets
        JWT_SECRET_KEY = secrets.token_urlsafe(32)
        print(f"[!] Warning: Using generated JWT_SECRET_KEY for development")
    
    # Access token short, refresh longer
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=int(os.environ.get('JWT_ACCESS_MINUTES', 30)))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.environ.get('JWT_REFRESH_DAYS', 7)))
    # Password reset token lifetime (in minutes)
    PASSWORD_RESET_TOKEN_EXPIRES_MINUTES = int(os.environ.get('PASSWORD_RESET_TOKEN_EXPIRES_MINUTES', 30))

    # Security settings
    # Session cookie security
    SESSION_COOKIE_SECURE = True  # HTTPS only in production
    SESSION_COOKIE_HTTPONLY = True  # No JavaScript access
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
    
    # Request size limit (1 MB)
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024
    
    # CORS allowed origins (override in environment)
    cors_env = os.environ.get('CORS_ORIGINS', 'http://localhost:5174,http://localhost:5175,http://localhost:3000')
    CORS_ORIGINS = [origin.strip() for origin in cors_env.split(',') if origin.strip()]
    
    # Swagger
    SWAGGER = {'title': 'BottledWater API', 'uiversion': 3}
