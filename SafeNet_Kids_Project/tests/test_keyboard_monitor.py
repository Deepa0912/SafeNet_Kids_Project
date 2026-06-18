import sys
import os
import unittest
from unittest.mock import MagicMock

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.keyboard_monitor import KeyboardMonitor

class MockEvent:
    def __init__(self, name):
        self.name = name

class TestKeyboardMonitor(unittest.TestCase):
    def setUp(self):
        # Mock dependencies
        self.db_path = "data/threat_database.json"
        self.log_path = "data/safenet_audit.log"
        self.mock_ai = MagicMock()
        self.mock_ai.predict.return_value = ("Safe", 1.0)
        self.mock_nlp = MagicMock()
        self.mock_nlp.is_highly_negative.return_value = False
        self.mock_callback = MagicMock()
        
        self.monitor = KeyboardMonitor(
            self.db_path, 
            self.log_path, 
            ai_classifier=self.mock_ai,
            nlp_analyzer=self.mock_nlp,
            alert_callback=self.mock_callback
        )
        self.monitor.is_running = True # Simulate running state

    def test_text_reconstruction(self):
        """Verify that characters are correctly reconstructed into words."""
        keys = ['h', 'e', 'l', 'l', 'o', 'space', 'w', 'o', 'r', 'l', 'd']
        for k in keys:
            self.monitor._handle_key_event(MockEvent(k))
        
        self.assertEqual(self.monitor.current_buffer, "hello world")

    def test_backspace_handling(self):
        """Verify that backspace correctly removes characters from the buffer."""
        keys = ['a', 'b', 'c', 'backspace', 'd']
        for k in keys:
            self.monitor._handle_key_event(MockEvent(k))
        
        self.assertEqual(self.monitor.current_buffer, "abd")

    def test_keyword_threat_detection(self):
        """Verify that harmful keywords trigger the alert callback."""
        # 'xxx' is a known keyword in the database for Adult Content
        keys = ['x', 'x', 'x', 'enter']
        for k in keys:
            self.monitor._handle_key_event(MockEvent(k))
        
        self.mock_callback.assert_called()
        category = self.mock_callback.call_args[0][0]
        self.assertEqual(category, "Adult Content")

    def test_cyberbullying_detection(self):
        """Verify that toxic sentiment triggers the alert callback."""
        # Mock NLP analyzer to return True for highly negative content
        self.mock_nlp.is_highly_negative.return_value = True
        
        keys = ['y', 'o', 'u', 'space', 'a', 'r', 'e', 'space', 'u', 'g', 'l', 'y', 'enter']
        for k in keys:
            self.monitor._handle_key_event(MockEvent(k))
        
        # Should be detected via NLP if keywords didn't catch it first
        # In this case 'ugly' is in keywords too, but we verify the mechanism
        self.assertTrue(self.mock_callback.called)

if __name__ == "__main__":
    unittest.main()
