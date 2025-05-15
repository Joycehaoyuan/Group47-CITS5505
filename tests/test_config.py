import pytest
from app import create_app

# Global configuration or plugin initialization
@pytest.fixture(scope='session', autouse=True)
def configure_env(monkeypatch):
    monkeypatch.setenv('FLASK_ENV', 'development')
    monkeypatch.setenv('TESTING', 'True')

@pytest.fixture(scope='session')
def app_config():
    app = create_app()
    return app.config
