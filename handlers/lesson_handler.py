from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class LessonHandler:
    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait

    def handle(self):
        """Handle lesson page and scrape educational content"""
        content = self._scrape_educational_content()
        return content

    def _scrape_educational_content(self):
        # Wait for transcript div to be present
        transcript_div = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.transcript'))
        )

        # Get all <p> tags within the transcript div
        paragraphs = transcript_div.find_elements(By.TAG_NAME, 'p')

        # Extract text from each paragraph
        content = [p.text for p in paragraphs]

        print(f"Scraped {len(content)} paragraphs")
        return content
