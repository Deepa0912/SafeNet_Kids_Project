"""gui/pages/home_page.py — Dashboard home with stats cards."""
import customtkinter as ctk
import os
from gui import theme as T


class HomePage(ctk.CTkFrame):
    """Parent dashboard landing page — stat cards + recent activity preview."""

    def __init__(self, master, monitor, username):
        super().__init__(master, fg_color=T.BG_PRIMARY, corner_radius=0)
        self.monitor  = monitor
        self.username = username
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # ── Header ────────────────────────────────────────────────────
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0, column=0, padx=28, pady=(24, 4), sticky="ew")
        ctk.CTkLabel(hdr, text=f"Welcome back, {self.username}  👋",
                     font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
                     text_color=T.TEXT_PRIMARY).pack(side="left")
        self._monitor_badge = ctk.CTkLabel(
            hdr, text="● STOPPED",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=T.DANGER)
        self._monitor_badge.pack(side="right", padx=(0, 4))

        ctk.CTkLabel(self, text="Security overview for your child's device",
                     font=ctk.CTkFont(size=12), text_color=T.TEXT_SECONDARY,
                     ).grid(row=1, column=0, padx=28, sticky="w")

        # ── Stats row ─────────────────────────────────────────────────
        stats = ctk.CTkFrame(self, fg_color="transparent")
        stats.grid(row=2, column=0, padx=28, pady=16, sticky="new")
        for i in range(4):
            stats.grid_columnconfigure(i, weight=1)

        cards_data = [
            ("🚨", "Threats Today",    "0",  T.DANGER,   "threats_val"),
            ("👁️",  "Active Sessions",  "0",  T.CYAN,     "sessions_val"),
            ("🛡️", "Blocked Apps",     "0",  T.WARNING,  "blocked_val"),
            ("📋", "Log Entries",      "0",  T.SUCCESS,  "logs_val"),
        ]
        self._stat_labels = {}
        for col, (icon, title, val, color, attr) in enumerate(cards_data):
            card = ctk.CTkFrame(stats, fg_color=T.BG_CARD,
                                corner_radius=12, border_width=1, border_color=T.BORDER)
            card.grid(row=0, column=col, padx=6, sticky="ew", ipady=12)
            ctk.CTkLabel(card, text=icon,
                         font=ctk.CTkFont(size=26)).pack(pady=(14, 2))
            lbl = ctk.CTkLabel(card, text=val,
                               font=ctk.CTkFont(size=28, weight="bold"),
                               text_color=color)
            lbl.pack()
            self._stat_labels[attr] = lbl
            ctk.CTkLabel(card, text=title,
                         font=ctk.CTkFont(size=11),
                         text_color=T.TEXT_SECONDARY).pack(pady=(0, 14))

        # ── Quick Actions ──────────────────────────────────────────────
        qa_frame = ctk.CTkFrame(self, fg_color="transparent")
        qa_frame.grid(row=3, column=0, padx=28, pady=(0, 16), sticky="ew")
        ctk.CTkLabel(qa_frame, text="Quick Actions",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=T.TEXT_SECONDARY).pack(anchor="w", pady=(0, 8))

        btns = ctk.CTkFrame(qa_frame, fg_color="transparent")
        btns.pack(fill="x")
        self._toggle_btn = ctk.CTkButton(
            btns, text="▶  Start Monitoring", width=180, height=38,
            fg_color=T.SUCCESS, hover_color="#059669",
            text_color=T.TEXT_BRIGHT, font=ctk.CTkFont(size=13, weight="bold"),
            corner_radius=8, command=self._toggle_monitoring)
        self._toggle_btn.pack(side="left", padx=(0, 10))

        T.ghost_btn(btns, text="📋  View Logs", width=140, height=38).pack(side="left", padx=(0, 10))
        T.ghost_btn(btns, text="⚙️  Settings",  width=130, height=38).pack(side="left")

        # ── Recent Activity ────────────────────────────────────────────
        ra = T.card(self)
        ra.grid(row=4, column=0, padx=28, pady=(0, 24), sticky="ew")
        ra.grid_columnconfigure(0, weight=1)

        hdr2 = ctk.CTkFrame(ra, fg_color="transparent")
        hdr2.grid(row=0, column=0, padx=16, pady=(14, 6), sticky="ew")
        ctk.CTkLabel(hdr2, text="Recent Activity",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=T.TEXT_PRIMARY).pack(side="left")
        ctk.CTkLabel(hdr2, text="Last 5 log entries",
                     font=ctk.CTkFont(size=11),
                     text_color=T.TEXT_MUTED).pack(side="right")

        self._activity_box = ctk.CTkTextbox(
            ra, height=100, fg_color=T.BG_INPUT,
            text_color=T.TEXT_SECONDARY, font=ctk.CTkFont(family="Consolas", size=11),
            border_width=0, corner_radius=8)
        self._activity_box.grid(row=1, column=0, padx=16, pady=(0, 14), sticky="ew")
        self._activity_box.configure(state="disabled")
        self._activity_box.insert("1.0", "No activity recorded yet.")
        self._activity_box.configure(state="disabled")

        # Start periodic refresh
        self._refresh()

    def _toggle_monitoring(self):
        if self.monitor.is_running:
            self.monitor.stop()
            self._toggle_btn.configure(text="▶  Start Monitoring", fg_color=T.SUCCESS)
            self._monitor_badge.configure(text="● STOPPED", text_color=T.DANGER)
        else:
            self.monitor.start()
            self._toggle_btn.configure(text="⏹  Stop Monitoring", fg_color=T.DANGER)
            self._monitor_badge.configure(text="● RUNNING", text_color=T.SUCCESS)

    def _refresh(self):
        try:
            log_file = "data/safenet_audit.log"
            if os.path.exists(log_file):
                with open(log_file, "r") as f:
                    lines = f.readlines()
                threats = sum(1 for l in lines if "Threat:" in l)
                self._stat_labels["threats_val"].configure(text=str(threats))
                self._stat_labels["logs_val"].configure(text=str(len(lines)))
                self._stat_labels["sessions_val"].configure(text="1" if self.monitor.is_running else "0")

                self._activity_box.configure(state="normal")
                self._activity_box.delete("1.0", "end")
                recent = lines[-5:] if lines else ["No activity yet."]
                self._activity_box.insert("1.0", "".join(recent))
                self._activity_box.configure(state="disabled")

            running = self.monitor.is_running
            self._monitor_badge.configure(
                text="● RUNNING" if running else "● STOPPED",
                text_color=T.SUCCESS if running else T.DANGER)
        except Exception:
            pass
        self.after(3000, self._refresh)
