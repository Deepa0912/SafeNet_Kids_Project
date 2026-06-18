import keyboard
import threading
import logging
import json
import os
import time
from datetime import datetime

class KeyboardMonitor:
    """
    Monitors keyboard activity in real-time, captures typed text,
    stores activity logs, and detects predefined harmful keywords/threats.
    """

    def __init__(self, db_path, log_path, ai_classifier=None, nlp_analyzer=None, alert_callback=None):
        self.db_path = db_path
        self.log_path = log_path
        self.ai_classifier = ai_classifier
        self.nlp_analyzer = nlp_analyzer
        self.alert_callback = alert_callback

        self.current_buffer = ""
        self.is_running = False
        self.categories = {}
        self.activity_log_file = "data/keyboard_activity.log"

        self._load_categories()
        self._setup_activity_logging()

    def _load_categories(self):
        """Loads threat categories and keywords from the database."""
        try:
            if os.path.exists(self.db_path):
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.categories = data.get('categories', {})
            else:
                print(f"KeyboardMonitor: Database not found at {self.db_path}")
        except Exception as e:
            print(f"KeyboardMonitor: Error loading database - {e}")

    def reload_database(self):
        """Reloads the threat database."""
        self._load_categories()

    def _setup_activity_logging(self):
        """Sets up a separate log file for raw keyboard activity."""
        os.makedirs(os.path.dirname(self.activity_log_file), exist_ok=True)
        # We use a dedicated logger for activity to avoid mixing with system logs
        self.activity_logger = logging.getLogger("KeyboardActivity")
        if not self.activity_logger.handlers:
            handler = logging.FileHandler(self.activity_log_file, encoding='utf-8')
            handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
            self.activity_logger.addHandler(handler)
            self.activity_logger.setLevel(logging.INFO)

    def start(self):
        """Starts the keyboard hook."""
        if not self.is_running:
            self.is_running = True
            keyboard.on_release(self._handle_key_event)
            print("Keyboard Monitor: Started capturing activity.")

    def stop(self):
        """Stops the keyboard hook."""
        self.is_running = False
        keyboard.unhook_all()
        print("Keyboard Monitor: Stopped capturing activity.")

    def _handle_key_event(self, event):
        """Processes individual key release events."""
        if not self.is_running:
            return

        key_name = event.name

        if key_name == 'space':
            self.current_buffer += " "
            self._analyze_buffer(final=False)
        elif key_name == 'enter':
            if self.current_buffer.strip():
                self._analyze_buffer(final=True)
            self.current_buffer = ""
        elif key_name == 'backspace':
            self.current_buffer = self.current_buffer[:-1]
        elif len(key_name) == 1:
            self.current_buffer += key_name
        
        # Buffer limit to check long strings without spaces/enters
        if len(self.current_buffer) > 100:
            self._analyze_buffer(final=False)
            self.current_buffer = self.current_buffer[-50:] # Keep recent context

    def _analyze_buffer(self, final=False):
        """Analyzes the current buffer for threat detection and logging."""
        text = self.current_buffer.strip()
        if not text:
            return

        # 1. Log activity
        if final or len(text) > 20: # Log chunks or final sentences
            self.activity_logger.info(f"Typed: {text}")

        # 2. Threat Detection - Keyword Matching
        text_lower = text.lower()
        detected_category = None
        trigger_keyword = None

        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    detected_category = category
                    trigger_keyword = keyword
                    break
            if detected_category:
                break

        if detected_category:
            self._trigger_threat_alert(detected_category, trigger_keyword, text)
            return

        # 3. AI Classification (if available)
        if self.ai_classifier:
            ai_label, confidence = self.ai_classifier.predict(text)
            if ai_label and ai_label != "Safe" and confidence > 0.65:
                self._trigger_threat_alert(f"AI_{ai_label}", text, text, confidence)
                return

        # 4. Sentiment Analysis (if available)
        if self.nlp_analyzer and self.nlp_analyzer.is_highly_negative(text):
            self._trigger_threat_alert("Cyberbullying", "Sentiment Analysis", text)

    def _trigger_threat_alert(self, category, trigger, full_text, confidence=None):
        """Logs the threat and triggers the external alert callback."""
        conf_str = f" (Conf: {confidence:.2f})" if confidence else ""
        alert_msg = f"THREAT DETECTED [{category}]: Triggered by '{trigger}'{conf_str} | Context: '{full_text}'"
        
        self.activity_logger.warning(alert_msg)
        
        if self.alert_callback:
            self.alert_callback(category, trigger, full_text)
