import pytest
import json
from app.models import Food, UserDietaryData, Recipe

# Test whether the is_suitable_for_diet method correctly identifies compatible diet types.
def test_food_suitability():
    food = Food(
        name='Test', calories=100, protein=10, carbs=5, fat=5,
        serving_size='100g', diet_types='keto,vegan', meal_type='any'
    )
    assert food.is_suitable_for_diet('Keto')
    assert not food.is_suitable_for_diet('Mediterranean')

# Test whether meals_json is properly deserialized into a list of meal dictionaries.
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

# Fixture-like helper function to create a sample Recipe instance with preset ingredients and instructions.
@pytest.fixture
def sample_recipe():
    test_ingredients = ["Ingredient 1", "Ingredient 2"]
    test_instructions = ["Step 1", "Step 2", "Step 3"]
    
    return Recipe(
        name="Test Recipe",
        description="A test recipe",
        ingredients=json.dumps(test_ingredients),
        instructions=json.dumps(test_instructions),
        meal_type="dinner",
        diet_types="vegetarian,vegan",
        prep_time=15,
        cook_time=30,
        calories_per_serving=250,
        servings=4
    )

# Test whether get_ingredients() correctly returns a list from the serialized JSON.
def test_get_ingredients(sample_recipe):
    ingredients = sample_recipe.get_ingredients()
    assert len(ingredients) == 2
    assert ingredients[0] == "Ingredient 1"
    assert ingredients[1] == "Ingredient 2"

# Test whether set_ingredients() properly updates and stores the new ingredients list.
def test_set_ingredients(sample_recipe):
    new_ingredients = ["New Ingredient 1", "New Ingredient 2", "New Ingredient 3"]
    sample_recipe.set_ingredients(new_ingredients)
    ingredients = sample_recipe.get_ingredients()
    assert len(ingredients) == 3
    assert ingredients[0] == "New Ingredient 1"

# Test whether get_instructions() correctly returns a list from the serialized JSON.
def test_get_instructions(sample_recipe):
    instructions = sample_recipe.get_instructions()
    assert len(instructions) == 3
    assert instructions[0] == "Step 1"
    assert instructions[2] == "Step 3"

# Test whether set_instructions() properly updates and stores the new instructions list.
def test_set_instructions(sample_recipe):
    new_instructions = ["New Step 1", "New Step 2"]
    sample_recipe.set_instructions(new_instructions)
    instructions = sample_recipe.get_instructions()
    assert len(instructions) == 2
    assert instructions[0] == "New Step 1"
