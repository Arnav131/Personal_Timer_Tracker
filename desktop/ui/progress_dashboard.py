"""
Progress Dashboard — dual progress ring indicators.

Premium glass-panel design showing:
- Macro Progress % and Micro Progress % as animated arc rings
- Glass container with border glow
- Color transitions based on completion percentage
"""

import customtkinter as ctk
import tkinter as tk
import math


def get_progress_color(pct, theme):
    """Return color based on progress percentage."""
    if pct <= 33:
        return theme.accent    # Accent color
    elif pct <= 66:
        return theme.blue      # Soft blue
    else:
        return theme.success   # Sage green


class ProgressRing(ctk.CTkFrame):
    """A single progress ring with percentage display — glass themed."""

    def __init__(self, parent, title="Progress", subtitle="", size=110, theme=None):
        super().__init__(parent, fg_color="transparent")

        self.theme = theme
        self._target_pct = 0.0
        self._current_pct = 0.0
        self._size = size
        self._line_width = 6
        self._animating = False

        # Canvas for the arc
        self.canvas = tk.Canvas(
            self,
            width=size,
            height=size,
            bg=theme.surface,
            highlightthickness=0,
        )
        self.canvas.pack(pady=(8, 2))

        # Percentage label
        self.pct_label = ctk.CTkLabel(
            self,
            text="0%",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=theme.text,
            fg_color="transparent",
        )
        self.pct_label.place(relx=0.5, rely=0.42, anchor="center")

        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=theme.text,
            fg_color="transparent",
        )
        self.title_label.pack(pady=(0, 0))

        # Subtitle
        self.subtitle_label = ctk.CTkLabel(
            self,
            text=subtitle,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=theme.text_sec,
            fg_color="transparent",
        )
        self.subtitle_label.pack(pady=(0, 4))

        # Initial draw
        self._draw_ring(0)

    def _draw_ring(self, pct):
        """Draw the progress arc ring."""
        self.canvas.delete("all")

        pad = self._line_width + 6
        s = self._size

        # Background ring (track)
        self.canvas.create_arc(
            pad, pad, s - pad, s - pad,
            start=90, extent=-360,
            outline=self.theme.border,
            width=self._line_width,
            style="arc",
        )

        # Progress arc
        if pct > 0:
            extent = -(pct / 100) * 360
            color = get_progress_color(pct, self.theme)
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
            color = get_progress_color(self._current_pct, self.theme)
            self.pct_label.configure(text_color=color)
            self._animating = False
            return

        # Ease towards target
        self._current_pct += diff * 0.15
        self._draw_ring(self._current_pct)
        self.pct_label.configure(text=f"{int(self._current_pct)}%")
        color = get_progress_color(self._current_pct, self.theme)
        self.pct_label.configure(text_color=color)

        self.after(30, self._animate)


class ProgressDashboard(ctk.CTkFrame):
    """Dashboard strip showing Macro and Micro progress — glass panel."""

    def __init__(self, parent, data_manager, theme):
        super().__init__(
            parent,
            fg_color=theme.surface,
            corner_radius=14,
            height=155,
            border_width=1,
            border_color=theme.border,
        )
        self.pack_propagate(False)
        self.data_manager = data_manager
        self.theme = theme

        # Container for rings
        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(expand=True)

        # Macro ring
        self.macro_ring = ProgressRing(
            inner,
            title="Macro Progress",
            subtitle="Study & Tasks",
            size=110,
            theme=theme,
        )
        self.macro_ring.pack(side="left", padx=50)

        # Divider
        divider = ctk.CTkFrame(
            inner, fg_color=theme.border, width=1, height=80
        )
        divider.pack(side="left", padx=24, pady=20)

        # Micro ring
        self.micro_ring = ProgressRing(
            inner,
            title="Micro Progress",
            subtitle="Daily Habits",
            size=110,
            theme=theme,
        )
        self.micro_ring.pack(side="left", padx=50)

        # Initial update
        self.update_progress()

    def update_progress(self):
        """Refresh both progress rings with current data."""
        macro_pct = self.data_manager.get_macro_progress()
        micro_pct = self.data_manager.get_micro_progress()
        self.macro_ring.set_progress(macro_pct)
        self.micro_ring.set_progress(micro_pct)
