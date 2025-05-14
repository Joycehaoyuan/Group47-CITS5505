import sys
import os
import pytest

sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/.."))

from app import create_app

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
    })
    return app

@pytest.fixture
def client(app):
    return app.test_client()
