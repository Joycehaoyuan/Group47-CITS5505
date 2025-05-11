from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import csv
import io
import json
from datetime import datetime, timedelta
import os

from app import db
from models import User, Food, MealPlan, UserDietaryData, SharedData, Recipe, RecipeIngredient
from forms import LoginForm, RegistrationForm, MealPlanForm, UploadDietaryDataForm, UploadCSVForm, ShareDataForm
from app import db
from models import User, Food, MealPlan, UserDietaryData, SharedData, Recipe, RecipeIngredient
from forms import LoginForm, RegistrationForm, MealPlanForm, UploadDietaryDataForm, UploadCSVForm, ShareDataForm
from utils import generate_meal_plan, recommend_macros, get_food_by_diet, generate_single_meal
from recipe_api import get_recipes_by_ingredients, search_recipes, format_recipe_for_display
from flask_wtf.csrf import CSRFError


bp = Blueprint('routes', __name__)

@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page."""
    if current_user.is_authenticated:
        return redirect(url_for('routes.meal_plan'))
        
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('routes.login'))
        
    return render_template('register.html', form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login page."""
    if current_user.is_authenticated:
        return redirect(url_for('routes.meal_plan'))
        
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page or url_for('routes.meal_plan'))
        else:
            flash('Login failed. Please check your username and password.', 'danger')
            
    return render_template('login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    """Logout user."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('routes.index'))

@bp.route('/meal-plan', methods=['GET', 'POST'])
def meal_plan():
    """Meal plan generation page."""
    form = MealPlanForm()
    
    if form.validate_on_submit():
        meal_plan_data = generate_meal_plan(
            form.diet_type.data,
            form.target_calories.data,
            form.meal_count.data
        )
        
        # If user is logged in, save the meal plan
        if current_user.is_authenticated:
            meal_plan = MealPlan(
                user_id=current_user.id,
                diet_type=form.diet_type.data,
                target_calories=form.target_calories.data,
                meal_count=form.meal_count.data,
                meals=json.dumps(meal_plan_data)
            )
            
            db.session.add(meal_plan)
            db.session.commit()
            
            return render_template('meal_plan.html', 
                                form=form, 
                                meal_plan=meal_plan,
                                meal_data=meal_plan_data,
                                macros=recommend_macros(form.target_calories.data))
        else:
            # For non-logged in users, just show the meal plan without saving
            return render_template('meal_plan.html', 
                                form=form, 
                                meal_plan=None,  # No saved plan for anonymous users
                                meal_data=meal_plan_data,
                                macros=recommend_macros(form.target_calories.data),
                                login_required_for_save=True)  # Flag to show login prompt
    
    # If user is logged in, show previous meal plan if available
    if current_user.is_authenticated:
        latest_meal_plan = MealPlan.query.filter_by(user_id=current_user.id).order_by(MealPlan.date_created.desc()).first()
        
        if latest_meal_plan and not form.is_submitted():
            form.diet_type.data = latest_meal_plan.diet_type
            form.target_calories.data = latest_meal_plan.target_calories
            form.meal_count.data = latest_meal_plan.meal_count
            
            return render_template('meal_plan.html', 
                                form=form, 
                                meal_plan=latest_meal_plan,
                                meal_data=latest_meal_plan.get_meals(),
                                macros=recommend_macros(latest_meal_plan.target_calories))
    
    # Default recommended macros
    default_calories = 2000
    return render_template('meal_plan.html', 
                        form=form, 
                        meal_plan=None,
                        meal_data=None,
                        macros=recommend_macros(default_calories))
     """API endpoint to refresh an individual meal."""
    data = request.json
    meal_plan_id = data.get('meal_plan_id')
    meal_index = data.get('meal_index')
    
    # Convert meal_index to integer
    try:
        meal_index = int(meal_index)
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid meal index format'}), 400
    
    meal_plan = MealPlan.query.get(meal_plan_id)
    
    if not meal_plan or meal_plan.user_id != current_user.id:
        return jsonify({'error': 'Meal plan not found or access denied'}), 404
    
    meals = meal_plan.get_meals()
    
    if meal_index >= len(meals):
        return jsonify({'error': 'Invalid meal index'}), 400
    
    # Calculate target calories for this meal
    meal_calories = meal_plan.target_calories / meal_plan.meal_count
    
    # Determine the appropriate meal type based on index
    meal_type = "any"
    meal_name = meals[meal_index]["name"]
    
    if "Breakfast" in meal_name:
        meal_type = "breakfast"
    elif "Lunch" in meal_name:
        meal_type = "lunch"
    elif "Dinner" in meal_name:
        meal_type = "dinner"
    elif "Snack" in meal_name:
        meal_type = "snack"
    
    # Get suitable foods for this meal type and diet
    suitable_foods = get_food_by_diet(meal_plan.diet_type, meal_type=meal_type)
    
    # If not enough suitable foods found, try any meal type
    if len(suitable_foods) < 5:
        suitable_foods = get_food_by_diet(meal_plan.diet_type)
    
    # If still not enough, use "anything" diet
    if len(suitable_foods) < 5:
        suitable_foods = get_food_by_diet("anything")
    
    # Generate a new single meal
    new_meal = generate_single_meal(suitable_foods, int(meal_calories), meal_name)
    
    # Update the meal in the meal plan
    meals[meal_index] = new_meal
    meal_plan.meals = json.dumps(meals)
    db.session.commit()
    
    return jsonify({'success': True, 'meal': new_meal})

@bp.route('/upload/manual', methods=['GET', 'POST'])
@login_required
def upload_dietary_data():
    form = UploadDietaryDataForm()
    if form.validate_on_submit():
        dietary_data = UserDietaryData(
            user_id=current_user.id,
            date=datetime.strptime(form.date.data, '%Y-%m-%d'),
            calories=form.calories.data,
            protein=form.protein.data,
            carbs=form.carbs.data,
            fat=form.fat.data,
            notes=form.notes.data,
        )
        # deal with meals_json data
        if form.meals_json.data:
            dietary_data.set_meals(json.loads(form.meals_json.data))
        else:
            dietary_data.set_meals([])

        db.session.add(dietary_data)
        db.session.commit()
        flash('Dietary data uploaded successfully.')
        return redirect(url_for('routes.upload_dietary_data'))

    return render_template('upload_manual.html', form=form)

@bp.route('/upload/csv', methods=['GET', 'POST'])
@login_required
def upload_csv():
    form = UploadCSVForm()
    if form.validate_on_submit():
        file = form.csv_file.data
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        reader = csv.DictReader(stream)

        for row in reader:
            try:
                dietary_data = UserDietaryData(
                    user_id=current_user.id,
                    date=datetime.strptime(row['date'], '%Y-%m-%d'),
                    calories=int(row['calories']),
                    protein=float(row['protein']),
                    carbs=float(row['carbs']),
                    fat=float(row['fat']),
                    notes=row.get('notes', '')
                )
                meals_data = json.loads(row.get('meals_json', '[]'))
                dietary_data.set_meals(meals_data)

                db.session.add(dietary_data)
            except Exception as e:
                flash(f"Error processing row: {row}. Error: {e}", 'danger')

        db.session.commit()
        flash('CSV file uploaded successfully.')
        return redirect(url_for('routes.upload_csv'))

    return render_template('upload_csv.html', form=form)


@bp.route('/visualize-data')
def visualize_data():
    """Data visualization page."""
    # Check if user is logged in
    if current_user.is_authenticated:
        # Get user's actual data
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)  # Show last 30 days of data
        
        dietary_data = UserDietaryData.query.filter(
            UserDietaryData.user_id == current_user.id,
            UserDietaryData.date >= start_date,
            UserDietaryData.date <= end_date
        ).order_by(UserDietaryData.date).all()
        
        # Calculate some statistics for the user
        stats = {
            'entries_count': len(dietary_data),
            'avg_calories': round(sum(d.calories for d in dietary_data) / len(dietary_data)) if dietary_data else 0,
            'avg_protein': round(sum(d.protein for d in dietary_data) / len(dietary_data), 1) if dietary_data else 0,
            'avg_carbs': round(sum(d.carbs for d in dietary_data) / len(dietary_data), 1) if dietary_data else 0,
            'avg_fat': round(sum(d.fat for d in dietary_data) / len(dietary_data), 1) if dietary_data else 0,
        }
        
        # Get latest meal plan for comparison
        latest_meal_plan = MealPlan.query.filter_by(user_id=current_user.id).order_by(MealPlan.date_created.desc()).first()
        
        # Generate chart data
        chart_data = {
            'dates': [d.date.strftime('%Y-%m-%d') for d in dietary_data],
            'calories': [d.calories for d in dietary_data],
            'protein': [d.protein for d in dietary_data],
            'carbs': [d.carbs for d in dietary_data],
            'fat': [d.fat for d in dietary_data],
        }
        
        # Check if user has shared data to view
        shared_with_me = SharedData.query.filter_by(recipient_id=current_user.id).all()
        has_shared_data = len(shared_with_me) > 0
        
        return render_template(
            'visualize_data.html',
            dietary_data=dietary_data,
            stats=stats,
            chart_data=json.dumps(chart_data),
            meal_plan=latest_meal_plan,
            has_shared_data=has_shared_data
        )
    else:
        # For non-logged in users, show example data
        # Create sample data for demonstration
        today = datetime.now().date()
        sample_dates = [(today - timedelta(days=i)) for i in range(7)]
        
        # Example dietary data
        sample_dietary_data = [
            {'date': sample_dates[0], 'calories': 2100, 'protein': 110, 'carbs': 210, 'fat': 70},
            {'date': sample_dates[1], 'calories': 1950, 'protein': 100, 'carbs': 200, 'fat': 65},
            {'date': sample_dates[2], 'calories': 2050, 'protein': 105, 'carbs': 205, 'fat': 68},
            {'date': sample_dates[3], 'calories': 2000, 'protein': 102, 'carbs': 202, 'fat': 66},
            {'date': sample_dates[4], 'calories': 2150, 'protein': 112, 'carbs': 215, 'fat': 72},
            {'date': sample_dates[5], 'calories': 1900, 'protein': 95, 'carbs': 190, 'fat': 63},
            {'date': sample_dates[6], 'calories': 2200, 'protein': 115, 'carbs': 220, 'fat': 73},
        ]
        
        # Calculate sample statistics
        sample_stats = {
            'entries_count': len(sample_dietary_data),
            'avg_calories': round(sum(d['calories'] for d in sample_dietary_data) / len(sample_dietary_data)),
            'avg_protein': round(sum(d['protein'] for d in sample_dietary_data) / len(sample_dietary_data), 1),
            'avg_carbs': round(sum(d['carbs'] for d in sample_dietary_data) / len(sample_dietary_data), 1),
            'avg_fat': round(sum(d['fat'] for d in sample_dietary_data) / len(sample_dietary_data), 1),
        }
        
        # Sample chart data
        sample_chart_data = {
            'dates': [d.strftime('%Y-%m-%d') for d in sample_dates],
            'calories': [d['calories'] for d in sample_dietary_data],
            'protein': [d['protein'] for d in sample_dietary_data],
            'carbs': [d['carbs'] for d in sample_dietary_data],
            'fat': [d['fat'] for d in sample_dietary_data],
        }
        
        return render_template(
            'visualize_data.html',
            dietary_data=[],  # No actual data for display in tables
            stats=sample_stats,
            chart_data=json.dumps(sample_chart_data),
            meal_plan=None,
            has_shared_data=False,
            login_required_for_real_data=True  # Flag to show login prompt
        )


