"""gui/pages/activity_logs_page.py — Activity logs viewer with filters."""
import customtkinter as ctk
import os, time, threading, csv
from datetime import datetime
from tkinter import filedialog
from gui import theme as T


class ActivityLogsPage(ctk.CTkFrame):

    def __init__(self, master, monitor=None):
        super().__init__(master, fg_color=T.BG_PRIMARY, corner_radius=0)
        self.monitor = monitor
        self._running = True
        self._all_lines = []
        self._build()
        threading.Thread(target=self._watch, daemon=True).start()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # ── Header ────────────────────────────────────────────────────
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0, column=0, padx=28, pady=(24, 4), sticky="ew")
        ctk.CTkLabel(hdr, text="📋  Activity Logs",
                     font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
                     text_color=T.TEXT_PRIMARY).pack(side="left")
        T.ghost_btn(hdr, text="🔄  Refresh", width=110, height=34,
                    command=self._load).pack(side="right")
        T.danger_btn(hdr, text="🗑  Clear", width=100, height=34,
                     command=self._clear).pack(side="right", padx=(0, 8))
        T.primary_btn(hdr, text="📧  Email Summary", width=130, height=34,
                      command=self._send_summary_email).pack(side="right", padx=(0, 8))
        T.primary_btn(hdr, text="📥  Export", width=100, height=34,
                      command=self._export_report).pack(side="right", padx=(0, 8))

        ctk.CTkLabel(self, text="Full audit trail of child activity and detected threats",
                     font=ctk.CTkFont(size=12), text_color=T.TEXT_SECONDARY,
                     ).grid(row=1, column=0, padx=28, sticky="w", pady=(0, 10))

        # ── Filter bar ────────────────────────────────────────────────
        fbar = T.card(self)
        fbar.grid(row=2, column=0, padx=28, pady=(0, 10), sticky="ew")
        fbar.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(fbar, text="Filter:",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=T.TEXT_SECONDARY).grid(row=0, column=0, padx=(14, 8), pady=10)

        self._search_var = ctk.StringVar()
        self._search_var.trace_add("write", lambda *_: self._apply_filter())
        T.entry(fbar, placeholder="Search logs…", var=self._search_var,
                height=36).grid(row=0, column=1, padx=(0, 10), pady=10, sticky="ew")

        self._filter_var = ctk.StringVar(value="All")
        seg = ctk.CTkSegmentedButton(
            fbar, values=["All", "Threats", "Keylog", "Info"],
            variable=self._filter_var,
            selected_color=T.CYAN, selected_hover_color=T.CYAN_DARK,
            unselected_color=T.BG_INPUT, unselected_hover_color=T.BG_HOVER,
            text_color=T.TEXT_PRIMARY, font=ctk.CTkFont(size=12),
            command=lambda _: self._apply_filter(),
        )
        seg.grid(row=0, column=2, padx=(0, 14), pady=10)

        self._count_lbl = ctk.CTkLabel(fbar, text="0 entries",
                                       font=ctk.CTkFont(size=11),
                                       text_color=T.TEXT_MUTED)
        self._count_lbl.grid(row=0, column=3, padx=(0, 14))

        # ── Source Selector ──────────────────────────────────────────
        sbar = T.card(self)
        sbar.grid(row=3, column=0, padx=28, pady=(0, 10), sticky="ew")
        
        ctk.CTkLabel(sbar, text="Log Source:",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=T.TEXT_SECONDARY).pack(side="left", padx=(14, 8), pady=10)
        
        self._source_var = ctk.StringVar(value="Audit Log")
        self._source_map = {
            "Audit Log": "data/safenet_audit.log",
            "Keyboard": "data/keyboard_activity.log",
            "Screen": "data/screen_threats.log",
            "AI Image": "data/moderation_history.log"
        }
        
        source_menu = ctk.CTkOptionMenu(
            sbar, values=list(self._source_map.keys()),
            variable=self._source_var,
            command=lambda _: self._load(),
            fg_color=T.BG_INPUT, button_color=T.BG_INPUT,
            button_hover_color=T.BG_HOVER, text_color=T.TEXT_PRIMARY,
            font=ctk.CTkFont(size=12)
        )
        source_menu.pack(side="left", padx=10, pady=10)

        # ── Log textbox ───────────────────────────────────────────────
        log_card = T.card(self)
        log_card.grid(row=4, column=0, padx=28, pady=(0, 24), sticky="nsew")
        self.grid_rowconfigure(4, weight=1)

        self._log_box = ctk.CTkTextbox(
            log_card, fg_color=T.BG_INPUT,
            text_color=T.TEXT_SECONDARY,
            font=ctk.CTkFont(family="Consolas", size=11),
            border_width=0, corner_radius=8)
        self._log_box.grid(row=0, column=0, padx=12, pady=12, sticky="nsew")
        self._log_box.configure(state="disabled")

        self._load()

    def _load(self):
        try:
            source_name = self._source_var.get()
            log = self._source_map.get(source_name, "data/safenet_audit.log")
            if os.path.exists(log):
                with open(log, "r", encoding='utf-8') as f:
                    self._all_lines = f.readlines()
            else:
                self._all_lines = []
        except Exception:
            self._all_lines = []
        self._apply_filter()

    def _apply_filter(self, return_lines=False):
        keyword  = self._search_var.get().lower()
        category = self._filter_var.get()

        lines = self._all_lines
        if category == "Threats":
            lines = [l for l in lines if "Threat:" in l]
        elif category == "Keylog":
            lines = [l for l in lines if "Key:" in l or "keylog" in l.lower()]
        elif category == "Info":
            lines = [l for l in lines if "Threat:" not in l]
        if keyword:
            lines = [l for l in lines if keyword in l.lower()]

        if return_lines:
            return lines

        self._log_box.configure(state="normal")
        self._log_box.delete("1.0", "end")
        if lines:
            self._log_box.insert("1.0", "".join(lines))
        else:
            self._log_box.insert("1.0", "No log entries match the current filter.")
        self._log_box.configure(state="disabled")
        self._count_lbl.configure(text=f"{len(lines)} entries")

    def _clear(self):
        try:
            source_name = self._source_var.get()
            log = self._source_map.get(source_name, "data/safenet_audit.log")
            open(log, "w").close()
        except Exception:
            pass
        self._all_lines = []
        self._apply_filter()

    def _watch(self):
        last_mtime = 0
        last_source = ""
        while self._running:
            try:
                source_name = self._source_var.get()
                log = self._source_map.get(source_name, "data/safenet_audit.log")
                if os.path.exists(log):
                    m = os.path.getmtime(log)
                    if m != last_mtime or source_name != last_source:
                        last_mtime = m
                        last_source = source_name
                        self._load()
            except Exception:
                pass
            time.sleep(3)

    def destroy(self):
        self._running = False
        super().destroy()

    def _export_report(self):
        """Exports the currently filtered logs to a CSV file."""
        lines = self._apply_filter(return_lines=True)
        if not lines:
            return

        source = self._source_var.get()
        filename = f"SafeNet_{source.replace(' ', '_')}_Report.csv"
        
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile=filename,
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        
        if not path:
            return

        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "Log Entry"])
                for line in lines:
                    parts = line.split(" - ", 2)
                    if len(parts) == 3:
                        writer.writerow([parts[0], parts[2].strip()])
                    else:
                        writer.writerow(["Unknown", line.strip()])
        except Exception:
            pass

    def _send_summary_email(self):
        """Triggers an immediate summary report email via the notification manager."""
        if self.monitor and hasattr(self.monitor, 'notif_manager'):
            self.monitor.notif_manager.generate_summary_report(days=1)
            # Log local success for feedback
            self._log_box.configure(state="normal")
            self._log_box.insert("1.0", f"--- Summary Report Requested at {datetime.now().strftime('%H:%M:%S')} ---\n")
            self._log_box.configure(state="disabled")
