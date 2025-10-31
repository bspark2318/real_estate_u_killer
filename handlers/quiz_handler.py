import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from .base_handler import BaseHandler
import time


class QuizHandler(BaseHandler):

    def handle(self):
        """Handle quiz page - start quiz and answer questions"""
        # Find and click the "Start new quiz" button
        try:
            self._attempt_quiz()

        except Exception as e:
            print(f"Error starting quiz: {e}")
    
    def _attempt_quiz(self):
        """Attempt the quiz by selecting random answers for each question"""
        start_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.btn.btn-primary'))
            )
        start_button.click()
        print("Clicked 'Start new quiz' button")
        
        time.sleep(2)  # Wait for quiz to load
        
        try:
            submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button.btn.btn-secondary')
            if submit_button:
                submit_button.click()
                time.sleep(2)
        except:
            pass
            
        # Wait for the quiz slide container to appear
        self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.slide-container'))
        )
        print("Quiz page loaded")

        # Answer all questions
        self._answer_all_questions()

    def _answer_all_questions(self):
        """Go through all quiz questions and answer randomly"""
        question_count = 0

        while True:
            try:
                # Wait for question to load
                question_wrap = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div.lesson-card.page.card-quiz'))
                )

                # Find all radio options within the current question wrap only
                radio_inputs = question_wrap.find_elements(By.CSS_SELECTOR, 'input[type="radio"]')

                if radio_inputs:
                    # Randomly select one option
                    selected_option = random.choice(radio_inputs)
                    selected_option.click()
                    question_count += 1
                    print(f"Answered question {question_count}")

                    time.sleep(1)  # Brief pause

                    # Look for Next button
                    try:
                        next_button = self.driver.find_element(By.CSS_SELECTOR, 'div.lesson-button--next:not(.lesson-button--disabled)')
                        next_button.click()
                        time.sleep(2)  # Wait for next question to load
                    except:
                        # No more next button, quiz is complete
                        print(f"Quiz completed! Answered {question_count} questions")
                        break
                else:
                    print("No more questions found")
                    break

            except Exception as e:
                print(f"Error answering questions: {e}")
                break