@bp.route('/share-data', methods=['GET', 'POST'])
@login_required
def share_data():
    """Page to share data with other users and view shared data."""
    form = ShareDataForm()
    
    if form.validate_on_submit():
        recipient = User.query.filter_by(username=form.recipient_username.data).first()
        
        if not recipient:
            flash('User not found.', 'danger')
            return redirect(url_for('routes.share_data'))
            
        if recipient.id == current_user.id:
            flash('You cannot share data with yourself.', 'warning')
            return redirect(url_for('routes.share_data'))
            
        # Validate that the data exists and belongs to the current user
        data_type = form.data_type.data
        data_id = form.data_id.data
        
        if data_type == 'meal_plan':
            data = MealPlan.query.get(data_id)
        else:  # dietary_data
            data = UserDietaryData.query.get(data_id)
            
        if not data or data.user_id != current_user.id:
            flash('Invalid data selected or you do not own this data.', 'danger')
            return redirect(url_for('routes.share_data'))
            
        # Check if already shared
        existing_share = SharedData.query.filter_by(
            owner_id=current_user.id,
            recipient_id=recipient.id,
            data_type=data_type,
            data_id=data_id
        ).first()
        
        if existing_share:
            flash(f'You have already shared this {data_type.replace("_", " ")} with {recipient.username}.', 'info')
            return redirect(url_for('routes.share_data'))
            
        # Create new share
        share = SharedData(
            owner_id=current_user.id,
            recipient_id=recipient.id,
            data_type=data_type,
            data_id=data_id
        )
        
        db.session.add(share)
        db.session.commit()
        
        flash(f'Successfully shared your {data_type.replace("_", " ")} with {recipient.username}!', 'success')
        return redirect(url_for('routes.share_data'))
    
    # Get user's data for sharing options
    meal_plans = MealPlan.query.filter_by(user_id=current_user.id).order_by(MealPlan.date_created.desc()).all()
    dietary_data = UserDietaryData.query.filter_by(user_id=current_user.id).order_by(UserDietaryData.date.desc()).all()
    
    # Get existing shares
    my_shares = SharedData.query.filter_by(owner_id=current_user.id).all()
    
    # Get data shared with the current user
    shared_data = SharedData.query.filter_by(recipient_id=current_user.id).all()
    
    # Fetch actual data objects for data shared with me
    shared_items = []
    for share in shared_data:
        if share.data_type == 'meal_plan':
            data_obj = MealPlan.query.get(share.data_id)
            if data_obj:
                shared_items.append({
                    'share': share,
                    'data': data_obj,
                    'owner': User.query.get(share.owner_id),
                    'meals': data_obj.get_meals()
                })
        else:  # dietary_data
            data_obj = UserDietaryData.query.get(share.data_id)
            if data_obj:
                shared_items.append({
                    'share': share,
                    'data': data_obj,
                    'owner': User.query.get(share.owner_id)
                })
    
    # Get all registered users for autocomplete (excluding current user)
    all_users = User.query.filter(User.id != current_user.id).all()
    
    return render_template(
        'share_data.html',
        form=form,
        meal_plans=meal_plans,
        dietary_data=dietary_data,
        my_shares=my_shares,
        shared_items=shared_items,
        all_users=all_users
    )

@bp.route('/shared-with-me')
@login_required
def shared_with_me():
    """Redirect to consolidated share page."""
    return redirect(url_for('routes.share_data'))

@bp.route('/profile')
@login_required
def profile():
    """User profile page."""
    meal_plan_count = MealPlan.query.filter_by(user_id=current_user.id).count()
    data_entry_count = UserDietaryData.query.filter_by(user_id=current_user.id).count()
    
    return render_template(
        'profile.html',
        meal_plan_count=meal_plan_count,
        data_entry_count=data_entry_count
    )

@bp.route('/delete-share/<int:share_id>', methods=['POST'])
@login_required
def delete_share(share_id):
    """Delete a data share."""
    share = SharedData.query.get_or_404(share_id)
    
    # Only the owner can delete a share
    if share.owner_id != current_user.id:
        abort(403)
        
    db.session.delete(share)
    db.session.commit()
    
    flash('Share has been removed.', 'success')
    return redirect(url_for('routes.share_data'))



