import customtkinter as ctk
import json
import os
from gui import theme as T

class ThreatDatabasePage(ctk.CTkFrame):
    """
    Threat Database Management page.
    Allows parents to customize monitored keywords and blocked websites.
    """

    def __init__(self, master, monitor):
        super().__init__(master, fg_color=T.BG_PRIMARY, corner_radius=0)
        self.monitor = monitor
        self.db_path = "data/threat_database.json"
        self._load_data()
        self._build()

    def _load_data(self):
        try:
            with open(self.db_path, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        except Exception:
            self.data = {"categories": {}, "blocked_sites": [], "blocked_apps": [], "active_hours": {}}

    def _save_data(self):
        try:
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
            self.monitor.reload_database()
        except Exception as e:
            print(f"Error saving database: {e}")

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Header
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0, column=0, padx=28, pady=(24, 0), sticky="ew")
        
        ctk.CTkLabel(hdr, text="🗄️  Threat Database",
                     font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
                     text_color=T.TEXT_PRIMARY).pack(side="left")

        ctk.CTkLabel(self, text="Customize monitored keywords and blocked websites",
                     font=ctk.CTkFont(size=12), text_color=T.TEXT_SECONDARY
                     ).grid(row=1, column=0, padx=28, sticky="w", pady=(2, 16))

        # Tabs
        self.tabs = ctk.CTkTabview(self, fg_color=T.BG_SECONDARY, segmented_button_selected_color=T.CYAN)
        self.tabs.grid(row=2, column=0, padx=28, pady=(0, 24), sticky="nsew")
        
        self.tabs.add("Keywords")
        self.tabs.add("Blocked Sites")
        self.tabs.add("Blocked Apps")
        self.tabs.add("Schedule")

        self._build_keywords_tab()
        self._build_sites_tab()
        self._build_apps_tab()
        self._build_schedule_tab()

    def _build_keywords_tab(self):
        tab = self.tabs.tab("Keywords")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)

        # Category Selector & Add Keyword
        top = ctk.CTkFrame(tab, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        self.cat_var = ctk.StringVar(value=list(self.data["categories"].keys())[0] if self.data["categories"] else "")
        self.cat_menu = ctk.CTkOptionMenu(top, values=list(self.data["categories"].keys()), 
                                         variable=self.cat_var, command=self._refresh_keywords,
                                         fg_color=T.BG_PRIMARY, button_color=T.BG_ACCENT)
        self.cat_menu.pack(side="left", padx=(0, 10))

        self.new_kw_var = ctk.StringVar()
        kw_entry = T.entry(top, placeholder="Add new keyword...", var=self.new_kw_var)
        kw_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        T.primary_btn(top, "Add", width=80, command=self._add_keyword).pack(side="right")

        # Scrollable List
        self.kw_list = ctk.CTkScrollableFrame(tab, fg_color=T.BG_PRIMARY)
        self.kw_list.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self._refresh_keywords()

    def _build_sites_tab(self):
        tab = self.tabs.tab("Blocked Sites")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)

        top = ctk.CTkFrame(tab, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        self.new_site_var = ctk.StringVar()
        site_entry = T.entry(top, placeholder="Add website (e.g. gambling.com)...", var=self.new_site_var)
        site_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        T.primary_btn(top, "Block Site", width=100, command=self._add_site).pack(side="right")

        self.site_list = ctk.CTkScrollableFrame(tab, fg_color=T.BG_PRIMARY)
        self.site_list.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self._refresh_sites()

    def _refresh_keywords(self, _=None):
        for widget in self.kw_list.winfo_children():
            widget.destroy()
        
        cat = self.cat_var.get()
        if not cat or cat not in self.data["categories"]:
            return

        for kw in self.data["categories"][cat]:
            row = ctk.CTkFrame(self.kw_list, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=2)
            ctk.CTkLabel(row, text=kw, font=ctk.CTkFont(size=12)).pack(side="left")
            T.danger_btn(row, "Remove", width=70, height=24, 
                         command=lambda k=kw: self._remove_keyword(k)).pack(side="right")

    def _refresh_sites(self):
        for widget in self.site_list.winfo_children():
            widget.destroy()
        
        for site in self.data["blocked_sites"]:
            row = ctk.CTkFrame(self.site_list, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=2)
            ctk.CTkLabel(row, text=site, font=ctk.CTkFont(size=12)).pack(side="left")
            T.danger_btn(row, "Remove", width=70, height=24, 
                         command=lambda s=site: self._remove_site(s)).pack(side="right")

    def _add_keyword(self):
        cat = self.cat_var.get()
        kw = self.new_kw_var.get().strip()
        if kw and cat:
            if kw not in self.data["categories"][cat]:
                self.data["categories"][cat].append(kw)
                self._save_data()
                self._refresh_keywords()
                self.new_kw_var.set("")

    def _remove_keyword(self, kw):
        cat = self.cat_var.get()
        if cat in self.data["categories"] and kw in self.data["categories"][cat]:
            self.data["categories"][cat].remove(kw)
            self._save_data()
            self._refresh_keywords()

    def _add_site(self):
        site = self.new_site_var.get().strip().lower()
        if site:
            if site not in self.data["blocked_sites"]:
                self.data["blocked_sites"].append(site)
                self._save_data()
                self._refresh_sites()
                self.new_site_var.set("")

    def _remove_site(self, site):
        if site in self.data["blocked_sites"]:
            self.data["blocked_sites"].remove(site)
            self._save_data()
            self._refresh_sites()

    def _build_apps_tab(self):
        tab = self.tabs.tab("Blocked Apps")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)

        top = ctk.CTkFrame(tab, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        self.new_app_var = ctk.StringVar()
        app_entry = T.entry(top, placeholder="Add app process (e.g. discord.exe)...", var=self.new_app_var)
        app_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        T.primary_btn(top, "Block App", width=100, command=self._add_app).pack(side="right")

        self.app_list = ctk.CTkScrollableFrame(tab, fg_color=T.BG_PRIMARY)
        self.app_list.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self._refresh_apps()

    def _refresh_apps(self):
        for widget in self.app_list.winfo_children():
            widget.destroy()
        
        for app in self.data.get("blocked_apps", []):
            row = ctk.CTkFrame(self.app_list, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=2)
            ctk.CTkLabel(row, text=app, font=ctk.CTkFont(size=12)).pack(side="left")
            T.danger_btn(row, "Remove", width=70, height=24, 
                         command=lambda a=app: self._remove_app(a)).pack(side="right")

    def _add_app(self):
        app = self.new_app_var.get().strip().lower()
        if app:
            if "blocked_apps" not in self.data: self.data["blocked_apps"] = []
            if app not in self.data["blocked_apps"]:
                self.data["blocked_apps"].append(app)
                self._save_data()
                self._refresh_apps()
                self.new_app_var.set("")

    def _remove_app(self, app):
        if "blocked_apps" in self.data and app in self.data["blocked_apps"]:
            self.data["blocked_apps"].remove(app)
            self._save_data()
            self._refresh_apps()

    def _build_schedule_tab(self):
        tab = self.tabs.tab("Schedule")
        tab.grid_columnconfigure(0, weight=1)
        
        info = ctk.CTkLabel(tab, text="Set Active Monitoring Hours (24h format)", font=ctk.CTkFont(size=12, slant="italic"))
        info.pack(pady=10)

        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.day_vars = {}

        for day in days:
            row = ctk.CTkFrame(tab, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=5)
            
            ctk.CTkLabel(row, text=day, width=100, anchor="w").pack(side="left")
            
            # Start/End Hour
            hours = [str(i).zfill(2) for i in range(25)]
            
            curr_start, curr_end = self.data.get("active_hours", {}).get(day, [0, 24])
            
            start_var = ctk.StringVar(value=str(curr_start).zfill(2))
            end_var = ctk.StringVar(value=str(curr_end).zfill(2))
            self.day_vars[day] = (start_var, end_var)

            ctk.CTkOptionMenu(row, values=hours, variable=start_var, width=70, 
                             command=lambda _, d=day: self._update_schedule(d)).pack(side="left", padx=5)
            ctk.CTkLabel(row, text="to").pack(side="left")
            ctk.CTkOptionMenu(row, values=hours, variable=end_var, width=70,
                             command=lambda _, d=day: self._update_schedule(d)).pack(side="left", padx=5)

    def _update_schedule(self, day):
        start = int(self.day_vars[day][0].get())
        end = int(self.day_vars[day][1].get())
        
        if "active_hours" not in self.data: self.data["active_hours"] = {}
        self.data["active_hours"][day] = [start, end]
        self._save_data()
        self.monitor.active_hours = self.data["active_hours"]
