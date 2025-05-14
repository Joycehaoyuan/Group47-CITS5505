import json
from app.models import User, MealPlan
from app import db

def test_multiple_refresh_calls(client, app):
    with app.app_context():
        user = User.query.first()
        plan = MealPlan(
            user_id=user.id,
            diet_type='high-protein',
            target_calories=2200,
            meal_count=3,
            meals=json.dumps([
                {"name": "Breakfast", "items": ["Whey"]},
                {"name": "Lunch", "items": ["Beef"]},
                {"name": "Dinner", "items": ["Lentils"]}
            ])
        )
        db.session.add(plan)
        db.session.commit()

    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
    for i in range(3):
        response = client.post('/meal-plan', json={'meal_plan_id': plan.id, 'meal_index': i})
        assert response.status_code == 200
        assert response.json['success']
