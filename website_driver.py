from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import os
import time
import re
from enum import Enum
from handlers import QuizHandler, LessonHandler, ActivityHandler, WalkthroughHandler, InfographicsHandler 

class CourseType(Enum):
    QUIZ = 'quiz'
    LESSON = 'lesson'
    ACTIVITY = 'activity'
    WALKTHROUGH = 'walkthrough'
    WALKTHROUGH_QUESTION = 'walkthrough_question'
    INFOGRAPHICS = 'infographics'
    INTRODDUCTION = 'introduction'

class WebsiteDriver:
    def __init__(self, username, password):
        load_dotenv()
        # Configure Chrome download preferences
        # Get project root directory (same directory as this file)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        download_dir = os.path.join(script_dir, "saved", "infographics")
        os.makedirs(download_dir, exist_ok=True)

        chrome_options = webdriver.ChromeOptions()
        prefs = {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)

        self.driver = webdriver.Chrome(options=chrome_options)
        self.download_dir = download_dir
        
        if not username or not password:
            if os.getenv('USERNAME') and os.getenv('PASSWORD'):
                username = os.getenv('USERNAME')
                password = os.getenv('PASSWORD')
            else:
                raise ValueError("Username and password must be provided either as arguments or in .env file")
        self.username = username
        self.password = password
        self.wait = WebDriverWait(self.driver, 10)
        self.url = 'https://courses.realestateu.com/login'

        # Initialize handlers
        self.quiz_handler = QuizHandler(self.driver, self.wait)
        self.lesson_handler = LessonHandler(self.driver, self.wait)
        self.activity_handler = ActivityHandler(self.driver, self.wait)
        self.walkthrough_handler = WalkthroughHandler(self.driver, self.wait)
        self.infographics_handler = InfographicsHandler(self.driver, self.wait, self.download_dir)

    def start_studying(self):
        """Start the studying session by navigating to the site"""
        try:
            self._navigate_to_site()
            self._login(self.username, self.password)
            self._begin_resume_course()
            while True: 
                self._go_through_each_course()
                time.sleep(3)
                
        finally:
            self._close()
        
    def _go_through_each_course(self):
        print("Going through a new course...")
        self._wait_to_load()
        course_type = self._determine_course_type()
        print(f"Course type determined: {course_type}")
        match course_type:
            case CourseType.QUIZ:
                self.quiz_handler.handle()
            case CourseType.LESSON:
                self.lesson_handler.handle()
                self._keep_going()
            case CourseType.ACTIVITY:
                self.activity_handler.handle()
                self._keep_going()
            case CourseType.WALKTHROUGH:
                self._keep_going()
            case CourseType.INFOGRAPHICS:
                self.infographics_handler.handle()
                self._keep_going()
            case CourseType.WALKTHROUGH_QUESTION:
                self.activity_handler.handle(False)
                self._keep_going()
            case _:
                self._keep_going()
                
        
    def _keep_going(self):
        """Check if there is a next button to continue to the next course"""
        try:
            print("Continuing to next section...")
            resolved = False
            while not resolved:
                time.sleep(5)
                next_button = self.driver.find_element(By.CSS_SELECTOR, 'button.next')
                # Check if button has 'next-disabled' class
                if 'next-disabled' in next_button.get_attribute('class'):
                    continue 
                next_button.click()
                resolved = True
                print("Navigated to next course.")
        except:
            print("No next button found, ending session.")
    
    def _determine_course_type(self):
        # Check for h1 elements (any h1)
        try:
            h1_elements = self.driver.find_elements(By.TAG_NAME, 'h1')
            for h1_element in h1_elements:
                h1_text = h1_element.text

                # Check for "Attempt the Question"
                if h1_text == "Attempt the Question":
                    return CourseType.WALKTHROUGH_QUESTION

                if h1_text == "Introduction":
                    return CourseType.INTRODDUCTION

                if h1_text == "Question Walkthrough Introduction":
                    return CourseType.WALKTHROUGH

                # Check if text matches "Activity #<number>"
                if re.search(r'^Activity\s+#\d+', h1_text):
                    return CourseType.ACTIVITY

        except:
            pass

        # Check for quiz elements (using the quiz__info class)
        try:
            self.driver.find_element(By.CSS_SELECTOR, 'div.quiz__info')
            return CourseType.QUIZ
        except:
            pass
        
        # Check for infographics by looking for both print and download buttons

        # Check for activity elements
        try:
            activity_container = self.driver.find_element(By.CSS_SELECTOR, 'div.activity-container')
            if activity_container:
                return CourseType.ACTIVITY

        except:
            pass
            
        try:
            time.sleep(1)
            print_button = self.driver.find_element(By.CSS_SELECTOR, 'button[data-testid="print__button"]')
            download_button = self.driver.find_element(By.CSS_SELECTOR, 'button[data-testid="get-file__download-button"]')
            pdf_container = self.driver.find_element(By.CSS_SELECTOR, 'div.pdf-container')
            
            if (print_button or download_button or pdf_container):
                return CourseType.INFOGRAPHICS
        except:
            pass

        # Default to educational content
        return CourseType.LESSON

    def _wait_to_load(self):
        """Wait for page to be fully loaded"""
        self.wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        print("Page loaded.")
        
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
        

