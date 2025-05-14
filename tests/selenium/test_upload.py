import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

pytestmark = [pytest.mark.selenium, pytest.mark.no_auto_login]

def test_upload_page_loads(browser, live_server):
    """Test whether the upload page loads correctly"""
    # Access upload page directly
    browser.get(f"{live_server}/upload-data")
    
    # Check page title
    assert "Upload Nutrition Data" in browser.title
    
    # Check if form elements are present
    form = browser.find_element(By.TAG_NAME, "form")
    assert form is not None, "Form element not found"
    
    # Check if basic form fields exist
    assert browser.find_element(By.NAME, "date") is not None
    assert browser.find_element(By.NAME, "calories") is not None
    assert browser.find_element(By.NAME, "protein") is not None
    assert browser.find_element(By.NAME, "carbs") is not None
    assert browser.find_element(By.NAME, "fat") is not None
