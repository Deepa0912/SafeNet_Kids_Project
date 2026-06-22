"""gui/pages/forgot_password_page.py — Forgot / Reset Password page."""
import customtkinter as ctk
from gui import theme as T


class ForgotPasswordPage(ctk.CTkFrame):
    """
    Two-step flow:
      Step 1 — enter username, show hint.
      Step 2 — enter current parent password + new password to reset.
    Calls on_back() to return to login.
    """

    def __init__(self, master, auth_manager, on_back):
        super().__init__(master, fg_color=T.BG_PRIMARY, corner_radius=0)
        self.auth_manager = auth_manager
        self.on_back = on_back

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        outer = ctk.CTkFrame(self, fg_color="transparent")
        outer.grid(row=0, column=0)

        # Card
        card = ctk.CTkFrame(outer, fg_color=T.BG_CARD,
                            corner_radius=16, border_width=1, border_color=T.BORDER,
                            width=480)
        card.pack(padx=0, pady=0)
        card.grid_columnconfigure(0, weight=1)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", padx=44, pady=36)
        inner.grid_columnconfigure(0, weight=1)

        # Icon + title
        ctk.CTkLabel(inner, text="🔑",
                     font=ctk.CTkFont(size=42)).pack()
        ctk.CTkLabel(inner, text="Reset Password",
                     font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
                     text_color=T.TEXT_PRIMARY).pack(pady=(4, 2))
        ctk.CTkLabel(inner, text="Reset your account password using your parent password",
                     font=ctk.CTkFont(size=11),
                     text_color=T.TEXT_SECONDARY,
                     wraplength=380).pack()

        ctk.CTkFrame(inner, height=1, fg_color=T.BORDER).pack(fill="x", pady=20)

        # Status
        self._status_var = ctk.StringVar()
        self._status_lbl = ctk.CTkLabel(inner, textvariable=self._status_var,
                                        font=ctk.CTkFont(size=12),
                                        text_color=T.DANGER, height=18,
                                        wraplength=380)
        self._status_lbl.pack()

        # Fields
        def lbl(t):
            ctk.CTkLabel(inner, text=t, font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=T.TEXT_SECONDARY).pack(anchor="w", pady=(12, 2))

        self._user_var       = ctk.StringVar()
        self._parent_var     = ctk.StringVar()
        self._new_pass_var   = ctk.StringVar()
        self._confirm_var    = ctk.StringVar()

        lbl("Username")
        T.entry(inner, placeholder="Enter your username",
                var=self._user_var).pack(fill="x")

        lbl("Current Parent Password")
        T.entry(inner, placeholder="Your parent / admin password",
                show="•", var=self._parent_var).pack(fill="x")

        ctk.CTkFrame(inner, height=1, fg_color=T.BORDER).pack(fill="x", pady=14)

        lbl("New Account Password")
        T.entry(inner, placeholder="Min. 4 characters",
                show="•", var=self._new_pass_var).pack(fill="x")

        lbl("Confirm New Password")
        T.entry(inner, placeholder="Re-enter new password",
                show="•", var=self._confirm_var).pack(fill="x")

        # Buttons
        T.primary_btn(inner, "Reset Password", command=self._do_reset,
                      height=44).pack(fill="x", pady=(24, 0))

        ctk.CTkButton(inner, text="← Back to Sign In",
                      fg_color="transparent", hover_color=T.BG_HOVER,
                      text_color=T.TEXT_SECONDARY, font=ctk.CTkFont(size=12),
                      command=self.on_back, cursor="hand2").pack(pady=(10, 0))

    # ── Action ────────────────────────────────────────────────────────

    def _do_reset(self):
        u   = self._user_var.get().strip()
        pp  = self._parent_var.get()
        np  = self._new_pass_var.get()
        cnp = self._confirm_var.get()

        if not all([u, pp, np, cnp]):
            self._err("All fields are required.")
            return
        if not self.auth_manager.username_exists(u):
            self._err("Username not found.")
            return
        if not self.auth_manager.verify_parent_password(u, pp):
            self._err("Incorrect parent password.")
            return
        if np != cnp:
            self._err("New passwords do not match.")
            return
        if len(np) < 4:
            self._err("Password must be at least 4 characters.")
            return

        # Re-register updates password keeping parent password
        import json, hashlib, secrets, os
        users_file = os.path.join("data", "users.json")
        with open(users_file, "r") as f:
            users = json.load(f)
        key = u.lower()
        salt = secrets.token_hex(16)
        users[key]["salt"] = salt
        users[key]["hashed_password"] = hashlib.sha256((salt + np).encode()).hexdigest()
        with open(users_file, "w") as f:
            json.dump(users, f, indent=2)

        self._status_var.set("✅  Password reset successfully! You can now sign in.")
        self._status_lbl.configure(text_color=T.SUCCESS)
        for v in (self._user_var, self._parent_var, self._new_pass_var, self._confirm_var):
            v.set("")

    def _err(self, msg):
        self._status_var.set(f"❌  {msg}")
        self._status_lbl.configure(text_color=T.DANGER)

    def reset(self):
        for v in (self._user_var, self._parent_var, self._new_pass_var, self._confirm_var):
            v.set("")
        self._status_var.set("")
