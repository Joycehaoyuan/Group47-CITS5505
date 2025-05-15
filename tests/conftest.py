
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
import os
import time
import pytest
from threading import Thread
from app import create_app, db
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup



def pytest_addoption(parser):
    parser.addini("selenium", "mark tests that require a live browser")

def pytest_configure(config):
    config.addinivalue_line(
        "markers", "selenium: mark test to run with selenium"
    )
    config.addinivalue_line(
        "markers", "no_auto_login: mark test to skip auto login"
    )



@pytest.fixture(scope="session")
def app():
    """Create and configure a new app instance for all tests."""
    cfg = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_I18N_ENABLED": False,
        "UPLOAD_FOLDER": "test_uploads",
        "MAX_CONTENT_LENGTH": 16 * 1024 * 1024,
        "SECRET_KEY": "test-secret-key",
        "WTF_CSRF_ENABLED": False
    }
    app = create_app(cfg)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
        # Clean up test upload folder
        import shutil
        if os.path.exists(app.config['UPLOAD_FOLDER']):
            shutil.rmtree(app.config['UPLOAD_FOLDER'])

@pytest.fixture(scope="session")
def client(app):
    """A Flask test client."""
    return app.test_client()


@pytest.fixture(scope="session")
def live_server(app):
    """Start the Flask dev server in a background thread."""
    def run():
        app.run(port=5001, use_reloader=False)
    thread = Thread(target=run, daemon=True)
    thread.start()
    time.sleep(1)
    yield "http://localhost:5001"


@pytest.fixture(scope="session")
def browser():
    """Start a headless Chrome for Selenium tests."""
    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=opts)
    yield driver
    driver.quit()



@pytest.fixture(autouse=True)
def auto_login(request, live_server, browser, client):
    """
    For any test marked with @pytest.mark.selenium,
    perform a shared login before running the test body.
    """
    if "no_auto_login" in request.keywords:
        return
    if "selenium" in request.keywords:
        try:
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.common.exceptions import TimeoutException
            
            # Register the test user
            client.post("/register", data={
                "username": "uiuser",
                "email": "ui@example.com",
                "password": "Passw0rd!",
                "password_confirm": "Passw0rd!"
            })
            
            # Login with the test user
            browser.get(f"{live_server}/login")
            
            # Wait for the form to be present
            wait = WebDriverWait(browser, 10)
            form = wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "form"))
            )
            
            # Fill in the login form
            username_field = wait.until(
                EC.element_to_be_clickable((By.NAME, "username"))
            )
            username_field.clear()
            username_field.send_keys("uiuser")
            
            password_field = wait.until(
                EC.element_to_be_clickable((By.NAME, "password"))
            )
            password_field.clear()
            password_field.send_keys("Passw0rd!")
            
            # Submit the form
            submit_button = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type=submit], button[type=submit]"))
            )
            submit_button.click()
            
            # Wait for successful login by checking for navbar
            wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "navbar"))
            )
            
        except Exception as e:
            print(f"\nError details: {str(e)}")
            print("\nPage source at time of error:")
            print(browser.page_source)
            pytest.fail(f"Auto login failed: {str(e)}")
   

@pytest.fixture
def auth_headers(client):
    """Return JSON headers after logging in (useful for API tests)."""
    client.post("/register", data={
        "username": "apiuser",
        "email": "api@example.com",
        "password": "Passw0rd!",
        "password_confirm": "Passw0rd!"
    })
    client.post("/login", data={"username": "apiuser", "password": "Passw0rd!"})
    return {"Content-Type": "application/json"}