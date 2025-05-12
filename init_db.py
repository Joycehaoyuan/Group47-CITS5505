import os
import sys
from app import app, db
from app.models import User, Food, MealPlan, UserDietaryData, SharedData, Recipe, RecipeIngredient
from app.utils import populate_initial_food_data
from sqlalchemy import inspect

# add the app directory to the python path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# ensure the instance directory exists
instance_dir = 'instance'
if not os.path.exists(instance_dir):
    os.makedirs(instance_dir)
    print(f"Created instance directory: {instance_dir}")

# use the app context
with app.app_context():
    print("Creating database tables...")
    db.create_all()
    print("Database tables created successfully!")
    
    # check if the food table is empty and populate initial data
    food_count = Food.query.count()
    print(f"Current food count: {food_count}")
    
    if food_count == 0:
        print("Populating initial food data...")
        populate_initial_food_data()
        new_count = Food.query.count()
        print(f"Food data populated! Now have {new_count} food items.")
    else:
        print("Food data already exists, skipping population.")
    
    # use inspect to list all tables
    inspector = inspect(db.engine)
    table_names = inspector.get_table_names()
    print("Created tables:", table_names)

    # list the record counts of the tables
    print("\nTable record counts:")
    print(f"User: {User.query.count()}")
    print(f"Food: {Food.query.count()}")
    print(f"MealPlan: {MealPlan.query.count()}")
    print(f"UserDietaryData: {UserDietaryData.query.count()}")
    print(f"SharedData: {SharedData.query.count()}")
    print(f"Recipe: {Recipe.query.count()}")
    print(f"RecipeIngredient: {RecipeIngredient.query.count()}")

    # check the sample data in the food table
    if Food.query.count() > 0:
        print("\nSample food items:")
        sample_foods = Food.query.limit(5).all()
        for food in sample_foods:
            print(f" - {food.name}: {food.calories} cal, P:{food.protein}g, C:{food.carbs}g, F:{food.fat}g")