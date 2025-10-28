from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class WebsiteDriver:
    def __init__(self, username, password):
        self.driver = webdriver.Chrome()  # or webdriver.Firefox()
        self.username = username
        self.password = password
        self.wait = WebDriverWait(self.driver, 10) 
        self.url = 'https://courses.realestateu.com/login'

    def start_studying(self):
        """Start the studying session by navigating to the site"""
        try:
            self._navigate_to_site()
            self._login(self.username, self.password)
        finally:
            self._close()
        
    
    def _navigate_to_site(self):
        """Navigate to the Real Estate U website"""
        self.driver.get(self.url)

    def _login(self, username, password):
        # Wait for email field and fill it
        email_field = self.wait.until(EC.presence_of_element_located((By.NAME, 'email')))
        email_field.send_keys(username)

        # Find and fill password field
        password_field = self.driver.find_element(By.NAME, 'password')
        password_field.send_keys(password)

        # Find and click login button
        login_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        login_button.click()

        # Wait for successful login
        self.wait.until(EC.url_changes(self.url))

        print("Login successful!")

    def _close(self):
        """Close the browser"""
        self.driver.quit()

