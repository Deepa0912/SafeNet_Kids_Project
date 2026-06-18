import os
import time
import json
import logging
from datetime import datetime
from PIL import ImageGrab
import pytesseract

# Explicitly set the tesseract path for Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class ScreenMonitor:
    """
    Monitors screen activity, captures screenshots, extracts text via OCR,
    and detects harmful content. Saves evidence for detected threats.
    """

    def __init__(self, db_path, log_path, alert_callback=None):
        self.db_path = db_path
        self.log_path = log_path
        self.alert_callback = alert_callback
        
        self.evidence_dir = "data/evidence"
        self.screen_log_file = "data/screen_threats.log"
        self.categories = {}
        
        self._load_categories()
        self._setup_logging()
        os.makedirs(self.evidence_dir, exist_ok=True)

    def _load_categories(self):
        """Loads threat categories and keywords from the database."""
        try:
            if os.path.exists(self.db_path):
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.categories = data.get('categories', {})
        except Exception as e:
            print(f"ScreenMonitor: Error loading database - {e}")

    def reload_database(self):
        """Reloads the threat database."""
        self._load_categories()

    def _setup_logging(self):
        """Sets up a dedicated log file for screen threats."""
        self.screen_logger = logging.getLogger("ScreenMonitor")
        if not self.screen_logger.handlers:
            handler = logging.FileHandler(self.screen_log_file, encoding='utf-8')
            handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            self.screen_logger.addHandler(handler)
            self.screen_logger.setLevel(logging.INFO)

    def capture_and_scan(self):
        """
        Captures a screenshot, performs OCR, and scans for threats.
        Returns: (detected_category, trigger, text) if found, else (None, None, None)
        """
        try:
            # Capture
            screenshot = ImageGrab.grab()
            
            # OCR
            text = pytesseract.image_to_string(screenshot)
            if not text.strip():
                return None, None, None

            # Scan
            text_lower = text.lower()
            for category, keywords in self.categories.items():
                for keyword in keywords:
                    if keyword.lower() in text_lower:
                        self._handle_detection(category, keyword, screenshot, text)
                        return category, keyword, text
            
            return None, None, None
            
        except Exception as e:
            # Pytesseract might not be configured, but we fail silently or log
            return None, None, None

    def _handle_detection(self, category, trigger, screenshot, full_text):
        """Saves evidence and logs the threat."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        evidence_path = os.path.join(self.evidence_dir, f"evidence_{timestamp}.png")
        
        try:
            screenshot.save(evidence_path)
        except Exception as e:
            evidence_path = "Failed to save screenshot"

        log_msg = f"THREAT DETECTED [{category}]: Triggered by '{trigger}' | Evidence: {evidence_path}"
        self.screen_logger.warning(log_msg)
        
        if self.alert_callback:
            self.alert_callback(category, trigger, evidence_path)
