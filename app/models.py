from app import db
from flask_login import UserMixin
from datetime import datetime
import json

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)

    preferred_diet_type = db.Column(db.String(30), default='Anything')
    daily_calorie_target = db.Column(db.Integer, default=2000)
    preferred_meal_count = db.Column(db.Integer, default=3)
    
    # Relationships
    meal_plans = db.relationship('MealPlan', backref='user', lazy=True)
    dietary_data = db.relationship('UserDietaryData', backref='user', lazy=True)
    shared_by_me = db.relationship('SharedData', 
                                  foreign_keys='SharedData.owner_id',
                                  backref='owner', 
                                  lazy=True)
    shared_with_me = db.relationship('SharedData', 
                                    foreign_keys='SharedData.recipient_id',
                                    backref='recipient', 
                                    lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

class Food(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    calories = db.Column(db.Integer, nullable=False)
    protein = db.Column(db.Float, nullable=False)  # in grams
    carbs = db.Column(db.Float, nullable=False)    # in grams
    fat = db.Column(db.Float, nullable=False)      # in grams
    serving_size = db.Column(db.String(30), nullable=False)
    diet_types = db.Column(db.String(100), nullable=False)  # Comma separated diet types this food belongs to
    meal_type = db.Column(db.String(50), default='any')  # 'breakfast', 'lunch', 'dinner', 'snack', 'any'
    
    def __repr__(self):
        return f'<Food {self.name}>'
    
    def is_suitable_for_diet(self, diet_type):
        if diet_type.lower() == 'anything':
            return True
        return diet_type.lower() in self.diet_types.lower()

class MealPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), default="My Meal Plan")
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    diet_type = db.Column(db.String(30), nullable=False)
    target_calories = db.Column(db.Integer, nullable=False)
    meal_count = db.Column(db.Integer, nullable=False)
    meals = db.Column(db.Text, nullable=False)  # JSON serialized meal data
    
    def get_meals(self):
        return json.loads(self.meals)
    
    def set_meals(self, meal_data):
        self.meals = json.dumps(meal_data)
    
    def __repr__(self):
        return f'<MealPlan {self.name} for {self.user_id}>'

class UserDietaryData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    meals_json = db.Column(db.Text, nullable=False)  # JSON serialized meals
    calories = db.Column(db.Integer, nullable=False)
    protein = db.Column(db.Float, nullable=False)
    carbs = db.Column(db.Float, nullable=False)
    fat = db.Column(db.Float, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_meals(self):
        return json.loads(self.meals_json)
    
    def set_meals(self, meals_data):
        self.meals_json = json.dumps(meals_data)
    
    def __repr__(self):
        return f'<UserDietaryData {self.date} for {self.user_id}>'

class SharedData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    data_type = db.Column(db.String(20), nullable=False)  # 'meal_plan' or 'dietary_data'
    data_id = db.Column(db.Integer, nullable=False)
    share_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<SharedData {self.data_type} from {self.owner_id} to {self.recipient_id}>'
        
class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    ingredients = db.Column(db.Text, nullable=False)  # JSON serialized ingredients list
    instructions = db.Column(db.Text, nullable=False)  # JSON serialized instructions
    meal_type = db.Column(db.String(50), default='any')  # breakfast, lunch, dinner, dessert, any
    diet_types = db.Column(db.String(200), nullable=False)  # Comma separated diet types
    prep_time = db.Column(db.Integer, nullable=True)  # in minutes
    cook_time = db.Column(db.Integer, nullable=True)  # in minutes
    calories_per_serving = db.Column(db.Integer, nullable=True)
    servings = db.Column(db.Integer, default=4)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    image_url = db.Column(db.String(500), nullable=True)
    rating = db.Column(db.Float, default=0.0)
    rating_count = db.Column(db.Integer, default=0)
    difficulty = db.Column(db.String(20), default='medium')
    is_featured = db.Column(db.Boolean, default=False)
    
    def get_ingredients(self):
        return json.loads(self.ingredients)
        
    def set_ingredients(self, ingredients_list):
        self.ingredients = json.dumps(ingredients_list)
        
    def get_instructions(self):
        return json.loads(self.instructions)
        
    def set_instructions(self, instructions_list):
        self.instructions = json.dumps(instructions_list)
    
    def __repr__(self):
        return f'<Recipe {self.name}>'
        
class RecipeIngredient(db.Model):
    """Table to facilitate many-to-many relationship between recipes and foods"""
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, nullable=False)
    food_name = db.Column(db.String(100), nullable=False)
    
    def __repr__(self):
        return f'<RecipeIngredient {self.food_name} for recipe {self.recipe_id}>'
