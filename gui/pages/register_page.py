"""gui/pages/register_page.py — Registration page."""
import customtkinter as ctk
from gui import theme as T


class RegisterPage(ctk.CTkFrame):
    """
    Full-window registration form.
    Calls on_registered(username) on success, on_back() to return to login.
    """

    def __init__(self, master, auth_manager, on_registered, on_back):
        super().__init__(master, fg_color=T.BG_PRIMARY, corner_radius=0)
        self.auth_manager = auth_manager
        self.on_registered = on_registered
        self.on_back = on_back

        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

        self._build_left()
        self._build_right()

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
        ctk.CTkLabel(inner, text="Create a Parent Account",
                     font=ctk.CTkFont(size=11),
                     text_color=T.TEXT_SECONDARY).pack(pady=(4, 28))

        steps = [
            ("①", "Create your parent account"),
            ("②", "Set a secure parent password"),
            ("③", "Monitor your child's activity"),
        ]
        for num, text in steps:
            row = ctk.CTkFrame(inner, fg_color=T.BG_CARD, corner_radius=8)
            row.pack(fill="x", pady=5, ipady=8, ipadx=10)
            ctk.CTkLabel(row, text=num,
                         font=ctk.CTkFont(size=16, weight="bold"),
                         text_color=T.CYAN).pack(side="left", padx=(12, 8))
            ctk.CTkLabel(row, text=text,
                         font=ctk.CTkFont(size=12),
                         text_color=T.TEXT_SECONDARY).pack(side="left")

    def _build_right(self):
        right = ctk.CTkFrame(self, fg_color=T.BG_PRIMARY, corner_radius=0)
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_rowconfigure(0, weight=1)
        right.grid_columnconfigure(0, weight=1)

        card = ctk.CTkFrame(right, fg_color=T.BG_CARD,
                            corner_radius=16, border_width=1, border_color=T.BORDER)
        card.grid(row=0, column=0, padx=60, pady=40, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(0, weight=1)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.grid(row=0, column=0, padx=36, pady=30, sticky="nsew")
        inner.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(inner, text="Create Account",
                     font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
                     text_color=T.TEXT_PRIMARY).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(inner, text="Fill in the details below to register",
                     font=ctk.CTkFont(size=12),
                     text_color=T.TEXT_SECONDARY).grid(row=1, column=0, sticky="w", pady=(2, 16))

        self._status_var = ctk.StringVar()
        self._status_lbl = ctk.CTkLabel(inner, textvariable=self._status_var,
                                        font=ctk.CTkFont(size=12),
                                        text_color=T.DANGER, height=18)
        self._status_lbl.grid(row=2, column=0, sticky="w", pady=(0, 4))

        self._user_var    = ctk.StringVar()
        self._pass_var    = ctk.StringVar()
        self._confirm_var = ctk.StringVar()
        self._parent_var  = ctk.StringVar()

        def field(row, label, var, show="", placeholder=""):
            ctk.CTkLabel(inner, text=label, font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=T.TEXT_SECONDARY).grid(row=row, column=0, sticky="w")
            T.entry(inner, placeholder=placeholder, show=show,
                    var=var).grid(row=row+1, column=0, sticky="ew", pady=(3, 10))

        field(3,  "Username",         self._user_var,    placeholder="Choose a username")
        field(5,  "Password",         self._pass_var,    show="•", placeholder="Min. 4 characters")
        field(7,  "Confirm Password", self._confirm_var, show="•", placeholder="Re-enter password")

        # Parent password section
        ctk.CTkFrame(inner, height=1, fg_color=T.BORDER).grid(row=9, column=0, sticky="ew", pady=6)
        ctk.CTkLabel(inner,
                     text="🔒  Parent / Admin Password",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=T.CYAN).grid(row=10, column=0, sticky="w")
        ctk.CTkLabel(inner,
                     text="Used to gate monitoring controls. Keep it secret from your child.",
                     font=ctk.CTkFont(size=10),
                     text_color=T.TEXT_MUTED).grid(row=11, column=0, sticky="w", pady=(0, 4))
        T.entry(inner, placeholder="Set a parent password", show="•",
                var=self._parent_var).grid(row=12, column=0, sticky="ew", pady=(0, 16))

        T.primary_btn(inner, "Create Account →", command=self._do_register,
                      height=44).grid(row=13, column=0, sticky="ew")

        back = ctk.CTkButton(inner, text="← Back to Sign In",
                             fg_color="transparent", hover_color=T.BG_HOVER,
                             text_color=T.TEXT_SECONDARY,
                             font=ctk.CTkFont(size=12), command=self.on_back,
                             cursor="hand2")
        back.grid(row=14, column=0, pady=(10, 0))

    def _do_register(self):
        u  = self._user_var.get().strip()
        p  = self._pass_var.get()
        c  = self._confirm_var.get()
        pp = self._parent_var.get()

        if not all([u, p, c, pp]):
            self._err("All fields are required.")
            return
        if p != c:
            self._err("Passwords do not match.")
            return

        ok, err = self.auth_manager.register(u, p, pp)
        if ok:
            self._status_var.set(f"✅  Account created! Welcome, {u}!")
            self._status_lbl.configure(text_color=T.SUCCESS)
            display = self.auth_manager.get_display_name(u)
            self.after(700, lambda: self.on_registered(display))
        else:
            self._err(err)

    def _err(self, msg):
        self._status_var.set(f"❌  {msg}")
        self._status_lbl.configure(text_color=T.DANGER)

    def reset(self):
        for v in (self._user_var, self._pass_var, self._confirm_var, self._parent_var):
            v.set("")
        self._status_var.set("")
