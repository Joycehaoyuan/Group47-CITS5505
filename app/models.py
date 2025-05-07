from app import db
from flask_login import UserMixin
from datetime import datetime
import json

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


# Relationships
meal_plans = db.relationship('MealPlan', backref='user', lazy=True)
class MealPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), default="My Meal Plan")
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    diet_type = db.Column(db.String(30), nullable=False)
    target_calories = db.Column(db.Integer, nullable=False)
    meal_count = db.Column(db.Integer, nullable=False)
    meals = db.Column(db.Text, nullable=False)  # JSON serialized meal data

class SharedData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    data_type = db.Column(db.String(20), nullable=False)  # 'meal_plan' or 'dietary_data'
    data_id = db.Column(db.Integer, nullable=False)
    share_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<SharedData {self.data_type} from {self.owner_id} to {self.recipient_id}>'
    
    def get_meals(self):
        return json.loads(self.meals)
    
    def set_meals(self, meal_data):
        self.meals = json.dumps(meal_data)
    
    def __repr__(self):
        return f'<MealPlan {self.name} for {self.user_id}>'
