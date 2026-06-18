"""gui/pages/activity_logs_page.py — Activity logs viewer with filters."""
import customtkinter as ctk
import os, time, threading
from gui import theme as T


class ActivityLogsPage(ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(master, fg_color=T.BG_PRIMARY, corner_radius=0)
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

        # ── Log textbox ───────────────────────────────────────────────
        log_card = T.card(self)
        log_card.grid(row=3, column=0, padx=28, pady=(0, 24), sticky="nsew")
        log_card.grid_columnconfigure(0, weight=1)
        log_card.grid_rowconfigure(0, weight=1)

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
            log = "data/safenet_audit.log"
            if os.path.exists(log):
                with open(log, "r") as f:
                    self._all_lines = f.readlines()
            else:
                self._all_lines = []
        except Exception:
            self._all_lines = []
        self._apply_filter()

    def _apply_filter(self):
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
            open("data/safenet_audit.log", "w").close()
        except Exception:
            pass
        self._all_lines = []
        self._apply_filter()

    def _watch(self):
        last_mtime = 0
        while self._running:
            try:
                log = "data/safenet_audit.log"
                if os.path.exists(log):
                    m = os.path.getmtime(log)
                    if m != last_mtime:
                        last_mtime = m
                        self._load()
            except Exception:
                pass
            time.sleep(3)

    def destroy(self):
        self._running = False
        super().destroy()
