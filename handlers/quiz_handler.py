import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from .base_handler import BaseHandler
import time
import re


class QuizHandler(BaseHandler):

    def __init__(self, driver, wait):
        super().__init__(driver, wait)
        self.quiz_bank = {}

    def handle(self):
        """Handle quiz page - start quiz and answer questions"""
        # Find and click the "Start new quiz" button
        try:
            # Check if next button exists and if it's disabled
            try:
                next_button = self.driver.find_element(By.CSS_SELECTOR, 'button.next')
                if 'next-disabled' in next_button.get_attribute('class'):
                    # Next button is disabled, attempt and review quiz
                    print("Next button is disabled, reviewing quiz")
                    self._attempt_quiz()
                    self._review_quiz()
                else:
                    # Next button is enabled, click it
                    self._save_quiz_bank()
                    next_button.click()
                    print("Clicked next button")
            except:
                print("Next button not found, starting new quiz")
                # Next button not found, attempt and review quiz
                self._attempt_quiz()
                self._review_quiz()

        except Exception as e:
            print(f"Error starting quiz: {e}")
    
    def _save_quiz_bank(self):
        """Convert quiz_bank to markdown and save it"""
        if not self.quiz_bank:
            print("Quiz bank is empty, nothing to save")
            return

        markdown_content = "# Quiz Bank\n\n"

        for idx, (question_text, data) in enumerate(self.quiz_bank.items(), 1):
            markdown_content += f"## Question {idx}\n\n"
            markdown_content += f"**Question:** {data['question']}\n\n"
            markdown_content += "**Options:**\n"

            # List all options with correct answer marked
            for option_idx, option in enumerate(data['options']):
                if option_idx == data['correct_index']:
                    markdown_content += f"{option_idx + 1}. {option} ✓\n"
                else:
                    markdown_content += f"{option_idx + 1}. {option}\n"

            markdown_content += f"\n**Correct Answer:** Option {data['correct_index'] + 1} - {data['correct_answer']}\n\n"

            if data['feedback']:
                markdown_content += f"**Feedback:** {data['feedback']}\n\n"

            markdown_content += "---\n\n"

        # Save using base handler's _save_content method
        self._save_content(markdown_content, "quiz")
        print(f"Saved {len(self.quiz_bank)} questions to quiz bank")
        
    
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

    def _review_quiz(self):
        """Review a failed quiz attempt"""
        try:
            # Find the quiz attempt div and click the Review button
            quiz_attempt = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.quiz-attempt'))
            )
            review_button = quiz_attempt.find_element(By.CSS_SELECTOR, 'div.quiz-attempt-buttons-wrapper button.btn.btn-primary')
            review_button.click()
            print("Clicked Review button")
            time.sleep(2)
            self._scrape_quiz_questions()
        except Exception as e:
            print(f"Error clicking Review button: {e}")

    def _scrape_quiz_questions(self):
        """Scrape all quiz questions, answers, and feedback"""
        try:
            finished = False
            while not finished:
                # Find the current question-wrap div
                question_wrap = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div.question-wrap'))
                )

                # Get question text and strip numbering (e.g., "1. ")
                question_label = question_wrap.find_element(By.CSS_SELECTOR, 'label.pb-2.form-label')
                full_question = question_label.text.strip()
                question_text = re.sub(r'^\d+\.\s*', '', full_question)

                # Get all options
                option_divs = question_wrap.find_elements(By.CSS_SELECTOR, 'div.cards-quiz--option')
                options = []
                correct_answer = None
                correct_index = None

                for idx, option_div in enumerate(option_divs):
                    # Get the option text (first span, not feedback-text)
                    spans = option_div.find_elements(By.CSS_SELECTOR, 'div.option-content-wrapper > span')
                    if spans:
                        option_text = spans[0].text.strip()
                        options.append(option_text)
                        # Check if this is the correct answer
                        if 'reveal-correct-feedback' in option_div.get_attribute('class') or 'correct-feedback' in option_div.get_attribute('class'):
                            correct_answer = option_text
                            correct_index = idx

                # Get feedback
                try:
                    feedback_div = question_wrap.find_element(By.CSS_SELECTOR, 'div.quiz-feedback')
                    feedback = feedback_div.text.strip()
                except:
                    feedback = ""

                # Store in quiz_bank
                self.quiz_bank[question_text] = {
                    "question": question_text,
                    "options": options,
                    "correct_answer": correct_answer,
                    "correct_index": correct_index,
                    "feedback": feedback
                }
                print(f"Scraped question: {question_text[:50]}...")
                
                
                print(f"Total questions in bank: {len(self.quiz_bank)}")
                try:
                    next_button = self.driver.find_element(By.CSS_SELECTOR, 'div.lesson-button--next:not(.lesson-button--disabled)')
                    next_button.click()
                    time.sleep(2)  # Wait for next question to load
                except:
                    leave_button = self.driver.find_element(By.CSS_SELECTOR, 'div.bd')
                    leave_button.click()
                    finished = True
                    print("No more questions to scrape, finished.")
                
        except Exception as e:
            print(f"Error scraping quiz questions: {e}")
    
    
    def _answer_all_questions(self):
        """Go through all quiz questions and answer using quiz bank or randomly"""
        question_count = 0
        reached_end = False
        while not reached_end:
            try:
                # Wait for question to load
                quiz_card = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div.lesson-card.page.card-quiz'))
                )

                # Try to get the question text to check if it's in the quiz bank
                try:
                    question_wrap = quiz_card.find_element(By.CSS_SELECTOR, 'div.question-wrap')
                    question_label = question_wrap.find_element(By.CSS_SELECTOR, 'label.pb-2.form-label')
                    full_question = question_label.text.strip()
                    question_text = re.sub(r'^\d+\.\s*', '', full_question)
                except:
                    question_text = None

                # Find all radio options within the current question wrap only
                radio_inputs = quiz_card.find_elements(By.CSS_SELECTOR, 'input[type="radio"]')

                if radio_inputs:
                    selected_option = None

                    # Check if question is in quiz bank
                    if question_text and question_text in self.quiz_bank:
                        correct_answer_text = self.quiz_bank[question_text]["correct_answer"]

                        # Find the radio input that matches the correct answer text
                        for radio_input in radio_inputs:
                            try:
                                # Get the label associated with this radio input
                                radio_id = radio_input.get_attribute('id')
                                label = quiz_card.find_element(By.CSS_SELECTOR, f'label[for="{radio_id}"]')

                                # Get only the first span text (not feedback text)
                                spans = label.find_elements(By.CSS_SELECTOR, 'div.option-content-wrapper > span')
                                if spans:
                                    option_text = spans[0].text.strip()
                                else:
                                    option_text = label.text.strip()

                                # Check if this option matches the correct answer
                                if option_text == correct_answer_text:
                                    selected_option = radio_input
                                    print(f"Found question in bank, using correct answer: {option_text[:50]}...")
                                    break
                            except:
                                continue

                        # If we didn't find a match, select randomly
                        if not selected_option:
                            selected_option = random.choice(radio_inputs)
                            print(f"Question in bank but couldn't match answer text, selecting randomly")
                            import json
                            print(json.dumps(self.quiz_bank[question_text], indent=2))
                            time.sleep(2)
                    else:
                        # Randomly select one option
                        selected_option = random.choice(radio_inputs)
                        print(f"Question not in bank, selecting randomly")

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
                        # No next button found, try to find and click submit button
                        try:
                            submit_button = self.driver.find_element(By.CSS_SELECTOR, 'div.check-answer-container button')
                            submit_button.click()
                            reached_end = True
                        except Exception as submit_error:
                            print(f"Error clicking submit button: {submit_error}")
                        # No more next button, quiz is complete
                        print(f"Quiz completed! Answered {question_count} questions")
                        break
                else:
                    print("No more questions found")
                    break

            except Exception as e:
                print(f"Error answering questions: {e}")
                break