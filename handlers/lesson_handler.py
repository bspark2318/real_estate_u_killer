from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from .base_handler import BaseHandler


class LessonHandler(BaseHandler):

    def handle(self):
        """Handle lesson page and scrape educational content"""
        markdown_content = self._scrape_educational_content()
        self._save_lesson(markdown_content)

    def _save_lesson(self, content):
        """Save lesson content"""
        self._save_content(content, "lessons")

    def _scrape_educational_content(self):
        """Scrape lesson content and format as markdown"""
        # Wait for transcript div to be present
        transcript_div = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.transcript'))
        )

        # Get all <p> tags within the transcript div
        paragraphs = transcript_div.find_elements(By.TAG_NAME, 'p')

        # Build markdown content
        markdown_content = "# Lesson\n\n"

        # Get lesson title if available
        try:
            lesson_element = self.driver.find_element(By.CSS_SELECTOR, 'div.page-header-lesson.header-text')
            markdown_content += f"## {lesson_element.text}\n\n"
        except:
            pass

        # Add paragraphs
        for p in paragraphs:
            if p.text.strip():
                markdown_content += f"{p.text}\n\n"

        print(f"Scraped {len(paragraphs)} paragraphs")
        return markdown_content
