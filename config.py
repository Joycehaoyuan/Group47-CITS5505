import os
import secrets

# API key - Get from environment variables with no default value
RECIPE_API_KEY = os.environ.get('RECIPE_API_KEY','replace with your own api key')

# Database configuration
DATABASE_URI = os.environ.get('DATABASE_URI', "sqlite:///mealplanner.db")

# Flask application configuration
SECRET_KEY = os.environ.get('SECRET_KEY', secrets.token_hex(24))  # Generate a secure key automatically
DEBUG = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 't')  # Convert string to boolean
TESTING = os.environ.get('TESTING', 'False').lower() in ('true', '1', 't')

# Security configuration
SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'True').lower() in ('true', '1', 't')
SESSION_COOKIE_HTTPONLY = True
PERMANENT_SESSION_LIFETIME = int(os.environ.get('SESSION_LIFETIME', '3600'))  # Session expiration time (seconds)

# Upload file configuration
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
ALLOWED_EXTENSIONS = {'csv'}
MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # Default 16MB

# Other application configuration
DEFAULT_DIET_TYPE = "Anything"
DEFAULT_CALORIES = 2000
DEFAULT_MEAL_COUNT = 3

# Development/debug-specific configuration, should be set to False in production
EXPLAIN_TEMPLATE_LOADING = False
TEMPLATES_AUTO_RELOAD = DEBUG