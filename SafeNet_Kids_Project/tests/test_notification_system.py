import unittest
import os
from core.report_generator import ReportGenerator
from core.notification_manager import NotificationManager

class TestNotificationSystem(unittest.TestCase):
    def setUp(self):
        # Use dummy paths for testing
        self.log_path = "data/test_audit.log"
        self.report_dir = "data/test_reports"
        
        # Create a dummy log file
        with open(self.log_path, "w", encoding="utf-8") as f:
            f.write("[2026-06-18 20:00:00] Threat: Restricted Activity (Adult) | Trigger: 'porn' | Source: 'Keyboard'\n")
            f.write("[2026-06-18 20:05:00] Threat: Restricted Activity (Violence) | Trigger: 'kill' | Source: 'Keyboard'\n")

        self.report_gen = ReportGenerator(log_path=self.log_path, output_dir=self.report_dir)
        self.notif_manager = NotificationManager(None) # No monitor needed for basic email tests

    def test_pdf_generation(self):
        """Verify that the ReportGenerator creates a valid PDF file."""
        filepath = self.report_gen.generate_report(days=1, report_type="Test")
        self.assertIsNotNone(filepath)
        self.assertTrue(os.path.exists(filepath))
        self.assertTrue(filepath.endswith(".pdf"))

    def test_chart_generation(self):
        """Verify that charts are generated in the temp directory."""
        data = self.report_gen._aggregate_data(days=1)
        chart_path = self.report_gen._generate_charts(data, "Test")
        self.assertIsNotNone(chart_path)
        self.assertTrue(os.path.exists(chart_path))

    def tearDown(self):
        # Cleanup
        if os.path.exists(self.log_path):
            os.remove(self.log_path)
        if os.path.exists(self.report_dir):
            for f in os.listdir(self.report_dir):
                os.remove(os.path.join(self.report_dir, f))
            os.rmdir(self.report_dir)

if __name__ == "__main__":
    unittest.main()
