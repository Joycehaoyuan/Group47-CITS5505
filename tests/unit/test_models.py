import pytest
from app.models import Food, UserDietaryData

def test_food_suitability():
    food = Food(
        name='Test', calories=100, protein=10, carbs=5, fat=5,
        serving_size='100g', diet_types='keto,vegan', meal_type='any'
    )
    assert food.is_suitable_for_diet('Keto')
    assert not food.is_suitable_for_diet('Mediterranean')

def test_user_dietary_serialization():
    data = UserDietaryData(
        user_id=1,
        date='2021-01-01',
        meals_json='[{"name":"A","calories":100}]',
        calories=100, protein=10, carbs=5, fat=5
    )
    meals = data.get_meals()
    assert isinstance(meals, list)
    assert meals[0]['name'] == 'A'