import os
import time
from datetime import datetime
from selenium.webdriver.common.by import By


class InfographicsHandler:
    def __init__(self, driver, wait, download_dir):
        self.driver = driver
        self.wait = wait
        self.download_dir = download_dir

    def handle(self):
        """Handle infographics page - download PDF"""
        # Click the download button
        download_button = self.driver.find_element(
            By.CSS_SELECTOR,
            'button[data-testid="get-file__download-button"]'
        )
        download_button.click()

        # Wait for download to complete
        self._wait_for_download()

        # Rename the downloaded file with a proper name
        filename = self._get_file_name()
        self._rename_latest_download(filename)

    def _get_file_name(self):
        """Generate filename from chapter and lesson headers with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        try:
            chapter_element = self.driver.find_element(By.CSS_SELECTOR, 'div.page-header-chapter.header-text')
            lesson_element = self.driver.find_element(By.CSS_SELECTOR, 'div.page-header-lesson.header-text')

            chapter_text = chapter_element.text.strip()
            lesson_text = lesson_element.text.strip()

            # Combine and sanitize for filename
            filename = f"{chapter_text}_{lesson_text}_{timestamp}.pdf"
            # Remove invalid filename characters and replace spaces with underscores
            filename = filename.replace('/', '_').replace('\\', '_').replace(':', '_').replace(' ', '_')

            return filename
        except:
            # Fallback to generic name if headers not found
            return f"infographic_{timestamp}.pdf"
    
    def _wait_for_download(self, timeout=30):
        """Wait for download to complete"""
        seconds = 0
        while seconds < timeout:
            time.sleep(1)
            # Check if there are any .crdownload files (Chrome's temporary download files)
            downloading = [f for f in os.listdir(self.download_dir) if f.endswith('.crdownload')]
            if not downloading:
                return True
            seconds += 1
        return False

    def _rename_latest_download(self, new_name):
        """Rename the most recently downloaded file"""
        files = os.listdir(self.download_dir)
        paths = [os.path.join(self.download_dir, f) for f in files if not f.endswith('.crdownload')]
        if not paths:
            return None
        latest_file = max(paths, key=os.path.getctime)
        new_path = os.path.join(self.download_dir, new_name)
        os.rename(latest_file, new_path)
        print(f"Renamed download to: {new_name}")
        return new_path
