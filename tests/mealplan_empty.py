import json
from app.models import User, MealPlan
from app import db

def test_refresh_empty_meal_items(client, app):
    with app.app_context():
        user = User.query.first()
        plan = MealPlan(
            user_id=user.id,
            diet_type='keto',
            target_calories=1500,
            meal_count=3,
            meals=json.dumps([
                {"name": "Breakfast", "items": []},
                {"name": "Lunch", "items": []},
                {"name": "Dinner", "items": []}
            ])
        )
        db.session.add(plan)
        db.session.commit()

    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
    response = client.post('/meal-plan', json={'meal_plan_id': plan.id, 'meal_index': 0})
    assert response.status_code == 200
    assert response.json['success']
