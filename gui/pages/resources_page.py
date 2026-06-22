import customtkinter as ctk
from gui import theme as T

class ResourcesPage(ctk.CTkFrame):
    """
    Parental Resources and Digital Safety Tips page.
    """

    def __init__(self, master):
        super().__init__(master, fg_color=T.BG_PRIMARY, corner_radius=0)
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Header
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0, column=0, padx=28, pady=(24, 0), sticky="ew")
        
        ctk.CTkLabel(hdr, text="🛡️  Safety Resources",
                     font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
                     text_color=T.TEXT_PRIMARY).pack(side="left")

        ctk.CTkLabel(self, text="Educational tips and tools for maintaining a safe digital environment",
                     font=ctk.CTkFont(size=12), text_color=T.TEXT_SECONDARY
                     ).grid(row=1, column=0, padx=28, sticky="w", pady=(2, 16))

        # Scrollable Content
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.grid(row=2, column=0, sticky="nsew", padx=10)
        scroll.grid_columnconfigure(0, weight=1)

        # 1. Digital Safety Tips
        self._add_section(scroll, "💡  Digital Safety Tips", [
            ("Set Clear Boundaries", "Establish specific 'tech-free' times and define which apps/sites are allowed."),
            ("Open Conversation", "Regularly talk to your child about what they encounter online. Safety is built on trust, not just tools."),
            ("Shared Spaces", "Encourage internet use in common areas like the living room rather than isolated bedrooms."),
            ("Privacy Matters", "Teach children to never share PII (Personal Identifiable Information) like addresses or phone numbers.")
        ])

        # 2. Recommended Resources
        self._add_section(scroll, "🔗  Helpful Links", [
            ("Common Sense Media", "Independent reviews and age-based ratings for movies, games, and apps."),
            ("Insafe (Better Internet for Kids)", "European network provides resources for safe and responsible internet use."),
            ("ConnectSafely", "Safety tips, parents' guides, and advice on social media and technology.")
        ])

        # 3. SafeNet Documentation
        self._add_section(scroll, "📖  App Documentation", [
            ("Threat Database", "Use the 'Database' tab to add specific slang or blocked applications unique to your needs."),
            ("AI Risk Score", "The Home Page provides a behavioral score. High Risk indicates repeated attempts to access harmful content."),
            ("Evidence Storage", "All screenshots for detected threats are stored in 'data/evidence/' for your review.")
        ])

    def _add_section(self, parent, title, items):
        section = ctk.CTkFrame(parent, fg_color=T.BG_SECONDARY, corner_radius=12)
        section.pack(fill="x", padx=18, pady=10)
        
        ctk.CTkLabel(section, text=title, 
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=T.CYAN).pack(anchor="w", padx=16, pady=(12, 8))

        for item_title, item_desc in items:
            item_frame = ctk.CTkFrame(section, fg_color="transparent")
            item_frame.pack(fill="x", padx=16, pady=4)
            
            ctk.CTkLabel(item_frame, text=f"• {item_title}:", 
                         font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=T.TEXT_PRIMARY).pack(side="left")
            
            ctk.CTkLabel(item_frame, text=item_desc, 
                         font=ctk.CTkFont(size=12),
                         text_color=T.TEXT_SECONDARY,
                         wraplength=600, justify="left").pack(side="left", padx=5)

        ctk.CTkLabel(section, text="", height=10).pack() # Spacer
