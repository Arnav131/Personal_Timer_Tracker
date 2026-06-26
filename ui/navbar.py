"""
Navigation Bar — top bar of the Productivity Enforcer window.

Contains:
- App name (left)
- Current date+time (center-right)
- PDF download button
- Window control buttons (minimize, maximize, close)
- Custom drag region for moving the frameless window
"""

import customtkinter as ctk
from datetime import datetime


class Colors:
    BG = "#1e1e2e"
    SURFACE = "#2a2a3e"
    ACCENT = "#d4a853"
    ACCENT_SOFT = "#c8956c"
    TEXT = "#f0e9d6"
    TEXT_SEC = "#a0998a"
    BORDER = "#3a3a52"
    HOVER = "#353550"
    DANGER = "#c75050"


class NavBar(ctk.CTkFrame):
    """Custom navigation bar with drag support and window controls."""

    def __init__(self, parent, on_minimize, on_maximize, on_close, on_pdf, app):
        super().__init__(parent, fg_color=Colors.SURFACE, height=48, corner_radius=0)
        self.pack_propagate(False)
        self.app = app
        self.on_pdf = on_pdf

        # ── Drag binding ──
        self.bind("<Button-1>", self.app.start_drag)
        self.bind("<B1-Motion>", self.app.do_drag)

        # ── Left: App Name ──
        self.app_name = ctk.CTkLabel(
            self,
            text="✦  Productivity Enforcer",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color=Colors.ACCENT,
            fg_color="transparent",
        )
        self.app_name.pack(side="left", padx=16)
        self.app_name.bind("<Button-1>", self.app.start_drag)
        self.app_name.bind("<B1-Motion>", self.app.do_drag)

        # ── Right: Window Controls ──
        controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        controls_frame.pack(side="right", padx=8)

        # Close button
        close_btn = ctk.CTkButton(
            controls_frame,
            text="✕",
            font=ctk.CTkFont(size=14),
            fg_color="transparent",
            hover_color=Colors.DANGER,
            text_color=Colors.TEXT_SEC,
            width=36,
            height=32,
            corner_radius=6,
            command=on_close,
        )
        close_btn.pack(side="right", padx=2)

        # Maximize button
        max_btn = ctk.CTkButton(
            controls_frame,
            text="□",
            font=ctk.CTkFont(size=13),
            fg_color="transparent",
            hover_color=Colors.HOVER,
            text_color=Colors.TEXT_SEC,
            width=36,
            height=32,
            corner_radius=6,
            command=on_maximize,
        )
        max_btn.pack(side="right", padx=2)

        # Minimize button
        min_btn = ctk.CTkButton(
            controls_frame,
            text="─",
            font=ctk.CTkFont(size=13),
            fg_color="transparent",
            hover_color=Colors.HOVER,
            text_color=Colors.TEXT_SEC,
            width=36,
            height=32,
            corner_radius=6,
            command=on_minimize,
        )
        min_btn.pack(side="right", padx=2)

        # PDF Download button
        pdf_btn = ctk.CTkButton(
            controls_frame,
            text="📥 PDF",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color=Colors.ACCENT,
            hover_color=Colors.ACCENT_SOFT,
            text_color="#1e1e2e",
            width=70,
            height=30,
            corner_radius=8,
            command=self.on_pdf,
        )
        pdf_btn.pack(side="right", padx=8)

        # ── Center-Right: Date & Time ──
        self.time_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=Colors.TEXT_SEC,
            fg_color="transparent",
        )
        self.time_label.pack(side="right", padx=16)
        self.time_label.bind("<Button-1>", self.app.start_drag)
        self.time_label.bind("<B1-Motion>", self.app.do_drag)

        self.update_time()

    def update_time(self):
        """Update the date/time display."""
        now = datetime.now()
        date_str = now.strftime("%A, %B %d, %Y")
        time_str = now.strftime("%I:%M:%S %p")
        self.time_label.configure(text=f"{date_str}  •  {time_str}")
