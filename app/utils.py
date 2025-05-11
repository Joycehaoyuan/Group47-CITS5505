from app import db
from models import Food
import random
import math
from datetime import datetime, timedelta

def populate_initial_food_data():
    """Populate the database with initial food data if it's empty."""
    # Drop existing food data
    Food.query.delete()
    
    # Define some sample foods for different diet types
    # Format: name, calories, protein, carbs, fat, serving_size, diet_types, meal_type
    sample_foods = [
        # BREAKFAST ITEMS
        # ---------------
        ('Scrambled Eggs', 155, 13, 1.1, 11, '100g', 'anything,keto,paleo,mediterranean,vegetarian', 'breakfast'),
        ('Oatmeal with Honey', 170, 5, 30, 3, '200g', 'anything,vegan,vegetarian', 'breakfast'),
        ('Greek Yogurt with Berries', 150, 15, 12, 4, '200g', 'anything,vegetarian,mediterranean', 'breakfast'),
        ('Avocado Toast', 260, 8, 22, 15, '1 serving', 'anything,vegan,vegetarian', 'breakfast'),
        ('Breakfast Burrito', 380, 15, 40, 18, '1 burrito', 'anything,vegetarian', 'breakfast'),
        ('Pancakes with Maple Syrup', 350, 8, 60, 9, '3 pancakes', 'anything,vegetarian', 'breakfast'),
        ('Bacon and Eggs', 300, 20, 2, 22, '2 eggs & 3 strips', 'anything,keto,paleo', 'breakfast'),
        ('Fruit Smoothie Bowl', 280, 8, 50, 6, '300ml', 'anything,vegan,vegetarian', 'breakfast'),
        ('Keto Breakfast Bowl', 450, 30, 5, 35, '250g', 'anything,keto', 'breakfast'),
        ('Overnight Chia Pudding', 220, 7, 25, 12, '200g', 'anything,vegan,vegetarian', 'breakfast'),
        ('Vegetable Frittata', 280, 18, 8, 18, '200g', 'anything,keto,vegetarian', 'breakfast'),
        ('Breakfast Smoothie', 220, 15, 30, 5, '300ml', 'anything,vegetarian,vegan', 'breakfast'),
        ('Croissant with Jam', 290, 5, 32, 16, '1 croissant', 'anything,vegetarian', 'breakfast'),
        ('English Breakfast', 550, 25, 30, 35, '1 plate', 'anything', 'breakfast'),
        ('Protein Pancakes', 340, 25, 30, 10, '3 pancakes', 'anything,vegetarian', 'breakfast'),
        ('Breakfast Hash', 320, 15, 35, 15, '250g', 'anything,vegetarian', 'breakfast'),
        ('Breakfast Sandwich', 380, 18, 35, 18, '1 sandwich', 'anything', 'breakfast'),
        ('Paleo Breakfast Bowl', 350, 25, 15, 20, '250g', 'anything,paleo', 'breakfast'),
        ('Vegan Breakfast Burritos', 320, 12, 45, 10, '1 burrito', 'anything,vegan,vegetarian', 'breakfast'),
        ('Mediterranean Breakfast Plate', 400, 15, 30, 25, '1 plate', 'anything,mediterranean,vegetarian', 'breakfast'),
        
        # LUNCH ITEMS
        # -----------
        ('Chicken Caesar Salad', 320, 25, 10, 20, '250g', 'anything', 'lunch'),
        ('Tuna Sandwich', 350, 25, 30, 15, '1 sandwich', 'anything', 'lunch'),
        ('Vegetable Soup', 180, 5, 25, 6, '300ml', 'anything,vegan,vegetarian', 'lunch'),
        ('Turkey Wrap', 320, 20, 35, 12, '1 wrap', 'anything', 'lunch'),
        ('Quinoa Bowl', 380, 12, 50, 14, '300g', 'anything,vegan,vegetarian', 'lunch'),
        ('Greek Salad', 300, 10, 12, 22, '250g', 'anything,mediterranean,vegetarian', 'lunch'),
        ('Beef and Vegetable Stir Fry', 380, 30, 20, 18, '300g', 'anything,paleo', 'lunch'),
        ('Hummus and Vegetable Wrap', 350, 12, 45, 12, '1 wrap', 'anything,vegan,vegetarian,mediterranean', 'lunch'),
        ('Poke Bowl', 450, 30, 45, 15, '350g', 'anything', 'lunch'),
        ('Lentil Soup', 220, 12, 30, 5, '300ml', 'anything,vegan,vegetarian,mediterranean', 'lunch'),
        ('Caprese Sandwich', 380, 15, 35, 18, '1 sandwich', 'anything,vegetarian,mediterranean', 'lunch'),
        ('Chicken Burrito Bowl', 450, 30, 50, 10, '350g', 'anything', 'lunch'),
        ('Mediterranean Plate', 420, 18, 40, 20, '300g', 'anything,mediterranean,vegetarian', 'lunch'),
        ('Sushi Roll Combo', 400, 20, 60, 8, '8 pieces', 'anything', 'lunch'),
        ('Falafel Plate', 450, 15, 50, 20, '300g', 'anything,vegan,vegetarian,mediterranean', 'lunch'),
        ('Keto Lunch Box', 480, 35, 8, 35, '300g', 'anything,keto', 'lunch'),
        ('BLT Sandwich', 380, 15, 35, 20, '1 sandwich', 'anything', 'lunch'),
        ('Cobb Salad', 450, 30, 10, 30, '300g', 'anything,keto', 'lunch'),
        ('Vegetarian Buddha Bowl', 380, 15, 50, 12, '350g', 'anything,vegan,vegetarian', 'lunch'),
        ('Italian Panini', 420, 18, 40, 22, '1 sandwich', 'anything,vegetarian', 'lunch'),
        ('Salmon Poke Bowl', 420, 30, 40, 15, '300g', 'anything', 'lunch'),
        ('Mediterranean Couscous Bowl', 380, 12, 55, 14, '300g', 'anything,vegetarian,mediterranean', 'lunch'),
        
        # DINNER ITEMS
        # ------------
        ('Grilled Salmon with Asparagus', 320, 30, 5, 18, '250g', 'anything,keto,paleo,mediterranean', 'dinner'),
        ('Spaghetti Bolognese', 450, 25, 60, 12, '300g', 'anything', 'dinner'),
        ('Tofu Stir Fry with Vegetables', 280, 15, 20, 14, '300g', 'anything,vegan,vegetarian', 'dinner'),
        ('Beef Steak with Vegetables', 420, 35, 10, 25, '300g', 'anything,keto,paleo', 'dinner'),
        ('Vegetable Curry with Rice', 400, 10, 60, 15, '350g', 'anything,vegan,vegetarian', 'dinner'),
        ('Grilled Chicken with Quinoa', 350, 30, 25, 12, '300g', 'anything,paleo', 'dinner'),
        ('Mediterranean Seafood Platter', 380, 30, 15, 20, '300g', 'anything,mediterranean', 'dinner'),
        ('Vegan Pasta Primavera', 380, 12, 60, 10, '300g', 'anything,vegan,vegetarian', 'dinner'),
        ('Keto Beef Bowl', 450, 35, 8, 30, '300g', 'anything,keto', 'dinner'),
        ('Paleo Chicken and Sweet Potato', 380, 30, 25, 15, '300g', 'anything,paleo', 'dinner'),
        ('Mediterranean Lamb with Salad', 420, 30, 15, 25, '300g', 'anything,mediterranean', 'dinner'),
        ('Vegetarian Lasagna', 420, 18, 50, 18, '300g', 'anything,vegetarian', 'dinner'),
        ('Grilled Fish Tacos', 380, 25, 35, 15, '2 tacos', 'anything', 'dinner'),
        ('Chicken Parmesan', 450, 35, 25, 22, '300g', 'anything', 'dinner'),
        ('Stuffed Bell Peppers', 320, 20, 30, 12, '300g', 'anything,vegetarian', 'dinner'),
        ('Beef Teriyaki with Rice', 450, 30, 50, 12, '350g', 'anything', 'dinner'),
        ('Vegan Buddha Bowl', 350, 15, 45, 15, '350g', 'anything,vegan,vegetarian', 'dinner'),
        ('Eggplant Parmesan', 380, 15, 30, 22, '300g', 'anything,vegetarian,mediterranean', 'dinner'),
        ('Salmon with Lemon-Dill Sauce', 350, 30, 5, 22, '250g', 'anything,keto,mediterranean', 'dinner'),
        ('Beef Bourguignon', 420, 35, 15, 25, '300g', 'anything', 'dinner'),
        
        # SNACKS
        # ------
        ('Mixed Nuts', 200, 6, 8, 18, '30g', 'anything,keto,paleo,vegan,vegetarian', 'snack'),
        ('Greek Yogurt with Honey', 120, 10, 15, 2, '100g', 'anything,vegetarian,mediterranean', 'snack'),
        ('Apple with Peanut Butter', 170, 5, 20, 8, '1 apple + 1 tbsp', 'anything,vegetarian', 'snack'),
        ('Protein Bar', 200, 15, 20, 8, '1 bar', 'anything,vegetarian', 'snack'),
        ('Vegetable Sticks with Hummus', 150, 5, 15, 8, '100g', 'anything,vegan,vegetarian,mediterranean', 'snack'),
        ('Cheese and Crackers', 180, 8, 15, 10, '30g cheese + crackers', 'anything,vegetarian', 'snack'),
        ('Trail Mix', 200, 6, 15, 15, '30g', 'anything,vegetarian,paleo', 'snack'),
        ('Fresh Fruit Cup', 100, 1, 25, 0, '150g', 'anything,vegan,vegetarian,paleo', 'snack'),
        ('Dark Chocolate Square', 80, 1, 6, 5, '15g', 'anything,vegetarian,vegan', 'snack'),
        ('Beef Jerky', 150, 25, 2, 5, '40g', 'anything,keto,paleo', 'snack'),
        ('Avocado on Rice Cake', 160, 2, 12, 12, '1/2 avocado + 2 cakes', 'anything,vegan,vegetarian', 'snack'),
        ('Edamame', 120, 10, 10, 5, '100g', 'anything,vegan,vegetarian', 'snack'),
        ('Keto Fat Bombs', 120, 2, 1, 12, '2 pieces', 'anything,keto,vegetarian', 'snack'),
        ('Overnight Chia Pudding', 150, 5, 15, 8, '100g', 'anything,vegan,vegetarian', 'snack'),
        ('Hard-Boiled Eggs', 140, 12, 1, 10, '2 eggs', 'anything,keto,paleo,vegetarian', 'snack'),
        
        # GENERIC ITEMS (can be used in multiple meal types)
        # -------------------------------------------------
        ('Chicken Breast', 165, 31, 0, 3.6, '100g', 'anything,paleo,mediterranean', 'any'),
        ('Salmon', 206, 22, 0, 13, '100g', 'anything,keto,paleo,mediterranean', 'any'),
        ('Eggs', 155, 13, 1.1, 11, '100g', 'anything,keto,paleo,mediterranean,vegetarian', 'any'),
        ('Spinach', 23, 2.9, 3.6, 0.4, '100g', 'anything,keto,paleo,mediterranean,vegan,vegetarian', 'any'),
        ('Avocado', 160, 2, 8.5, 14.7, '100g', 'anything,keto,paleo,mediterranean,vegan,vegetarian', 'any'),
        ('Olive Oil', 119, 0, 0, 13.5, '1 tbsp', 'anything,keto,paleo,mediterranean,vegan,vegetarian', 'any'),
        ('Almonds', 579, 21, 21.6, 49.9, '100g', 'anything,paleo,mediterranean,vegan,vegetarian', 'any'),
        ('Bacon', 417, 13, 1.4, 42, '100g', 'anything,keto', 'any'),
        ('Butter', 717, 0.9, 0.1, 81, '100g', 'anything,keto,vegetarian', 'any'),
        ('Cheddar Cheese', 403, 25, 1.3, 33, '100g', 'anything,keto,vegetarian', 'any'),
        ('Tofu', 76, 8, 1.9, 4.8, '100g', 'anything,vegan,vegetarian,mediterranean', 'any'),
        ('Tempeh', 193, 20.3, 7.6, 10.8, '100g', 'anything,vegan,vegetarian', 'any'),
        ('Lentils', 116, 9, 20, 0.4, '100g', 'anything,mediterranean,vegan,vegetarian', 'any'),
        ('Quinoa', 120, 4.4, 21.3, 1.9, '100g', 'anything,mediterranean,vegan,vegetarian', 'any'),
        ('Greek Yogurt', 59, 10, 3.6, 0.4, '100g', 'anything,mediterranean,vegetarian', 'any'),
        ('Feta Cheese', 264, 14.2, 4.1, 21.3, '100g', 'anything,mediterranean,vegetarian', 'any'),
        ('Hummus', 166, 7.9, 14.3, 9.6, '100g', 'anything,mediterranean,vegan,vegetarian', 'any'),
        ('Sweet Potato', 86, 1.6, 20.1, 0.1, '100g', 'anything,paleo,vegan,vegetarian', 'any'),
        ('Grass-Fed Beef', 250, 26, 0, 17, '100g', 'anything,paleo,keto', 'any'),
        ('Brown Rice', 112, 2.6, 23.5, 0.9, '100g', 'anything,vegan,vegetarian', 'any'),
        ('Oatmeal', 68, 2.4, 12, 1.4, '100g', 'anything,vegan,vegetarian', 'any'),
        ('Banana', 89, 1.1, 22.8, 0.3, '100g', 'anything,vegan,vegetarian', 'any'),
        ('Apple', 52, 0.3, 13.8, 0.2, '100g', 'anything,paleo,vegan,vegetarian', 'any'),
        ('Broccoli', 34, 2.8, 6.6, 0.4, '100g', 'anything,keto,paleo,mediterranean,vegan,vegetarian', 'any'),
        ('Strawberries', 32, 0.7, 7.7, 0.3, '100g', 'anything,paleo,vegan,vegetarian', 'any'),
        ('Peanut Butter', 588, 25, 20, 50, '100g', 'anything,vegetarian', 'any'),
        ('Whole Wheat Bread', 247, 13, 41, 3.4, '100g', 'anything,vegetarian,vegan', 'any'),
    ]
    
    # Add foods to database
    for food_data in sample_foods:
        food = Food(
            name=food_data[0],
            calories=food_data[1],
            protein=food_data[2],
            carbs=food_data[3],
            fat=food_data[4],
            serving_size=food_data[5],
            diet_types=food_data[6],
            meal_type=food_data[7]
        )
        db.session.add(food)
    
    db.session.commit()
    print("Initial food data populated!")

