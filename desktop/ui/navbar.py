"""
Navigation Bar — top bar of the Productivity Enforcer window.

Premium glass-panel style with:
- App name (left)
- Current date+time (center-right)
- PDF download button
- Settings button
- Window control buttons (minimize, maximize, close)
- Custom drag region for moving the frameless window
"""

import customtkinter as ctk
from datetime import datetime


class NavBar(ctk.CTkFrame):
    """Custom navigation bar with glass styling, drag support, and window controls."""

    def __init__(self, parent, on_minimize, on_maximize, on_close, on_pdf, on_settings, app, theme):
        super().__init__(
            parent,
            fg_color=theme.surface,
            height=52,
            corner_radius=0,
            border_width=0,
        )
        self.pack_propagate(False)
        self.app = app
        self.theme = theme
        self.on_pdf = on_pdf
        self.on_settings = on_settings

        # ── Drag binding ──
        self.bind("<Button-1>", self.app.start_drag)
        self.bind("<B1-Motion>", self.app.do_drag)

        # ── Left: App Name ──
        self.app_name = ctk.CTkLabel(
            self,
            text="✦  Productivity Enforcer",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=theme.accent,
            fg_color="transparent",
        )
        self.app_name.pack(side="left", padx=20)
        self.app_name.bind("<Button-1>", self.app.start_drag)
        self.app_name.bind("<B1-Motion>", self.app.do_drag)

        # ── Right: Window Controls ──
        controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        controls_frame.pack(side="right", padx=10)

        # Close button
        close_btn = ctk.CTkButton(
            controls_frame,
            text="✕",
            font=ctk.CTkFont(size=14),
            fg_color="transparent",
            hover_color=theme.danger,
            text_color=theme.text_sec,
            width=38,
            height=34,
            corner_radius=8,
            command=on_close,
        )
        close_btn.pack(side="right", padx=2)

        # Maximize button
        max_btn = ctk.CTkButton(
            controls_frame,
            text="□",
            font=ctk.CTkFont(size=13),
            fg_color="transparent",
            hover_color=theme.hover,
            text_color=theme.text_sec,
            width=38,
            height=34,
            corner_radius=8,
            command=on_maximize,
        )
        max_btn.pack(side="right", padx=2)

        # Minimize button
        min_btn = ctk.CTkButton(
            controls_frame,
            text="─",
            font=ctk.CTkFont(size=13),
            fg_color="transparent",
            hover_color=theme.hover,
            text_color=theme.text_sec,
            width=38,
            height=34,
            corner_radius=8,
            command=on_minimize,
        )
        min_btn.pack(side="right", padx=2)

        # Settings button
        settings_btn = ctk.CTkButton(
            controls_frame,
            text="⚙",
            font=ctk.CTkFont(size=16),
            fg_color="transparent",
            hover_color=theme.hover,
            text_color=theme.text_sec,
            width=38,
            height=34,
            corner_radius=8,
            command=self.on_settings,
        )
        settings_btn.pack(side="right", padx=2)

        # PDF Download button
        pdf_btn = ctk.CTkButton(
            controls_frame,
            text="📥 PDF",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color=theme.accent,
            hover_color=theme.accent_soft,
            text_color="#0a0a14",
            width=72,
            height=32,
            corner_radius=8,
            command=self.on_pdf,
        )
        pdf_btn.pack(side="right", padx=8)

        # ── Center-Right: Date & Time ──
        self.time_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=theme.text_sec,
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
