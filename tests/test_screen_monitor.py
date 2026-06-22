import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.screen_monitor import ScreenMonitor

class TestScreenMonitor(unittest.TestCase):
    def setUp(self):
        self.db_path = "data/threat_database.json"
        self.log_path = "data/safenet_audit.log"
        self.mock_callback = MagicMock()
        self.monitor = ScreenMonitor(self.db_path, self.log_path, alert_callback=self.mock_callback)

    @patch('pytesseract.image_to_string')
    @patch('PIL.ImageGrab.grab')
    def test_screen_threat_detection(self, mock_grab, mock_ocr):
        """Verify that harmful text on screen triggers the alert callback."""
        mock_ocr.return_value = "This is a casino website"
        mock_grab.return_value = MagicMock() # Mock screenshot object
        
        self.monitor.capture_and_scan()
        
        self.mock_callback.assert_called()
        category = self.mock_callback.call_args[0][0]
        self.assertEqual(category, "Gambling")

    @patch('pytesseract.image_to_string')
    @patch('PIL.ImageGrab.grab')
    def test_evidence_saving(self, mock_grab, mock_ocr):
        """Verify that a screenshot is saved when a threat is detected."""
        mock_ocr.return_value = "buy weed online"
        mock_screenshot = MagicMock()
        mock_grab.return_value = mock_screenshot
        
        self.monitor.capture_and_scan()
        
        # Verify screenshot.save was called
        mock_screenshot.save.assert_called()

if __name__ == "__main__":
    unittest.main()