def recommend_macros(calories):
    """Calculate recommended macronutrients based on calorie intake."""
    # Default balanced macros: 30% protein, 40% carbs, 30% fat
    protein_cal = calories * 0.3
    carbs_cal = calories * 0.4
    fat_cal = calories * 0.3
    
    # Convert to grams (4 cal/g for protein and carbs, 9 cal/g for fat)
    protein_g = round(protein_cal / 4)
    carbs_g = round(carbs_cal / 4)
    fat_g = round(fat_cal / 9)
    
    return {
        'protein': protein_g,
        'carbs': carbs_g,
        'fat': fat_g
    }

def get_food_by_diet(diet_type, excluded_ids=None, meal_type=None):
    """Get foods suitable for a specific diet type and meal type."""
    if excluded_ids is None:
        excluded_ids = []
    
    query = Food.query
    
    # Filter by diet type
    if diet_type.lower() != 'anything':
        # Find foods that match this diet type (case insensitive)
        query = query.filter(Food.diet_types.ilike(f'%{diet_type.lower()}%'))
    
    # Filter by meal type if specified
    if meal_type:
        # Get foods that are suitable for this meal type or 'any'
        query = query.filter((Food.meal_type == meal_type) | (Food.meal_type == 'any'))
    
    # Exclude specific food IDs if provided
    if excluded_ids:
        query = query.filter(~Food.id.in_(excluded_ids))
    
    # Return all matching foods
    return query.all()

