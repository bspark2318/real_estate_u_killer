import random
import os
from datetime import datetime
from selenium.webdriver.common.by import By

class ActivityHandler:
    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait
        # Get project root directory (one level up from handlers/)
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.activities_dir = os.path.join(script_dir, "saved", "activities")
        os.makedirs(self.activities_dir, exist_ok=True)

    def handle(self):
        """Handle activity page"""
        # Try to make selections, if it fails go straight to review
        try:
            self._make_selections()
            print("All questions answered randomly")
            self._submit_activity()
        except Exception as e:
            print(f"Could not make selections (possibly already submitted): {e}")

        # Review answers
        scraped_content = self._review_answers()

        # Save to file
        filename = self._get_section_name() + ".md"
        filepath = os.path.join(self.activities_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(scraped_content)
        print(f"Saved activity review to: {filepath}")
    
    def _get_section_name(self):
        """Generate filename from chapter and lesson headers with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d")

        try:
            chapter_element = self.driver.find_element(By.CSS_SELECTOR, 'div.page-header-chapter.header-text')
            lesson_element = self.driver.find_element(By.CSS_SELECTOR, 'div.page-header-lesson.header-text')

            chapter_text = chapter_element.text.strip()
            lesson_text = lesson_element.text.strip()

            # Combine and sanitize for filename
            filename = f"{chapter_text}_{lesson_text}_{timestamp}"
            # Remove invalid filename characters and replace spaces with underscores
            filename = filename.replace('/', '-').replace('\\', '-').replace(':', '-').replace(' ', '_')

            return filename
        except:
            # Fallback to generic name if headers not found
            return f"activity_{timestamp}"

    def _make_selections(self):
        """Randomly select an answer for a given question element"""
        questions = self.driver.find_elements(By.CSS_SELECTOR, 'div.question')
        print(f"Found {len(questions)} questions")
        for idx, question in enumerate(questions, 1):
            # Find all radio options within this question
            radio_inputs = question.find_elements(By.CSS_SELECTOR, 'input[type="radio"]')
            if radio_inputs:
                # Randomly select one option
                selected_option = random.choice(radio_inputs)
                selected_option.click()
                print(f"Question {idx}: Selected random option")
                
    def _submit_activity(self):
        """Submit the activity and wait for page to load"""
        # Find and click submit button
        submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button.btn.bp')
        submit_button.click()
        print("Clicked Submit button")

        # Wait for page to load (document ready state)
        self.wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        print("New page loaded after submission") 
    
    def _review_answers(self):
        """Review answers and format as markdown"""
        questions_container = self.driver.find_element(By.CSS_SELECTOR, 'div.questions')
        all_children = questions_container.find_elements(By.XPATH, './child::*')

        markdown_content = "# Activity Review\n\n"

        question_num = 0
        i = 0
        while i < len(all_children):
            element = all_children[i]

            # Check if this is a question div
            if 'question' in element.get_attribute('class') and 'question-message' not in element.get_attribute('class'):
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

                        # Check if this was the correct answer
                        if 'correct-feedback' in option.get_attribute('class') or 'reveal-correct-feedback' in option.get_attribute('class'):
                            markdown_content += f"- **{option_text}** ✓ (Correct)\n"
                        # Check if this was the user's incorrect answer
                        elif 'incorrect-feedback' in option.get_attribute('class'):
                            markdown_content += f"- {option_text} ✗ (Your answer - Incorrect)\n"
                        else:
                            markdown_content += f"- {option_text}\n"
                    except:
                        pass

                # Check if next sibling is the explanation
                if i + 1 < len(all_children):
                    next_element = all_children[i + 1]
                    if 'question-message' in next_element.get_attribute('class'):
                        try:
                            explanation = next_element.find_element(By.CSS_SELECTOR, 'p.feedback-container')
                            markdown_content += f"\n**Explanation:** {explanation.text}\n\n"
                        except:
                            pass

                markdown_content += "---\n\n"

            i += 1

        return markdown_content