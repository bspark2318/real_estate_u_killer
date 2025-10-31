import random
from selenium.webdriver.common.by import By
from .base_handler import BaseHandler


class ActivityHandler(BaseHandler):

    def handle(self, is_acitivity=True):
        """Handle activity page"""
        # Try to make selections, if it fails go straight to review
        try:
            self._make_selections()
            print("All questions answered randomly")
            self._submit_activity()
        except Exception as e:
            print(f"Could not make selections (possibly already submitted): {e}")

        if is_acitivity:
            scraped_content = self._review_activity_answers()
            self._save_activity(scraped_content)
        else:
            scraped_content = self._review_walkthrough_answers()
            self._save_walkthrough(scraped_content)
    
    def _save_activity(self, content):
        """Save activity content"""
        self._save_content(content, "activities")

    def _save_walkthrough(self, content):
        """Save walkthrough content"""
        self._save_content(content, "walkthroughs")

    def _make_selections(self):
        """Randomly select an answer for a given question element"""
        questions = self.driver.find_elements(By.CSS_SELECTOR, 'div.question')
        print(f"Found {len(questions)} questions")
        for idx, question in enumerate(questions, 1):
            # Check for radio inputs first
            radio_inputs = question.find_elements(By.CSS_SELECTOR, 'input[type="radio"]')
            if radio_inputs:
                # Randomly select one radio option
                selected_option = random.choice(radio_inputs)
                selected_option.click()
                print(f"Question {idx}: Selected random radio option")
                continue

            # Check for select dropdowns
            select_elements = question.find_elements(By.CSS_SELECTOR, 'select')
            if select_elements:
                for select in select_elements:
                    # Get all options except the first one (empty value)
                    options = select.find_elements(By.CSS_SELECTOR, 'option[value]:not([value="-1"])')
                    if options:
                        # Randomly select one option
                        selected_option = random.choice(options)
                        selected_option.click()
                        print(f"Question {idx}: Selected random dropdown option")
                continue

            print(f"Question {idx}: No selectable elements found")
                
    def _submit_activity(self):
        """Submit the activity and wait for page to load"""
        # Find and click submit button
        submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button.btn.bp')
        submit_button.click()
        print("Clicked Submit button")

        # Wait for page to load (document ready state)
        self.wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        print("New page loaded after submission") 
        
    def _review_walkthrough_answers(self):
        """Review walkthrough answers and format as markdown"""
        # Get the question/answer content
        question_content = self._review_activity_answers()
        markdown_content = "# Walkthrough Review\n\n"
        markdown_content += "## Walkthrough Question\n\n"
        markdown_content += question_content

        # Get the transcript content
        
        markdown_content += "## Educational Content\n\n"

        try:
            transcript_container = self.driver.find_element(By.CSS_SELECTOR, 'div.transcript')
            paragraphs = transcript_container.find_elements(By.TAG_NAME, 'p')

            for p in paragraphs:
                if p.text.strip():
                    markdown_content += f"{p.text}\n\n"
        except Exception as e:
            print(f"Could not find transcript: {e}")

        markdown_content += "---\n\n"

        return markdown_content
    
    def _review_activity_answers(self):
        """Review answers and format as markdown"""
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.common.exceptions import StaleElementReferenceException

        # Wait for questions container to be present
        questions_container = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.questions'))
        )

        markdown_content = "# Activity Review\n\n"

        question_num = 0
        i = 0

        # Get initial count
        all_children = questions_container.find_elements(By.XPATH, './child::*')
        total_children = len(all_children)

        while i < total_children:
            try:
                # Re-fetch elements to avoid stale references
                all_children = questions_container.find_elements(By.XPATH, './child::*')
                element = all_children[i]

                # Check if this is a question div
                element_class = element.get_attribute('class')
                if 'question' in element_class and 'question-message' not in element_class:
                    question_num += 1

                    # Get question text
                    question_text = element.find_element(By.CSS_SELECTOR, 'p').text

                    # Get all options
                    options = element.find_elements(By.CSS_SELECTOR, 'div.option')

                    markdown_content += f"## Question {question_num}\n\n"
                    markdown_content += f"**{question_text}**\n\n"
                    markdown_content += "### Options:\n\n"

                    for option in options:
                        try:
                            option_text_elem = option.find_element(By.CSS_SELECTOR, 'span.option-content')
                            option_text = option_text_elem.text
                            option_class = option.get_attribute('class')

                            # Check if this was the correct answer
                            if 'correct-feedback' in option_class or 'reveal-correct-feedback' in option_class:
                                markdown_content += f"- **{option_text}** ✓ (Correct)\n"
                            # Check if this was the user's incorrect answer
                            elif 'incorrect-feedback' in option_class:
                                markdown_content += f"- {option_text} ✗ (Your answer - Incorrect)\n"
                            else:
                                markdown_content += f"- {option_text}\n"
                        except:
                            pass

                    # Check if next sibling is the explanation
                    if i + 1 < total_children:
                        try:
                            all_children = questions_container.find_elements(By.XPATH, './child::*')
                            if i + 1 < len(all_children):  # Double-check bounds after refetch
                                next_element = all_children[i + 1]
                                next_class = next_element.get_attribute('class')
                                if 'question-message' in next_class:
                                    explanation = next_element.find_element(By.CSS_SELECTOR, 'p.feedback-container')
                                    markdown_content += f"\n**Explanation:** {explanation.text}\n\n"
                        except:
                            pass

                    markdown_content += "---\n\n"

            except StaleElementReferenceException:
                print(f"Stale element at index {i}, retrying...")
                continue

            i += 1

        return markdown_content