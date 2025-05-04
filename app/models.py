from app import db
from flask_login import UserMixin
from datetime import datetime
import json

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
    
    def get_meals(self):
        return json.loads(self.meals)
    
    def set_meals(self, meal_data):
        self.meals = json.dumps(meal_data)
    
    def __repr__(self):
        return f'<MealPlan {self.name} for {self.user_id}>'
