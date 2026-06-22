"""gui/pages/login_page.py — Split-panel Login page."""
import customtkinter as ctk
from gui import theme as T


class LoginPage(ctk.CTkFrame):
    """
    Left: Branding panel.
    Right: Login form card.
    Calls on_login(username), on_register(), on_forgot().
    """

    def __init__(self, master, auth_manager, on_login, on_register, on_forgot):
        super().__init__(master, fg_color=T.BG_PRIMARY, corner_radius=0)
        self.auth_manager = auth_manager
        self.on_login = on_login
        self.on_register = on_register
        self.on_forgot = on_forgot

        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

        self._build_left()
        self._build_right()

    # ── Left branding panel ───────────────────────────────────────────

    def _build_left(self):
        left = ctk.CTkFrame(self, fg_color=T.BG_SIDEBAR, corner_radius=0)
        left.grid(row=0, column=0, sticky="nsew")
        left.grid_rowconfigure(0, weight=1)
        left.grid_columnconfigure(0, weight=1)

        inner = ctk.CTkFrame(left, fg_color="transparent")
        inner.grid(row=0, column=0, padx=40)

        ctk.CTkLabel(inner, text="🛡️",
                     font=ctk.CTkFont(size=60)).pack(pady=(0, 8))
        ctk.CTkLabel(inner, text="SafeNet Kids",
                     font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"),
                     text_color=T.CYAN).pack()
        ctk.CTkLabel(inner, text="Parental Control & Safety Platform",
                     font=ctk.CTkFont(size=11),
                     text_color=T.TEXT_SECONDARY).pack(pady=(4, 28))

        features = [
            ("🔍", "Real-time NLP threat detection"),
            ("📷", "Computer vision content filter"),
            ("⌨️", "Keystroke activity monitoring"),
            ("🚫", "App & process blocking"),
            ("📊", "Detailed activity reports"),
        ]
        for icon, text in features:
            row = ctk.CTkFrame(inner, fg_color="transparent")
            row.pack(fill="x", pady=4)
            ctk.CTkLabel(row, text=icon,
                         font=ctk.CTkFont(size=14)).pack(side="left", padx=(0, 10))
            ctk.CTkLabel(row, text=text,
                         font=ctk.CTkFont(size=12),
                         text_color=T.TEXT_SECONDARY).pack(side="left")
            back = ctk.CTkButton(inner, text="← Back to Sign In",
                                 fg_color="transparent", hover_color=T.BG_HOVER,
                                 text_color=T.TEXT_SECONDARY,).pack(side="left")

        # Bottom version
        ctk.CTkLabel(left, text="v2.0.0  |  © 2025 SafeNet Labs",
                     font=ctk.CTkFont(size=10),
                     text_color=T.TEXT_MUTED).grid(row=1, column=0, pady=14)
        left.grid_rowconfigure(1, weight=0)

    # ── Right form panel ──────────────────────────────────────────────

    def _build_right(self):
        right = ctk.CTkFrame(self, fg_color=T.BG_PRIMARY, corner_radius=0)
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_rowconfigure(0, weight=1)
        right.grid_columnconfigure(0, weight=1)

        # Card
        card = ctk.CTkFrame(right, fg_color=T.BG_CARD,
                            corner_radius=16, border_width=1, border_color=T.BORDER)
        card.grid(row=0, column=0, padx=60, pady=60, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(0, weight=1)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.grid(row=0, column=0, padx=36, pady=36, sticky="nsew")
        inner.grid_columnconfigure(0, weight=1)

        # Title
        ctk.CTkLabel(inner, text="Welcome Back",
                     font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
                     text_color=T.TEXT_PRIMARY).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(inner, text="Sign in to your parent account",
                     font=ctk.CTkFont(size=12),
                     text_color=T.TEXT_SECONDARY).grid(row=1, column=0, sticky="w", pady=(2, 24))

        # Status label
        self._status_var = ctk.StringVar()
        self._status_lbl = ctk.CTkLabel(inner, textvariable=self._status_var,
                                        font=ctk.CTkFont(size=12),
                                        text_color=T.DANGER, height=18)
        self._status_lbl.grid(row=2, column=0, sticky="w", pady=(0, 4))

        # Fields
        self._user_var = ctk.StringVar()
        self._pass_var = ctk.StringVar()

        ctk.CTkLabel(inner, text="Username", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=T.TEXT_SECONDARY).grid(row=3, column=0, sticky="w")
        T.entry(inner, placeholder="Enter your username",
                var=self._user_var).grid(row=4, column=0, sticky="ew", pady=(4, 12))

        ctk.CTkLabel(inner, text="Password", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=T.TEXT_SECONDARY).grid(row=5, column=0, sticky="w")
        T.entry(inner, placeholder="Enter your password",
                show="•", var=self._pass_var).grid(row=6, column=0, sticky="ew", pady=(4, 6))

        # Forgot password link
        forgot_btn = ctk.CTkButton(
            inner, text="Forgot password?", fg_color="transparent",
            hover_color=T.BG_HOVER, text_color=T.CYAN,
            font=ctk.CTkFont(size=11), width=0, height=20,
            command=self.on_forgot, cursor="hand2")
        forgot_btn.grid(row=7, column=0, sticky="e", pady=(0, 20))

        # Sign In button
        T.primary_btn(inner, text="Sign In →", command=self._do_login,
                      height=44).grid(row=8, column=0, sticky="ew")

        # Divider
        div = ctk.CTkFrame(inner, fg_color="transparent", height=30)
        div.grid(row=9, column=0, sticky="ew")
        ctk.CTkFrame(div, height=1, fg_color=T.BORDER).place(relx=0, rely=0.5, relwidth=1)
        ctk.CTkLabel(div, text="  OR  ", fg_color=T.BG_CARD,
                     font=ctk.CTkFont(size=11),
                     text_color=T.TEXT_MUTED).place(anchor="center", relx=0.5, rely=0.5)

        # Register button
        T.ghost_btn(inner, text="Create New Account",
                    command=self.on_register,
                    height=42).grid(row=10, column=0, sticky="ew", pady=(0, 0))

        self.bind("<Return>", lambda e: self._do_login())

    # ── Action ────────────────────────────────────────────────────────

    def _do_login(self):
        u = self._user_var.get().strip()
        p = self._pass_var.get()
        if not u or not p:
            self._status_var.set("⚠️  Please fill in all fields.")
            self._status_lbl.configure(text_color=T.WARNING)
            return
        ok, err = self.auth_manager.login(u, p)
        if ok:
            self._status_var.set("✅  Authenticated!")
            self._status_lbl.configure(text_color=T.SUCCESS)
            display = self.auth_manager.get_display_name(u)
            self.after(500, lambda: self.on_login(display))
        else:
            self._status_var.set(f"❌  {err}")
            self._status_lbl.configure(text_color=T.DANGER)

    def reset(self):
        self._user_var.set("")
        self._pass_var.set("")
        self._status_var.set("")
