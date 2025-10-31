import os
import time
from selenium.webdriver.common.by import By
from .base_handler import BaseHandler


class InfographicsHandler(BaseHandler):
    def __init__(self, driver, wait, download_dir):
        super().__init__(driver, wait)
        self.temp_download_dir = download_dir

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

        # Move and rename the downloaded file
        self._move_and_rename_download()

    def _move_and_rename_download(self):
        """Move downloaded file to chapter/lesson directory structure"""
        lesson_text = self._get_lesson_text()
        directory = self._create_directory_path("infographics")

        # Get the latest downloaded file from temp directory
        files = os.listdir(self.temp_download_dir)
        paths = [os.path.join(self.temp_download_dir, f) for f in files if not f.endswith('.crdownload')]
        if not paths:
            print("No downloaded file found")
            return

        latest_file = max(paths, key=os.path.getctime)

        # Create new filepath with lesson text
        filename = f"{lesson_text}.pdf" if lesson_text else "infographic.pdf"
        new_filepath = os.path.join(directory, filename)

        # Move and rename
        os.rename(latest_file, new_filepath)
        print(f"Saved infographic to: {new_filepath}")
    
    def _wait_for_download(self, timeout=30):
        """Wait for download to complete"""
        seconds = 0
        while seconds < timeout:
            time.sleep(1)
            # Check if there are any .crdownload files (Chrome's temporary download files)
            downloading = [f for f in os.listdir(self.temp_download_dir) if f.endswith('.crdownload')]
            if not downloading:
                return True
            seconds += 1
        return False
