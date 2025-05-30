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
from app.models import User, Food, MealPlan, UserDietaryData, SharedData, Recipe, RecipeIngredient
from app.forms import LoginForm, RegistrationForm, MealPlanForm, UploadDietaryDataForm, UploadCSVForm, ShareDataForm
from app.utils import generate_meal_plan, recommend_macros, get_food_by_diet, generate_single_meal
from app.recipe_api import get_recipes_by_ingredients, search_recipes, format_recipe_for_display
from flask_wtf.csrf import CSRFError

bp = Blueprint('routes', __name__)

@bp.errorhandler(CSRFError)
def handle_csrf_error(e):
    return render_template('csrf_error.html', reason=e.description), 400

@bp.route('/')
def index():
    """Landing page with app introduction."""
    return render_template('index.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page."""
    if current_user.is_authenticated:
        return redirect(url_for('routes.meal_plan'))
        
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
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
        except Exception as e:
            db.session.rollback()
            flash('Registration failed: ' + str(e), 'danger')
            
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

@bp.route('/api/users', methods=['GET'])
@login_required
def api_users():
    # Implement user search functionality
    term = request.args.get('term', '')
    users = User.query.filter(User.username.like(f'%{term}%')).all()
    return jsonify({"users": [user.username for user in users]})

@bp.route('/api/preview-data', methods=['POST'])
@login_required
def preview_data():
    # Implement data preview functionality
    data = request.json
    # Process data and return preview
    return jsonify({"preview": "Data processed successfully"})

@bp.route('/api/refresh-meal', methods=['POST'])
@login_required
def refresh_meal():
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
    
    # Enhance my_shares with recipient info
    enhanced_my_shares = []
    for share in my_shares:
        recipient = User.query.get(share.recipient_id)
        # Only add if recipient exists
        if recipient:
            enhanced_my_shares.append({
                'share': share,
                'recipient': recipient
            })
    
    # Get data shared with the current user
    shared_data = SharedData.query.filter_by(recipient_id=current_user.id).all()
    
    # Fetch actual data objects for data shared with me
    shared_items = []
    for share in shared_data:
        owner = User.query.get(share.owner_id)
        if not owner:
            continue  # Skip if owner doesn't exist
            
        if share.data_type == 'meal_plan':
            data_obj = MealPlan.query.get(share.data_id)
            if data_obj:
                shared_items.append({
                    'share': share,
                    'data': data_obj,
                    'owner': owner,
                    'meals': data_obj.get_meals()
                })
        else:  # dietary_data
            data_obj = UserDietaryData.query.get(share.data_id)
            if data_obj:
                shared_items.append({
                    'share': share,
                    'data': data_obj,
                    'owner': owner
                })
    
    # Get all registered users for autocomplete (excluding current user)
    all_users = User.query.filter(User.id != current_user.id).all()
    
    return render_template(
        'share_data.html',
        form=form,
        meal_plans=meal_plans,
        dietary_data=dietary_data,
        my_shares=enhanced_my_shares,
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
    
@bp.route('/api/recipe-suggestions', methods=['POST'])
def recipe_suggestions():
    """API to get recipe suggestions based on ingredients."""
    data = request.json
    foods = data.get('foods', [])
    meal_name = data.get('meal_name', '')
    
    if not foods:
        return jsonify({'error': 'No foods provided'}), 400
    
    # Debug foods received 
    print(f"Received foods for recipe suggestions: {foods}")
    
    # Determine meal type and diet type from meal name
    meal_type = "any"
    if "breakfast" in meal_name.lower():
        meal_type = "breakfast"
    elif "lunch" in meal_name.lower():
        meal_type = "lunch"
    elif "dinner" in meal_name.lower():
        meal_type = "dinner"
    elif "snack" in meal_name.lower():
        meal_type = "snack"
    
    # Determine diet type if mentioned in meal name
    diet_type = None
    if "vegetarian" in meal_name.lower():
        diet_type = "vegetarian"
    elif "vegan" in meal_name.lower():
        diet_type = "vegan"
    elif "keto" in meal_name.lower():
        diet_type = "ketogenic"
    elif "paleo" in meal_name.lower():
        diet_type = "paleo"
    elif "mediterranean" in meal_name.lower():
        diet_type = "mediterranean"
        
    try:
        # Try to use external API to get recipes
        api_recipes = []
        
        # Method 1: Find recipes by ingredient list
        ingredient_recipes = get_recipes_by_ingredients(foods, diet_type, limit=3)
        if ingredient_recipes:
            for recipe in ingredient_recipes:
                formatted = format_recipe_for_display(recipe)
                if formatted:
                    api_recipes.append({
                        'name': formatted.get('title', 'Recipe'),
                        'image': formatted.get('image', ''),
                        'ingredients': [ing.get('name', '') for ing in formatted.get('extendedIngredients', [])] 
                                      if 'extendedIngredients' in formatted
                                      else formatted.get('usedIngredients', []) + formatted.get('missedIngredients', []),
                        'instructions': formatted.get('instructions', '').split('.') if formatted.get('instructions') else [],
                        'source_url': formatted.get('sourceUrl', ''),
                        'ready_in_minutes': formatted.get('readyInMinutes', 0),
                        'servings': formatted.get('servings', 0)
                    })
                    
        # Method 2: If the first method doesn't find enough recipes, try searching for them
        if len(api_recipes) < 2:
            # Join ingredients into a query string    
            query = " ".join(foods[:3])  # Use the first 3 ingredients as search terms
            if meal_type != "any":
                query += f" {meal_type}"  # Add meal type
                
            search_results = search_recipes(query, diet_type, limit=3)
            if search_results:
                for recipe in search_results:
                    # Avoid adding duplicate recipes
                    existing_names = [r.get('name') for r in api_recipes]
                    if recipe.get('title') not in existing_names:
                        formatted = format_recipe_for_display(recipe)
                        if formatted:
                            api_recipes.append({
                                'name': formatted.get('title', 'Recipe'),
                                'image': formatted.get('image', ''),
                                'ingredients': [ing.get('name', '') for ing in formatted.get('extendedIngredients', [])] 
                                              if 'extendedIngredients' in formatted
                                              else [],
                                'instructions': formatted.get('instructions', '').split('.') if formatted.get('instructions') else [],
                                'source_url': formatted.get('sourceUrl', ''),
                                'ready_in_minutes': formatted.get('readyInMinutes', 0),
                                'servings': formatted.get('servings', 0)
                            })
        
        # Use recipes from external API
        if api_recipes:
            return jsonify({
                'success': True,
                'meal_name': meal_name,
                'recipes': api_recipes
            })
            
    except Exception as e:
        print(f"Error fetching recipes from API: {e}")
        # If API call fails, we will fall back to local recipes
        pass
    
    # Fallback: If API cannot get recipes, use local static recipes
    # This ensures that even if the API key is not available or usage quota is exceeded, the application can still work
    recipes = []
    foods_lower = [food.lower() for food in foods]
    
    # Check if there is egg
    if any("egg" in food for food in foods_lower):
        recipes.append({
            'name': "Simple Scrambled Eggs",
            'ingredients': [
                "3 large eggs",
                "1 tbsp butter or oil",
                "Salt and pepper to taste",
                "Optional: chopped herbs, cheese, or vegetables"
            ],
            'instructions': [
                "Beat eggs in a bowl with a pinch of salt and pepper.",
                "Heat butter or oil in a non-stick pan over medium heat.",
                "Pour in eggs and cook, stirring gently until they begin to set.",
                "When eggs are mostly set but still slightly wet, remove from heat (they will continue cooking).",
                "Add any optional ingredients like herbs or cheese, and serve immediately."
            ]
        })
    
    # Check if there is sweet potato
    if any("sweet potato" in food for food in foods_lower):
        recipes.append({
            'name': "Roasted Sweet Potato Cubes",
            'ingredients': [
                "2 large sweet potatoes, peeled and diced",
                "2 tbsp olive oil",
                "1 tsp paprika",
                "1/2 tsp ground cumin",
                "Salt and pepper to taste",
                "Fresh herbs like rosemary or thyme (optional)"
            ],
            'instructions': [
                "Preheat oven to 425°F (220°C).",
                "Toss sweet potato cubes with olive oil, paprika, cumin, salt, and pepper.",
                "Spread in a single layer on a baking sheet.",
                "Roast for 25-30 minutes, turning halfway through, until tender and caramelized.",
                "Sprinkle with fresh herbs if using and serve hot."
            ]
        })
        
        # If we have both sweet potato and eggs
        if any("egg" in food for food in foods_lower):
            recipes.append({
                'name': "Sweet Potato and Egg Breakfast Hash",
                'ingredients': [
                    "1 large sweet potato, diced small",
                    "1/2 onion, diced",
                    "1 bell pepper, diced (optional)",
                    "2 tbsp olive oil",
                    "2-4 eggs",
                    "1/2 tsp paprika",
                    "Salt and pepper to taste",
                    "Fresh herbs (parsley, chives, etc.)"
                ],
                'instructions': [
                    "Heat olive oil in a large skillet over medium heat.",
                    "Add diced sweet potato and cook for 5-7 minutes until starting to soften.",
                    "Add onion and bell pepper, continue cooking for 5 minutes, stirring occasionally.",
                    "Season with paprika, salt, and pepper.",
                    "Create wells in the hash and crack eggs into them.",
                    "Cover and cook until eggs reach desired doneness (about 3-5 minutes).",
                    "Garnish with fresh herbs and serve immediately."
                ]
            })
    
    # If no specific recipe is found, add a generic recipe
    if not recipes:
        recipes.append({
            'name': "Simple Mixed Bowl",
            'ingredients': [
                *foods,
                "Olive oil or butter",
                "Your favorite seasonings (salt, pepper, herbs)",
                "Optional: garlic, lemon juice, or vinegar for extra flavor"
            ],
            'instructions': [
                "Prepare all ingredients to appropriate sizes (chop vegetables, cook proteins if needed).",
                "Heat oil or butter in a large pan over medium heat.",
                "Add ingredients that take longest to cook first.",
                "Season with your favorite spices and herbs.",
                "Continue adding ingredients in order of cooking time.",
                "Toss everything together until well combined and heated through.",
                "Adjust seasoning to taste and serve hot."
            ]
        })
    
    return jsonify({
        'success': True,
        'meal_name': meal_name,
        'recipes': recipes
    })
@bp.route('/delete-dietary-data/<int:data_id>', methods=['POST'])
@login_required
def delete_dietary_data(data_id):
    """Delete a dietary data entry."""
    data_entry = UserDietaryData.query.get_or_404(data_id)
    
    # Only allow deletion if the entry belongs to the current user
    if data_entry.user_id != current_user.id:
        abort(403)
        
    # Save the date for flash message
    entry_date = data_entry.date.strftime('%Y-%m-%d')
     
    db.session.delete(data_entry)
    db.session.commit()
    
    flash(f'Data（{entry_date}）is removed successfully', 'success')
    return redirect(url_for('routes.visualize_data'))