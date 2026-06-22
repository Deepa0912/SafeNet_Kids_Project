import os
import smtplib
import ssl
import logging
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from plyer import notification
from core.report_generator import ReportGenerator

class NotificationManager:
    """
    Centralized manager for Desktop, Email, and Reporting notifications.
    """

    def __init__(self, monitor=None):
        self.monitor = monitor
        self.desktop_enabled = True
        self.email_enabled = False
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 465
        self.parent_email = ""
        self.app_password = ""
        self.report_gen = ReportGenerator()

    def send_desktop_alert(self, title, message):
        """Triggers a local Windows desktop notification."""
        if not self.desktop_enabled:
            return
            
        try:
            notification.notify(
                title=f"SafeNet: {title}",
                message=message,
                app_name="SafeNet Kids",
                timeout=10
            )
        except Exception as e:
            logging.error(f"NotificationManager: Desktop alert failed: {e}")

    def send_email_alert(self, category, trigger, context):
        """Sends an immediate remote email for critical threats."""
        if not self.email_enabled or not self.parent_email or not self.app_password:
            return

        subject = f"CRITICAL - SafeNet Alert: {category} Detected"
        msg_body = f"""
        SafeNet Kids - Critical Threat Alert
        ------------------------------------
        Category: {category}
        Trigger:  {trigger}
        Time:     {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        Details:  {context}
        
        This notification was triggered because your child encountered high-risk content.
        Please review the SafeNet Dashboard for full logs and evidence.
        """
        self._dispatch_email(subject, msg_body)

    def generate_summary_report(self, days=1):
        """Generates and emails a professional activity summary for the last X days."""
        if not self.parent_email:
            return
            
        log_path = "data/safenet_audit.log"
        if not os.path.exists(log_path):
            return

        summary = []
        threat_count = 0
        categories = {}
        
        target_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                for line in f:
                    if target_date in line:
                        threat_count += 1
                        if "Category:" in line:
                            cat = line.split("Category:")[1].split(",")[0].strip()
                            categories[cat] = categories.get(cat, 0) + 1
                        summary.append(line.strip())
        except Exception as e:
            logging.error(f"NotificationManager: Report generation failed: {e}")
            return

        subject = f"SafeNet Kids: Daily Safety Report ({target_date})"
        report_body = f"""
        SafeNet Kids - Activity Summary Report
        --------------------------------------
        Date: {target_date}
        Total Threats Detected: {threat_count}
        
        Breakdown by Category:
        """
        for cat, count in categories.items():
            report_body += f"- {cat}: {count}\n"
            
        report_body += "\nRecent Activity Samples:\n"
        report_body += "\n".join(summary[-10:]) if summary else "No activity detected."
        
        report_body += "\n\nLogin to the Control Center to view full activity logs."
        
        self._dispatch_email(subject, report_body)

    def send_pdf_summary(self, days=1, report_type="Daily"):
        """Generates and emails a professional PDF report."""
        if not self.email_enabled or not self.parent_email:
            return

        pdf_path = self.report_gen.generate_report(days=days, report_type=report_type)
        if pdf_path:
            subject = f"SafeNet Kids: {report_type} Safety Report ({datetime.now().strftime('%Y-%m-%d')})"
            body = f"Please find the attached {report_type} Safety Report for SafeNet Kids."
            self._dispatch_email(subject, body, attachment_path=pdf_path)

    def _dispatch_email(self, subject, body, attachment_path=None):
        """Internal helper to send email via SMTP with optional attachment."""
        try:
            if attachment_path:
                msg = MIMEMultipart()
                msg['Subject'] = subject
                msg['From'] = self.parent_email
                msg['To'] = self.parent_email
                msg.attach(MIMEText(body))
                
                with open(attachment_path, "rb") as f:
                    part = MIMEApplication(f.read(), Name=os.path.basename(attachment_path))
                    part['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment_path)}"'
                    msg.attach(part)
            else:
                msg = MIMEText(body)
                msg['Subject'] = subject
                msg['From'] = self.parent_email
                msg['To'] = self.parent_email
            
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=context) as server:
                server.login(self.parent_email, self.app_password)
                server.sendmail(self.parent_email, self.parent_email, msg.as_string())
            logging.info(f"NotificationManager: Email sent to {self.parent_email}")
        except Exception as e:
            logging.error(f"NotificationManager: Email dispatch failed: {e}")
