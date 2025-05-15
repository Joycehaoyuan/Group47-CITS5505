import os
import logging

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate


# Configure logging
logging.basicConfig(level=logging.DEBUG)

try:
    import config
    print("The configuration file was successfully imported")
except ImportError:
    print("Warning: The configuration file was not found. The default configuration will be used.")
    # Set default configuration
    class config:
        SECRET_KEY = os.environ.get("SESSION_SECRET", "dev-secret-key")
        DATABASE_URI = "sqlite:///mealplanner.db"
        DEBUG = True
        TESTING = False
        RECIPE_API_KEY = os.environ.get('RECIPE_API_KEY')

class Base(DeclarativeBase):
    pass

# Initialize extensions
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
csrf = CSRFProtect()
migrate = Migrate()

def create_app(test_config=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_mapping(
            SECRET_KEY=os.environ.get("SESSION_SECRET", "dev-secret-key"),
            SQLALCHEMY_DATABASE_URI=config.DATABASE_URI,
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            SQLALCHEMY_ENGINE_OPTIONS={
                "pool_recycle": 300,
                "pool_pre_ping": True,
            },
            WTF_I18N_ENABLED=False,
            SESSION_COOKIE_SECURE=getattr(config, 'SESSION_COOKIE_SECURE', False),
            SESSION_COOKIE_HTTPONLY=getattr(config, 'SESSION_COOKIE_HTTPONLY', True),
            SESSION_COOKIE_SAMESITE='Lax',
            PERMANENT_SESSION_LIFETIME=getattr(config, 'PERMANENT_SESSION_LIFETIME', 3600),
            UPLOAD_FOLDER=getattr(config, 'UPLOAD_FOLDER', 'uploads'),
            MAX_CONTENT_LENGTH=getattr(config, 'MAX_CONTENT_LENGTH', 16 * 1024 * 1024),
        )
    else:
        # Load the test config if passed in
        app.config.update(test_config)

    # Ensure the upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)

    # Configure login manager
    login_manager.login_view = 'routes.login'
    login_manager.login_message_category = 'info'

    # Add security headers
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        return response

    # Import models and routes
    from app import models
    from app import routes
    
    # Register routes
    app.register_blueprint(routes.bp)

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))

    def init_db():
        """Initialize the database with tables and initial data."""
        with app.app_context():
            db.create_all()
            from app.models import Food
            from app.utils import populate_initial_food_data
            if Food.query.count() == 0:
                populate_initial_food_data()

    # Initialize database if not in testing mode
    if not app.config.get('TESTING', False):
        init_db()

    return app

# Create the application instance
app = create_app()
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https