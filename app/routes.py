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

@bp.route('/meal-plan')
def meal_plan():
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

@bp.route('/upload-data', methods=['GET', 'POST'])
@login_required
def upload_data():
    """Page to manually upload dietary data."""
    form = UploadDietaryDataForm()
    csv_form = UploadCSVForm()
    
    if form.validate_on_submit():
        try:
            meals_data = json.loads(form.meals_json.data) if form.meals_json.data else []
            date_obj = datetime.strptime(form.date.data, '%Y-%m-%d').date()
            
            # Check if entry for this date already exists
            existing_entry = UserDietaryData.query.filter_by(
                user_id=current_user.id,
                date=date_obj
            ).first()
            
            if existing_entry:
                existing_entry.calories = form.calories.data
                existing_entry.protein = form.protein.data
                existing_entry.carbs = form.carbs.data
                existing_entry.fat = form.fat.data
                existing_entry.notes = form.notes.data
                existing_entry.meals_json = json.dumps(meals_data)
                flash('Dietary data updated for this date.', 'success')
            else:
                new_entry = UserDietaryData(
                    user_id=current_user.id,
                    date=date_obj,
                    calories=form.calories.data,
                    protein=form.protein.data,
                    carbs=form.carbs.data,
                    fat=form.fat.data,
                    notes=form.notes.data,
                    meals_json=json.dumps(meals_data)
                )
                db.session.add(new_entry)
                flash('Dietary data saved successfully!', 'success')
                
            db.session.commit()
            return redirect(url_for('routes.visualize_data'))
            
        except Exception as e:
            flash(f'Error saving data: {str(e)}', 'danger')
    
    if csv_form.validate_on_submit():
        try:
            csv_file = csv_form.csv_file.data
            stream = io.StringIO(csv_file.stream.read().decode("UTF8"), newline=None)
            csv_reader = csv.DictReader(stream)
            
            # Validate CSV format
            required_fields = ['date', 'calories', 'protein', 'carbs', 'fat']
            first_row = next(csv_reader)
            stream.seek(0)  # Reset stream position
            next(csv_reader)  # Skip header row again
            
            for field in required_fields:
                if field not in first_row:
                    flash(f'CSV file missing required column: {field}', 'danger')
                    return redirect(url_for('routes.upload_data'))
            
            # Process CSV data
            entries_added = 0
            for row in csv_reader:
                try:
                    date_obj = datetime.strptime(row['date'], '%Y-%m-%d').date()
                    
                    # Check if entry already exists
                    existing = UserDietaryData.query.filter_by(
                        user_id=current_user.id,
                        date=date_obj
                    ).first()
                    
                    if existing:
                        # Update existing entry
                        existing.calories = int(row['calories'])
                        existing.protein = float(row['protein'])
                        existing.carbs = float(row['carbs'])
                        existing.fat = float(row['fat'])
                        existing.notes = row.get('notes', '')
                        if 'meals' in row:
                            existing.meals_json = row['meals']
                    else:
                        # Create new entry
                        meals_json = row.get('meals', '[]')
                        entry = UserDietaryData(
                            user_id=current_user.id,
                            date=date_obj,
                            calories=int(row['calories']),
                            protein=float(row['protein']),
                            carbs=float(row['carbs']),
                            fat=float(row['fat']),
                            notes=row.get('notes', ''),
                            meals_json=meals_json
                        )
                        db.session.add(entry)
                        entries_added += 1
                        
                except Exception as e:
                    flash(f'Error processing row: {row.get("date", "unknown")}: {str(e)}', 'warning')
                    continue
                    
            db.session.commit()
            flash(f'Successfully imported {entries_added} dietary data entries!', 'success')
            return redirect(url_for('routes.visualize_data'))
            
        except Exception as e:
            flash(f'Error processing CSV file: {str(e)}', 'danger')
    
    return render_template('upload_data.html', form=form, csv_form=csv_form)

@bp.route('/visualize-data')
def visualize_data():
    return render_template('visualize_data.html')

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



