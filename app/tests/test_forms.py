import pytest
from app.forms import RegistrationForm
from app.models import User

def test_registration_form_valid():
    form = RegistrationForm(
        username="testuser",
        email="test@example.com",
        password="password123",
        password_confirm="password123"
    )
    assert form.validate() is True

def test_registration_form_invalid_email():
    form = RegistrationForm(
        username="testuser",
        email="invalid-email",
        password="password123",
        password_confirm="password123"
    )
    assert form.validate() is False