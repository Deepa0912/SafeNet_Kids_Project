"""gui/pages/splash_screen.py — Animated splash screen."""
import customtkinter as ctk
from gui import theme as T


class SplashScreen(ctk.CTkFrame):
    """Full-window animated splash. Calls on_done() after ~2.5 s."""

    def __init__(self, master, on_done):
        super().__init__(master, fg_color=T.BG_ROOT, corner_radius=0)
        self.on_done = on_done
        self._progress = 0
        self._build()
        self.after(200, self._animate)

    # ── Build ─────────────────────────────────────────────────────────

    def _build(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        center = ctk.CTkFrame(self, fg_color="transparent")
        center.grid(row=0, column=0)

        # Shield icon + title
        ctk.CTkLabel(
            center, text="🛡️",
            font=ctk.CTkFont(size=80),
        ).pack(pady=(0, 8))

        ctk.CTkLabel(
            center, text="SafeNet Kids",
            font=ctk.CTkFont(family="Segoe UI", size=42, weight="bold"),
            text_color=T.CYAN,
        ).pack()

        ctk.CTkLabel(
            center,
            text="Advanced Parental Control & Threat Detection System",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=T.TEXT_SECONDARY,
        ).pack(pady=(6, 0))

        # Divider line
        ctk.CTkFrame(
            center, height=1, width=360, fg_color=T.BORDER,
        ).pack(pady=28)

        # Progress bar
        self._bar = ctk.CTkProgressBar(
            center, width=360, height=6,
            fg_color=T.BG_CARD,
            progress_color=T.CYAN,
            corner_radius=3,
        )
        self._bar.set(0)
        self._bar.pack()

        self._status_lbl = ctk.CTkLabel(
            center, text="Initializing security modules…",
            font=ctk.CTkFont(size=11),
            text_color=T.TEXT_MUTED,
        )
        self._status_lbl.pack(pady=(10, 0))

        # Version tag
        ctk.CTkLabel(
            self, text="v2.0.0  |  © 2025 SafeNet Labs",
            font=ctk.CTkFont(size=10),
            text_color=T.TEXT_MUTED,
        ).grid(row=1, column=0, pady=(0, 16))

    # ── Animation ─────────────────────────────────────────────────────

    _STEPS = [
        (0.15, "Loading threat database…"),
        (0.35, "Starting NLP analyzer…"),
        (0.55, "Initializing image scanner…"),
        (0.75, "Configuring process monitor…"),
        (0.95, "Applying security policies…"),
        (1.00, "Ready."),
    ]

    def _animate(self):
        if not self._steps_remaining:
            self._steps_remaining = list(self._STEPS)
        target, label = self._steps_remaining.pop(0)
        self._bar.set(target)
        self._status_lbl.configure(text=label)
        if self._steps_remaining:
            self.after(380, self._animate)
        else:
            self.after(500, self.on_done)

    def _steps_remaining_init(self):
        self._steps_remaining = list(self._STEPS)

    # override after() to lazily init the step list
    def _animate(self):
        if not hasattr(self, "_steps_remaining"):
            self._steps_remaining = list(self._STEPS)
        if not self._steps_remaining:
            self.after(400, self.on_done)
            return
        target, label = self._steps_remaining.pop(0)
        self._bar.set(target)
        self._status_lbl.configure(text=label)
        self.after(380, self._animate)
