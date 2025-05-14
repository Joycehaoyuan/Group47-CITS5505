import json
from app import db
from app.models import MealPlan, User

def test_meal_plan_refresh_success(client, app):
    with app.app_context():
        user = User.query.filter_by(username='testuser').first()
        meal_plan = MealPlan(
            user_id=user.id,
            diet_type='balanced',
            target_calories=2000,
            meal_count=3,
            meals=json.dumps([
                {"name": "Breakfast", "items": ["Eggs"]},
                {"name": "Lunch", "items": ["Rice"]},
                {"name": "Dinner", "items": ["Soup"]}
            ])
        )
        db.session.add(meal_plan)
        db.session.commit()

    # Login
    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass'
    })

    response = client.post('/meal-plan', json={
        'meal_plan_id': meal_plan.id,
        'meal_index': 1
    })

    assert response.status_code == 200
    assert response.json['success'] is True
    assert 'meal' in response.json
