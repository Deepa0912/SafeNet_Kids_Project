import customtkinter as ctk
from gui import theme as T
from datetime import datetime

class ReportsPage(ctk.CTkFrame):
    """
    Parental Reporting Center for generating PDF safety analytics.
    """

    def __init__(self, master, monitor):
        super().__init__(master, fg_color=T.BG_PRIMARY, corner_radius=0)
        self.monitor = monitor
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # ── Header ────────────────────────────────────────────────────
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0, column=0, padx=28, pady=(24, 4), sticky="ew")
        
        ctk.CTkLabel(hdr, text="📊  Safety Reporting Center",
                     font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
                     text_color=T.TEXT_PRIMARY).pack(side="left")

        # ── Statistics Overview ────────────────────────────────────────
        stats_frame = T.card(self)
        stats_frame.grid(row=1, column=0, padx=28, pady=20, sticky="ew")
        
        ctk.CTkLabel(stats_frame, text="Quick Insights", 
                     font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, padx=20, pady=(10, 5), sticky="w")
        
        # We can pull some quick stats from monitor.risk_engine or logs
        # For now, let's show the report generation buttons
        
        # ── Report Generation ─────────────────────────────────────────
        controls = T.card(self)
        controls.grid(row=2, column=0, padx=28, pady=0, sticky="nsew")
        controls.grid_columnconfigure((0, 1, 2), weight=1)

        # Daily Report Card
        self._create_report_card(controls, 0, "Daily Report", "Last 24 hours of activity.", 1)
        # Weekly Report Card
        self._create_report_card(controls, 1, "Weekly Report", "Last 7 days of trends.", 7)
        # Monthly Report Card
        self._create_report_card(controls, 2, "Monthly Report", "Full month safety audit.", 30)

    def _create_report_card(self, parent, col, title, desc, days):
        card = ctk.CTkFrame(parent, fg_color=T.BG_INPUT, corner_radius=12)
        card.grid(row=0, column=col, padx=15, pady=20, sticky="nsew")
        
        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(15, 5))
        ctk.CTkLabel(card, text=desc, text_color=T.TEXT_SECONDARY, font=ctk.CTkFont(size=12)).pack(pady=5)
        
        btn = T.primary_btn(card, "Generate PDF", command=lambda: self._generate(days, title.split(" ")[0]))
        btn.pack(pady=20)

    def _generate(self, days, report_type):
        if hasattr(self.monitor, 'notif_manager'):
            # Trigger PDF generation and email
            self.monitor.notif_manager.send_pdf_summary(days=days, report_type=report_type)
            # Show feedback
            msg = f"{report_type} Report generated and emailed to your inbox!"
            self._show_feedback(msg)

    def _show_feedback(self, text):
        lbl = ctk.CTkLabel(self, text=text, text_color=T.CYAN, font=ctk.CTkFont(size=12, slant="italic"))
        lbl.grid(row=3, column=0, pady=10)
        self.after(5000, lbl.destroy)
