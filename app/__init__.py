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

db = SQLAlchemy(model_class=Base)
# create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mealplanner.db"
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Force English language for WTForms messages
app.config['WTF_I18N_ENABLED'] = False

# Add security configuration
app.config['SESSION_COOKIE_SECURE'] = getattr(config, 'SESSION_COOKIE_SECURE', False)
app.config['SESSION_COOKIE_HTTPONLY'] = getattr(config, 'SESSION_COOKIE_HTTPONLY', True)
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = getattr(config, 'PERMANENT_SESSION_LIFETIME', 3600)

# Configure the upload folder
app.config['UPLOAD_FOLDER'] = getattr(config, 'UPLOAD_FOLDER', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = getattr(config, 'MAX_CONTENT_LENGTH', 16 * 1024 * 1024)

# Ensure the upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


# Initialize the app with the extension
db.init_app(app)

# Initialize migration
migrate = Migrate(app, db)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'routes.login'
login_manager.login_message_category = 'info'

# Add security headers
@app.after_request
def add_security_headers(response):
    # Prevent content type sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    # Enable XSS protection in browsers
    response.headers['X-XSS-Protection'] = '1; mode=block'
    # Prevent clickjacking
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    return response

with app.app_context():
    # Import models and routes
    import models
    import routes
    
    # Register routes
    app.register_blueprint(routes.bp)
    
    # Create database tables
    db.create_all()

    from models import User, Food, MealPlan, UserDietaryData, SharedData
    
    # Ensure the food database has some initial data
    if Food.query.count() == 0:
        from utils import populate_initial_food_data
        populate_initial_food_data()

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))
