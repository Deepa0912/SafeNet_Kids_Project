import time
import json
import logging
import threading
import pygetwindow as gw
from plyer import notification

from core.nlp_analyzer import NLPAnalyzer
from core.key_logger import KeyLogger
from core.image_analyzer import ImageAnalyzer
from core.ai_classifier import AIClassifier


class SafeNetMonitor:
    def __init__(self, db_path, log_path, process_manager=None):
        self.db_path = db_path
        self.log_path = log_path
        self.process_manager = process_manager
        self.nlp_analyzer = NLPAnalyzer()
        self.image_analyzer = ImageAnalyzer()
        self.ai_classifier = AIClassifier()

        self.is_running = False
        self.monitor_thread = None
        self.categories = {}
        self.blocked_sites = []

        self._load_database()
        self._setup_logging()

        self.key_logger = KeyLogger(self._analyze_typed_text)

    def _load_database(self):
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.categories = data.get('categories', {})
                self.blocked_sites = data.get('blocked_sites', [])
        except Exception as e:
            pass

    def _setup_logging(self):
        logging.basicConfig(
            filename=self.log_path,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def start(self):
        if not self.is_running:
            self.is_running = True
            self._load_database()
            self.monitor_thread = threading.Thread(target=self._scan_loop, daemon=True)
            self.monitor_thread.start()
            self.key_logger.start()

    def stop(self):
        self.is_running = False
        self.key_logger.stop()
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)

    def _scan_loop(self):
        last_title = ""
        counter = 0
        while self.is_running:
            try:
                current_window = gw.getActiveWindow()
                if current_window is not None:
                    title = current_window.title.lower()
                    if title and title != last_title:
                        self._analyze_title(title)
                        last_title = title

                counter += 1
                if counter >= 3:
                    if self.image_analyzer.capture_and_analyze():
                        self._trigger_alert("Explicit Image Detected", "Screen Analysis", "Background Scanner")
                    counter = 0

            except Exception as e:
                pass
            time.sleep(3)

    def _analyze_title(self, title):
        for site in self.blocked_sites:
            if site.lower() in title:
                self._trigger_alert("Blocked Website", site, title)
                return

        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword.lower() in title:
                    self._trigger_alert(f"Restricted Keyword ({category})", keyword, title)
                    return

    def _analyze_typed_text(self, text):
        # 1. AI Prediction (High Priority)
        ai_label, confidence = self.ai_classifier.predict(text)
        if ai_label and ai_label != "Safe" and confidence > 0.6:
            self._trigger_alert(f"AI Detected: {ai_label} (Conf: {confidence:.2f})", text, "Keyboard AI")
            return

        # 2. VADER Sentiment (Bulying)
        if self.nlp_analyzer.is_highly_negative(text):
            self._trigger_alert("Cyberbullying/Toxic Chat Detected", text, "Keyboard Input")
            return

        # 3. Keyword Matching
        text_lower = text.lower()
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    self._trigger_alert(f"Restricted Typed Keyword ({category})", keyword, "Keyboard Input")
                    return

    def _trigger_alert(self, threat_type, trigger_word, source):
        log_message = f"Threat: {threat_type} | Trigger: '{trigger_word}' | Source: '{source}'"
        logging.info(log_message)

        if self.process_manager:
            self.process_manager.kill_active_browsers()

        try:
            notification.notify(
                title="SafeNet Kids Alert",
                message=f"Blocked content: {trigger_word}",
                app_name="SafeNet Kids",
                timeout=5
            )
        except Exception as e:
            pass