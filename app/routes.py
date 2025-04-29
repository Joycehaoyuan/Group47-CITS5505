from flask import Blueprint, render_template

bp = Blueprint('routes', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/meal-plan')
def meal_plan():
    return render_template('meal_plan.html')

@bp.route('/upload-data')
def upload_data():
    return render_template('upload_data.html')

@bp.route('/visualize-data')
def visualize_data():
    return render_template('visualize_data.html')

@bp.route('/share-data')
def share_data():
    return render_template('share_data.html')

@bp.route('/login')
def login():
    return render_template('login.html')

@bp.route('/register')
def register():
    return render_template('register.html')
