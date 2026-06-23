import time
import os
import json
import logging
import threading
from datetime import datetime
import pygetwindow as gw

from core.notification_manager import NotificationManager
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
        self.active_hours = {} 
        self._last_report_time = datetime.now()
        self._last_weekly_report = datetime.now()
        self._last_monthly_report = datetime.now()
        self.last_report_date = datetime.now().strftime("%Y-%m-%d")
        
        # Centralized Notification Manager
        self.notif_manager = NotificationManager(self)

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
            if not os.path.exists(self.db_path):
                return
            with open(self.db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.categories = data.get('categories', {})
                self.blocked_sites = data.get('blocked_sites', [])
                self.active_hours = data.get('active_hours', {})
                
                # Sync Notification Manager
                self.notif_manager.email_enabled = data.get('email_enabled', False)
                self.notif_manager.parent_email = data.get('parent_email', "")
                self.notif_manager.app_password = data.get('app_password', "")
                self.notif_manager.desktop_enabled = self.notifications_enabled

                if self.process_manager:
                    self.process_manager.blocked_processes = [a.lower() for a in data.get('blocked_apps', [])]
        except Exception as e:
            logging.error(f"SafeNetMonitor: Failed to load database: {e}")

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

    def _is_within_schedule(self):
        """Checks if current time is within parent-defined active hours."""
        if not self.active_hours:
            return True # No schedule means monitor 24/7
            
        now = datetime.now()
        day = now.strftime("%A")
        if day not in self.active_hours:
            return True
            
        start, end = self.active_hours[day]
        return start <= now.hour < end

    def start(self):
        if not self.is_running:
            # Check automated reporting
            self._check_periodic_reports()
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
        import os # Ensure os is available
        while self.is_running:
            try:
                if not self._is_within_schedule():
                    time.sleep(30)
                    continue

                current_window = gw.getActiveWindow()
                if current_window is not None:
                    title = current_window.title.lower()
                    if title and title != last_title:
                        self._analyze_title(title)
                        last_title = title

                counter += 1
                if counter >= self.scan_interval:
                    # 1. AI Image Moderation
                    label, confidence = self.image_analyzer.capture_and_analyze()
                    if label != "Safe" and confidence > 0.7:
                        self._trigger_alert(f"AI Detected Image: {label}", f"Confidence: {confidence:.2f}", "Screen Monitor")
                    
                    # 2. Screen OCR Analysis
                    self.screen_monitor.capture_and_scan()
                    counter = 0

                # 3. Daily Summary Report (Run once a day)
                self._check_periodic_reports()

            except Exception as e:
                pass
            time.sleep(1)

    def _check_periodic_reports(self):
        """Triggers automated Daily, Weekly, and Monthly PDF reports."""
        now = datetime.now()
        
        # 1. Daily Summary (Once every 24h)
        if (now - self._last_report_time).total_seconds() >= 86400:
            self.notif_manager.send_pdf_summary(days=1, report_type="Daily")
            self._last_report_time = now
            
        # 2. Weekly Report (Once every 7 days)
        if (now - self._last_weekly_report).days >= 7:
            self.notif_manager.send_pdf_summary(days=7, report_type="Weekly")
            self._last_weekly_report = now
            
        # 3. Monthly Report (Once every 30 days)
        if (now - self._last_monthly_report).days >= 30:
            self.notif_manager.send_pdf_summary(days=30, report_type="Monthly")
            self._last_monthly_report = now

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
        self.notif_manager.send_desktop_alert(f"Restricted Activity ({category})", f"Trigger: '{trigger}'")
        if category in ["Self-Harm", "Adult Content", "Drugs"]:
            self.notif_manager.send_email_alert(category, trigger, f"Keyboard Entry: {context}")
        self._trigger_alert(f"Restricted Activity ({category})", trigger, f"Keyboard: {context}")

    def _on_screen_threat(self, category, trigger, evidence_path):
        """Callback for threat detection from the ScreenMonitor."""
        self.notif_manager.send_desktop_alert(f"Screen Threat ({category})", f"Detected: '{trigger}'")
        if category in ["Self-Harm", "Adult Content", "Drugs"]:
            self.notif_manager.send_email_alert(category, trigger, f"Screen OCR (Evidence: {evidence_path})")
        self._trigger_alert(f"Screen Threat ({category})", trigger, f"Screen OCR (Evidence: {evidence_path})")

    def _trigger_alert(self, threat_type, trigger_word, source):
        log_message = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Threat: {threat_type} | Trigger: '{trigger_word}' | Source: '{source}'"
        logging.info(log_message)
        
        self.risk_engine.calculate_score()
        
        # Panic Lock: Instantly terminate browsers for high-risk categories
        # Covers: Illegal, Abusive/Harassment, Self-Harm, Adult Content, Extreme Intents, Gambling
        critical_categories = ["Self-Harm", "Abuse", "Illegal", "Harassment", "Violence", "Adult", "Extreme Intent", "Gambling"]
        is_critical = any(cat in threat_type or cat in trigger_word for cat in critical_categories)
        
        if self.process_manager and is_critical:
            self.process_manager.kill_active_browsers()
            logging.warning(f"Panic Lock: Terminated browsers due to critical threat: {threat_type}")