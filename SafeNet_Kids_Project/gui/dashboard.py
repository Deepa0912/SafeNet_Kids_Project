"""gui/dashboard.py — Main dashboard shell with sidebar navigation."""
import customtkinter as ctk
from gui import theme as T
from gui.pages.home_page import HomePage
from gui.pages.threat_monitor_page import ThreatMonitorPage
from gui.pages.activity_logs_page import ActivityLogsPage
from gui.pages.threat_database_page import ThreatDatabasePage
from gui.pages.settings_page import SettingsPage


class Dashboard(ctk.CTkFrame):
    """
    Main dashboard shell containing the sidebar and a content area
    where different pages are swapped in/out.
    """

    def __init__(self, master, monitor, process_manager, auth_manager, username, on_logout):
        super().__init__(master, fg_color=T.BG_PRIMARY, corner_radius=0)
        self.monitor = monitor
        self.process_manager = process_manager
        self.auth_manager = auth_manager
        self.username = username
        self.on_logout_callback = on_logout

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._current_page = None
        self._nav_buttons = {}

        self._build_sidebar()
        self._build_content_area()

        # Show home page by default
        self._show_page("home")

    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=240, fg_color=T.BG_SIDEBAR, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_rowconfigure(7, weight=1)

        # Logo
        logo_row = ctk.CTkFrame(sidebar, fg_color="transparent")
        logo_row.pack(fill="x", padx=20, pady=(32, 24))
        ctk.CTkLabel(logo_row, text="🛡️", font=ctk.CTkFont(size=28)).pack(side="left", padx=(10, 10))
        ctk.CTkLabel(logo_row, text="SafeNet", font=T.bold(20), text_color=T.TEXT_PRIMARY).pack(side="left")
        ctk.CTkLabel(logo_row, text="Kids", font=T.bold(20), text_color=T.CYAN).pack(side="left")

        # Nav Items
        self._add_nav_item(sidebar, "Home", "🏠", "home")
        self._add_nav_item(sidebar, "Threat Monitor", "🔍", "monitor")
        self._add_nav_item(sidebar, "Activity Logs", "📋", "logs")
        self._add_nav_item(sidebar, "Settings", "⚙️", "settings")

        # User Info at Bottom
        user_card = ctk.CTkFrame(sidebar, fg_color=T.BG_CARD, corner_radius=12)
        user_card.pack(side="bottom", padx=16, pady=24, fill="x")
        
        display_name = self.auth_manager.get_display_name(self.username)
        ctk.CTkLabel(user_card, text="👤", font=ctk.CTkFont(size=20)).pack(side="left", padx=(12, 8), pady=12)
        
        vbox = ctk.CTkFrame(user_card, fg_color="transparent")
        vbox.pack(side="left", fill="both", expand=True)
        ctk.CTkLabel(vbox, text=display_name, font=T.bold(13), text_color=T.TEXT_PRIMARY, anchor="w").pack(fill="x", pady=(8, 0))
        ctk.CTkLabel(vbox, text="Parent Admin", font=T.font(11), text_color=T.TEXT_MUTED, anchor="w").pack(fill="x", pady=(0, 8))

    def _add_nav_item(self, parent, text, icon, page_id):
        btn = ctk.CTkButton(
            parent, text=f"  {icon}   {text}", anchor="w",
            fg_color="transparent", hover_color=T.BG_HOVER,
            text_color=T.TEXT_SECONDARY, font=T.font(13),
            height=44, corner_radius=8,
            command=lambda: self._show_page(page_id)
        )
        btn.pack(fill="x", padx=12, pady=2)
        self._nav_buttons[page_id] = btn

    def _build_content_area(self):
        self.content_frame = ctk.CTkFrame(self, fg_color=T.BG_PRIMARY, corner_radius=0)
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

    def _show_page(self, page_id):
        # Update Nav Styles
        for pid, btn in self._nav_buttons.items():
            if pid == page_id:
                btn.configure(fg_color=T.BG_CARD, text_color=T.CYAN, font=T.bold(13))
            else:
                btn.configure(fg_color="transparent", text_color=T.TEXT_SECONDARY, font=T.font(13))

        # Destroy current page
        if self._current_page:
            self._current_page.destroy()

        # Swapping logic
        if page_id == "home":
            self._current_page = HomePage(self.content_frame, self.monitor, self.username)
        elif page_id == "monitor":
            from gui.auth_window import AuthWindow  # late import to avoid cycle
            
            def on_auth_success():
                self._current_page = ThreatMonitorPage(
                    self.content_frame, self.monitor, self.process_manager, 
                    self.auth_manager, self.username
                )
                self._current_page.grid(row=0, column=0, sticky="nsew")

            # Monitoring might require parent auth if not already running?
            # Or just show it. Let's just show it for now as per user request flow.
            self._current_page = ThreatMonitorPage(
                self.content_frame, self.monitor, self.process_manager, 
                self.auth_manager, self.username
            )
        elif page_id == "logs":
            self._current_page = ActivityLogsPage(self.content_frame)
        elif page_id == "database":
            self._current_page = ThreatDatabasePage(self.content_frame, self.monitor)
        elif page_id == "settings":
            self._current_page = SettingsPage(
                self.content_frame, self.auth_manager, self.monitor,
                self.username, self.on_logout_callback
            )

        if self._current_page:
            self._current_page.grid(row=0, column=0, sticky="nsew")

    def logout(self):
        self.monitor.stop()
        self.process_manager.stop_process_blocker()
        self.destroy()
        if self.on_logout_callback:
            self.on_logout_callback()