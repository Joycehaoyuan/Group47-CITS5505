import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

pytestmark = pytest.mark.selenium

@pytest.mark.no_auto_login
def test_registration_flow(live_server, browser):
    """Verify whether the registration process is working properly"""
    try:
        # Ensure user is logged out
        browser.get(f"{live_server}/logout")
        print("Navigated to logout page")
        
        # Wait for redirection to complete
        WebDriverWait(browser, 10).until(
            EC.url_contains("/login")
        )
        print("Successfully redirected to login page")
        
        # Visit registration page
        browser.get(f"{live_server}/register")
        print("Navigated to register page")
        
        # Print current page source for debugging
        print("Current page source:", browser.page_source)
        
        # Wait for form to load
        form = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "form"))
        )
        print("Form found")
        
        # Fill in the form
        username_field = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.NAME, "username"))
        )
        username_field.clear()
        username_field.send_keys("uiuser2")
        print("Username entered")
        
        email_field = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.NAME, "email"))
        )
        email_field.clear()
        email_field.send_keys("ui2@example.com")
        print("Email entered")
        
        password_field = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.NAME, "password"))
        )
        password_field.clear()
        password_field.send_keys("Passw0rd!")
        print("Password entered")
        
        password_confirm_field = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.NAME, "password_confirm"))
        )
        password_confirm_field.clear()
        password_confirm_field.send_keys("Passw0rd!")
        print("Password confirmation entered")
        
        # Wait and click submit button
        submit_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type=submit], button[type=submit], .btn-primary"))
        )
        print("Submit button found")
        
        # Ensure button is in view
        browser.execute_script("arguments[0].scrollIntoView(true);", submit_button)
        time.sleep(1)
        
        # Try clicking the button
        try:
            submit_button.click()
            print("Submit button clicked")
        except Exception as e:
            print(f"Regular click failed: {str(e)}")
            # If regular click fails, try using JavaScript to click
            browser.execute_script("arguments[0].click();", submit_button)
            print("JavaScript click executed")
        
        # Wait for success message
        WebDriverWait(browser, 10).until(
            EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Your account has been created")
        )
        print("Success message found")
        
    except TimeoutException as e:
        print(f"Timeout occurred: {str(e)}")
        print("Current URL:", browser.current_url)
        print("Page source:", browser.page_source)
        raise
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        print("Current URL:", browser.current_url)
        print("Page source:", browser.page_source)
        raise

@pytest.mark.no_auto_login
def test_login_flow(live_server, browser):
    """Verify whether the login process is working properly"""
    try:
        # Visit login page
        browser.get(f"{live_server}/login")
        print("Navigated to login page")
        
        # Wait for form to load
        form = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "form"))
        )
        print("Form found")
        
        # Fill in the form
        username_field = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.NAME, "username"))
        )
        username_field.clear()
        username_field.send_keys("uiuser")
        print("Username entered")
        
        password_field = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.NAME, "password"))
        )
        password_field.clear()
        password_field.send_keys("Passw0rd!")
        print("Password entered")
        
        # Wait and click submit button
        submit_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type=submit], button[type=submit], .btn-primary"))
        )
        print("Submit button found")
        
        # Ensure button is in view
        browser.execute_script("arguments[0].scrollIntoView(true);", submit_button)
        time.sleep(1)
        
        # Try clicking the button
        try:
            submit_button.click()
            print("Submit button clicked")
        except Exception as e:
            print(f"Regular click failed: {str(e)}")
            browser.execute_script("arguments[0].click();", submit_button)
            print("JavaScript click executed")
        
        # Wait for success message and navbar
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "navbar"))
        )
        print("Login successful")
        
    except TimeoutException as e:
        print(f"Timeout occurred: {str(e)}")
        print("Current URL:", browser.current_url)
        print("Page source:", browser.page_source)
        raise
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        print("Current URL:", browser.current_url)
        print("Page source:", browser.page_source)
        raise

@pytest.mark.no_auto_login
def test_invalid_login(live_server, browser):
    """Verify that invalid login attempts are handled properly"""
    try:
        # Visit login page
        browser.get(f"{live_server}/login")
        print("Navigated to login page")
        
        # Wait for form to load
        form = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "form"))
        )
        print("Form found")
        
        # Fill in the form with invalid credentials
        username_field = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.NAME, "username"))
        )
        username_field.clear()
        username_field.send_keys("nonexistent")
        print("Invalid username entered")
        
        password_field = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.NAME, "password"))
        )
        password_field.clear()
        password_field.send_keys("wrongpassword")
        print("Invalid password entered")
        
        # Wait and click submit button
        submit_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type=submit], button[type=submit], .btn-primary"))
        )
        print("Submit button found")
        
        # Ensure button is in view
        browser.execute_script("arguments[0].scrollIntoView(true);", submit_button)
        time.sleep(1)
        
        # Try clicking the button
        try:
            submit_button.click()
            print("Submit button clicked")
        except Exception as e:
            print(f"Regular click failed: {str(e)}")
            browser.execute_script("arguments[0].click();", submit_button)
            print("JavaScript click executed")
        
        # Wait for error message
        WebDriverWait(browser, 10).until(
            EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Login failed")
        )
        print("Error message found")
        
        # Verify we're still on the login page
        assert "/login" in browser.current_url
        print("Still on login page")
        
    except TimeoutException as e:
        print(f"Timeout occurred: {str(e)}")
        print("Current URL:", browser.current_url)
        print("Page source:", browser.page_source)
        raise
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        print("Current URL:", browser.current_url)
        print("Page source:", browser.page_source)
        raise
