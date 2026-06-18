"""main.py — SafeNet Kids application entry point and state controller."""
import customtkinter as ctk
import os
from core.monitor import SafeNetMonitor
from core.process_manager import ProcessManager
from core.auth_manager import AuthManager

from gui import theme as T
from gui.pages.splash_screen import SplashScreen
from gui.pages.login_page import LoginPage
from gui.pages.register_page import RegisterPage
from gui.pages.forgot_password_page import ForgotPasswordPage
from gui.dashboard import Dashboard


class SafeNetApp(ctk.CTk):
    """
    Main application class that manages window state and page transitions.
    Transitions: Splash -> Login <-> (Register | Forgot) -> Dashboard
    """

    def __init__(self):
        super().__init__()
        
        # Initial Window Setup
        self.title("SafeNet Kids — Intelligence & Protection")
        self.geometry("1100x700")
        self.resizable(False, False)
        self.configure(fg_color=T.BG_ROOT)
        self.withdraw()  # Start hidden

        # Backend Modules
        self._init_backend()

        # State Variables
        self.current_page = None

        # Start with Splash Screen
        self._show_splash()

    def _init_backend(self):
        os.makedirs("data", exist_ok=True)
        if not os.path.exists("data/safenet_audit.log"):
            open("data/safenet_audit.log", "w").close()

        self.auth_manager = AuthManager()
        self.process_manager = ProcessManager()
        self.monitor = SafeNetMonitor(
            "data/threat_database.json",
            "data/safenet_audit.log",
            self.process_manager
        )

        # Handle app closure
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _on_closing(self):
        self.monitor.stop()
        self.process_manager.stop_process_blocker()
        self.destroy()

    def _clear_window(self):
        if self.current_page:
            self.current_page.destroy()

    # ── Page Transitions ──────────────────────────────────────────────

    def _show_splash(self):
        self.deiconify()
        self.current_page = SplashScreen(self, on_done=self._show_login)
        self.current_page.pack(fill="both", expand=True)

    def _show_login(self, username_to_fill=None):
        self._clear_window()
        self.title("SafeNet Kids — Sign In")
        self.current_page = LoginPage(
            self, self.auth_manager,
            on_login=self._show_dashboard,
            on_register=self._show_register,
            on_forgot=self._show_forgot
        )
        self.current_page.pack(fill="both", expand=True)

    def _show_register(self):
        self._clear_window()
        self.title("SafeNet Kids — Create Account")
        self.current_page = RegisterPage(
            self, self.auth_manager,
            on_registered=self._show_dashboard,
            on_back=self._show_login
        )
        self.current_page.pack(fill="both", expand=True)

    def _show_forgot(self):
        self._clear_window()
        self.title("SafeNet Kids — Reset Password")
        self.current_page = ForgotPasswordPage(
            self, self.auth_manager,
            on_back=self._show_login
        )
        self.current_page.pack(fill="both", expand=True)

    def _show_dashboard(self, username):
        self._clear_window()
        self.title(f"SafeNet Kids Control Center — {self.auth_manager.get_display_name(username)}")
        self.current_page = Dashboard(
            self, self.monitor, self.process_manager, 
            self.auth_manager, username,
            on_logout=self._show_login
        )
        self.current_page.pack(fill="both", expand=True)


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    app = SafeNetApp()
    app.mainloop()