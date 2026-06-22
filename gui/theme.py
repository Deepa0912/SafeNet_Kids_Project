# gui/theme.py  — Shared design tokens for SafeNet Kids UI

# ── Background layers ───────────────────────────────────────────────
BG_ROOT     = "#080C18"   # deepest background
BG_PRIMARY  = "#0A0E1A"   # main window bg
BG_SIDEBAR  = "#0D1321"   # sidebar
BG_CARD     = "#111827"   # card surface
BG_CARD2    = "#1A2035"   # elevated card
BG_INPUT    = "#0F172A"   # input fields
BG_HOVER    = "#1E293B"   # hover state

# ── Accent / brand colors ───────────────────────────────────────────
CYAN        = "#00D4FF"   # primary accent (cyber cyan)
CYAN_DIM    = "#0EA5E9"   # softer cyan
CYAN_DARK   = "#0369A1"   # dark cyan for hover
PURPLE      = "#7C3AED"   # secondary accent
PURPLE_DIM  = "#6D28D9"

# ── Semantic colors ─────────────────────────────────────────────────
SUCCESS     = "#10B981"
SUCCESS_DIM = "#065F46"
DANGER      = "#EF4444"
DANGER_DIM  = "#7F1D1D"
WARNING     = "#F59E0B"
WARNING_DIM = "#78350F"
INFO        = "#3B82F6"

# ── Text ────────────────────────────────────────────────────────────
TEXT_PRIMARY   = "#F1F5F9"
TEXT_SECONDARY = "#94A3B8"
TEXT_MUTED     = "#475569"
TEXT_BRIGHT    = "#FFFFFF"

# ── Border / divider ────────────────────────────────────────────────
BORDER      = "#1E293B"
BORDER_DIM  = "#0F172A"

# ── Fonts ────────────────────────────────────────────────────────────
import customtkinter as ctk

def font(size=13, weight="normal", family="Segoe UI"):
    return ctk.CTkFont(family=family, size=size, weight=weight)

def bold(size=13, family="Segoe UI"):
    return font(size, "bold", family)

# ── Reusable widget factories ────────────────────────────────────────

def card(master, **kwargs):
    defaults = dict(fg_color=BG_CARD, corner_radius=12, border_width=1, border_color=BORDER)
    defaults.update(kwargs)
    return ctk.CTkFrame(master, **defaults)

def card2(master, **kwargs):
    defaults = dict(fg_color=BG_CARD2, corner_radius=10, border_width=1, border_color=BORDER)
    defaults.update(kwargs)
    return ctk.CTkFrame(master, **defaults)

def heading(master, text, size=18, color=TEXT_PRIMARY, **kwargs):
    return ctk.CTkLabel(master, text=text, font=bold(size), text_color=color, **kwargs)

def sub(master, text, size=12, color=TEXT_SECONDARY, **kwargs):
    return ctk.CTkLabel(master, text=text, font=font(size), text_color=color, **kwargs)

def primary_btn(master, text, command=None, width=160, height=42, **kwargs):
    return ctk.CTkButton(
        master, text=text, command=command, width=width, height=height,
        fg_color=CYAN, hover_color=CYAN_DARK, text_color="#000000",
        font=bold(13), corner_radius=8, **kwargs
    )

def danger_btn(master, text, command=None, width=160, height=38, **kwargs):
    return ctk.CTkButton(
        master, text=text, command=command, width=width, height=height,
        fg_color=DANGER, hover_color="#B91C1C", text_color=TEXT_BRIGHT,
        font=bold(13), corner_radius=8, **kwargs
    )

def ghost_btn(master, text, command=None, width=160, height=38, **kwargs):
    return ctk.CTkButton(
        master, text=text, command=command, width=width, height=height,
        fg_color="transparent", hover_color=BG_HOVER,
        border_width=1, border_color=BORDER,
        text_color=TEXT_SECONDARY, font=font(13), corner_radius=8, **kwargs
    )

def entry(master, placeholder="", show="", var=None, **kwargs):
    defaults = dict(
        fg_color=BG_INPUT, border_color=BORDER,
        text_color=TEXT_PRIMARY,
        placeholder_text_color=TEXT_MUTED,
        font=font(13), height=42, corner_radius=8,
        placeholder_text=placeholder,
    )
    if show:
        defaults["show"] = show
    if var:
        defaults["textvariable"] = var
    defaults.update(kwargs)
    return ctk.CTkEntry(master, **defaults)

def divider(master, color=BORDER, **kwargs):
    return ctk.CTkFrame(master, height=1, fg_color=color, **kwargs)

def badge(master, text, color=CYAN, bg=None, **kwargs):
    bg = bg or BG_CARD2
    f = ctk.CTkFrame(master, fg_color=bg, corner_radius=6, **kwargs)
    ctk.CTkLabel(f, text=text, font=bold(10), text_color=color).pack(padx=8, pady=3)
    return f

def status_dot(master, color=SUCCESS):
    return ctk.CTkFrame(master, width=10, height=10, corner_radius=5, fg_color=color)
