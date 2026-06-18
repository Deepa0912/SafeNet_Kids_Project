import time
import json
import logging
import threading
import pygetwindow as gw
from plyer import notification

from core.nlp_analyzer import NLPAnalyzer
from core.keyboard_monitor import KeyboardMonitor
from core.ai_image_moderator import AIImageModerator
from core.ai_classifier import AIClassifier
from core.risk_engine import RiskEngine
from core.screen_monitor import ScreenMonitor


class SafeNetMonitor:
    def __init__(self, db_path, log_path, process_manager=None):
        self.db_path = db_path
        self.log_path = log_path
        self.process_manager = process_manager
        self.nlp_analyzer = NLPAnalyzer()
        self.image_analyzer = AIImageModerator("data/moderation_model.h5")
        self.ai_classifier = AIClassifier()
        self.risk_engine = RiskEngine(log_path)
        
        # Configuration
        self.notifications_enabled = True
        self.scan_interval = 9 

        self.is_running = False
        self.monitor_thread = None
        self.categories = {}
        self.blocked_sites = []

        self._load_database()
        self._setup_logging()

        self.key_logger = KeyboardMonitor(
            db_path,
            log_path,
            ai_classifier=self.ai_classifier,
            nlp_analyzer=self.nlp_analyzer,
            alert_callback=self._on_keyboard_threat
        )
        self.screen_monitor = ScreenMonitor(
            db_path,
            log_path,
            alert_callback=self._on_screen_threat
        )

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

    def reload_database(self):
        """Reloads the threat database and synchronizes all modules."""
        self._load_database()
        self.key_logger.reload_database()
        self.screen_monitor.reload_database()
        logging.info("SafeNetMonitor: Threat database reloaded and synchronized.")

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
                    # 1. AI Image Moderation (Adult, Violence, etc.)
                    label, confidence = self.image_analyzer.capture_and_analyze()
                    if label != "Safe" and confidence > 0.7:
                        self._trigger_alert(f"AI Detected Image: {label}", f"Confidence: {confidence:.2f}", "Screen Monitor")
                    
                    # 2. Screen OCR Analysis
                    self.screen_monitor.capture_and_scan()
                    
                    counter = 0

            except Exception as e:
                pass
            time.sleep(self.scan_interval)

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

    def _on_keyboard_threat(self, category, trigger, context):
        """Callback for threat detection from the KeyboardMonitor."""
        self._trigger_alert(f"Restricted Activity ({category})", trigger, f"Keyboard: {context}")

    def _on_screen_threat(self, category, trigger, evidence_path):
        """Callback for threat detection from the ScreenMonitor."""
        self._trigger_alert(f"Screen Threat ({category})", trigger, f"Screen OCR (Evidence: {evidence_path})")

    def _trigger_alert(self, threat_type, trigger_word, source):
        log_message = f"Threat: {threat_type} | Trigger: '{trigger_word}' | Source: '{source}'"
        logging.info(log_message)
        
        # Desktop Notification
        if self.notifications_enabled:
            try:
                notification.notify(
                    title=f"SafeNet Alert: {threat_type}",
                    message=f"Detected on {source}: '{trigger_word}'",
                    app_name="SafeNet Kids",
                    timeout=5
                )
            except Exception as e:
                logging.error(f"Notification error: {e}")

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