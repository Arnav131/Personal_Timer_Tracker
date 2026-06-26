"""
Progress Dashboard — dual progress ring indicators.

Displays Macro Progress % and Micro Progress % as animated arc rings.
Always visible between the navbar and content area.

Color transitions:
- 0-33%: amber (#d4a853)
- 34-66%: soft blue (#6ba3d6)
- 67-100%: sage green (#7cb899)
"""

import customtkinter as ctk
import tkinter as tk
import math


class Colors:
    BG = "#1e1e2e"
    SURFACE = "#2a2a3e"
    ACCENT = "#d4a853"
    TEXT = "#f0e9d6"
    TEXT_SEC = "#a0998a"
    SUCCESS = "#7cb899"
    BLUE_MID = "#6ba3d6"
    BORDER = "#3a3a52"


def get_progress_color(pct):
    """Return color based on progress percentage."""
    if pct <= 33:
        return Colors.ACCENT   # Amber
    elif pct <= 66:
        return Colors.BLUE_MID  # Soft blue
    else:
        return Colors.SUCCESS   # Sage green


class ProgressRing(ctk.CTkFrame):
    """A single progress ring with percentage display."""

    def __init__(self, parent, title="Progress", subtitle="", size=100):
        super().__init__(parent, fg_color="transparent")

        self._target_pct = 0.0
        self._current_pct = 0.0
        self._size = size
        self._line_width = 8
        self._animating = False

        # Canvas for the arc
        self.canvas = tk.Canvas(
            self,
            width=size,
            height=size,
            bg=Colors.SURFACE,
            highlightthickness=0,
        )
        self.canvas.pack(pady=(8, 2))

        # Percentage label
        self.pct_label = ctk.CTkLabel(
            self,
            text="0%",
            font=ctk.CTkFont(family="Consolas", size=20, weight="bold"),
            text_color=Colors.TEXT,
            fg_color="transparent",
        )
        self.pct_label.place(relx=0.5, rely=0.42, anchor="center")

        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=Colors.TEXT,
            fg_color="transparent",
        )
        self.title_label.pack(pady=(0, 0))

        # Subtitle
        self.subtitle_label = ctk.CTkLabel(
            self,
            text=subtitle,
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=Colors.TEXT_SEC,
            fg_color="transparent",
        )
        self.subtitle_label.pack(pady=(0, 4))

        # Initial draw
        self._draw_ring(0)

    def _draw_ring(self, pct):
        """Draw the progress arc ring."""
        self.canvas.delete("all")

        pad = self._line_width + 4
        s = self._size

        # Background ring (track)
        self.canvas.create_arc(
            pad, pad, s - pad, s - pad,
            start=90, extent=-360,
            outline=Colors.BORDER,
            width=self._line_width,
            style="arc",
        )

        # Progress arc
        if pct > 0:
            extent = -(pct / 100) * 360
            color = get_progress_color(pct)
            self.canvas.create_arc(
                pad, pad, s - pad, s - pad,
                start=90, extent=extent,
                outline=color,
                width=self._line_width + 1,
                style="arc",
            )

    def set_progress(self, pct):
        """Set target progress and animate to it."""
        self._target_pct = max(0, min(100, pct))
        if not self._animating:
            self._animate()

    def _animate(self):
        """Smoothly animate the ring fill."""
        self._animating = True
        diff = self._target_pct - self._current_pct

        if abs(diff) < 0.5:
            self._current_pct = self._target_pct
            self._draw_ring(self._current_pct)
            self.pct_label.configure(text=f"{int(self._current_pct)}%")
            color = get_progress_color(self._current_pct)
            self.pct_label.configure(text_color=color)
            self._animating = False
            return

        # Ease towards target
        self._current_pct += diff * 0.15
        self._draw_ring(self._current_pct)
        self.pct_label.configure(text=f"{int(self._current_pct)}%")
        color = get_progress_color(self._current_pct)
        self.pct_label.configure(text_color=color)

        self.after(30, self._animate)


class ProgressDashboard(ctk.CTkFrame):
    """Dashboard strip showing Macro and Micro progress rings side by side."""

    def __init__(self, parent, data_manager):
        super().__init__(parent, fg_color=Colors.SURFACE, corner_radius=12, height=150)
        self.pack_propagate(False)
        self.data_manager = data_manager

        # Container for rings
        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(expand=True)

        # Macro ring
        self.macro_ring = ProgressRing(
            inner,
            title="Macro Progress",
            subtitle="Study & Tasks",
            size=110,
        )
        self.macro_ring.pack(side="left", padx=40)

        # Divider
        divider = ctk.CTkFrame(
            inner, fg_color=Colors.BORDER, width=1, height=80
        )
        divider.pack(side="left", padx=20, pady=20)

        # Micro ring
        self.micro_ring = ProgressRing(
            inner,
            title="Micro Progress",
            subtitle="Daily Habits",
            size=110,
        )
        self.micro_ring.pack(side="left", padx=40)

        # Initial update
        self.update_progress()

    def update_progress(self):
        """Refresh both progress rings with current data."""
        macro_pct = self.data_manager.get_macro_progress()
        micro_pct = self.data_manager.get_micro_progress()
        self.macro_ring.set_progress(macro_pct)
        self.micro_ring.set_progress(micro_pct)
