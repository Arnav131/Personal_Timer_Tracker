"""
Break Decision Prompt — glass-styled modal after Pomodoro session ends.

Three options:
1. Take a Break (10 min) — starts break countdown
2. Do a Micro Task — switches to Micro view
3. Continue Studying — starts next work session immediately
"""

import customtkinter as ctk


class BreakPrompt(ctk.CTkToplevel):
    """Glass-styled modal overlay for the Break Decision Prompt."""

    def __init__(self, parent, data_manager, audio_manager, app, theme):
        super().__init__(parent)

        self.data_manager = data_manager
        self.audio_manager = audio_manager
        self.app = app
        self.theme = theme

        # ── Window Configuration ──
        self.title("Session Complete")
        self.geometry("480x380")
        self.resizable(False, False)
        self.configure(fg_color=theme.bg)

        # Make modal — prevent interaction with main window
        self.transient(parent)
        self.grab_set()

        # Disable close
        self.protocol("WM_DELETE_WINDOW", lambda: None)

        # Center on parent
        self.update_idletasks()
        px = parent.winfo_x() + (parent.winfo_width() - 480) // 2
        py = parent.winfo_y() + (parent.winfo_height() - 380) // 2
        self.geometry(f"480x380+{px}+{py}")

        self._build_ui()

        # Force focus
        self.focus_force()
        self.lift()

    def _build_ui(self):
        """Build the glass-styled prompt UI."""
        # Glass container
        container = ctk.CTkFrame(
            self,
            fg_color=self.theme.surface,
            corner_radius=18,
            border_width=1,
            border_color=self.theme.border,
        )
        container.pack(fill="both", expand=True, padx=10, pady=10)

        # Title
        ctk.CTkLabel(
            container,
            text="🎉  Session Complete!",
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color=self.theme.accent,
        ).pack(pady=(30, 4))

        ctk.CTkLabel(
            container,
            text="Great work! What's next?",
            font=ctk.CTkFont(family="Segoe UI", size=15),
            text_color=self.theme.text_sec,
        ).pack(pady=(0, 24))

        # ── Option Buttons (pill-shaped) ──

        # Take a Break
        break_btn = ctk.CTkButton(
            container,
            text="☕   Take a Break (10 min)",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            fg_color=self.theme.blue,
            hover_color="#5a92c5",
            text_color="#ffffff",
            width=360,
            height=52,
            corner_radius=26,
            command=self._take_break,
        )
        break_btn.pack(pady=5)

        # Do a Micro Task
        micro_btn = ctk.CTkButton(
            container,
            text="⚡   Do a Micro Task",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            fg_color=self.theme.accent_soft,
            hover_color="#b07f5a",
            text_color="#ffffff",
            width=360,
            height=52,
            corner_radius=26,
            command=self._do_micro,
        )
        micro_btn.pack(pady=5)

        # Continue Studying
        continue_btn = ctk.CTkButton(
            container,
            text="📖   Continue Studying",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            fg_color=self.theme.success,
            hover_color="#69a584",
            text_color="#0a0a14",
            width=360,
            height=52,
            corner_radius=26,
            command=self._continue_study,
        )
        continue_btn.pack(pady=5)

    def _take_break(self):
        """Start break countdown."""
        self.destroy()
        # Start break timer on the Pomodoro widget
        pomodoro = self.app.macro_view.pomodoro
        pomodoro.start_break_timer()

    def _do_micro(self):
        """Switch to Micro view."""
        self.destroy()
        self.app.switch_mode("micro")
        # The micro view will show a "Back to Study" button
        self.app.micro_view.show_back_to_study_button()

    def _continue_study(self):
        """Start next Pomodoro session immediately."""
        self.destroy()
        pomodoro = self.app.macro_view.pomodoro
        pomodoro.start_work_session()
