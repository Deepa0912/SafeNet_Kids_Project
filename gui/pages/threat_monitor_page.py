"""gui/pages/threat_monitor_page.py — Real-time threat monitoring page."""
import customtkinter as ctk
import os, time, threading
from gui import theme as T


class ThreatMonitorPage(ctk.CTkFrame):

    def __init__(self, master, monitor, process_manager, auth_manager, username):
        super().__init__(master, fg_color=T.BG_PRIMARY, corner_radius=0)
        self.monitor         = monitor
        self.process_manager = process_manager
        self.auth_manager    = auth_manager
        self.username        = username
        self._running        = True
        self._build()
        threading.Thread(target=self._watch_log, daemon=True).start()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)

        # ── Header ────────────────────────────────────────────────────
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0, column=0, padx=28, pady=(24, 4), sticky="ew")
        ctk.CTkLabel(hdr, text="🔍  Threat Monitor",
                     font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
                     text_color=T.TEXT_PRIMARY).pack(side="left")

        self._status_badge = ctk.CTkLabel(
            hdr, text="  ● STOPPED  ",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=T.DANGER,
            fg_color=T.DANGER_DIM, corner_radius=6)
        self._status_badge.pack(side="right")

        ctk.CTkLabel(self, text="Live detection feed — NLP · Computer Vision · Keylogger",
                     font=ctk.CTkFont(size=12), text_color=T.TEXT_SECONDARY,
                     ).grid(row=1, column=0, padx=28, sticky="w", pady=(0, 12))

        # ── Sensor cards row ──────────────────────────────────────────
        sensors = ctk.CTkFrame(self, fg_color="transparent")
        sensors.grid(row=2, column=0, padx=28, sticky="ew")
        for i in range(5):
            sensors.grid_columnconfigure(i, weight=1)

        sensor_data = [
            ("🧠", "NLP",    "Typed text threats",        "nlp_status"),
            ("📷", "Visual", "AI inappropriate check",   "img_status"),
            ("⌨️",  "Keys",   "Keystroke activity",       "key_status"),
            ("🖼️", "OCR",    "Text from screen",        "ocr_status"),
            ("🛡️", "Safety", "Violence & Adult check", "mod_status"),
        ]
        self._sensor_labels = {}
        for col, (icon, title, desc, attr) in enumerate(sensor_data):
            c = T.card(sensors)
            c.grid(row=0, column=col, padx=4, sticky="ew", ipady=8)
            row = ctk.CTkFrame(c, fg_color="transparent")
            row.pack(padx=10, pady=(10, 0), fill="x")
            ctk.CTkLabel(row, text=icon, font=ctk.CTkFont(size=20)).pack(side="left", padx=(0, 6))
            ctk.CTkLabel(row, text=title,
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=T.TEXT_PRIMARY).pack(side="left")
            lbl = ctk.CTkLabel(c, text="● IDLE",
                               font=ctk.CTkFont(size=10, weight="bold"),
                               text_color=T.TEXT_MUTED)
            lbl.pack(padx=10, anchor="w")
            self._sensor_labels[attr] = lbl
            ctk.CTkLabel(c, text=desc, font=ctk.CTkFont(size=10),
                         text_color=T.TEXT_MUTED).pack(padx=10, pady=(0, 10), anchor="w")

        # ── Control bar ───────────────────────────────────────────────
        ctrl = ctk.CTkFrame(self, fg_color=T.BG_CARD,
                            corner_radius=10, border_width=1, border_color=T.BORDER)
        ctrl.grid(row=3, column=0, padx=28, pady=14, sticky="ew")
        ctrl.grid_columnconfigure(1, weight=1)

        self._toggle_btn = ctk.CTkButton(
            ctrl, text="▶  Start Monitoring", width=180, height=38,
            fg_color=T.SUCCESS, hover_color="#059669",
            text_color=T.TEXT_BRIGHT,
            font=ctk.CTkFont(size=13, weight="bold"),
            corner_radius=8, command=self._toggle)
        self._toggle_btn.grid(row=0, column=0, padx=14, pady=12)

        self._threat_count_lbl = ctk.CTkLabel(
            ctrl, text="Total threats detected: 0",
            font=ctk.CTkFont(size=12), text_color=T.TEXT_SECONDARY)
        self._threat_count_lbl.grid(row=0, column=1, padx=8)

        T.ghost_btn(ctrl, text="🗑  Clear Log", width=130, height=36,
                    command=self._clear_log).grid(row=0, column=2, padx=14, pady=12)

        # ── Live log ──────────────────────────────────────────────────
        log_card = T.card(self)
        log_card.grid(row=4, column=0, padx=28, pady=(0, 24), sticky="nsew")
        self.grid_rowconfigure(4, weight=1)
        log_card.grid_columnconfigure(0, weight=1)
        log_card.grid_rowconfigure(1, weight=1)

        lhdr = ctk.CTkFrame(log_card, fg_color="transparent")
        lhdr.grid(row=0, column=0, padx=14, pady=(12, 4), sticky="ew")
        ctk.CTkLabel(lhdr, text="Live Feed",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=T.TEXT_PRIMARY).pack(side="left")
        self._auto_lbl = ctk.CTkLabel(lhdr, text="● Auto-refresh ON",
                                      font=ctk.CTkFont(size=11),
                                      text_color=T.SUCCESS)
        self._auto_lbl.pack(side="right")

        self._log_box = ctk.CTkTextbox(
            log_card, fg_color=T.BG_INPUT,
            text_color=T.TEXT_SECONDARY,
            font=ctk.CTkFont(family="Consolas", size=11),
            border_width=0, corner_radius=8)
        self._log_box.grid(row=1, column=0, padx=14, pady=(0, 14), sticky="nsew")
        self._log_box.configure(state="disabled")

    def _toggle(self):
        if self.monitor.is_running:
            self.monitor.stop()
            self._toggle_btn.configure(text="▶  Start Monitoring", fg_color=T.SUCCESS)
            self._status_badge.configure(text="  ● STOPPED  ",
                                         text_color=T.DANGER, fg_color=T.DANGER_DIM)
            for lbl in self._sensor_labels.values():
                lbl.configure(text="● IDLE", text_color=T.TEXT_MUTED)
        else:
            self.monitor.start()
            self._toggle_btn.configure(text="⏹  Stop Monitoring", fg_color=T.DANGER)
            self._status_badge.configure(text="  ● RUNNING  ",
                                         text_color=T.SUCCESS, fg_color=T.SUCCESS_DIM)
            for key, lbl in self._sensor_labels.items():
                lbl.configure(text="● ACTIVE", text_color=T.SUCCESS)

    def _clear_log(self):
        try:
            open("data/safenet_audit.log", "w").close()
        except Exception:
            pass

    def _watch_log(self):
        last_mtime = 0
        while self._running:
            try:
                log = "data/safenet_audit.log"
                if os.path.exists(log):
                    mtime = os.path.getmtime(log)
                    if mtime != last_mtime:
                        last_mtime = mtime
                        with open(log, "r") as f:
                            lines = f.readlines()
                        threats = sum(1 for l in lines if "Threat:" in l)
                        self._log_box.configure(state="normal")
                        self._log_box.delete("1.0", "end")
                        for line in lines[-50:]:
                            tag_color = T.DANGER if "Threat:" in line else T.TEXT_SECONDARY
                            self._log_box.insert("end", line)
                        self._log_box.configure(state="disabled")
                        self._threat_count_lbl.configure(
                            text=f"Total threats detected: {threats}")
            except Exception:
                pass
            time.sleep(2)

    def destroy(self):
        self._running = False
        super().destroy()
