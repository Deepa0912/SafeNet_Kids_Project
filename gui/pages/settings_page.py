"""gui/pages/settings_page.py — App settings (Account, Security, About)."""
import customtkinter as ctk
from gui import theme as T


class SettingsPage(ctk.CTkFrame):

    def __init__(self, master, auth_manager, monitor, username, on_logout):
        super().__init__(master, fg_color=T.BG_PRIMARY, corner_radius=0)
        self.auth_manager = auth_manager
        self.monitor      = monitor
        self.username     = username
        self.on_logout    = on_logout
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)

        # ── Header ────────────────────────────────────────────────────
        ctk.CTkLabel(self, text="⚙️  Settings",
                     font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
                     text_color=T.TEXT_PRIMARY,
                     ).grid(row=0, column=0, padx=28, pady=(24, 2), sticky="w")
        ctk.CTkLabel(self, text="Account, security, and application preferences",
                     font=ctk.CTkFont(size=12), text_color=T.TEXT_SECONDARY,
                     ).grid(row=1, column=0, padx=28, sticky="w", pady=(0, 16))

        # Scrollable container
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent",
                                        scrollbar_button_color=T.BORDER)
        scroll.grid(row=2, column=0, padx=28, pady=(0, 24), sticky="nsew")
        self.grid_rowconfigure(2, weight=1)
        scroll.grid_columnconfigure(0, weight=1)

        r = 0

        # ── Account Section ───────────────────────────────────────────
        r = self._section(scroll, r, "👤  Account", "Your profile information")

        info_card = T.card(scroll)
        info_card.grid(row=r, column=0, sticky="ew", pady=(0, 6))
        r += 1

        disp = self.auth_manager.get_display_name(self.username)
        self._row_info(info_card, "Logged in as",  disp)
        self._row_info(info_card, "Username (key)", self.username.lower())

        # ── Change Password Section ───────────────────────────────────
        r = self._section(scroll, r, "🔑  Change Account Password", "Update your sign-in password")

        pw_card = T.card(scroll)
        pw_card.grid(row=r, column=0, sticky="ew", pady=(0, 6))
        r += 1
        inner_pw = ctk.CTkFrame(pw_card, fg_color="transparent")
        inner_pw.pack(fill="x", padx=20, pady=16)
        inner_pw.grid_columnconfigure(1, weight=1)

        self._cur_pass_var  = ctk.StringVar()
        self._new_pass_var  = ctk.StringVar()
        self._conf_pass_var = ctk.StringVar()
        self._pw_status_var = ctk.StringVar()

        for rr, (lbl, var, ph) in enumerate([
            ("Current Password",  self._cur_pass_var,  "Enter current password"),
            ("New Password",      self._new_pass_var,  "Min. 4 characters"),
            ("Confirm New",       self._conf_pass_var, "Re-enter new password"),
        ]):
            ctk.CTkLabel(inner_pw, text=lbl, font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=T.TEXT_SECONDARY).grid(row=rr*2, column=0, sticky="w", pady=(8, 0), padx=(0, 12))
            T.entry(inner_pw, placeholder=ph, show="•", var=var,
                    height=36).grid(row=rr*2, column=1, sticky="ew", pady=(8, 0))

        self._pw_status = ctk.CTkLabel(inner_pw, textvariable=self._pw_status_var,
                                       font=ctk.CTkFont(size=11), text_color=T.DANGER)
        self._pw_status.grid(row=6, column=0, columnspan=2, sticky="w", pady=(8, 0))

        T.primary_btn(inner_pw, "Update Password", command=self._change_password,
                      height=38, width=160).grid(row=7, column=0, columnspan=2,
                                                  sticky="w", pady=(12, 0))

        # ── Parent Password Section ────────────────────────────────────
        r = self._section(scroll, r, "🔒  Change Parent Password",
                          "The password that gates monitoring controls")

        pp_card = T.card(scroll)
        pp_card.grid(row=r, column=0, sticky="ew", pady=(0, 6))
        r += 1
        inner_pp = ctk.CTkFrame(pp_card, fg_color="transparent")
        inner_pp.pack(fill="x", padx=20, pady=16)
        inner_pp.grid_columnconfigure(1, weight=1)

        self._cur_pp_var  = ctk.StringVar()
        self._new_pp_var  = ctk.StringVar()
        self._conf_pp_var = ctk.StringVar()
        self._pp_status_var = ctk.StringVar()

        for rr, (lbl, var, ph) in enumerate([
            ("Current Parent Password", self._cur_pp_var,  "Current parent password"),
            ("New Parent Password",     self._new_pp_var,  "Min. 4 characters"),
            ("Confirm New",             self._conf_pp_var, "Re-enter new parent password"),
        ]):
            ctk.CTkLabel(inner_pp, text=lbl, font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=T.TEXT_SECONDARY).grid(row=rr*2, column=0, sticky="w", pady=(8, 0), padx=(0, 12))
            T.entry(inner_pp, placeholder=ph, show="•", var=var,
                    height=36).grid(row=rr*2, column=1, sticky="ew", pady=(8, 0))

        self._pp_status = ctk.CTkLabel(inner_pp, textvariable=self._pp_status_var,
                                       font=ctk.CTkFont(size=11), text_color=T.DANGER)
        self._pp_status.grid(row=6, column=0, columnspan=2, sticky="w", pady=(8, 0))
        T.primary_btn(inner_pp, "Update Parent Password", command=self._change_parent_pw,
                      height=38, width=190).grid(row=7, column=0, columnspan=2,
                                                  sticky="w", pady=(12, 0))

        # ── Monitoring Preferences ───────────────────────────────────
        r = self._section(scroll, r, "🔍  Monitoring Preferences", "Adjust safety scan behavior")
        
        mon_wrap = T.card(scroll)
        mon_wrap.grid(row=r, column=0, sticky="ew", pady=(0, 6))
        r += 1
        
        ctk.CTkLabel(mon_wrap, text="📊 Monitoring Preferences", font=T.bold(14)).pack(side="top", anchor="w", padx=16, pady=(12, 8))
        
        # Email Notifications
        email_row = ctk.CTkFrame(mon_wrap, fg_color="transparent")
        email_row.pack(fill="x", padx=16, pady=4)
        ctk.CTkLabel(email_row, text="Email Alerts (High Risk)").pack(side="left")
        self.email_switch = ctk.CTkSwitch(email_row, text="", command=self._update_email_prefs)
        self.email_switch.pack(side="right")
        if self.monitor.email_enabled: self.email_switch.select()

        # Email Fields
        self.email_fields = ctk.CTkFrame(mon_wrap, fg_color="transparent")
        self.email_fields.pack(fill="x", padx=16, pady=(0, 10))
        
        self.email_var = ctk.StringVar(value=self.monitor.parent_email)
        T.entry(self.email_fields, placeholder="Parent Email (e.g. gmail)...", var=self.email_var).pack(fill="x", pady=2)
        
        self.pass_var = ctk.StringVar(value=self.monitor.app_password)
        T.entry(self.email_fields, placeholder="App Password...", show="*", var=self.pass_var).pack(fill="x", pady=2)
        
        T.primary_btn(self.email_fields, "Save & Test Email", command=self._test_email).pack(pady=5)

        # Original Interval settings
        int_row = ctk.CTkFrame(mon_wrap, fg_color="transparent")
        int_row.pack(fill="x", padx=16, pady=4)
        ctk.CTkLabel(int_row, text="Scan Interval (3-300s)").pack(side="left")
        self.interval_label = ctk.CTkLabel(int_row, text=f"{int(self.monitor.scan_interval)}s", text_color=T.CYAN)
        self.interval_label.pack(side="right")

        self.interval_slider = ctk.CTkSlider(mon_wrap, from_=3, to_=300, 
                                             command=self._update_scan_interval,
                                             button_color=T.CYAN, progress_color=T.CYAN)
        self.interval_slider.pack(fill="x", padx=16, pady=(0, 12))
        self.interval_slider.set(self.monitor.scan_interval)

        # ── About ─────────────────────────────────────────────────────
        r = self._section(scroll, r, "ℹ️  About SafeNet Kids", "")
        about = T.card(scroll)
        about.grid(row=r, column=0, sticky="ew", pady=(0, 6))
        r += 1
        self._row_info(about, "Version",     "2.0.0")
        self._row_info(about, "Build",       "2025.06")
        self._row_info(about, "Python",      "3.11+")
        self._row_info(about, "AI Modules",  "TensorFlow · NLTK · OpenCV")
        self._row_info(about, "License",     "MIT — Educational Use")

        # ── Danger Zone ───────────────────────────────────────────────
        r = self._section(scroll, r, "🚪  Session", "")
        T.danger_btn(scroll, "Logout", command=self.on_logout,
                     width=130, height=38).grid(row=r, column=0, sticky="w", pady=(0, 24))

    # ── Helpers ───────────────────────────────────────────────────────

    def _section(self, parent, row, title, subtitle):
        ctk.CTkLabel(parent, text=title,
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=T.CYAN).grid(row=row, column=0, sticky="w", pady=(18, 2))
        if subtitle:
            ctk.CTkLabel(parent, text=subtitle,
                         font=ctk.CTkFont(size=11),
                         text_color=T.TEXT_MUTED).grid(row=row+1, column=0, sticky="w", pady=(0, 6))
            return row + 2
        return row + 1

    def _row_info(self, card, label, value):
        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=5)
        ctk.CTkLabel(row, text=label, font=ctk.CTkFont(size=11),
                     text_color=T.TEXT_MUTED, width=180, anchor="w").pack(side="left")
        ctk.CTkLabel(row, text=value, font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=T.TEXT_PRIMARY).pack(side="left")

    def _change_password(self):
        cur  = self._cur_pass_var.get()
        new  = self._new_pass_var.get()
        conf = self._conf_pass_var.get()
        if not all([cur, new, conf]):
            return self._set_pw_err("All fields required.")
        ok, _ = self.auth_manager.login(self.username, cur)
        if not ok:
            return self._set_pw_err("Current password incorrect.")
        if new != conf:
            return self._set_pw_err("New passwords do not match.")
        if len(new) < 4:
            return self._set_pw_err("Min. 4 characters required.")
        # Patch via re-register keeping parent pw — reuse auth_manager internals
        import json, hashlib, secrets, os
        users_file = os.path.join("data", "users.json")
        with open(users_file, "r") as f:
            users = json.load(f)
        key  = self.username.lower()
        salt = secrets.token_hex(16)
        users[key]["salt"]            = salt
        users[key]["hashed_password"] = hashlib.sha256((salt + new).encode()).hexdigest()
        with open(users_file, "w") as f:
            json.dump(users, f, indent=2)
        self._pw_status_var.set("✅  Password updated successfully.")
        self._pw_status.configure(text_color=T.SUCCESS)
        for v in (self._cur_pass_var, self._new_pass_var, self._conf_pass_var):
            v.set("")

    def _set_pw_err(self, msg):
        self._pw_status_var.set(f"❌  {msg}")
        self._pw_status.configure(text_color=T.DANGER)

    def _change_parent_pw(self):
        cur  = self._cur_pp_var.get()
        new  = self._new_pp_var.get()
        conf = self._conf_pp_var.get()
        if not all([cur, new, conf]):
            return self._set_pp_err("All fields required.")
        if not self.auth_manager.verify_parent_password(self.username, cur):
            return self._set_pp_err("Current parent password incorrect.")
        if new != conf:
            return self._set_pp_err("New passwords do not match.")
        if len(new) < 4:
            return self._set_pp_err("Min. 4 characters required.")
        import json, hashlib, secrets, os
        users_file = os.path.join("data", "users.json")
        with open(users_file, "r") as f:
            users = json.load(f)
        key = self.username.lower()
        salt = secrets.token_hex(16)
        users[key]["parent_salt"]            = salt
        users[key]["parent_hashed_password"] = hashlib.sha256((salt + new).encode()).hexdigest()
        with open(users_file, "w") as f:
            json.dump(users, f, indent=2)
        self._pp_status_var.set("✅  Parent password updated successfully.")
        self._pp_status.configure(text_color=T.SUCCESS)
        for v in (self._cur_pp_var, self._new_pp_var, self._conf_pp_var):
            v.set("")

    def _set_pp_err(self, msg):
        self._pp_status_var.set(f"❌  {msg}")
        self._pp_status.configure(text_color=T.DANGER)

    def _update_scan_interval(self, val):
        self.monitor.scan_interval = int(val)
        self.interval_label.configure(text=f"{int(val)}s")

    def _update_email_prefs(self):
        self.monitor.email_enabled = self.email_switch.get() == 1

    def _test_email(self):
        self.monitor.notif_manager.parent_email = self.email_var.get()
        self.monitor.notif_manager.app_password = self.pass_var.get()
        self.monitor.notif_manager.send_email_alert("TEST ALERT", "Parent verified email setup", "Your SafeNet Remote Notifications are now working.")
