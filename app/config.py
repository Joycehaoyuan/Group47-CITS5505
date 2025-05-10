import os
import secrets

# API key - Get from environment variables with no default value
RECIPE_API_KEY = os.environ.get('RECIPE_API_KEY','replace with your own api key')


# Flask application configuration
SECRET_KEY = os.environ.get('SECRET_KEY', secrets.token_hex(24))  # Generate a secure key automatically
DEBUG = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 't')  # Convert string to boolean
TESTING = os.environ.get('TESTING', 'False').lower() in ('true', '1', 't')

