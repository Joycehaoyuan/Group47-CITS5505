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
