from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


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
            self._begin_resume_course()
            while True: 
                self._go_through_each_course()
                
        finally:
            self._close()
        
    def _go_through_each_course(self):
        print("Going a new course...")
        self._scrape_course_content()
        pass
    I need to scrape this which should be so easy
    <div class="transcript"><p>This is the module on listing requirements and agreements. In this lesson, you will learn about the requirements for listing agreements in New Jersey.</p><p>You have already learned about the different types of listing agreements in the national portion. Before we proceed to requirements that are specific to the state, let’s do a recap on what types of listing agreements are there and what they mean.</p><p>Listing agreements are legally binding contracts that authorize real estate brokerages to perform specific tasks for property owners, such as selling or renting their property.</p><p>The most common and preferred type of listing agreement is the Exclusive Right to Sell agreement. Under this agreement, the property owner authorizes one brokerage as their exclusive agent to sell or rent the property. The brokerage is entitled to compensation regardless of who ultimately finds the buyer or tenant.</p><p>The next option is an Exclusive Agency agreement, where the brokerage receives a commission only if they find the buyer, not if the owner secures the sale themselves.</p><p>Other agreement types include the Open Listing, which is non-exclusive and only pays the broker who produces the buyer, and the Net Listing, where the broker's compensation is the excess amount above an agreed-upon net sale price with the owner. Remember, net listings are illegal in NJ.</p><p>Now, let’s learn about the state specific requirements for listing agreements in the next lesson.</p></div>
    
    def _scrape_course_content(self):
        pass
    
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

    def _begin_resume_course(self):
        # Wait for and click the Resume button
        resume_button = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.course-button[href="/courses/67a2b9e85bb7fdb592a0d8f6"]'))
        )
        resume_button.click()
        print("Resumed course!")
        time.sleep(5)  # Let the user see the course page for a bit

    def _close(self):
        """Close the browser"""
        self.driver.quit()
        pass
        

