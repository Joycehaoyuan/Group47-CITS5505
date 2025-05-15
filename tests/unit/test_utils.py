import pytest
from app import db
from app.models import Food
from app.utils import generate_meal_plan, populate_initial_food_data

def test_generate_meal_plan_length(app):
    with app.app_context():
        plan = generate_meal_plan(diet_type='Anything', target_calories=2000, meal_count=4)
        assert isinstance(plan, list)
        assert len(plan) == 4

