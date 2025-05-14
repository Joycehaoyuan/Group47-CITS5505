import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

pytestmark = pytest.mark.selenium

def test_meal_plan_page_loads(browser, live_server):
    """Test whether the menu page is loaded correctly"""
    browser.get(f"{live_server}/meal-plan")
    assert "Meal Plan" in browser.title 