def generate_meal_plan(diet_type, target_calories, meal_count):
    """Generate a meal plan based on diet type and target calories."""
    # Convert meal_count to int if it's a string
    if isinstance(meal_count, str):
        meal_count = int(meal_count)
    
    # Calculate calories per meal (approximately)
    calories_per_meal = target_calories / meal_count
    
    # Generate meals
    meals = []
    for i in range(meal_count):
        meal_name = ""
        meal_type = "any"  # Default
        
        # Assign meal names and types based on position
        if i == 0:
            meal_name = "Breakfast"
            meal_type = "breakfast"
        elif i == 1:
            meal_name = "Lunch"
            meal_type = "lunch"
        elif i == 2:
            meal_name = "Dinner"
            meal_type = "dinner"
        elif i >= 3 and i <= 4:
            meal_name = f"Snack {i-2}"
            meal_type = "snack"
        else:
            meal_name = f"Meal {i+1}"
            # For additional meals beyond standard meals, we'll alternate
            meal_types = ["breakfast", "lunch", "dinner", "snack"]
            meal_type = meal_types[i % 4]
        
        # Get suitable foods for this meal type and diet
        suitable_foods = get_food_by_diet(diet_type, meal_type=meal_type)
        
        # If not enough suitable foods, try any meal type with this diet
        if len(suitable_foods) < 5:
            suitable_foods = get_food_by_diet(diet_type)
            
        # If still not enough suitable foods, use "anything" diet
        if len(suitable_foods) < 5:
            suitable_foods = get_food_by_diet('anything')
        
        # Slightly vary calories per meal for more realistic distribution
        meal_target_calories = calories_per_meal * random.uniform(0.9, 1.1)
        
        # Generate a meal with target calories
        meal = generate_single_meal(suitable_foods, meal_target_calories, meal_name)
        meals.append(meal)
    
    return meals

