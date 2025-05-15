import pytest
from app.forms import RegistrationForm

def test_registration_form_valid(app):
    app.config['WTF_CSRF_ENABLED'] = False
    with app.app_context():
        form = RegistrationForm(data={
            'username': 'abc123',
            'email': 'a@b.com',
            'password': 'Passw0rd!',
            'password_confirm': 'Passw0rd!'
        })
        assert form.validate()

@pytest.mark.parametrize('username', ['inv@lid', 'a'*51])
def test_registration_username_invalid(app, username):
    app.config['WTF_CSRF_ENABLED'] = False
    with app.app_context():
        form = RegistrationForm(data={
            'username': username,
            'email': 'a@b.com',
            'password': 'Passw0rd!',
            'password_confirm': 'Passw0rd!'
        })
        assert not form.validate()
