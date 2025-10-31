import os
from selenium.webdriver.common.by import By


class BaseHandler:
    """Base handler class with common functionality for all handlers"""

    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait
        # Get project root directory (one level up from handlers/)
        self.script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def _get_chapter_text(self):
        """Extract and sanitize chapter text"""
        try:
            chapter_element = self.driver.find_element(By.CSS_SELECTOR, 'div.page-header-chapter.header-text')
            chapter_text = chapter_element.text.strip()
            # Sanitize for filename
            chapter_text = chapter_text.replace('/', '_').replace('\\', '_').replace(':', '').replace(' ', '_')
            return chapter_text
        except:
            return None

    def _get_lesson_text(self):
        """Extract and sanitize lesson text"""
        try:
            lesson_element = self.driver.find_element(By.CSS_SELECTOR, 'div.page-header-lesson.header-text')
            lesson_text = lesson_element.text.strip()
            # Sanitize for filename
            lesson_text = lesson_text.replace('/', '_').replace('\\', '_').replace(':', '').replace(' ', '_')
            return lesson_text
        except:
            return None

    def _create_directory_path(self, content_type):
        """Create and return directory path: content/{chapter}/{content_type}/"""
        chapter_text = self._get_chapter_text()

        if chapter_text:
            directory = os.path.join(self.script_dir, "content", chapter_text, content_type)
        else:
            directory = os.path.join(self.script_dir, "content", content_type)

        os.makedirs(directory, exist_ok=True)
        return directory

    def _save_content(self, content, content_type, extension="md"):
        """Save content to chapter/content_type directory structure"""
        lesson_text = self._get_lesson_text()
        directory = self._create_directory_path(content_type)

        # Create filename with lesson text
        filename = f"{lesson_text}.{extension}" if lesson_text else f"{content_type}.{extension}"
        filepath = os.path.join(directory, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"Saved {content_type} to: {filepath}")
        return filepath