def generate_single_meal(food_options, target_calories, meal_name):
    """Generate a single meal with approximately the target calories."""
    selected_foods = []
    current_calories = 0
    current_protein = 0
    current_carbs = 0
    current_fat = 0
    
    # Try to get at least 2-4 food items per meal
    min_items = 2
    max_items = 4
    
    # First, randomly select a "main" food item that's less than the target calories
    suitable_mains = [f for f in food_options if f.calories < target_calories * 0.7]
    
    if suitable_mains:
        main_food = random.choice(suitable_mains)
        portion = 1.0  # Base portion
        
        # Add the main food
        food_item = {
            'id': main_food.id,
            'name': main_food.name,
            'calories': round(main_food.calories * portion),
            'protein': round(main_food.protein * portion, 1),
            'carbs': round(main_food.carbs * portion, 1),
            'fat': round(main_food.fat * portion, 1),
            'serving': f"{portion} {main_food.serving_size}"
        }
        selected_foods.append(food_item)
        
        current_calories += food_item['calories']
        current_protein += food_item['protein']
        current_carbs += food_item['carbs']
        current_fat += food_item['fat']
    
    # Add additional items until we approach the target calories or reach max items
    used_food_ids = [f['id'] for f in selected_foods]
    remaining_options = [f for f in food_options if f.id not in used_food_ids]
    
    # Keep adding foods until we're close to target calories or have enough items
    attempts = 0
    while (current_calories < target_calories * 0.85 and 
           len(selected_foods) < max_items and 
           attempts < 15 and
           remaining_options):
        
        # Select a random food
        food = random.choice(remaining_options)
        
        # Calculate how much of this food to add (adjust portion if needed)
        calories_needed = target_calories - current_calories
        portion = min(1.0, calories_needed / food.calories * random.uniform(0.5, 0.8))
        
        # If portion is too small, try another food
        if portion < 0.2:
            attempts += 1
            remaining_options.remove(food)
            continue
        
        # Add the food with calculated portion
        food_item = {
            'id': food.id,
            'name': food.name,
            'calories': round(food.calories * portion),
            'protein': round(food.protein * portion, 1),
            'carbs': round(food.carbs * portion, 1),
            'fat': round(food.fat * portion, 1),
            'serving': f"{round(portion, 1)} {food.serving_size}"
        }
        
        selected_foods.append(food_item)
        used_food_ids.append(food.id)
        
        current_calories += food_item['calories']
        current_protein += food_item['protein']
        current_carbs += food_item['carbs']
        current_fat += food_item['fat']
        
        # Remove this food from options to avoid duplicates
        remaining_options.remove(food)
        attempts += 1
    
    # Create the meal object
    meal = {
        'name': meal_name,
        'total_calories': current_calories,
        'total_protein': round(current_protein, 1),
        'total_carbs': round(current_carbs, 1),
        'total_fat': round(current_fat, 1),
        'foods': selected_foods
    }
    
    return meal
