"""gui/auth_window.py — Password confirmation popup (Parent Auth)."""
import customtkinter as ctk
from gui import theme as T
from core.auth_manager import AuthManager


class AuthWindow(ctk.CTkToplevel):
    """
    Password confirmation popup to gate sensitive monitoring controls.
    Styled to match the cyber-security theme.
    """

    def __init__(self, master, auth_manager: AuthManager, username: str, on_success):
        super().__init__(master)
        self.title("Parent Verification")
        self.geometry("380x280")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.configure(fg_color=T.BG_PRIMARY)
        self.grab_set()

        self.auth_manager = auth_manager
        self.username = username
        self.on_success = on_success

        self.password_var = ctk.StringVar()
        self._build_ui()

    def _build_ui(self):
        # Card style container
        card = T.card(self, fg_color=T.BG_CARD)
        card.pack(fill="both", expand=True, padx=20, pady=20)

        # Icon and Title
        ctk.CTkLabel(card, text="🔒", font=ctk.CTkFont(size=32)).pack(pady=(16, 4))
        ctk.CTkLabel(card, text="Parent Verification", font=T.bold(18), text_color=T.TEXT_PRIMARY).pack()
        
        display_name = self.auth_manager.get_display_name(self.username)
        ctk.CTkLabel(card, text=f"Confirm access for admin: {display_name}", 
                     font=T.font(11), text_color=T.TEXT_MUTED).pack(pady=(0, 16))

        # Password Input
        self.password_entry = T.entry(card, placeholder="Enter parent password", show="•", var=self.password_var)
        self.password_entry.pack(fill="x", padx=30, pady=4)
        self.password_entry.bind("<Return>", lambda e: self.verify_password())
        self.password_entry.focus()

        # Error Label
        self.error_label = ctk.CTkLabel(card, text="", font=T.font(11), text_color=T.DANGER)
        self.error_label.pack(pady=4)

        # Action Buttons
        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.pack(fill="x", padx=30, pady=(4, 16))
        
        T.ghost_btn(btn_row, text="Cancel", command=self.destroy, width=100, height=36).pack(side="left", padx=(0, 10))
        T.primary_btn(btn_row, text="Confirm", command=self.verify_password, width=150, height=36).pack(side="right")

    def verify_password(self):
        if self.auth_manager.verify_parent_password(self.username, self.password_var.get()):
            self.grab_release()
            self.on_success()
            self.destroy()
        else:
            self.error_label.configure(text="❌  Incorrect parent password.")
            self.password_entry.configure(border_color=T.DANGER)