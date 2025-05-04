from flask import Blueprint, render_template

bp = Blueprint('routes', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

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
