import customtkinter as ctk
from core.auth_manager import AuthManager


class LoginWindow(ctk.CTkToplevel):
    """Full-screen sign-in / sign-up window shown before the main dashboard."""

    ACCENT = "#2563EB"
    ACCENT_HOVER = "#1D4ED8"
    DANGER = "#EF4444"
    SUCCESS = "#22C55E"
    BG_CARD = "#1E2435"

    def __init__(self, master, auth_manager: AuthManager, on_login_success):
        super().__init__(master)
        self.auth_manager = auth_manager
        self.on_login_success = on_login_success

        self.title("SafeNet Kids — Welcome")
        self.geometry("500x640")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.grab_set()
        self.focus()

        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        self.configure(fg_color="#12172B")

        # ── Header ────────────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(pady=(30, 0))

        ctk.CTkLabel(
            header,
            text="🛡️ SafeNet Kids",
            font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold"),
            text_color="#E2E8F0",
        ).pack()

        ctk.CTkLabel(
            header,
            text="Protect · Monitor · Secure",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#64748B",
        ).pack(pady=(2, 0))

        # ── Card ──────────────────────────────────────────────────────
        card = ctk.CTkFrame(self, fg_color=self.BG_CARD, corner_radius=16)
        card.pack(padx=50, pady=20, fill="both", expand=True)

        # Tab buttons
        tab_row = ctk.CTkFrame(card, fg_color="transparent")
        tab_row.pack(fill="x", padx=24, pady=(18, 0))

        self._signin_tab_btn = ctk.CTkButton(
            tab_row, text="Sign In", width=150, height=36,
            corner_radius=8,
            fg_color=self.ACCENT, hover_color=self.ACCENT_HOVER,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._show_signin,
        )
        self._signin_tab_btn.pack(side="left", padx=(0, 8))

        self._signup_tab_btn = ctk.CTkButton(
            tab_row, text="Sign Up", width=150, height=36,
            corner_radius=8,
            fg_color="#2D3748", hover_color="#374151",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._show_signup,
        )
        self._signup_tab_btn.pack(side="left")

        # ── Status label — fixed slot BELOW tabs, always visible ──────
        self._status_var = ctk.StringVar(value="")
        self._status_label = ctk.CTkLabel(
            card, textvariable=self._status_var,
            font=ctk.CTkFont(size=12),
            text_color=self.DANGER,
            height=22,
        )
        self._status_label.pack(pady=(6, 0))

        # ── Scrollable content area ────────────────────────────────────
        self._content = ctk.CTkFrame(card, fg_color="transparent")
        self._content.pack(fill="both", expand=True, padx=24, pady=(4, 18))

        self._build_signin_frame()
        self._build_signup_frame()
        self._show_signin()

        # Bind Enter key at window level
        self.bind("<Return>", self._on_enter)

    # -- Sign-In frame ------------------------------------------------

    def _build_signin_frame(self):
        f = ctk.CTkFrame(self._content, fg_color="transparent")
        self._signin_frame = f

        self._si_user_var = ctk.StringVar()
        self._si_pass_var = ctk.StringVar()

        self._make_field(f, "Username", self._si_user_var)
        self._make_field(f, "Password", self._si_pass_var, is_password=True)

        ctk.CTkButton(
            f, text="Sign In →", height=42, corner_radius=10,
            fg_color=self.ACCENT, hover_color=self.ACCENT_HOVER,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._do_signin,
        ).pack(fill="x", pady=(20, 0))

    # -- Sign-Up frame ------------------------------------------------

    def _build_signup_frame(self):
        f = ctk.CTkFrame(self._content, fg_color="transparent")
        self._signup_frame = f

        self._su_user_var = ctk.StringVar()
        self._su_pass_var = ctk.StringVar()
        self._su_confirm_var = ctk.StringVar()
        self._su_parent_var = ctk.StringVar()

        self._make_field(f, "Username", self._su_user_var)
        self._make_field(f, "Password", self._su_pass_var, is_password=True)
        self._make_field(f, "Confirm Password", self._su_confirm_var, is_password=True)

        ctk.CTkLabel(
            f,
            text="Parent / Admin Password  (used to control monitoring)",
            font=ctk.CTkFont(size=11),
            text_color="#94A3B8",
        ).pack(anchor="w", pady=(10, 2))
        self._make_field(f, "Parent Password", self._su_parent_var, is_password=True, skip_label=True)

        ctk.CTkButton(
            f, text="Create Account →", height=42, corner_radius=10,
            fg_color="#059669", hover_color="#047857",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._do_signup,
        ).pack(fill="x", pady=(16, 0))

    # ------------------------------------------------------------------
    # Helper: field builder
    # ------------------------------------------------------------------

    def _make_field(self, parent, label: str, var, is_password=False, skip_label=False):
        if not skip_label:
            ctk.CTkLabel(
                parent, text=label,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#CBD5E1",
            ).pack(anchor="w", pady=(8, 2))
        entry = ctk.CTkEntry(
            parent, textvariable=var, height=38, corner_radius=8,
            show="•" if is_password else "",
            fg_color="#0F172A", border_color="#334155",
            font=ctk.CTkFont(size=13),
        )
        entry.pack(fill="x")

    # ------------------------------------------------------------------
    # Tab switching
    # ------------------------------------------------------------------

    def _show_signin(self):
        self._signup_frame.pack_forget()
        self._signin_frame.pack(fill="both", expand=True)
        self._signin_tab_btn.configure(fg_color=self.ACCENT)
        self._signup_tab_btn.configure(fg_color="#2D3748")
        self._status_var.set("")

    def _show_signup(self):
        self._signin_frame.pack_forget()
        self._signup_frame.pack(fill="both", expand=True)
        self._signup_tab_btn.configure(fg_color=self.ACCENT)
        self._signin_tab_btn.configure(fg_color="#2D3748")
        self._status_var.set("")

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _on_enter(self, event=None):
        if self._signin_frame.winfo_ismapped():
            self._do_signin()
        else:
            self._do_signup()

    def _set_error(self, msg: str):
        self._status_label.configure(text_color=self.DANGER)
        self._status_var.set(msg)

    def _set_success(self, msg: str):
        self._status_label.configure(text_color=self.SUCCESS)
        self._status_var.set(msg)

    def _do_signin(self):
        username = self._si_user_var.get().strip()
        password = self._si_pass_var.get()
        if not username or not password:
            self._set_error("Please enter both username and password.")
            return
        ok, err = self.auth_manager.login(username, password)
        if not ok:
            self._set_error(f"❌  {err}")
        else:
            display = self.auth_manager.get_display_name(username)
            self._set_success(f"✅  Welcome back, {display}!")
            self.after(600, lambda: self._finish(display))

    def _do_signup(self):
        username = self._su_user_var.get().strip()
        password = self._su_pass_var.get()
        confirm  = self._su_confirm_var.get()
        parent   = self._su_parent_var.get()

        if not username or not password or not confirm or not parent:
            self._set_error("All fields are required.")
            return
        if password != confirm:
            self._set_error("Passwords do not match.")
            return

        ok, err = self.auth_manager.register(username, password, parent)
        if not ok:
            self._set_error(f"❌  {err}")
        else:
            self._set_success(f"✅  Account created! Signing in as {username}…")
            self.after(700, lambda: self._finish(username))

    def _finish(self, username: str):
        self.grab_release()
        self.destroy()
        self.on_login_success(username)
